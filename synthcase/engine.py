from copy import deepcopy
import hashlib
import json
import random
import re
import sqlite3
import time

from ortools.sat.python import cp_model

OPS = {"==": lambda a,b:a==b, "!=": lambda a,b:a!=b, ">=":lambda a,b:a>=b,
       ">":lambda a,b:a>b, "<=":lambda a,b:a<=b, "<":lambda a,b:a<b}
INVERSE = {"==":"!=", "!=":"==", ">=":"<", ">":"<=", "<=":">", "<":">="}


def expression_valid(expression, variables, depth=0):
    if not isinstance(expression, dict) or depth > 5:
        return False
    for key in ("all", "any"):
        if key in expression:
            children = expression[key]
            return isinstance(children, list) and 1 <= len(children) <= 20 and all(expression_valid(c,variables,depth+1) for c in children)
    if "not" in expression:
        return expression_valid(expression["not"],variables,depth+1)
    terms = expression.get("terms")
    return isinstance(terms, dict) and 1 <= len(terms) <= 20 and all(k in variables and type(v) is int and abs(v)<=10000 for k,v in terms.items()) and expression.get("op") in OPS and type(expression.get("rhs")) is int and abs(expression["rhs"])<=10**9


def validate(spec):
    if not isinstance(spec, dict) or not isinstance(spec.get("variables"), dict) or not 1 <= len(spec["variables"]) <= 20:
        raise ValueError("invalid_variables")
    variables = spec["variables"]
    for name, bounds in variables.items():
        if not isinstance(name,str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,50}",name) or not isinstance(bounds,list) or len(bounds)!=2 or any(type(x) is not int or abs(x)>1_000_000 for x in bounds) or bounds[0]>bounds[1]:
            raise ValueError("invalid_variable")
    constraints = spec.get("constraints",{})
    labels = spec.get("labels",{})
    if not isinstance(constraints,dict) or len(constraints)>40 or not isinstance(labels,dict) or not 1<=len(labels)<=20:
        raise ValueError("invalid_predicates")
    for key, predicate in list(constraints.items()) + list(labels.items()):
        if not isinstance(key,str) or not key or not expression_valid(predicate,variables):
            raise ValueError("invalid_predicate")
    products = spec.get("products",[])
    if not isinstance(products,list) or len(products)>20:
        raise ValueError("invalid_products")
    for item in products:
        if not isinstance(item,dict) or any(item.get(k) not in variables for k in ("out","left","right")):
            raise ValueError("invalid_product")
    immutable = spec.get("immutable",[])
    if not isinstance(immutable,list) or any(k not in variables for k in immutable):
        raise ValueError("invalid_immutable")
    cohorts = spec.get("cohorts",[])
    if not isinstance(cohorts,list) or not 1<=len(cohorts)<=20:
        raise ValueError("invalid_cohorts")
    total = 0
    names = set()
    for cohort in cohorts:
        if not isinstance(cohort,dict) or not isinstance(cohort.get("id"),str) or not cohort["id"] or cohort["id"] in names or type(cohort.get("count")) is not int or not 0<=cohort["count"]<=50:
            raise ValueError("invalid_cohort")
        names.add(cohort["id"])
        total += cohort["count"]
        requirements = cohort.get("require",{})
        if not isinstance(requirements,dict) or any(k not in labels or type(v) is not bool for k,v in requirements.items()):
            raise ValueError("invalid_cohort_requirements")
    if not 1<=total<=100:
        raise ValueError("invalid_total_count")
    return variables


def evaluate(expression, row):
    """Independent Python predicate evaluation, without CP-SAT variables."""
    if "all" in expression:
        return all(evaluate(c,row) for c in expression["all"])
    if "any" in expression:
        return any(evaluate(c,row) for c in expression["any"])
    if "not" in expression:
        return not evaluate(expression["not"],row)
    value = sum(row[k]*v for k,v in expression["terms"].items())
    return OPS[expression["op"]](value, expression["rhs"])


def verify_row(spec, row):
    variables = validate(spec)
    if not isinstance(row,dict) or set(row)!=set(variables):
        return {"valid":False,"errors":["variable_set"],"labels":{}}
    errors = [k for k,(a,b) in variables.items() if type(row[k]) is not int or not a<=row[k]<=b]
    if errors:
        return {"valid":False,"errors":errors,"labels":{}}
    errors += [k for k,p in spec.get("constraints",{}).items() if not evaluate(p,row)]
    errors += ["product:"+p["out"] for p in spec.get("products",[]) if row[p["out"]]!=row[p["left"]]*row[p["right"]]]
    return {"valid":not errors,"errors":errors,"labels":{k:evaluate(p,row) for k,p in spec["labels"].items()}}


def build(spec, requirements=None):
    bounds = validate(spec)
    model = cp_model.CpModel()
    variables = {k:model.new_int_var(a,b,k) for k,(a,b) in bounds.items()}
    index = 0

    def reify(predicate):
        nonlocal index
        index += 1
        truth = model.new_bool_var(f"predicate:{index}")
        if "all" in predicate or "any" in predicate:
            conjunction = "all" in predicate
            children = [reify(c) for c in predicate["all" if conjunction else "any"]]
            if conjunction:
                model.add_bool_and(children).only_enforce_if(truth)
                model.add_bool_or([c.Not() for c in children]).only_enforce_if(truth.Not())
            else:
                model.add_bool_or(children).only_enforce_if(truth)
                model.add_bool_and([c.Not() for c in children]).only_enforce_if(truth.Not())
        elif "not" in predicate:
            child = reify(predicate["not"])
            model.add(truth+child==1)
        else:
            value = sum(variables[k]*v for k,v in predicate["terms"].items())
            model.add(OPS[predicate["op"]](value,predicate["rhs"])).only_enforce_if(truth)
            model.add(OPS[INVERSE[predicate["op"]]](value,predicate["rhs"])).only_enforce_if(truth.Not())
        return truth

    assumptions = {}
    for name, predicate in spec.get("constraints",{}).items():
        truth = reify(predicate)
        model.add_assumption(truth)
        assumptions[truth.index] = "constraint:"+name
    labels = {k:reify(p) for k,p in spec["labels"].items()}
    for key, value in (requirements or {}).items():
        literal = labels[key] if value else labels[key].Not()
        model.add_assumption(literal)
        assumptions[literal.index] = "label:"+key+"="+str(value).lower()
    for product in spec.get("products",[]):
        model.add_multiplication_equality(variables[product["out"]], [variables[product["left"]],variables[product["right"]]])
    return model, variables, assumptions


def solve(model, variables, assumptions, seconds=1):
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = max(.001,min(5,seconds))
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        return {"status":solver.status_name(status),"row":None,"conflict":[assumptions[i] for i in solver.sufficient_assumptions_for_infeasibility() if i in assumptions] if status==cp_model.INFEASIBLE else [],"conflict_is_minimal":False}
    return {"status":solver.status_name(status),"row":{k:solver.value(v) for k,v in variables.items()}}


def generate(spec, seed=7, seconds=10):
    bounds = validate(spec)
    if type(seed) is not int or not 0<=seed<2**32 or type(seconds) not in (int,float) or not 0<seconds<=30:
        raise ValueError("invalid_generation_options")
    rng = random.Random(seed)
    deadline = time.monotonic()+seconds
    records, missing, seen = [],[],[]
    derived = {p["out"] for p in spec.get("products",[])}
    for cohort in spec["cohorts"]:
        completed = 0
        reason = None
        for _ in range(cohort["count"]):
            if time.monotonic()>=deadline:
                reason = {"status":"TIME_BUDGET"}
                break
            model, variables, assumptions = build(spec,cohort.get("require"))
            if seen:
                model.add_forbidden_assignments(list(variables.values()),seen)
            distances = []
            for k,(a,b) in bounds.items():
                if k in derived:
                    continue
                target = rng.randint(a,b)
                distance = model.new_int_var(0,b-a,"distance:"+k)
                model.add_abs_equality(distance,variables[k]-target)
                distances.append(distance*max(1,1_000_000//(b-a+1)))
            model.minimize(sum(distances))
            result = solve(model,variables,assumptions,min(1,deadline-time.monotonic()))
            if result["row"] is None:
                reason = result
                break
            row = result["row"]
            proof = verify_row(spec,row)
            if not proof["valid"] or any(proof["labels"][k]!=v for k,v in cohort.get("require",{}).items()):
                raise RuntimeError("independent_verification_failed")
            seen.append([row[k] for k in variables])
            completed += 1
            records.append({"id":f"case-{len(records)+1:04d}","cohort":cohort["id"],"values":row,
                            "labels":proof["labels"],"synthetic":True,"solve_status":result["status"]})
        if completed<cohort["count"]:
            missing.append({"cohort":cohort["id"],"requested":cohort["count"],"completed":completed,"reason":reason})
    return {"status":"complete" if not missing else "partial","synthetic":True,"seed":seed,
            "sampling":"seeded_random_target_optimization_not_uniform_sampling",
            "spec_sha256":hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
            "records":records,"missing_quotas":missing,"source_spec":deepcopy(spec)}


def counterfactual(spec, row, label, seconds=2):
    if type(seconds) not in (int,float) or not 0<seconds<=10:
        raise ValueError("invalid_counterfactual_budget")
    proof = verify_row(spec,row)
    if not proof["valid"] or label not in spec["labels"]:
        raise ValueError("invalid_counterfactual")
    model, variables, assumptions = build(spec,{label:not proof["labels"][label]})
    for key in spec.get("immutable",[]):
        model.add(variables[key]==row[key])
    derived = {p["out"] for p in spec.get("products",[])}
    changed, distances = [],[]
    for key,(a,b) in spec["variables"].items():
        if key in derived:
            continue
        change = model.new_bool_var("changed:"+key)
        model.add(variables[key]!=row[key]).only_enforce_if(change)
        model.add(variables[key]==row[key]).only_enforce_if(change.Not())
        changed.append(change)
        distance = model.new_int_var(0,b-a,"distance:"+key)
        model.add_abs_equality(distance,variables[key]-row[key])
        distances.append(distance)
    model.minimize(sum(changed))
    result = solve(model,variables,assumptions,seconds/2)
    if result["row"] is None:
        return result
    count = sum(result["row"][k]!=row[k] for k in variables if k not in derived)
    cardinality_proven = result["status"]=="OPTIMAL"
    distance_proven = False
    if cardinality_proven:
        model.add(sum(changed)==count)
        model.minimize(sum(distances))
        second = solve(model,variables,assumptions,seconds/2)
        if second["row"] is not None:
            result = second
            distance_proven = second["status"]=="OPTIMAL"
    check = verify_row(spec,result["row"])
    if not check["valid"] or check["labels"][label]==proof["labels"][label]:
        raise RuntimeError("independent_counterfactual_failed")
    return {"status":"OPTIMAL" if cardinality_proven and distance_proven else "FEASIBLE", "row":result["row"],
            "label":label,"before_label":proof["labels"][label],"after_label":check["labels"][label],
            "interventions":{k:{"before":row[k],"after":result["row"][k]} for k in variables if k not in derived and row[k]!=result["row"][k]},
            "derived_changes":{k:{"before":row[k],"after":result["row"][k]} for k in derived if row[k]!=result["row"][k]},
            "minimum_interventions_proven":cardinality_proven,"minimum_distance_proven":distance_proven}


def export_sqlite(dataset, destination):
    path = str(destination)
    # Exclusive creation: never replace a user's existing database.
    with open(path,"xb"):
        pass
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("CREATE TABLE cases (case_id TEXT PRIMARY KEY, cohort TEXT NOT NULL, synthetic INTEGER NOT NULL CHECK(synthetic=1))")
        db.execute("CREATE TABLE facts (case_id TEXT REFERENCES cases(case_id), variable TEXT, value INTEGER NOT NULL, PRIMARY KEY(case_id,variable))")
        db.execute("CREATE TABLE labels (case_id TEXT REFERENCES cases(case_id), predicate TEXT, value INTEGER NOT NULL CHECK(value IN(0,1)), PRIMARY KEY(case_id,predicate))")
        db.execute("CREATE INDEX labels_lookup ON labels(predicate,value)")
        for record in dataset["records"]:
            proof = verify_row(dataset["source_spec"],record["values"])
            if not proof["valid"] or proof["labels"]!=record["labels"]:
                raise ValueError("invalid_dataset_record")
            db.execute("INSERT INTO cases VALUES (?,?,1)",(record["id"],record["cohort"]))
            db.executemany("INSERT INTO facts VALUES (?,?,?)",[(record["id"],k,v) for k,v in record["values"].items()])
            db.executemany("INSERT INTO labels VALUES (?,?,?)",[(record["id"],k,int(v)) for k,v in record["labels"].items()])
