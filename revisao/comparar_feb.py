#!/usr/bin/env python3
"""Revisão: compara os dados da FEB com a leitura visual independente dos PDFs."""
import json, os, re, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IND = sys.argv[1]
ach = []
def dados(p):
    t = open(os.path.join(RAIZ, p), encoding="utf-8").read(); return json.loads(t[t.index("registrar(") + 10: t.rindex(");")])
for nome, arq in (("civil", "feb/engenharia-civil/dados-engenharia-civil-0104.js"), ("mecanica", "feb/engenharia-mecanica/dados-engenharia-mecanica-0204.js"),
                  ("eletrica", "feb/engenharia-eletrica/dados-engenharia-eletrica-0304.js"), ("producao", "feb/engenharia-de-producao/dados-engenharia-de-producao-4403.js")):
    D = dados(arq); J = json.load(open(os.path.join(IND, f"feb-{nome}.json")))
    M = {d["c"]: d for d in D["disciplinas"]}
    corr = {c["cod"]: c for c in D.get("correcoes", [])}
    regras = D.get("regras") or {}
    vist = set()
    for x in J["disciplinas"]:
        d = M.get(x["cod"]); 
        if not d: ach.append((nome, f"{x['cod']} ausente dos dados")); continue
        vist.add(x["cod"])
        n_orig = corr[x["cod"]]["de"] if x["cod"] in corr else d["n"]
        if re.sub(r"\s+", " ", n_orig) != re.sub(r"\s+", " ", x["n"]): ach.append((nome, f"{x['cod']}: nome “{n_orig}” (original nos dados) × leitura “{x['n']}”"))
        if d["t"] != x["t"]: ach.append((nome, f"{x['cod']}: termo {d['t']} × {x['t']}"))
        if (d.get("ch") or 0) != (x["ch"] or 0) or (d.get("aceu") or 0) != (x["aceu"] or 0): ach.append((nome, f"{x['cod']}: carga {d.get('ch')}/{d.get('aceu')} × {x['ch']}/{x['aceu']}"))
        if d["tipo"] != x["tipo"]: ach.append((nome, f"{x['cod']}: tipo {d['tipo']} × {x['tipo']}"))
        pre = sorted(c for t, c in x["req"] if t and t.startswith("Pr"))
        co = sorted(c for t, c in x["req"] if t and t.startswith("Co"))
        outros = [t for t, c in x["req"] if t and not (t.startswith("Pr") or t.startswith("Co"))]
        txt = (d.get("preTexto") or "") + (d.get("coTexto") or "")
        dp = sorted(d.get("pre", [])); dc = sorted(d.get("co", []))
        for c in pre:
            if c not in dp and c not in txt: ach.append((nome, f"{x['cod']}: pré-requisito {c} ausente dos dados"))
        for c in co:
            if c not in dc and c not in txt: ach.append((nome, f"{x['cod']}: correquisito {c} ausente dos dados"))
        for c in dp:
            if c not in pre: ach.append((nome, f"{x['cod']}: pré-requisito {c} nos dados não está no documento"))
        for c in dc:
            if c not in co: ach.append((nome, f"{x['cod']}: correquisito {c} nos dados não está no documento"))
        for o in outros:
            r = regras.get(x["cod"])
            if not r or r["texto"].replace(",", ".") not in o.replace(",", "."): ach.append((nome, f"{x['cod']}: requisito “{o}” sem regra correspondente nos dados ({r})"))
        if x["cod"] in regras and not outros: ach.append((nome, f"{x['cod']}: regra {regras[x['cod']]} nos dados sem texto no documento"))
    for c in M:
        if c not in vist: ach.append((nome, f"{c} nos dados e não no documento"))
    print(nome, len(J["disciplinas"]), "disciplinas lidas;", sum(len(x["req"]) for x in J["disciplinas"]), "requisitos")
for c, a in ach: print(f"  [{c}] {a}")
print(f"\n{len(ach)} diferença(s).")
