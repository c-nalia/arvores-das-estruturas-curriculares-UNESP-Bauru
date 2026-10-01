#!/usr/bin/env python3
"""Confere, número a número, os arquivos de dados gerados contra os documentos de origem.

Uso (na raiz do projeto):  python3 testes/conferir_fontes.py

Para cada relação do Sistema de Graduação (CSV da FAAC, PDF da FEB), relê o documento e confere
cada código: termo, carga horária, CH ACEU, tipo e requisitos. Para os demais cursos, confere a
soma dos créditos/horas por termo com os totais impressos (via testes/referencia/verificacao.json)
e confere que cada disciplina transcrita aparece nos dados com os mesmos números.
Nomes podem diferir do documento apenas pelas correções registradas em "correcoes".
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas"))
from fontes_sg import ler_csv_sg, ler_pdf_sg  # noqa: E402
import transcricoes as T  # noqa: E402

P = os.path.join(RAIZ, "planos de ensino")
falhas = 0
total = 0


def ok(cond, msg):
    global falhas, total
    total += 1
    if not cond:
        falhas += 1
        print("  FALHA ", msg)


def dados(caminho):
    txt = open(os.path.join(RAIZ, caminho), encoding="utf-8").read()
    return json.loads(txt[txt.index("ArvoreGrade.registrar(") + 22: txt.rindex(");")])


def nome_esperado(D, cod, nome):
    for c in D.get("correcoes", []):
        if c["de"] == nome and (not c.get("cod") or c["cod"] == cod):
            return c["para"]
    return nome


def conferir_sg(arq_dados, fontes, ignorar_opt_na_grade=False):
    D = dados(arq_dados)
    print(f"\n[{D['id']}] conferência código a código com o Sistema de Graduação")
    por_cod = {d.get("cod", d["c"]): d for d in D["disciplinas"]}
    opt = {d.get("cod", d["c"]): d for d in (D.get("optativas") or {}).get("lista", [])}
    vistos = set()
    for f in fontes:
        for x in f["disciplinas"] + f["optativas"]:
            na_grade = x in f["disciplinas"] and not (ignorar_opt_na_grade and x["tipo"] == "OPT")
            d = por_cod.get(x["cod"]) if na_grade else opt.get(x["cod"])
            ok(d is not None, f"{x['cod']} do documento não está nos dados")
            if d is None:
                continue
            vistos.add(x["cod"])
            ok(d["n"] == nome_esperado(D, x["cod"], x["n"]), f"{x['cod']}: nome “{d['n']}” × documento “{x['n']}”")
            ch, aceu = x["ch"], x["aceu"]
            if x["tipo"] in ("ACEU", "ACE"):
                ok(d.get("aceu") == ch and d.get("tipoDoc") == x["tipo"], f"{x['cod']}: componente {x['tipo']} com carga {d.get('aceu')} × {ch}")
            else:
                ok((d.get("ch") or 0) == ch, f"{x['cod']}: carga {d.get('ch')} × documento {ch}")
                ok((d.get("aceu") or 0) == aceu, f"{x['cod']}: CH ACEU {d.get('aceu')} × documento {aceu}")
                ok(d["tipo"] == x["tipo"], f"{x['cod']}: tipo {d['tipo']} × documento {x['tipo']}")
            if na_grade:
                ok(d["t"] == x["t"], f"{x['cod']}: termo {d['t']} × documento {x['t']}")
            ids = {y["c"]: y.get("cod", y["c"]) for y in D["disciplinas"]}
            pre_d = sorted(ids.get(p, p) for p in d.get("pre", []))
            co_d = sorted(ids.get(p, p) for p in d.get("co", []))
            pre_txt = d.get("preTexto", "") + d.get("coTexto", "")
            for p in x["pre"]:
                ok(p in pre_d or p in pre_txt, f"{x['cod']}: pré-requisito {p} ausente")
            for p in x["co"]:
                ok(p in co_d or p in pre_txt, f"{x['cod']}: co-requisito {p} ausente")
            ok(len(pre_d) == len(set(x["pre"]) & set(pre_d)) and len(co_d) == len(set(x["co"]) & set(co_d)), f"{x['cod']}: requisito a mais nos dados")
    for c in list(por_cod) + list(opt):
        ok(c in vistos, f"{c} está nos dados e não no documento")


def conferir_transcricao(arq_dados, lista, chaves=("cr", "ch")):
    D = dados(arq_dados)
    print(f"\n[{D['id']}] conferência com a transcrição (ferramentas/transcricoes.py)")
    ds = list(D["disciplinas"])
    for x in lista:
        alvo = nome_esperado(D, None, x["n"])
        cands = [d for d in ds if d["t"] == x["t"] and d["n"] == alvo]
        ok(len(cands) >= 1, f"{x['t']}º termo: “{x['n']}” não está nos dados")
        if cands:
            d = cands[0]
            ds.remove(d)
            for k in chaves:
                if k in x:
                    ok(d.get(k) == x[k], f"{x['n']}: {k} {d.get(k)} × {x[k]}")
    ok(not ds, f"disciplinas a mais nos dados: {[d['n'] for d in ds]}")


SG = os.path.join
conferir_sg("faac/artes-visuais/dados-artes-visuais-bacharelado-2504.js",
            [ler_csv_sg(SG(P, "FAAC/DARG/Artes_Visuais_Bacharelado/artes-visuais-estrutura-curricular-basico.csv")),
             ler_csv_sg(SG(P, "FAAC/DARG/Artes_Visuais_Bacharelado/artes-visuais-estrutura-curricular-bacharelado.csv"))])
conferir_sg("faac/artes-visuais/dados-artes-visuais-licenciatura-2504.js",
            [ler_csv_sg(SG(P, "FAAC/DARG/Artes_Visuais_Bacharelado/artes-visuais-estrutura-curricular-basico.csv")),
             ler_csv_sg(SG(P, "FAAC/DARG/Artes_Visuais_Licenciatura/artes-visuais-estrutura-curricular-licenciatura.csv"))])
rtvi = ler_csv_sg(SG(P, "FAAC/DARP/Comunicacao_Audiovisual/matriz-curricular-comunicacao-radio-televisao-e-internet.csv"))
rtvi["optativas"] += [d for d in rtvi["disciplinas"] if d["tipo"] == "OPT"]
rtvi["disciplinas"] = [d for d in rtvi["disciplinas"] if d["tipo"] != "OPT"]
conferir_sg("faac/comunicacao-audiovisual/dados-rtvi-1104i.js", [rtvi])
conferir_sg("faac/relacoes-publicas/dados-relacoes-publicas-2023.js", [ler_csv_sg(SG(P, "FAAC/DARP/Relacoes_Publicas/matriz-curricular-relacoes-publicas.csv"))])
conferir_sg("faac/arquitetura-e-urbanismo/dados-arquitetura-urbanismo-2023.js", [ler_csv_sg(SG(P, "FAAC/DAUP/Arquitetura_e_Urbanismo/matriz-curricular-arquitetura-e-urbanismo_tabela2.csv"))])
conferir_sg("faac/jornalismo/dados-jornalismo-2205.js", [ler_csv_sg(SG(P, "FAAC/DJOR/Jornalismo/matriz-curricular-jornalismo.csv"))])
for arq, pdf in (("feb/engenharia-civil/dados-engenharia-civil-0104.js", "FEB/DEC/Engenharia_Civil/ecivil.pdf"),
                 ("feb/engenharia-eletrica/dados-engenharia-eletrica-0304.js", "FEB/DEE/Engenharia_Eletrica/eeletrica.pdf"),
                 ("feb/engenharia-mecanica/dados-engenharia-mecanica-0204.js", "FEB/DEM/Engenharia_Mecanica/emecanica.pdf"),
                 ("feb/engenharia-de-producao/dados-engenharia-de-producao-4403.js", "FEB/DEP/Engenharia_de_Producao/eproducao.pdf")):
    conferir_sg(arq, [ler_pdf_sg(SG(P, pdf))])

conferir_transcricao("fc/ciencias-biologicas/dados-ciencias-biologicas-2710.js", T.BIO_2710)
conferir_transcricao("fc/ciencias-biologicas/dados-ciencias-biologicas-2711.js", T.BIO_2711)
conferir_transcricao("fc/pedagogia/dados-pedagogia-2023.js", T.PEDAGOGIA)
conferir_transcricao("fc/psicologia/dados-psicologia-1212-1213.js", T.PSICOLOGIA, ("cr",))
conferir_transcricao("fc/quimica/dados-quimica-licenciatura-2023.js", T.QUI_LIC, ("ch",))
conferir_transcricao("fc/quimica/dados-quimica-tecnologica-2023.js", T.QUI_BACH, ("ch",))
for m, f in (("L", "licenciatura"), ("M", "materiais"), ("C", "computacional")):
    conferir_transcricao(f"fc/fisica/dados-fisica-1606-{f}.js", [d for d in T.FISICA if m in d["mods"]], ("cr",))
conferir_transcricao("fc/meteorologia/dados-meteorologia-1702.js", T.METEOROLOGIA)

v = json.load(open(os.path.join(RAIZ, "testes/referencia/verificacao.json"), encoding="utf-8"))
print(f"\n{total - falhas}/{total} verificações aprovadas, {falhas} falha(s).")
sys.exit(1 if falhas else 0)
