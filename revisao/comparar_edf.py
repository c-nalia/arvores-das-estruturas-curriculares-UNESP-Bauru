#!/usr/bin/env python3
"""Revisão: Educação Física — segunda leitura dos .doc por outro caminho (LibreOffice → texto puro,
em vez de → HTML como no gerador) e comparação com os dados."""
import json, os, re, subprocess, sys, tempfile
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(RAIZ, "planos de ensino/FC/DEF/Educacao_Fisica")
tmp = tempfile.mkdtemp()
ach = []
def dados(p):
    t = open(os.path.join(RAIZ, p), encoding="utf-8").read(); return json.loads(t[t.index("registrar(") + 10: t.rindex(");")])
for doc, cid in (("curriculo-2610---bacharelado-integral-a-partir-de-2015", "educacao-fisica-2610-bacharelado"),
                 ("curriculo-2610---licenciatura-integral-a-partir-de-2015", "educacao-fisica-2610-licenciatura"),
                 ("curriculo-2611---bacharelado-noturno-a-partir-de-2015", "educacao-fisica-2611-bacharelado"),
                 ("curriculo-2611---licenciatura-noturno-a-partir-de-2015", "educacao-fisica-2611-licenciatura")):
    subprocess.run(["soffice", "--headless", "--convert-to", "txt:Text (encoded):UTF8", "--outdir", tmp, os.path.join(P, doc + ".doc")], capture_output=True)
    L = [l.strip() for l in open(os.path.join(tmp, doc + ".txt"), encoding="utf-8-sig") if l.strip()]
    reg, t, tot, i = [], 0, {}, 0
    while i < len(L):
        l = L[i]
        m = re.match(r"^(\d+)º\s*Termo$", l)
        if m: t = int(m.group(1)); i += 1; continue
        if l == "Créditos" and i + 1 < len(L) and re.fullmatch(r"\d+", L[i + 1]): tot[t] = int(L[i + 1]); i += 2; continue
        if t and re.fullmatch(r"(Bio|Def|DEF|Chu|Ep|Dep|Psi|Edu)", l) and i + 2 < len(L) and re.fullmatch(r"\d{2}", L[i + 2]):
            dep, nome, nc = l, L[i + 1], int(L[i + 2]); j = i + 3; pre = []
            while j < len(L) and L[j] not in ("TC", "B", "L"):
                pre.append(L[j]); j += 1
            reg.append({"t": t, "d": dep, "n": nome, "cr": nc, "pre": " ".join(pre)}); i = j + 1; continue
        if t and l == "A":  # célula de código com "A"
            i += 1; continue
        i += 1
    D = dados(f"fc/educacao-fisica/dados-{cid}.js")
    corr = {c["para"]: c["de"] for c in D.get("correcoes", [])}
    M = {d["c"]: d for d in D["disciplinas"]}
    ds = list(D["disciplinas"])
    for r in reg:
        c = [d for d in ds if d["t"] == r["t"] and corr.get(d["n"], d["n"]) == r["n"]]
        if not c: ach.append((cid, f"{r['t']}º termo: “{r['n']}” não encontrado nos dados")); continue
        d = c[0]; ds.remove(d)
        if d["cr"] != r["cr"] or d.get("d") != r["d"]: ach.append((cid, f"{r['n']}: {d['cr']}/{d.get('d')} × {r['cr']}/{r['d']}"))
        pre_d = [corr.get(M[x]["n"], M[x]["n"]) for x in d.get("pre", [])] + ([d["preTexto"]] if d.get("preTexto") else [])
        if bool(r["pre"]) != bool(pre_d): ach.append((cid, f"{r['n']}: pré-requisito documento “{r['pre']}” × dados {pre_d}"))
    for d in ds: ach.append((cid, f"{d['t']}º termo: “{d['n']}” nos dados e não no documento"))
    soma = {}
    for r in reg: soma[r["t"]] = soma.get(r["t"], 0) + r["cr"]
    print(cid, len(reg), "linhas; totais doc", tot, "\n   somas", soma)
for c, a in ach: print(f"  [{c}] {a}")
print(f"\n{len(ach)} diferença(s).")
