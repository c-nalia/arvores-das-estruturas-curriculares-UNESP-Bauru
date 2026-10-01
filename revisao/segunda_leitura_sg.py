#!/usr/bin/env python3
"""Revisão: segunda leitura das relações do Sistema de Graduação por caminhos independentes do
gerador (ferramentas/fontes_sg.py):
  * FAAC  — lê as páginas HTML (não os CSV usados pelo gerador), célula a célula, com lxml;
  * FEB   — lê os PDFs pela GRADE DE BORDAS das células (retângulos do PDF), não pelo centro
            vertical das palavras como o gerador;
e compara código a código com os arquivos de dados: termo, nome, carga, CH ACEU, tipo e TODO
código citado na célula de requisitos (inclusive textos que não sejam pré/correquisito).
"""
import json, os, re, sys, unicodedata
from collections import defaultdict
import lxml.html
import pdfplumber

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(RAIZ, "planos de ensino")
achados = []
COD = r"(?:[A-Z]{2,5}-E\s?\d{1,3}|[A-Z]{2}\d{4}[A-Z]\d{2}|OPDES\d+|[A-Z]{3,}\d{2,}|\d{7}|\d{4,}[A-Z]?)"


def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s or "")).strip()


def dados(p):
    t = open(os.path.join(RAIZ, p), encoding="utf-8").read()
    return json.loads(t[t.index("registrar(") + 10: t.rindex(");")])


def original(D, cod, nome):
    for c in D.get("correcoes", []):
        if c.get("cod") == cod and c["para"] == nome:
            return c["de"]
    return nome


# ---------------- FAAC: HTML ----------------
def ler_html(arq):
    doc = lxml.html.parse(arq).getroot()
    linhas = []
    for tr in doc.iter("tr"):
        cel = [norm(td.text_content()) for td in tr if td.tag in ("td", "th")]
        if any(cel):
            linhas.append(cel)
    reg, termo, cab, pos_total = [], None, None, False
    for cel in linhas:
        a = cel[0]
        m = re.match(r"S[ée]rie:\s*(\d+)\s*-\s*Per[ií]odo:\s*(\d+)", a)
        if m:
            termo = (int(m.group(1)) - 1) * 2 + int(m.group(2)); continue
        if a == "Disciplina":
            cab = cel; continue
        if a.startswith("Total Carga Horária"):
            pos_total = True; termo = None; continue
        if a.startswith("Total de Carga"):
            continue
        m = re.match(r"^(" + COD + r")\s+-\s+(.+)$", a)
        if m and cab:
            r = dict(zip(cab, cel))
            reg.append({"cod": m.group(1), "n": m.group(2), "t": termo, "ch": float(r.get("Carga Horária") or 0),
                        "aceu": float(r.get("CH Aceu") or 0), "tipo": r.get("Tipo", ""), "req": r.get("Requisitos", r.get("Pré-Requisito", "")),
                        "fim": pos_total})
        elif not a and reg and cab:   # continuação de requisitos
            r = dict(zip(cab, cel))
            reg[-1]["req"] += " " + (r.get("Requisitos") or r.get("Pré-Requisito") or "")
    return reg


def comparar(nome, D, reg, opt_fora_da_grade=True):
    print(f"[{nome}] {len(reg)} linhas no documento")
    porc = {d.get("cod", d["c"]): d for d in D["disciplinas"]}
    opt = {d.get("cod", d["c"]): d for d in (D.get("optativas") or {}).get("lista", [])}
    ids = {d["c"]: d.get("cod", d["c"]) for d in D["disciplinas"]}
    vistos = set()
    for r in reg:
        d = porc.get(r["cod"]) or opt.get(r["cod"])
        if not d:
            achados.append((nome, f"{r['cod']} – {r['n']} está no documento e não nos dados")); continue
        vistos.add(r["cod"])
        if norm(original(D, r["cod"], d["n"])) != norm(r["n"]):
            achados.append((nome, f"{r['cod']}: nome “{d['n']}” × documento “{r['n']}”"))
        if r["cod"] in porc and r["t"] is not None and d["t"] != r["t"]:
            achados.append((nome, f"{r['cod']}: termo {d['t']} × documento {r['t']}"))
        if r["cod"] in porc and r["t"] is None:
            achados.append((nome, f"{r['cod']}: está na grade dos dados mas no documento não tem Série/Período"))
        tipo = r["tipo"]
        if tipo in ("ACEU", "ACE"):
            if d.get("tipoDoc") != tipo or (d.get("aceu") or 0) != r["ch"]:
                achados.append((nome, f"{r['cod']}: componente {tipo} {r['ch']} h representado como {d.get('tipoDoc')}/{d.get('aceu')}"))
        else:
            if (d.get("ch") or 0) != r["ch"] or (d.get("aceu") or 0) != r["aceu"]:
                achados.append((nome, f"{r['cod']}: carga {d.get('ch')}/{d.get('aceu')} × documento {r['ch']}/{r['aceu']}"))
            if d.get("tipo") != tipo:
                achados.append((nome, f"{r['cod']}: tipo {d.get('tipo')} × documento {tipo}"))
        citados = set(re.findall(COD, r["req"]))
        citados -= {r["cod"]}
        nos_dados = {ids.get(x, x) for x in d.get("pre", []) + d.get("co", [])}
        txt = (d.get("preTexto") or "") + (d.get("coTexto") or "")
        for c in citados:
            if c not in nos_dados and c not in txt:
                achados.append((nome, f"{r['cod']}: requisito {c} citado no documento (“{r['req'][:120]}”) não está nos dados"))
        for c in nos_dados - citados:
            achados.append((nome, f"{r['cod']}: requisito {c} nos dados não aparece no documento"))
        # tipo do requisito
        for kind, lista in (("Pré-Requisito", d.get("pre", [])), ("Correquisito", d.get("co", []))):
            for c in lista:
                cc = ids.get(c, c)
                if not re.search(kind + r"\s*:\s*" + re.escape(cc), r["req"]) and not (kind == "Pré-Requisito" and "Requisitos" not in r and cc in r["req"] and "Correquisito" not in r["req"]):
                    if not (kind == "Pré-Requisito" and cc in r["req"] and not re.search(r"Correquisito\s*:\s*" + re.escape(cc), r["req"])):
                        achados.append((nome, f"{r['cod']}: {cc} está como {kind} nos dados, mas o documento diz: {r['req'][:140]}"))
        sobra = re.sub(r"(Pr[ée]-Requisito|Correquisito)\s*:\s*" + COD + r"\s*-\s*", "", r["req"])
        if re.search(r"Percentual|Ter cumprido|cr[ée]ditos|Carga", sobra) and not (D.get("regras") or {}).get(d["c"]):
            achados.append((nome, f"{r['cod']}: requisito textual sem regra nos dados: {sobra[:140]}"))
    for c in list(porc) + list(opt):
        if c not in vistos:
            achados.append((nome, f"{c} está nos dados e não no documento"))


F = os.path.join(P, "FAAC")
bas = ler_html(os.path.join(F, "DARG/Artes_Visuais_Bacharelado/artes-visuais-estrutura-curricular-basico.html"))
comparar("artes-visuais-bach", dados("faac/artes-visuais/dados-artes-visuais-bacharelado-2504.js"),
         bas + ler_html(os.path.join(F, "DARG/Artes_Visuais_Bacharelado/artes-visuais-estrutura-curricular-bacharelado.html")))
comparar("artes-visuais-lic", dados("faac/artes-visuais/dados-artes-visuais-licenciatura-2504.js"),
         ler_html(os.path.join(F, "DARG/Artes_Visuais_Bacharelado/artes-visuais-estrutura-curricular-basico.html")) +
         ler_html(os.path.join(F, "DARG/Artes_Visuais_Licenciatura/artes-visuais-estrutura-curricular-licenciatura.html")))
rt = ler_html(os.path.join(F, "DARP/Comunicacao_Audiovisual/matriz-curricular-comunicacao-radio-televisao-e-internet.html"))
comparar("rtvi", dados("faac/comunicacao-audiovisual/dados-rtvi-1104i.js"), rt)
comparar("relacoes-publicas", dados("faac/relacoes-publicas/dados-relacoes-publicas-2023.js"), ler_html(os.path.join(F, "DARP/Relacoes_Publicas/matriz-curricular-relacoes-publicas.html")))
comparar("arquitetura", dados("faac/arquitetura-e-urbanismo/dados-arquitetura-urbanismo-2023.js"), ler_html(os.path.join(F, "DAUP/Arquitetura_e_Urbanismo/matriz-curricular-arquitetura-e-urbanismo.html")))
comparar("jornalismo", dados("faac/jornalismo/dados-jornalismo-2205.js"), ler_html(os.path.join(F, "DJOR/Jornalismo/matriz-curricular-jornalismo.html")))


# FEB: os PDFs não têm borda por linha (cada termo é uma única célula), então a segunda leitura
# da FEB é a transcrição visual das páginas (revisao/comparar_feb.py).

for c, a in achados:
    print(f"  [{c}] {a}")
print(f"\n{len(achados)} diferença(s).")
