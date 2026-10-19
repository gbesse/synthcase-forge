from collections import Counter
from copy import deepcopy
import itertools
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from synthcase.engine import counterfactual, generate, verify_row
from synthcase.review import MODEL, request_body, review, validate_response

ROOT = Path(__file__).resolve().parent.parent


def example():
    return json.loads((ROOT / "synthcase/examples/invoice-cases.json").read_text())


class ForgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = example()
        cls.dataset = generate(cls.spec)

    def test_exact_cohort_quotas_and_known_truth(self):
        self.assertEqual(self.dataset["status"],"complete")
        self.assertEqual(Counter(r["cohort"] for r in self.dataset["records"]),{"ready":4,"quantity-only":3,"price-only":3,"combined":2})
        for record in self.dataset["records"]:
            proof=verify_row(self.spec,record["values"])
            self.assertTrue(proof["valid"])
            self.assertEqual(record["labels"],proof["labels"])
            self.assertTrue(record["synthetic"])

    def test_seed_controls_random_targets_and_uniqueness(self):
        second=generate(self.spec)
        self.assertEqual(second["records"],self.dataset["records"])
        rows=[json.dumps(r["values"],sort_keys=True) for r in second["records"]]
        self.assertEqual(len(rows),len(set(rows)))
        self.assertNotEqual(generate(self.spec,seed=9)["records"],self.dataset["records"])

    def test_product_totals_are_not_independently_random(self):
        for r in self.dataset["records"]:
            v=r["values"]
            self.assertEqual(v["invoice_total_cents"],v["billed_quantity"]*v["billed_unit_cents"])

    def test_counterfactual_freezes_facts_and_recomputes_totals(self):
        row=next(r["values"] for r in self.dataset["records"] if r["cohort"]=="quantity-only")
        result=counterfactual(self.spec,row,"quantity_exceeds_receipt")
        self.assertEqual(result["status"],"OPTIMAL")
        self.assertEqual(set(result["interventions"]),{"billed_quantity"})
        self.assertTrue(result["minimum_interventions_proven"])
        self.assertFalse(result["after_label"])
        for k in self.spec["immutable"]:self.assertEqual(row[k],result["row"][k])
        self.assertTrue(verify_row(self.spec,result["row"])["valid"])

    def test_minimum_counterfactual_matches_exhaustive_oracle(self):
        spec={"variables":{"x":[0,3],"y":[0,3]},"constraints":{"total":{"terms":{"x":1,"y":1},"op":"<=","rhs":4}},"labels":{"over":{"terms":{"x":1,"y":-1},"op":">","rhs":0}},"cohorts":[{"id":"any","count":1}]}
        original={"x":3,"y":0}
        target=counterfactual(spec,original,"over")
        costs=[]
        for x,y in itertools.product(range(4),repeat=2):
            row={"x":x,"y":y};p=verify_row(spec,row)
            if p["valid"] and not p["labels"]["over"]:costs.append((sum(row[k]!=original[k] for k in row),sum(abs(row[k]-original[k]) for k in row)))
        self.assertEqual((len(target["interventions"]),sum(abs(c["after"]-c["before"]) for c in target["interventions"].values())),min(costs))

    def test_impossible_cohort_explains_missing_quota(self):
        spec=example();spec["constraints"]["no_overbilling"]={"terms":{"billed_quantity":1,"received_quantity":-1},"op":"<=","rhs":0}
        result=generate(spec)
        self.assertEqual(result["status"],"partial")
        missing=next(m for m in result["missing_quotas"] if m["cohort"]=="quantity-only")
        self.assertEqual(missing["completed"],0)
        self.assertEqual(missing["reason"]["status"],"INFEASIBLE")
        self.assertTrue(missing["reason"]["conflict"])

    def test_finite_domain_exhaustion_is_not_hidden(self):
        spec={"variables":{"x":[0,1]},"labels":{"positive":{"terms":{"x":1},"op":">","rhs":0}},"cohorts":[{"id":"all","count":3}]}
        result=generate(spec)
        self.assertEqual(len(result["records"]),2)
        self.assertEqual(result["status"],"partial")

    def test_negation_and_disjunction_are_independently_checked(self):
        spec={"variables":{"x":[0,4]},"labels":{"middle":{"not":{"any":[{"terms":{"x":1},"op":"==","rhs":0},{"terms":{"x":1},"op":"==","rhs":4}]}}},"cohorts":[{"id":"middle","count":3,"require":{"middle":True}}]}
        result=generate(spec)
        self.assertEqual({r["values"]["x"] for r in result["records"]},{1,2,3})

    def test_all_immutable_can_make_counterfactual_impossible(self):
        spec=example();spec["immutable"]=list(spec["variables"])
        row=self.dataset["records"][0]["values"]
        self.assertEqual(counterfactual(spec,row,"ready")["status"],"INFEASIBLE")

    def test_sqlite_export_has_foreign_keys_and_truth_labels(self):
        from synthcase.engine import export_sqlite
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"cases.sqlite"
            export_sqlite(self.dataset,target)
            with sqlite3.connect(target) as db:
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
                self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],12)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM labels WHERE predicate='ready' AND value=1").fetchone()[0],4)
            before=target.read_bytes()
            with self.assertRaises(FileExistsError):export_sqlite(self.dataset,target)
            self.assertEqual(target.read_bytes(),before)

    def test_tampered_label_is_not_exported_as_truth(self):
        from synthcase.engine import export_sqlite
        data=deepcopy(self.dataset);data["records"][0]["labels"]["ready"]=False
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):export_sqlite(data,Path(tmp)/"cases.sqlite")

    def test_review_is_one_bounded_call_with_localized_instructions(self):
        for lang in ("fr","en","es"):
            body=request_body(self.dataset,lang=lang)
            self.assertEqual(len(body["questions"]),3)
            self.assertEqual(set(body["state"]["cases"]),set(body["questions"]))
            self.assertTrue(all("instructions" in q and "description" not in q for q in body["questions"].values()))

    def test_model_opinions_cannot_overwrite_deterministic_labels(self):
        before=deepcopy(self.dataset)
        def fake(body):return {"model":MODEL,"answers":{k:{"type":"choice","choice":"implausible","confidence":.9,"probabilities":{"plausible":.05,"implausible":.9,"uncertain":.05}} for k in body["questions"]},"usage":{"input_tokens":50,"output_tokens":30}}
        result=review(self.dataset,api_key="synthetic-test-token",transport=fake)
        self.assertTrue(result["model_opinion_not_ground_truth"])
        self.assertFalse(result["deterministic_labels_modified"])
        self.assertEqual(self.dataset,before)

    def test_model_response_and_probabilities_are_fail_closed(self):
        body=request_body(self.dataset)
        for response in ({"model":"other","answers":{}},{"model":MODEL,"answers":{k:None for k in body["questions"]}}):
            with self.assertRaises(ValueError):validate_response(body,response)


if __name__=="__main__":unittest.main()
