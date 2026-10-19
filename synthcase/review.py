"""Optional one-call semantic review. Model opinions never replace predicate truth."""
import json
import math
import os
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler, HTTPSHandler

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.13.0"
CRITERIA = {
"plausible":"The supplied synthetic invoice values describe a plausible operational situation. Discrepancies are allowed: plausibility does not mean the invoice is correct or payable.",
"implausible":"The numerical situation is impossible or nonsensical even as an example of an operational discrepancy.",
"uncertain":"There is insufficient context to judge whether this synthetic situation could occur."}
PROMPTS = {
"en": {"criteria":CRITERIA,"instructions":"Judge only the operational plausibility of synthetic case {id}. Do not decide whether its invoice should be paid.","description":"Independent plausibility review; deterministic labels are stored separately and must not be overwritten."},
"fr": {"criteria":{"plausible":"Les valeurs synthétiques décrivent une situation opérationnelle plausible. Les écarts sont autorisés : plausible ne signifie ni correct ni payable.","implausible":"La situation numérique est impossible ou dépourvue de sens, même comme exemple d’écart opérationnel.","uncertain":"Le contexte est insuffisant pour juger si cette situation synthétique peut se produire."},"instructions":"Juger uniquement la plausibilité opérationnelle du cas synthétique {id}. Ne pas décider si la facture doit être payée.","description":"Revue de plausibilité indépendante ; les étiquettes déterministes sont stockées séparément et ne doivent pas être modifiées."},
"es": {"criteria":{"plausible":"Los valores sintéticos describen una situación operativa plausible. Se admiten diferencias: plausible no significa correcto ni pagadero.","implausible":"La situación numérica es imposible o carece de sentido incluso como ejemplo de diferencia operativa.","uncertain":"No hay contexto suficiente para juzgar si esta situación sintética puede ocurrir."},"instructions":"Juzgar solo la plausibilidad operativa del caso sintético {id}. No decidir si debe pagarse la factura.","description":"Revisión de plausibilidad independiente; las etiquetas deterministas se guardan por separado y no deben modificarse."}}


def request_body(dataset, max_rows=3, lang="en"):
    if type(max_rows) is not int or not 1<=max_rows<=6:
        raise ValueError("invalid_review_budget")
    if lang not in PROMPTS:
        raise ValueError("invalid_language")
    representatives = {}
    for row in dataset["records"]:
        representatives.setdefault(row["cohort"],row)
    rows = list(representatives.values())[:max_rows]
    if not rows or any(not r.get("synthetic") for r in rows):
        raise ValueError("invalid_synthetic_review")
    state = {"synthetic":True,"description":PROMPTS[lang]["description"],
             "cases":{r["id"]:r["values"] for r in rows}}
    questions = {r["id"]:{"type":"choice","instructions":PROMPTS[lang]["instructions"].format(id=r["id"]),"criteria":PROMPTS[lang]["criteria"]} for r in rows}
    return {"model":MODEL,"state":state,"questions":questions}


def validate_response(body, response):
    if not isinstance(response,dict) or response.get("model")!=MODEL or not isinstance(response.get("answers"),dict) or set(response["answers"])!=set(body["questions"]):
        raise ValueError("invalid_review_response")
    opinions = []
    for key, answer in response["answers"].items():
        if not isinstance(answer,dict):
            raise ValueError("invalid_review_answer")
        p = answer.get("probabilities") if isinstance(answer,dict) else None
        confidence = answer.get("confidence")
        if answer.get("type")!="choice" or answer.get("choice") not in CRITERIA or not isinstance(p,dict) or set(p)!=set(CRITERIA) or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in p.values()) or abs(sum(p.values())-1)>.001 or type(confidence) not in (int,float) or not math.isfinite(confidence) or not 0<=confidence<=1 or p[answer["choice"]]+1e-6<max(p.values()):
            raise ValueError("invalid_review_answer")
        opinions.append({"case_id":key,"opinion":answer["choice"],"confidence":confidence,"probabilities":p,
                         "review_required":answer["choice"]=="uncertain" or confidence<.8})
    usage = response.get("usage")
    if not isinstance(usage,dict) or any(type(usage.get(k)) is not int or usage[k]<0 for k in ("input_tokens","output_tokens")):
        raise ValueError("invalid_review_usage")
    return {"model":MODEL,"opinions":opinions,"usage":{k:usage[k] for k in ("input_tokens","output_tokens")},"model_opinion_not_ground_truth":True,"deterministic_labels_modified":False}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None


def review(dataset, api_key=None, max_rows=3, transport=None, lang="en"):
    body = request_body(dataset,max_rows,lang)
    key = api_key or os.environ.get("TYPESAFE_API_KEY")
    if not isinstance(key,str) or not key:
        raise ValueError("invalid_missing_typesafe_key")
    if transport:
        response = transport(body)
    else:
        try:
            import certifi
        except ImportError:
            raise ValueError("invalid_missing_certifi") from None
        request = Request(ENDPOINT,data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
        try:
            context=ssl.create_default_context(cafile=certifi.where())
            with build_opener(NoRedirect(),HTTPSHandler(context=context)).open(request,timeout=30) as response:
                data = response.read(500001)
                if len(data)>500000:
                    raise ValueError("invalid_review_size")
                response = json.loads(data)
        except HTTPError as error:
            raise ValueError("invalid_review_http_"+str(error.code)) from None
        except (URLError,TimeoutError) as error:
            # Never echo upstream response bodies, headers, request objects or secrets.
            raise ValueError("invalid_review_transport") from None
    return validate_response(body,response)
