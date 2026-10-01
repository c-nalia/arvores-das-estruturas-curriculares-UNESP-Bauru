#!/usr/bin/env python3
"""Revisão: compara os arquivos de dados com transcrições INDEPENDENTES (feitas às cegas,
sem acesso aos dados nem ao gerador) das matrizes publicadas como imagem/tabela.

Uso: python3 revisao/comparar_independente.py revisao/transcricoes-independentes
"""
import json, os, re, sys, unicodedata
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IND = sys.argv[1]
achados = []


def norm(s):
    s = unicodedata.normalize("NFC", str(s or ""))
    return re.sub(r"\s+", " ", s).strip()


def dados(p):
    t = open(os.path.join(RAIZ, p), encoding="utf-8").read()
    return json.loads(t[t.index("registrar(") + 10: t.rindex(");")])


def original(D, nome):
    """Nome do documento correspondente ao nome dos dados (desfaz as correções registradas)."""
    for c in D.get("correcoes", []):
        if c.get("campo") != "ementa" and c["para"] == nome:
            return c["de"]
    return nome


def nomes_req(D, d, k):
    M = {x["c"]: x for x in D["disciplinas"]}
    out = [norm(original(D, M[c]["n"])) for c in d.get(k, [])]
    txt = d.get(k + "Texto")
    if txt:
        out += [norm(re.sub(r" \(a própria disciplina, conforme o documento\)$", "", x)) for x in txt.split("; ")]
    return sorted(out)


def split_req(s):
    s = norm(s)
    if not s:
        return []
    partes = [norm(x) for x in re.split(r";\s*|,\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕ])", s) if norm(x)]
    # "Políticas Públicas, Instituições e Saúde" é um nome só
    out = []
    for x in partes:
        if out and x.startswith("Instituições e Saúde") and out[-1] == "Políticas Públicas":
            out[-1] += ", " + x
        else:
            out.append(x)
    return sorted(out)


def comparar(curso, D, esperado, chaves, req=True):
    """esperado: lista de dicts {t, n, <chaves>, pre?, co?} do documento."""
    obtidos = [{"t": d["t"], "n": norm(original(D, d["n"])), **{k: (d.get(k) or (d["c"] if k == "cod" and not d.get("semCodigo") else None)) for k in chaves},
                "pre": nomes_req(D, d, "pre"), "co": nomes_req(D, d, "co"), "_d": d} for d in D["disciplinas"]]
    livres = list(obtidos)
    for e in esperado:
        cand = [o for o in livres if o["t"] == e["t"] and o["n"].lower() == norm(e["n"]).lower()]
        if not cand:
            achados.append((curso, f"{e['t']}º termo: “{e['n']}” do documento não está nos dados (ou está em outro termo/com outro nome)"))
            continue
        o = cand[0]
        livres.remove(o)
        if o["n"] != norm(e["n"]):
            achados.append((curso, f"{e['t']}º termo: grafia “{o['n']}” × documento “{norm(e['n'])}”"))
        for k in chaves:
            if e.get(k) is not None and o[k] != e[k]:
                achados.append((curso, f"{e['t']}º termo, “{e['n']}”: {k} = {o[k]} nos dados × {e[k]} no documento"))
        if req:
            for k in ("pre", "co"):
                exp = sorted(norm(x) for x in e.get(k, []))
                if [x.lower() for x in exp] != [x.lower() for x in o[k]]:
                    achados.append((curso, f"{e['t']}º termo, “{e['n']}”: {k} nos dados {o[k]} × documento {exp}"))
    for o in livres:
        achados.append((curso, f"{o['t']}º termo: “{o['n']}” está nos dados e não no documento"))


# Meteorologia
j = json.load(open(os.path.join(IND, "meteorologia.json")))
D = dados("fc/meteorologia/dados-meteorologia-1702.js")
esp = []
for tb in j["tabelas"]:
    if tb["termo"] == 0:
        continue
    for l in tb["linhas"]:
        esp.append({"t": tb["termo"], "n": l["nome"], "cod": l["cod"], "cr": l["creditos"], "ch": l["horas"], "d": l["dep"],
                    "pre": split_req(l["prerequisito"]), "co": split_req(l["correquisito"])})
comparar("meteorologia", D, esp, ["cod", "cr", "ch", "d"])
opt_doc = [l for tb in j["tabelas"] if tb["termo"] == 0 for l in tb["linhas"]]
opt_dad = D["optativas"]["lista"]
M = {x["c"]: x for x in D["disciplinas"]}
for l in opt_doc:
    o = [x for x in opt_dad if norm(original(D, x["n"])) == norm(l["nome"])]
    if not o:
        achados.append(("meteorologia", f"optativa “{l['nome']}” ausente")); continue
    o = o[0]
    for a, b in (("cod", "cod"), ("cr", "creditos"), ("ch", "horas"), ("d", "dep")):
        if (o.get(a) or o.get("c") if a == "cod" and not o.get("semCodigo") else o.get(a)) != (l[b] or None) and not (a == "cod" and o.get("semCodigo") and not l[b]):
            achados.append(("meteorologia", f"optativa {l['nome']}: {a} {o.get(a, o.get('c'))} × {l[b]}"))
    pre = sorted([norm(M[c]["n"]) for c in o.get("pre", [])] + ([o["preTexto"]] if o.get("preTexto") else []))
    co = sorted([norm(M[c]["n"]) for c in o.get("co", [])])
    if pre != split_req(l["prerequisito"]) or co != split_req(l["correquisito"]):
        achados.append(("meteorologia", f"optativa {l['nome']}: requisitos {pre}/{co} × {split_req(l['prerequisito'])}/{split_req(l['correquisito'])}"))
if len(opt_doc) != len(opt_dad):
    achados.append(("meteorologia", f"optativas: {len(opt_dad)} nos dados × {len(opt_doc)} no documento"))

# Química
j = json.load(open(os.path.join(IND, "quimica.json")))
for chave, arq in (("licenciatura", "fc/quimica/dados-quimica-licenciatura-2023.js"), ("bacharelado", "fc/quimica/dados-quimica-tecnologica-2023.js")):
    D = dados(arq)
    comparar("quimica-" + chave, D, [{"t": l["termo"], "n": l["nome"], "ch": l["ch"]} for l in j[chave]["linhas"]], ["ch"], req=False)

# Pedagogia
j = json.load(open(os.path.join(IND, "pedagogia.json")))
D = dados("fc/pedagogia/dados-pedagogia-2023.js")
comparar("pedagogia", D, [{"t": t["termo"], "n": c["nome"], "cr": c["creditos"], "ch": c.get("horas")} for t in j["termos"] for c in t["componentes"]], ["cr", "ch"], req=False)

# Biologia
for f, arq in (("bio2710", "fc/ciencias-biologicas/dados-ciencias-biologicas-2710.js"), ("bio2711", "fc/ciencias-biologicas/dados-ciencias-biologicas-2711.js")):
    j = json.load(open(os.path.join(IND, f + ".json")))
    D = dados(arq)
    esp = [{"t": tb["termo"], "n": l["nome"], "cr": l["creditos"], "ch": l["horas"], "anual": True if l["s_a"] == "A" else None,
            "pre": split_req(l.get("pre")), "co": [norm(l["co"])] if norm(l.get("co")) else []} for tb in j["tabelas"] for l in tb["linhas"]]
    comparar(f, D, esp, ["cr", "ch", "anual"])

# Psicologia
j = json.load(open(os.path.join(IND, "psicologia.json")))
D = dados("fc/psicologia/dados-psicologia-1212-1213.js")
esp = []
for l in j["linhas"]:
    m = re.match(r"(\d+)", l["sem"] or "")
    t = int(m.group(1)) if m else None
    if t and t > 8:
        t = 9
    esp.append({"t": t or 4, "n": l["nome"], "cr": l["creditos"], "pre": split_req(l["pre"]), "co": split_req(l["co"]),
                "_xc": l.get("extraclasse"), "_ext": l.get("extensao")})
comparar("psicologia", D, esp, ["cr"])
for e in esp:
    d = [x for x in D["disciplinas"] if norm(original(D, x["n"])).lower() == norm(e["n"]).lower() and x["t"] == e["t"]]
    if d:
        ex = {r: v for r, v, _ in d[0].get("extras", [])}
        if (ex.get("Atividade extraclasse ou prática") or None) != (e["_xc"] or None) or (ex.get("Extensão") or None) != (e["_ext"] or None):
            achados.append(("psicologia", f"{e['n']}: extraclasse/extensão {ex} × documento {e['_xc']}/{e['_ext']}"))

# Design
j = json.load(open(os.path.join(IND, "design.json")))
D = dados("faac/design/dados-design-2023.js")
comparar("design", D, [{"t": t["termo"], "n": n} for t in j["termos"] for n in t["componentes"]], [], req=False)

for c, a in achados:
    print(f"[{c}] {a}")
print(f"\n{len(achados)} diferença(s).")
