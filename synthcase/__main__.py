import json
import os
from pathlib import Path
import stat
import subprocess
import sys

from .engine import counterfactual, export_sqlite, generate

ROOT=Path(__file__).resolve().parent
MESSAGES={
"fr":{"help":"Utilisation : python -m synthcase demo|generate spec.json|pair données.json identifiant étiquette|export données.json sortie.sqlite|review données.json|serve [port] [--seed entier] [--lang fr|en|es] [--output fichier] [--env .env]", "error":"Entrée non valide ou service indisponible", "ready":"Laboratoire synthétique local"},
"en":{"help":"Usage: python -m synthcase demo|generate spec.json|pair data.json id label|export data.json output.sqlite|review data.json|serve [port] [--seed integer] [--lang fr|en|es] [--output file] [--env .env]", "error":"Invalid input or unavailable service", "ready":"Local synthetic laboratory"},
"es":{"help":"Uso: python -m synthcase demo|generate spec.json|pair datos.json id etiqueta|export datos.json salida.sqlite|review datos.json|serve [puerto] [--seed entero] [--lang fr|en|es] [--output archivo] [--env .env]", "error":"Entrada no válida o servicio no disponible", "ready":"Laboratorio sintético local"}}


def example():
    return json.loads((ROOT/"examples/invoice-cases.json").read_text())


def demo(seed=7):
    data=generate(example(),seed)
    record=next(r for r in data["records"] if r["cohort"]=="quantity-only")
    pair=counterfactual(data["source_spec"],record["values"],"quantity_exceeds_receipt")
    return {"dataset":data,"pair_case_id":record["id"],"counterfactual":pair}


def env_key(path):
    file=Path(path).resolve()
    if stat.S_IMODE(file.stat().st_mode)&0o077:
        raise ValueError("invalid_env_permissions")
    check=subprocess.run(["git","check-ignore","--quiet","--",str(file)],cwd=file.parent,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if check.returncode!=0:
        raise ValueError("invalid_env_not_ignored")
    for line in file.read_text().splitlines():
        line=line.strip()
        if line.startswith("export "):line=line[7:]
        if line.startswith("TYPESAFE_API_KEY="):
            return line.split("=",1)[1].strip().strip('"').strip("'")
    raise ValueError("invalid_missing_typesafe_key")


def main(argv=None):
    args=list(sys.argv[1:] if argv is None else argv)
    options={"--seed":"7","--lang":"en","--output":None,"--env":None}
    try:
        for key in options:
            if key in args:
                i=args.index(key);options[key]=args[i+1];del args[i:i+2]
        lang=options["--lang"]
        if lang not in MESSAGES:raise ValueError("invalid_language")
        seed=int(options["--seed"])
        if not args or args[0] in ("help","--help"):
            print(MESSAGES[lang]["help"]);return 0
        command=args.pop(0)
        if command=="demo":result=demo(seed)
        elif command=="generate" and len(args)==1:result=generate(json.loads(Path(args[0]).read_text()),seed)
        elif command=="pair" and len(args)==3:
            data=json.loads(Path(args[0]).read_text());record=next(r for r in data["records"] if r["id"]==args[1]);result=counterfactual(data["source_spec"],record["values"],args[2])
        elif command=="export" and len(args)==2:
            data=json.loads(Path(args[0]).read_text());export_sqlite(data,args[1]);result={"status":"exported","records":len(data["records"]),"synthetic":True}
        elif command=="review" and len(args)==1:
            from .review import review
            key=env_key(options["--env"]) if options["--env"] else None
            result=review(json.loads(Path(args[0]).read_text()),api_key=key,lang=lang)
        elif command=="serve":
            from .server import serve
            port=int(args[0]) if args else 8767
            print(f'{MESSAGES[lang]["ready"]}: http://127.0.0.1:{port}/?lang={lang}',flush=True);serve(port);return 0
        else:raise ValueError("invalid_command")
        content=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)
        if options["--output"]:
            target=Path(options["--output"]);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content)
        else:print(content)
        return 1 if result.get("status") in ("partial","INFEASIBLE","UNKNOWN") else 0
    except (ValueError,TypeError,KeyError,IndexError,StopIteration,OSError,RuntimeError):
        lang=options.get("--lang") if options.get("--lang") in MESSAGES else "en"
        print(json.dumps({"error":"operation_failed","message":MESSAGES[lang]["error"]}),file=sys.stderr);return 2


if __name__=="__main__":raise SystemExit(main())
