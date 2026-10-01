#!/usr/bin/env python3
"""Gera os arquivos de dados e as páginas da Árvore de Grade para todos os cursos de Bauru.

Uso (na raiz do projeto):
    python3 ferramentas/construir.py

Lê os documentos oficiais em "planos de ensino/" (CSV e PDF do Sistema de Graduação, PDFs das
faculdades, DOCs da Educação Física) e as transcrições de ferramentas/transcricoes.py, e escreve:

    <faculdade>/<curso>/dados-<id>.js      dados de cada currículo
    <faculdade>/<curso>/index.html         página do curso (com seletor quando há mais de um currículo)
    index.html                             índice de todos os cursos (página de avaliação)
    testes/referencia/verificacao.json     totais por termo do documento × soma dos dados

Regras:
  * Números (códigos, créditos, horas) são copiados do documento, nunca recalculados.
  * Nomes passam por CORRECOES (erros de grafia evidentes). Cada correção fica registrada no
    campo "correcoes" do arquivo de dados e é exibida no rodapé da página.
  * Requisitos citados por nome são ligados à disciplina correspondente; o que não corresponder a
    nenhuma disciplina da matriz vira texto ("preTexto"/"coTexto") e gera um aviso.
  * BCC e BSI (fc/bcc, fc/bsi) foram transcritos e conferidos à mão e NÃO são gerados aqui.
"""
import html as htmlmod
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict, OrderedDict

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from fontes_sg import ler_csv_sg, ler_pdf_sg  # noqa: E402
import transcricoes as T  # noqa: E402

PLANOS = os.path.join(RAIZ, "planos de ensino")
ATUALIZADO = "2026-09-30"

UNIDADES = {
    "FC": "Faculdade de Ciências · Câmpus de Bauru",
    "FAAC": "Faculdade de Arquitetura, Artes, Comunicação e Design · Câmpus de Bauru",
    "FEB": "Faculdade de Engenharia de Bauru · Câmpus de Bauru",
}
FONTES = json.load(open(os.path.join(AQUI, "fontes.json"), encoding="utf-8"))

# ---------------------------------------------------------------------------
# Correções de grafia. Cada item: (padrão regex, substituição, motivo). Só erros evidentes:
# ortografia, acentuação, letras trocadas pela fonte do PDF (l por I em numerais romanos),
# palavras duplicadas, maiúsculas indevidas e preposições/crases.
# ---------------------------------------------------------------------------
CORRECOES = [
    (r"\bComputacão\b", "Computação", "ortografia (cedilha)"),
    (r"\bCiêntifica\b", "Científica", "acentuação"),
    (r"\bCientifica\b", "Científica", "acentuação"),
    (r"\bEstagio\b", "Estágio", "acentuação"),
    (r"\bDIsciplinas\b", "Disciplinas", "maiúscula indevida"),
    (r"^ARQUITETURA$", "Arquitetura", "nome todo em maiúsculas"),
    (r"^URBANISMO$", "Urbanismo", "nome todo em maiúsculas"),
    (r"\blsostática\b", "Isostática", "letra trocada (l por I)"),
    (r"(?<=\s)(?=[IlV]*l)(?:[Il]{1,3}|[Il]?V|V[Il]{1,3})$", None, "numeral romano grafado com a letra l"),
    (r"\bPúblicas Em Educação\b", "Públicas em Educação", "maiúscula indevida na preposição"),
    (r"\bAplicado à Sistemas\b", "Aplicado a Sistemas", "crase indevida antes de palavra no plural"),
    (r"\bao Ensino e a pesquisa\b", "ao Ensino e à Pesquisa", "crase e uniformização de maiúsculas"),
    (r"Exercício de Força Exercício de Força", "Exercício de Força", "trecho repetido"),
    (r"\bBases Teórico-Prática do\b", "Bases Teórico-Práticas do", "concordância (como no nome da disciplina teórica)"),
    (r"\bProcessos de Produção e do Conhecimento\b", "Processos de Produção do Conhecimento", "palavras sobrando (como na disciplina II)"),
    (r"–I$", "– I", "espaço antes do numeral"),
    (r"\bprescrição para o Exercício\b", "Prescrição para o Exercício", "uniformização de maiúsculas (como na disciplina teórica)"),
    (r"^Ecologia (Comunidades|Populações|Ecossistemas)$", r"Ecologia de \1", "preposição ausente (como em “Ecologia de Populações”, 2710)"),
    (r"^Interação Biosfera Atmosfera$", "Interação Biosfera-Atmosfera", "hífen (como em “Interação Oceano-Atmosfera”)"),
    (r"\bHistória e Teorias e da Arquitetura\b", "História e Teorias da Arquitetura", "conjunção sobrando"),
    (r"\bvídeoarte\b", "videoarte", "acentuação (sem acento)"),
    (r"\bSócio- histórica\b", "Sócio-histórica", "espaço indevido"),
]
_ROMANO_L = re.compile(r"(?<=\s)([IlV]{1,4})(?=$|\s|:|,)")


def corrigir(nome):
    """Retorna (nome_corrigido, [motivos])."""
    motivos = []
    novo = nome
    for padrao, sub, motivo in CORRECOES:
        if sub is None:  # numerais romanos com "l": só tokens formados por I/l/V que contenham l
            def troca(m):
                tok = m.group(1)
                if "l" in tok and re.fullmatch(r"[IlV]+", tok):
                    return tok.replace("l", "I")
                return tok
            n2 = _ROMANO_L.sub(troca, novo)
        else:
            n2 = re.sub(padrao, sub, novo)
        if n2 != novo:
            motivos.append(motivo)
            novo = n2
    return novo, motivos


def norm(s):
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = s.replace("sócio- histórica", "socio-historica").replace("socio- historica", "socio-historica")
    s = re.sub(r"\s*[–-]\s*", "-", s)
    s = re.sub(r"\s+", " ", s).strip(" .;")
    return s


def num(v):
    if v is None:
        return None
    f = float(v)
    return int(f) if f == int(f) else f


# ---------------------------------------------------------------------------
# Montagem de um currículo a partir de uma lista "bruta" de disciplinas
# ---------------------------------------------------------------------------
class Curriculo:
    def __init__(self, **meta):
        self.meta = meta
        self.disc = []          # dicts brutos (com pre/co por nome ou código)
        self.opt = []
        self.avisos = []
        self.correcoes = []
        self.ref_totais = {}    # totais por termo impressos no documento
        self.unidade_ref = None  # "ch" | "cr" | "ch+aceu"

    # -- requisitos ------------------------------------------------------
    def _candidatos(self, ref, lista):
        r = norm(ref)
        return [d for d in lista if norm(d["_n0"]) == r or norm(d["n"]) == r or (d.get("cod") and norm(d["cod"]) == r)]

    def _escolher(self, cands, d, tipo):
        if not cands:
            return None
        if len(cands) == 1:
            return cands[0]
        if tipo == "pre":
            ant = [c for c in cands if c["t"] < d["t"]]
            return max(ant, key=lambda c: c["t"]) if ant else min(cands, key=lambda c: c["t"])
        mesmo = [c for c in cands if c["t"] == d["t"] and c is not d]
        if mesmo:
            return mesmo[0]
        ant = [c for c in cands if c["t"] <= d["t"] and c is not d]
        return max(ant, key=lambda c: c["t"]) if ant else cands[0]

    def resolver(self, aliases=None):
        aliases = {norm(k): v for k, v in (aliases or {}).items()}
        todos = self.disc
        for d in todos + self.opt:
            for tipo in ("pre", "co"):
                ids, textos = [], []
                for ref in d.get("_" + tipo, []):
                    alvo_nome = aliases.get(norm(ref), ref)
                    cands = self._candidatos(alvo_nome, todos)
                    c = self._escolher(cands, d, tipo)
                    if c is d:
                        textos.append(ref + " (a própria disciplina, conforme o documento)")
                        self.avisos.append(f"{rotulo_disc(d)}: o documento indica a própria disciplina como {'pré' if tipo == 'pre' else 'co'}-requisito.")
                        continue
                    if c is None:
                        nome_ref = d.get("_refnome", {}).get(ref, ref)
                        textos.append(nome_ref)
                        self.avisos.append(f"{rotulo_disc(d)}: {'pré' if tipo == 'pre' else 'co'}-requisito “{nome_ref}” não corresponde a nenhuma disciplina desta matriz; mantido como texto.")
                        continue
                    if norm(alvo_nome) != norm(ref):
                        self.avisos.append(f"{rotulo_disc(d)}: requisito citado como “{ref}” ligado a “{c['n']}”.")
                    if c["c"] not in ids:
                        ids.append(c["c"])
                if tipo == "pre":
                    for i in ids:
                        alvo = next(x for x in todos if x["c"] == i)
                        if alvo["t"] >= d.get("t", 0) and d.get("t", 99) != 99:
                            self.avisos.append(f"{rotulo_disc(d)} ({d['t']}º termo) tem como pré-requisito “{alvo['n']}”, do {alvo['t']}º termo, como está no documento.")
                d[tipo] = ids
                if textos:
                    d[tipo + "Texto"] = "; ".join(textos)

    # -- correções -------------------------------------------------------
    def aplicar_correcoes(self):
        vistos = set()
        for d in self.disc + self.opt:
            d["_n0"] = d["n"]
            novo, motivos = corrigir(d["n"])
            if motivos:
                d["n"] = novo
                chave = (d["_n0"], novo)
                if chave not in vistos:
                    vistos.add(chave)
                    self.correcoes.append({"de": d["_n0"], "para": novo, "motivo": "; ".join(motivos),
                                           "cod": d.get("cod") or None})

    # -- saída ------------------------------------------------------------
    def para_js(self):
        m = self.meta
        out = OrderedDict()
        for k in ("id", "sigla", "rotuloSeletor", "curso", "curriculo", "vigencia", "unidade"):
            if m.get(k) is not None:
                out[k] = m[k]
        out["atualizadoEm"] = ATUALIZADO
        for k in ("rotuloTermo", "creditosNoDocumento", "tiposNoDocumento", "fonte", "pagina", "contato", "quadroResumo", "regras"):
            if m.get(k):
                out[k] = m[k]
        disc = []
        for d in self.disc:
            x = OrderedDict()
            x["c"] = d["c"]
            if d.get("cod") and d["cod"] != d["c"]:
                x["cod"] = d["cod"]
            if d.get("semCodigo"):
                x["semCodigo"] = True
            x["t"] = d["t"]
            for k in ("ch", "cr", "aceu"):
                if d.get(k) is not None and not (k == "aceu" and not d[k]):
                    x[k] = d[k]
            x["tipo"] = d.get("tipo", "OBR")
            if d.get("d"):
                x["d"] = d["d"]
            x["n"] = d["n"]
            for k in ("pre", "co"):
                if d.get(k):
                    x[k] = d[k]
            for k in ("preTexto", "coTexto", "anual", "tipoDoc", "extras", "ementa", "classificacao"):
                if d.get(k):
                    x[k] = d[k]
            disc.append(x)
        out["disciplinas"] = disc
        o = m.get("optativas") or {}
        if self.opt or o:
            ob = OrderedDict()
            if o.get("fonte"):
                ob["fonte"] = o["fonte"]
            if o.get("exigencia"):
                ob["exigencia"] = o["exigencia"]
            if o.get("nota"):
                ob["nota"] = o["nota"]
            lst = []
            for d in self.opt:
                x = OrderedDict()
                x["c"] = d["c"]
                if d.get("cod") and d["cod"] != d["c"]:
                    x["cod"] = d["cod"]
                if d.get("semCodigo"):
                    x["semCodigo"] = True
                for k in ("ch", "cr", "aceu"):
                    if d.get(k):
                        x[k] = d[k]
                x["tipo"] = d.get("tipo", "OPT")
                if d.get("d"):
                    x["d"] = d["d"]
                x["n"] = d["n"]
                for k in ("pre", "co", "preTexto", "coTexto"):
                    if d.get(k):
                        x[k] = d[k]
                lst.append(x)
            ob["lista"] = lst
            out["optativas"] = ob
        av = []
        for a in (m.get("avisos") or []) + self.avisos:
            if a not in av:
                av.append(a)
        if av:
            out["avisos"] = av
        if self.correcoes:
            out["correcoes"] = self.correcoes
        return out


def rotulo_disc(d):
    return (d.get("cod") + " – " if d.get("cod") else "") + d["n"]


# ---------------------------------------------------------------------------
# Leitores por tipo de fonte
# ---------------------------------------------------------------------------
RE_PERC = re.compile(r"Percentual do Curso Exigido:\s*([\d.]+)%")


def _cod_id(cod):
    return cod.replace(" ", "")


def de_sg(cur, fonte, lista_extra=None):
    """Acrescenta ao currículo as disciplinas de uma relação do Sistema de Graduação."""
    for d in fonte["disciplinas"]:
        x = {"c": _cod_id(d["cod"]), "cod": d["cod"], "t": d["t"], "n": d["n"],
             "ch": num(d["ch"]), "aceu": num(d["aceu"]), "tipo": d["tipo"],
             "_pre": list(d["pre"]), "_co": list(d["co"])}
        bruto = " ".join(d["_req_bruto"])
        # nomes dos requisitos, para o caso de o código não estar nesta matriz
        x["_refnome"] = {}
        for cod in d["pre"] + d["co"]:
            mm = re.search(re.escape(cod) + r"\s*-\s*(.+?)(?=(?:Pr[ée]-Requisito|Correquisito|Percentual)|$)", bruto)
            x["_refnome"][cod] = cod + (" – " + mm.group(1).strip(" ,;") if mm else "")
        mp = RE_PERC.search(bruto)
        if mp:
            v = float(mp.group(1))
            x["_regra"] = {"tipo": "percentualObrigatorias", "valor": round(v / 100, 4),
                           "texto": "Percentual do Curso Exigido: " + mp.group(1).replace(".", ",") + "%"}
        if d["tipo"] in ("ACEU", "ACE"):  # Arquitetura: componentes de extensão com carga própria
            x["aceu"], x["ch"], x["tipoDoc"], x["tipo"] = x["ch"], 0, d["tipo"], "OBR"
            x["classificacao"] = "extensao"
        cur.disc.append(x)
    for d in fonte["optativas"] + (lista_extra or []):
        cur.opt.append({"c": _cod_id(d["cod"]), "cod": d["cod"], "n": d["n"], "ch": num(d["ch"]),
                        "aceu": num(d["aceu"]), "tipo": d["tipo"] or "OPT", "_pre": list(d["pre"]), "_co": list(d["co"]),
                        "t": 99})
    for t, tots in fonte["totais_termo"].items():
        cur.ref_totais.setdefault(t, []).append(tots[0][0])


def ids_sem_codigo(lista):
    cont = defaultdict(int)
    for d in lista:
        cont[d["t"]] += 1
        d["c"] = f"{d['t']}.{cont[d['t']]}"
        d["semCodigo"] = True


def de_transcricao(cur, lista, ids=True):
    for d in lista:
        x = dict(d)
        x["_pre"] = list(d.get("pre", []))
        x["_co"] = list(d.get("co", []))
        x.pop("pre", None)
        x.pop("co", None)
        x.setdefault("tipo", "OBR")
        cur.disc.append(x)
    if ids:
        ids_sem_codigo(cur.disc)


def resumo_quadro(linhas, prefixo=""):
    """Linhas "Total Carga Horária ... do Curso: N (sendo M em aceus)" → linhas de quadro."""
    out, exig = [], []
    for l in linhas:
        m = re.match(r"Total Carga Horária (.+?) do Curso:\s*([\d.]+)(\*?)(?:\s*\(sendo ([\d.]+) em aceus\))?", l)
        if not m:
            if l.startswith("*"):
                exig.append(l)
            continue
        rot = prefixo + "Carga horária " + m.group(1).lower() + m.group(3)
        rot = rot.replace("tcc", "TCC")
        if m.group(4):
            rot += f" (sendo {num(m.group(4))} h em ACEU)"
        v = num(m.group(2))
        out.append([rot, v])
        if "optativa" in m.group(1).lower() and v:
            exig.append(l)
    return out, exig


def fonte_de(pasta, i=0, titulo=None):
    f = FONTES[pasta]["arquivos"][i]
    return {"titulo": titulo or f["texto"].strip(" -;"), "url": f["origem"]}


def pagina_de(pasta):
    return {"titulo": "página do curso", "url": FONTES[pasta]["pagina"]}


# ---------------------------------------------------------------------------
# Cursos
# ---------------------------------------------------------------------------
CURSOS = []  # (pasta_saida, titulo_pagina, descricao, [Curriculo...])


def faac():
    P = os.path.join(PLANOS, "FAAC")
    un = UNIDADES["FAAC"]
    # Artes Visuais: núcleo básico + bacharelado / licenciatura (currículo 2504)
    bas = ler_csv_sg(os.path.join(P, "DARG/Artes_Visuais_Bacharelado/artes-visuais-estrutura-curricular-basico.csv"))
    curs = []
    for sufixo, arq, pasta, nome, rot in (
        ("bacharelado", "DARG/Artes_Visuais_Bacharelado/artes-visuais-estrutura-curricular-bacharelado.csv", "FAAC/DARG/Artes_Visuais_Bacharelado", "Bacharelado em Artes Visuais", "Bacharelado"),
        ("licenciatura", "DARG/Artes_Visuais_Licenciatura/artes-visuais-estrutura-curricular-licenciatura.csv", "FAAC/DARG/Artes_Visuais_Licenciatura", "Licenciatura em Artes Visuais", "Licenciatura"),
    ):
        esp = ler_csv_sg(os.path.join(P, arq))
        cur = Curriculo(id="artes-visuais-" + sufixo + "-2504", sigla="Artes Visuais", rotuloSeletor=rot, curso=nome,
                        curriculo="2504 (núcleo básico) + " + esp["cabecalho"].split(" - ")[0] + " (" + rot.lower() + ")",
                        vigencia="Estrutura curricular vigente", unidade=un, rotuloTermo="serie-periodo", tiposNoDocumento=True,
                        fonte={"titulo": "Estrutura Curricular – Básico e " + rot, "url": FONTES[pasta]["pagina"]},
                        pagina=pagina_de(pasta), contato=pagina_de(pasta))
        de_sg(cur, bas)
        de_sg(cur, esp)
        q1, e1 = resumo_quadro(bas["resumo"], "2504 · núcleo básico — ")
        q2, e2 = resumo_quadro(esp["resumo"], esp["cabecalho"].split(" - ")[0] + " · " + rot.lower() + " — ")
        cur.meta["quadroResumo"] = {"titulo": "Totais informados no documento", "cabecalho": "Componente", "colunas": ["Horas"], "linhas": q1 + q2}
        cur.meta["avisos"] = ["A matriz reúne as duas relações publicadas pelo curso: o núcleo básico (2504) e a formação específica (" + rot.lower() + "). As disciplinas da formação específica começam no 3º termo."]
        if e2:
            cur.meta["optativas"] = {"exigencia": e2 + [x for x in esp["resumo"] if x.startswith("*")]}
        curs.append(cur)
    CURSOS.append(("faac/artes-visuais", "Artes Visuais", "Bacharelado e Licenciatura · currículo 2504", curs))

    # Comunicação: Rádio, TV e Internet (Audiovisual)
    pasta = "FAAC/DARP/Comunicacao_Audiovisual"
    f = ler_csv_sg(os.path.join(P, "DARP/Comunicacao_Audiovisual/matriz-curricular-comunicacao-radio-televisao-e-internet.csv"))
    opt_extra = [d for d in f["disciplinas"] if d["tipo"] == "OPT"]
    f["disciplinas"] = [d for d in f["disciplinas"] if d["tipo"] != "OPT"]
    for t in list(f["totais_termo"]):
        f["totais_termo"][t] = f["totais_termo"][t][:1]
    cur = Curriculo(id="rtvi-1104i", sigla="Comunicação: Rádio, TV e Internet", curso="Comunicação: Rádio, TV e Internet (Audiovisual)",
                    curriculo="1104I", vigencia="Ingressantes a partir de 2023", unidade=un, rotuloTermo="serie-periodo", tiposNoDocumento=True,
                    fonte={"titulo": "Matriz curricular – ingressantes a partir de 2023", "url": FONTES[pasta]["pagina"]},
                    pagina=pagina_de(pasta), contato=pagina_de(pasta))
    de_sg(cur, f, opt_extra)
    q, _ = resumo_quadro(f["resumo"])
    cur.meta["quadroResumo"] = {"titulo": "Totais informados no documento", "cabecalho": "Componente", "colunas": ["Horas"], "linhas": q}
    cur.meta["optativas"] = {"fonte": {"titulo": "Matriz curricular – ingressantes a partir de 2023", "url": FONTES[pasta]["pagina"]}}
    CURSOS.append(("faac/comunicacao-audiovisual", "Comunicação: Rádio, TV e Internet", "Currículo 1104I · ingressantes a partir de 2023", [cur]))

    # Relações Públicas
    pasta = "FAAC/DARP/Relacoes_Publicas"
    f = ler_csv_sg(os.path.join(P, "DARP/Relacoes_Publicas/matriz-curricular-relacoes-publicas.csv"))
    cur = Curriculo(id="relacoes-publicas-2023", sigla="Relações Públicas", curso="Relações Públicas",
                    curriculo=None, vigencia="Ingressantes a partir de 2023", unidade=un, rotuloTermo="serie-periodo", tiposNoDocumento=True,
                    fonte={"titulo": "Matriz curricular – ingressantes a partir de 2023", "url": FONTES[pasta]["pagina"]},
                    pagina=pagina_de(pasta), contato=pagina_de(pasta))
    de_sg(cur, f)
    q, _ = resumo_quadro(f["resumo"])
    cur.meta["quadroResumo"] = {"titulo": "Totais informados no documento", "cabecalho": "Componente", "colunas": ["Horas"], "linhas": q}
    cur.meta["avisos"] = ["O documento publicado não informa o número do currículo."]
    CURSOS.append(("faac/relacoes-publicas", "Relações Públicas", "Ingressantes a partir de 2023", [cur]))

    # Arquitetura e Urbanismo
    pasta = "FAAC/DAUP/Arquitetura_e_Urbanismo"
    f = ler_csv_sg(os.path.join(P, "DAUP/Arquitetura_e_Urbanismo/matriz-curricular-arquitetura-e-urbanismo_tabela2.csv"))
    cur = Curriculo(id="arquitetura-urbanismo-2023", sigla="Arquitetura e Urbanismo", curso="Arquitetura e Urbanismo",
                    curriculo=None, vigencia="Ingressantes a partir de 2023", unidade=un, rotuloTermo="serie-periodo", tiposNoDocumento=True,
                    fonte={"titulo": "Estrutura curricular – Resolução Unesp nº 123/2023", "url": FONTES[pasta]["arquivos"][1]["origem"]},
                    pagina=pagina_de(pasta), contato=pagina_de(pasta))
    de_sg(cur, f)
    import csv
    linhas = list(csv.reader(open(os.path.join(P, "DAUP/Arquitetura_e_Urbanismo/matriz-curricular-arquitetura-e-urbanismo_tabela1.csv"), encoding="utf-8-sig")))
    corpo = [[l[0], num(l[1])] for l in linhas[1:] if l and l[0] != "Carga Horária Total"]
    total = [num(l[1]) for l in linhas[1:] if l and l[0] == "Carga Horária Total"]
    cur.meta["quadroResumo"] = {"cabecalho": "Componentes Curriculares", "colunas": ["Horas"], "linhas": corpo, "total": total, "rotuloTotal": "Carga Horária Total"}
    cur.meta["optativas"] = {"exigencia": ["O quadro-resumo exige 240 horas em disciplinas optativas. A relação de optativas não consta do documento publicado."]}
    cur.meta["avisos"] = ["Componentes dos tipos “ACEU” e “ACE” no documento (atividades curriculares de extensão) aparecem com a sua carga como CH ACEU e fora da soma das obrigatórias.",
                          "O documento publicado não informa o número do currículo."]
    CURSOS.append(("faac/arquitetura-e-urbanismo", "Arquitetura e Urbanismo", "Ingressantes a partir de 2023", [cur]))

    # Jornalismo
    pasta = "FAAC/DJOR/Jornalismo"
    f = ler_csv_sg(os.path.join(P, "DJOR/Jornalismo/matriz-curricular-jornalismo.csv"))
    cur = Curriculo(id="jornalismo-2205", sigla="Jornalismo", curso="Jornalismo", curriculo="2205",
                    vigencia="Ingressantes a partir de 2023", unidade=un, rotuloTermo="serie-periodo", tiposNoDocumento=True,
                    fonte={"titulo": "Matriz curricular – ingressantes a partir de 2023 (estrutura 2205)", "url": FONTES[pasta]["pagina"]},
                    pagina=pagina_de(pasta), contato=pagina_de(pasta))
    de_sg(cur, f)
    q, _ = resumo_quadro(f["resumo"])
    cur.meta["quadroResumo"] = {"titulo": "Totais informados no documento", "cabecalho": "Componente", "colunas": ["Horas"], "linhas": q}
    CURSOS.append(("faac/jornalismo", "Jornalismo", "Estrutura 2205 · ingressantes a partir de 2023", [cur]))

    # Design
    pasta = "FAAC/DDI/Design"
    cur = Curriculo(id="design-2023", sigla="Design", curso="Bacharelado em Design", curriculo="2023",
                    vigencia="Ingressantes a partir de 2024", unidade=un,
                    fonte=fonte_de(pasta, 0, "Estrutura curricular Bacharelado Design 2023"), pagina=pagina_de(pasta), contato=pagina_de(pasta))
    lst = []
    for t, nomes in T.DESIGN:
        for n in nomes:
            tipo = "SLOT" if n.startswith("OPTATIVA") else "TRA" if n.startswith("TCC") else "OBR"
            lst.append({"t": t, "n": n, "tipo": tipo})
    de_transcricao(cur, lst)
    cur.meta["semCarga"] = True
    cur.meta["avisos"] = ["O documento publicado apresenta apenas os componentes de cada termo: não informa códigos, cargas horárias nem pré-requisitos. A árvore mostra a sequência dos termos, sem ligações."]
    cur.meta["optativas"] = {"exigencia": ["A matriz prevê três optativas (7º e 8º termos). A relação de optativas não consta do documento publicado."]}
    CURSOS.append(("faac/design", "Design", "Estrutura curricular 2023 · ingressantes a partir de 2024", [cur]))


def feb():
    P = os.path.join(PLANOS, "FEB")
    un = UNIDADES["FEB"]
    for arq, pasta, slug, nome, cod in (
        ("DEC/Engenharia_Civil/ecivil.pdf", "FEB/DEC/Engenharia_Civil", "engenharia-civil", "Engenharia Civil", "0104"),
        ("DEE/Engenharia_Eletrica/eeletrica.pdf", "FEB/DEE/Engenharia_Eletrica", "engenharia-eletrica", "Engenharia Elétrica", "0304"),
        ("DEM/Engenharia_Mecanica/emecanica.pdf", "FEB/DEM/Engenharia_Mecanica", "engenharia-mecanica", "Engenharia Mecânica", "0204"),
        ("DEP/Engenharia_de_Producao/eproducao.pdf", "FEB/DEP/Engenharia_de_Producao", "engenharia-de-producao", "Engenharia de Produção", "4403"),
    ):
        f = ler_pdf_sg(os.path.join(P, arq))
        cur = Curriculo(id=slug + "-" + cod, sigla=nome, curso=nome, curriculo=cod, vigencia="Ingressantes a partir de 2023",
                        unidade=un, rotuloTermo="serie-periodo", tiposNoDocumento=True,
                        fonte=fonte_de(pasta, 0, "Estrutura curricular vigente (a partir de 2023)"), pagina=pagina_de(pasta), contato=pagina_de(pasta))
        de_sg(cur, f)
        q, ex = resumo_quadro(f["resumo"])
        if q:
            cur.meta["quadroResumo"] = {"titulo": "Totais informados no documento", "cabecalho": "Componente", "colunas": ["Horas"], "linhas": q}
        if ex:
            cur.meta["optativas"] = {"exigencia": ["O documento exige 240 horas em disciplinas optativas (“" + ex[0] + "”). A relação de optativas não consta do documento publicado."]}
        if any(d["tipo"] == "OPT" for d in cur.disc):
            cur.meta["avisos"] = ["Disciplinas do tipo OPT aparecem na grade porque o documento as posiciona num termo e as inclui no total do termo."]
        CURSOS.append(("feb/" + slug, nome, "Currículo " + cod + " · ingressantes a partir de 2023", [cur]))


def fc():
    P = os.path.join(PLANOS, "FC")
    un = UNIDADES["FC"]

    # Ciências Biológicas
    pasta = "FC/DCB/Ciencias_Biologicas"
    curs = []
    for i, (cid, cod, nome, rot, lista, tots, quadro, aceus) in enumerate((
        ("ciencias-biologicas-2710", "2710", "Ciências Biológicas – Bacharelado (integral)", "Bacharelado · integral (2710)", T.BIO_2710, T.BIO_2710_TOTAIS, T.BIO_2710_QUADRO, "390h"),
        ("ciencias-biologicas-2711", "2711", "Ciências Biológicas – Licenciatura (noturno)", "Licenciatura · noturno (2711)", T.BIO_2711, T.BIO_2711_TOTAIS, T.BIO_2711_QUADRO, "392h"),
    )):
        cur = Curriculo(id=cid, sigla="Ciências Biológicas", rotuloSeletor=rot, curso=nome, curriculo=cod, vigencia="Vigente",
                        unidade=un, rotuloTermo="ano-semestre", creditosNoDocumento=True,
                        fonte=fonte_de(pasta, i), pagina=pagina_de(pasta), contato=pagina_de(pasta))
        de_transcricao(cur, lista)
        cur.ref_totais = {t: [v[1]] for t, v in tots.items()}
        cur.unidade_ref = "ch"
        cur.meta["quadroResumo"] = {"titulo": "Quadro resumo", "cabecalho": "Componente Curricular", "colunas": ["Créditos", "Horas"], "linhas": quadro}
        cur.meta["avisos"] = [
            "Disciplinas anuais (A) aparecem nos dois semestres do ano, como na planilha oficial, que conta os créditos em cada semestre.",
            "A planilha não informa códigos das disciplinas; o quadro resumo indica que as obrigatórias incluem " + aceus + " de ACEUs, sem dizer em quais disciplinas.",
        ]
        curs.append(cur)
    CURSOS.append(("fc/ciencias-biologicas", "Ciências Biológicas", "Bacharelado (2710) e Licenciatura (2711)", curs))

    # Pedagogia
    pasta = "FC/DED/Pedagogia"
    cur = Curriculo(id="pedagogia-2023", sigla="Pedagogia", curso="Licenciatura em Pedagogia", curriculo="2023",
                    vigencia="Ingressantes a partir de 2023", unidade=un, creditosNoDocumento=True,
                    fonte=fonte_de(pasta), pagina=pagina_de(pasta), contato=pagina_de(pasta))
    de_transcricao(cur, T.PEDAGOGIA)
    cur.meta["avisos"] = ["A matriz não informa códigos nem pré-requisitos. Carga por termo impressa no documento: " +
                          "; ".join(f"{t}º termo: {v}" for t, v in T.PEDAGOGIA_CH.items()) + "."]
    CURSOS.append(("fc/pedagogia", "Pedagogia", "Licenciatura · ingressantes a partir de 2023", [cur]))

    # Psicologia
    pasta = "FC/DPSI/Psicologia"
    cur = Curriculo(id="psicologia-1212-1213", sigla="Psicologia", curso="Graduação em Psicologia (integral e noturno)",
                    curriculo="1212/1213", vigencia="Ingressantes a partir de 2023", unidade=un, creditosNoDocumento=True,
                    fonte=fonte_de(pasta, 0, "Currículo 1212/1213, Integral e Noturno"), pagina=pagina_de(pasta), contato=pagina_de(pasta))
    lst = []
    for d in T.PSICOLOGIA:
        x = dict(d)
        ex = []
        if x.pop("xc", None):
            ex.append(["Atividade extraclasse ou prática", d["xc"]])
        if x.pop("ext", None):
            ex.append(["Extensão", d["ext"]])
        if ex:
            x["extras"] = [[r, v, "cr"] for r, v in ex]
        x.pop("semSemestre", None)
        x.pop("semestreImpresso", None)
        if x.get("tipo") == "AC":
            x["tipo"] = "OBR"
        lst.append(x)
    de_transcricao(cur, lst)
    cur.meta["quadroResumo"] = {"titulo": "Carga horária total (ajuste do PPP às DCN)", "cabecalho": "Carga horária", "colunas": ["Créditos", "Horas"],
                                "linhas": [[r[0], r[1], r[2]] for r in T.PSICOLOGIA_QUADRO["linhas"]], "total": T.PSICOLOGIA_QUADRO["total"],
                                "nota": "Detalhamento por modalidade: " + "; ".join(f"{a} {b} créditos ({c} h)" for a, b, c in T.PSICOLOGIA_QUADRO["detalhamento"]) + "."}
    cur.meta["avisos"] = [
        "Estágios específicos (9º e 10º semestres, anuais): " + T.PSICOLOGIA_OBS + ". No documento, os semestres aparecem como “9 e 10”, “10 e 10”, “11 e 10” e “12 e 10”; aqui os quatro programas ficam no 9º termo.",
        "“" + T.ACA + ": Processos Educativos I” não tem semestre informado no documento; está no 4º termo, posição que ocupa na tabela.",
        "As colunas “Atividade Extraclasse ou Prática” e “Extensão” aparecem ao lado dos créditos de cada disciplina, como no documento.",
    ]
    cur.meta["optativas"] = {"exigencia": ["A matriz prevê duas optativas (6º e 7º semestres). A relação de optativas não consta do documento publicado."]}
    aliases = {"Fundamentos das Teorias Sistêmicas e Complexas": "Fundamentos das Teorias Sistêmica e Complexa"}
    cur._aliases = aliases
    CURSOS.append(("fc/psicologia", "Psicologia", "Currículo 1212/1213 · integral e noturno", [cur]))

    # Química
    pasta = "FC/DQ/Quimica"
    curs = []
    for cid, nome, rot, lista, fora, decl in (
        ("quimica-licenciatura-2023", "Licenciatura em Química", "Licenciatura", T.QUI_LIC, T.QUI_LIC_FORA, T.QUI_LIC_DECLARADO),
        ("quimica-tecnologica-2023", "Bacharelado em Química Tecnológica", "Bacharelado em Química Tecnológica", T.QUI_BACH, T.QUI_BACH_FORA, T.QUI_BACH_DECLARADO),
    ):
        cur = Curriculo(id=cid, sigla="Química", rotuloSeletor=rot, curso=nome, curriculo="2023", vigencia="Vigente a partir do ano letivo de 2023",
                        unidade=un, rotuloTermo="ano-semestre", fonte=fonte_de(pasta, 0, "Matrizes curriculares e ementário – Química"),
                        pagina=pagina_de(pasta), contato=pagina_de(pasta))
        de_transcricao(cur, lista)
        soma = sum(d["ch"] for d in lista) + sum(v for _, v in fora)
        cur.meta["quadroResumo"] = {"titulo": "Carga horária", "cabecalho": "Componente", "colunas": ["Horas"],
                                    "linhas": [["Disciplinas da matriz (soma)", sum(d["ch"] for d in lista)]] + [[a, b] for a, b in fora],
                                    "nota": f"Carga horária declarada no documento: {decl[0]} horas ({decl[1]} créditos)."}
        av = ["Disciplinas que ocupam dois semestres aparecem nos dois, como na matriz oficial, com a carga indicada em cada um.",
              "A matriz não informa códigos nem pré-requisitos."]
        if soma != decl[0]:
            av.append(f"A soma das cargas da matriz ({soma} h, incluindo {fora[0][0].lower()}) difere da carga declarada no documento ({decl[0]} h). Os números foram mantidos como publicados.")
        cur.meta["avisos"] = av
        curs.append(cur)
    CURSOS.append(("fc/quimica", "Química", "Licenciatura e Bacharelado em Química Tecnológica", curs))

    # Física
    pasta = "FC/DFM/Fisica"
    ementas = ementas_fisica(os.path.join(P, "DFM/Fisica/grade-por-termo-com-ementa-e-objetivo-2.pdf"))
    curs = []
    for m, cid, nome, rot in (("L", "fisica-1606-licenciatura", "Licenciatura em Física", "Licenciatura"),
                              ("M", "fisica-1606-materiais", "Bacharelado em Física – Física de Materiais", "Bacharelado · Física de Materiais"),
                              ("C", "fisica-1606-computacional", "Bacharelado em Física – Física Computacional", "Bacharelado · Física Computacional")):
        cur = Curriculo(id=cid, sigla="Física", rotuloSeletor=rot, curso=nome, curriculo="1606", vigencia="Estrutura curricular vigente",
                        unidade=un, creditosNoDocumento=True, fonte=fonte_de(pasta, 0, "Grade das disciplinas por termos, com ementas e objetivos"),
                        pagina=pagina_de(pasta), contato=pagina_de(pasta))
        lst = []
        for d in T.FISICA:
            if m not in d["mods"]:
                continue
            x = {k: v for k, v in d.items() if k != "mods"}
            e = ementas.get(norm(x["n"]))
            if e:
                x["ementa"] = e["ementa"]
                x["d"] = e["dep"]
            lst.append(x)
        de_transcricao(cur, lst)
        cur.ref_totais = {t: [v] for t, v in T.FISICA_TOTAIS[m].items()}
        cur.unidade_ref = "cr"
        h, c = T.FISICA_DECLARADO[m]
        cur.meta["quadroResumo"] = {"titulo": "Carga horária da modalidade", "cabecalho": "Modalidade", "colunas": ["Créditos", "Horas"],
                                    "linhas": [[nome, c, h]]}
        cur.meta["avisos"] = ["O documento não estabelece pré-requisitos formais: as ementas indicam apenas a seriação ideal (e, em dois casos, um “pré-requisito recomendado”).",
                              "Ementas e departamentos foram copiados do próprio documento, quando ele traz a ementa da disciplina."]
        if m == "L" or m == "M":
            cur.meta["avisos"].append("“Química Geral II” tem 4 créditos na tabela do 3º termo e 2 créditos no cabeçalho da sua ementa; vale a tabela, cujos totais conferem.")
        curs.append(cur)
    CURSOS.append(("fc/fisica", "Física", "Estrutura curricular 1606 · Licenciatura e Bacharelado", curs))

    # Meteorologia
    pasta = "FC/DFM/Meteorologia"
    cur = Curriculo(id="meteorologia-1702", sigla="Meteorologia", curso="Bacharelado em Meteorologia", curriculo="1702",
                    vigencia="Vigente", unidade=un, rotuloTermo="ano-semestre", creditosNoDocumento=True,
                    fonte={"titulo": "Grade curricular (página do curso)", "url": FONTES[pasta]["pagina"]}, pagina=pagina_de(pasta), contato=pagina_de(pasta))
    for d in T.METEOROLOGIA:
        x = dict(d)
        x["c"] = x["cod"]
        x["_pre"], x["_co"] = x.pop("pre"), x.pop("co")
        cur.disc.append(x)
    for i, d in enumerate(T.METEOROLOGIA_OPT):
        x = dict(d)
        x["c"] = x["cod"] or f"opt{i + 1}"
        if not x["cod"]:
            x["semCodigo"] = True
            x.pop("cod")
        x["tipo"] = "OPT"
        x["t"] = 99
        x["_pre"], x["_co"] = x.pop("pre"), x.pop("co")
        cur.opt.append(x)
    cur.ref_totais = {t: [v[1]] for t, v in T.METEOROLOGIA_TOTAIS.items()}
    cur.unidade_ref = "ch"
    cur.meta["optativas"] = {"fonte": {"titulo": "Disciplinas optativas (página do curso)", "url": FONTES[pasta]["pagina"]}}
    cur.meta["avisos"] = [
        "Os códigos 7005 (6 créditos) e 7050 (4 créditos), no 2º semestre do 1º ano, têm o mesmo nome no documento: “Energia e Sustentabilidade Ambiental”.",
        "A soma dos créditos da grade (197) difere do total de disciplinas obrigatórias informado na página do curso (187 créditos, 2805 h, além de 60 h de estágio e 195 h de atividades complementares; total 3150 h).",
    ]
    CURSOS.append(("fc/meteorologia", "Meteorologia", "Bacharelado · currículo 1702", [cur]))

    # Matemática
    pasta = "FC/DM/Matematica"
    import csv
    linhas = list(csv.reader(open(os.path.join(P, "DM/Matematica/grade-curricular-1507.csv"), encoding="utf-8-sig")))
    cur = Curriculo(id="matematica-1507", sigla="Matemática", curso="Licenciatura em Matemática", curriculo="1507", vigencia="Vigente",
                    unidade=un, creditosNoDocumento=True, fonte={"titulo": "Grade curricular 1507 (página do curso)", "url": FONTES[pasta]["pagina"]},
                    pagina=pagina_de(pasta), contato=pagina_de(pasta))
    t = 0
    for l in linhas[1:]:
        l = (l + [""] * 7)[:7]
        if re.match(r"\d+º Termo", l[2]):
            t = int(l[2].split("º")[0])
            continue
        if l[2] == "Total":
            cur.ref_totais[t] = [num(l[3])]
            continue
        if not l[0]:
            continue
        cur.disc.append({"c": f"{l[0]}" if not any(d["cod"] == l[0] for d in cur.disc) else f"{l[0]}-{t}", "cod": l[0], "d": l[1], "n": l[2], "cr": num(l[3]),
                         "t": t, "tipo": "EST" if l[2].startswith("Estágio") else "TRA" if l[2].startswith("TCC") else "OBR",
                         "anual": l[4] == "Anual", "_pre": [x for x in l[5].split("/") if x], "_co": [x for x in l[6].split("/") if x]})
    # a primeira ocorrência de disciplina anual também recebe sufixo de termo, para ids simétricos
    for d in cur.disc:
        if d["anual"] and d["c"] == d["cod"]:
            d["c"] = f"{d['cod']}-{d['t']}"
    cur.unidade_ref = "cr"
    cur.meta["avisos"] = ["Disciplinas anuais aparecem nos dois termos do ano, com os créditos indicados em cada um, como na tabela oficial.",
                          "O código 8101A (Estágio Curricular Supervisionado I) tem 06 créditos no 5º termo e 07 no 6º termo, como publicado."]
    CURSOS.append(("fc/matematica", "Matemática", "Licenciatura · currículo 1507", [cur]))

    # Educação Física
    pasta = "FC/DEF/Educacao_Fisica"
    curs = []
    for i_arq, cid, nome, rot in ((3, "educacao-fisica-2610-bacharelado", "Educação Física – Bacharelado (integral)", "Bacharelado · integral (2610)"),
                                  (2, "educacao-fisica-2610-licenciatura", "Educação Física – Licenciatura (integral)", "Licenciatura · integral (2610)"),
                                  (1, "educacao-fisica-2611-bacharelado", "Educação Física – Bacharelado (noturno)", "Bacharelado · noturno (2611)"),
                                  (0, "educacao-fisica-2611-licenciatura", "Educação Física – Licenciatura (noturno)", "Licenciatura · noturno (2611)")):
        arq = FONTES[pasta]["arquivos"][i_arq]
        lista, tots, obs = ler_edf(os.path.join(P, "DEF/Educacao_Fisica", arq["arquivo"]))
        cur = Curriculo(id=cid, sigla="Educação Física", rotuloSeletor=rot, curso=nome, curriculo=cid.split("-")[2],
                        vigencia="Ingressantes a partir de 2015", unidade=un, creditosNoDocumento=True,
                        fonte={"titulo": arq["texto"].strip(" -;"), "url": arq["origem"]}, pagina=pagina_de(pasta), contato=pagina_de(pasta))
        de_transcricao(cur, lista)
        cur.ref_totais = {t: [v] for t, v in tots.items()}
        cur.unidade_ref = "cr"
        cur.meta["quadroResumo"] = {"titulo": "Integralização (conforme o documento)", "cabecalho": "Componente", "colunas": ["Créditos", "H/A"],
                                    "linhas": obs["linhas"], "total": obs["total"], "rotuloTotal": "Total de Créditos Exigidos"}
        cur.meta["optativas"] = {"exigencia": ["O documento exige 08 créditos (120 H/A) em disciplinas optativas, previstos como Optativa I e Optativa II. A relação de optativas não consta do documento publicado."]}
        cur.meta["avisos"] = [obs["legenda"], "Pré-requisitos foram indicados no documento por siglas: “PPCCEF -I” (Processos de Produção do Conhecimento Científico em Educação Física I) e “FE - I” (Fisiologia do Exercício I)."] + obs["avisos"]
        cur._aliases = {"PPCCEF -I": "Processos de Produção e do Conhecimento Científico em Educação Física I", "FE - I": "Fisiologia do Exercício I"}
        curs.append(cur)
    CURSOS.append(("fc/educacao-fisica", "Educação Física", "Bacharelado e Licenciatura · currículos 2610 (integral) e 2611 (noturno)", curs))


def ementas_fisica(pdf):
    txt = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout.replace("\f", "\n")
    cab = list(re.finditer(r"(?m)^([^\n()]{3,120}?)\s*\((\d+)\s*cr[ée]ditos\s*[–-]\s*([^–\n)]*?)\s*[–-]\s*([A-Za-z]+)\s*\)", txt))
    out = {}
    for i, h in enumerate(cab):
        fim = cab[i + 1].start() if i + 1 < len(cab) else len(txt)
        bloco = txt[h.end():fim]
        m = re.search(r"Ementa:\s*(.+?)(?:\n\s*Objetivos?:|$)", bloco, re.S)
        if not m:
            continue
        ementa = re.sub(r"\s+", " ", m.group(1)).strip()
        chave = norm(h.group(1))
        out.setdefault(chave, {"ementa": ementa, "dep": h.group(4)})
    return out


def ler_edf(doc):
    """Lê uma estrutura curricular da Educação Física (DOC convertido em HTML pelo LibreOffice)."""
    import pandas as pd
    cache = os.path.join(AQUI, ".cache", "edf")
    os.makedirs(cache, exist_ok=True)
    htmlp = os.path.join(cache, os.path.splitext(os.path.basename(doc))[0] + ".html")
    if not os.path.exists(htmlp):
        subprocess.run(["soffice", "--headless", "--convert-to", "html", "--outdir", cache, doc], check=True, capture_output=True)
    tab = pd.read_html(htmlp)[0].fillna("")
    lista, tots, t = [], {}, 0
    for _, r in tab.iterrows():
        vals = []
        for v in r.tolist():
            v = re.sub(r"\s+", " ", str(v)).strip()
            if not vals or vals[-1] != v:
                vals.append(v)
        linha = " | ".join(vals)
        m = re.search(r"(\d+)º Termo", linha)
        if m and len(vals) <= 3:
            t = int(m.group(1))
            continue
        if len(vals) >= 3 and vals[1] == "Créditos":
            tots[t] = num(vals[2])
            continue
        if len(vals) >= 4 and re.fullmatch(r"\d{2}", vals[3] or ""):
            dep, nome, nc = vals[1], vals[2], num(vals[3])
            pre = vals[4] if len(vals) > 4 and vals[4] not in ("TC", "B", "L") else ""
            tipo = "SLOT" if nome.startswith("Optativa") else "EST" if re.match(r"Est[áa]gio", nome) else "TRA" if nome.startswith("Trabalho de Conclusão") else "OBR"
            lista.append({"t": t, "n": nome, "cr": nc, "d": dep, "tipo": tipo, "pre": [pre] if pre else []})
    texto = htmlmod.unescape(re.sub(r"<[^>]+>", " ", open(htmlp, encoding="utf-8", errors="ignore").read()))
    texto = re.sub(r"\s+", " ", texto)
    i = texto.find("Obs.:")
    obs_txt = texto[i:]
    leg = re.match(r"Obs\.:\s*(.+?Educação Física)\s+(?=Graduação|Licenciatura)", obs_txt)
    linhas = []
    for m in re.finditer(r"- (Créditos em [^0-9]+?|Atividades Acadêmico-Científico-Culturais \(inclui TCC\)) (\d+) Créditos – (\d+) H/A", obs_txt):
        linhas.append([m.group(1).strip(), num(m.group(2)), num(m.group(3))])
    mt = re.search(r"Total de Créditos Exigidos (\d+) Créditos – (\d+) H/A", obs_txt)
    avisos = []
    for rot, cr, h in linhas:
        if cr * 15 != h:
            avisos.append(f"No quadro do documento, “{rot}” tem {cr} créditos e {h} H/A ({cr} × 15 = {cr * 15}); os números foram mantidos como publicados.")
    return lista, tots, {"linhas": linhas, "total": [num(mt.group(1)), num(mt.group(2))] if mt else None,
                         "legenda": (leg.group(1) if leg else "").replace("“", "“").strip(), "avisos": avisos}


# ---------------------------------------------------------------------------
# Verificação numérica (somas por termo × totais do documento)
# ---------------------------------------------------------------------------
def verificar(cur):
    """Compara a soma de cada termo com o total impresso no documento e registra divergências como aviso."""
    res = {"id": cur.meta["id"], "termos": {}, "divergencias": []}
    un = cur.unidade_ref or "ch+aceu"
    nome_un = {"cr": "créditos", "ch": "horas", "ch+aceu": "horas"}[un]
    for t, refs in sorted(cur.ref_totais.items()):
        ds = [d for d in cur.disc if d["t"] == t]
        if un == "cr":
            soma = sum(d.get("cr") or 0 for d in ds)
            alt = None
        else:
            so_ch = sum(d.get("ch") or 0 for d in ds)
            soma = so_ch + (sum(d.get("aceu") or 0 for d in ds) if un == "ch+aceu" else 0)
            alt = so_ch if un == "ch+aceu" and so_ch != soma else None
        alvo = refs[0] if len(refs) == 1 else sum(refs)
        nota = None
        if soma == alvo:
            ok = True
        elif alt is not None and alt == alvo:
            ok, nota = True, "sem-aceu"
            impresso = fmt(alvo) + " h" if len(refs) == 1 else " + ".join(fmt(r) + " h" for r in refs) + ", nas duas relações"
            cur.avisos.append(f"{t}º termo: o total impresso no documento ({impresso}) soma apenas a coluna Carga Horária, sem os {fmt(soma - alt)} h de CH ACEU das disciplinas do termo.")
        else:
            ok = False
            cur.avisos.append(f"{t}º termo: o documento informa total de {fmt(alvo)} {nome_un}, mas a soma das disciplinas listadas é {fmt(soma)} {nome_un}. Os números foram mantidos como publicados.")
        res["termos"][t] = {"documento": alvo, "dados": soma, "confere": ok, **({"observacao": nota} if nota else {})}
        if not ok:
            res["divergencias"].append(t)
    return res


def fmt(v):
    return f"{v:,}".replace(",", ".") if isinstance(v, int) else str(v).replace(".", ",")


# ---------------------------------------------------------------------------
# Escrita
# ---------------------------------------------------------------------------
CABECALHO_JS = """/*
 * Árvore de Grade — dados do curso
 * {curso}{curriculo}
 * {unidade}
 *
 * ARQUIVO GERADO por ferramentas/construir.py a partir de "planos de ensino/{pasta}".
 * Não edite à mão: corrija a fonte, a transcrição ou a tabela de correções e gere de novo.
 * Números (códigos, créditos, horas) são os do documento oficial. Correções de grafia
 * aplicadas aos nomes estão listadas no campo "correcoes".
 */
"""

PAGINA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} · Árvore de Pré-requisitos · {fac} · Unesp Bauru</title>
<meta name="description" content="Árvore de pré-requisitos de {titulo} ({descricao}), {unidade_longa}, Unesp, Câmpus de Bauru.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700&display=swap">
<link rel="stylesheet" href="../../assets/arvore-grade.css">
<script>if (new URLSearchParams(location.search).get("embed") === "1") document.documentElement.className += " embed";</script>
</head>
<body class="ag-pagina">
<script>if (document.documentElement.className.indexOf("embed") > -1) document.body.className += " embed";</script>
<main class="ag-container">
  <div data-arvore-grade="{ids}"></div>
  <noscript><p>Esta ferramenta requer JavaScript. Consulte a <a href="{url_fonte}">matriz curricular oficial</a> na página do curso.</p></noscript>
</main>
<script src="../../assets/arvore-grade.js"></script>
{scripts}
</body>
</html>
"""


def pasta_fonte(dados):
    url = (dados.get("pagina") or {}).get("url")
    achadas = [k for k, v in FONTES.items() if v["pagina"] == url]
    return " e ".join(achadas) if achadas else "?"


def js_compacto(dados):
    """JSON legível: uma linha por disciplina, por optativa, por aviso e por correção."""
    um = lambda v: json.dumps(v, ensure_ascii=False)
    linhas = ["{"]
    itens = list(dados.items())
    for i, (k, v) in enumerate(itens):
        fim = "," if i < len(itens) - 1 else ""
        if k in ("disciplinas", "avisos", "correcoes") and isinstance(v, list):
            linhas.append(f'  "{k}": [')
            linhas += [f"    {um(x)}" + ("," if j < len(v) - 1 else "") for j, x in enumerate(v)]
            linhas.append("  ]" + fim)
        elif k == "optativas" and isinstance(v, dict):
            linhas.append('  "optativas": {')
            sub = list(v.items())
            for j, (k2, v2) in enumerate(sub):
                f2 = "," if j < len(sub) - 1 else ""
                if k2 == "lista":
                    linhas.append('    "lista": [')
                    linhas += [f"      {um(x)}" + ("," if m < len(v2) - 1 else "") for m, x in enumerate(v2)]
                    linhas.append("    ]" + f2)
                else:
                    linhas.append(f'    "{k2}": {um(v2)}{f2}')
            linhas.append("  }" + fim)
        else:
            linhas.append(f'  "{k}": {um(v)}{fim}')
    linhas.append("}")
    return "\n".join(linhas)


def escrever(curso_pasta, titulo, descricao, curs):
    pasta_abs = os.path.join(RAIZ, curso_pasta)
    os.makedirs(pasta_abs, exist_ok=True)
    scripts = []
    fac = curso_pasta.split("/")[0].upper()
    for cur in curs:
        dados = cur.para_js()
        if cur.meta.get("semCarga"):
            dados["semCarga"] = True
        nome = f"dados-{dados['id']}.js"
        cab = CABECALHO_JS.format(curso=dados["curso"], curriculo=(" · Currículo " + dados["curriculo"]) if dados.get("curriculo") else "",
                                  unidade=dados["unidade"], pasta=pasta_fonte(dados))
        corpo = js_compacto(dados)
        open(os.path.join(pasta_abs, nome), "w", encoding="utf-8").write(cab + "ArvoreGrade.registrar(" + corpo + ");\n")
        scripts.append(f'<script src="{nome}"></script>')
    html = PAGINA.format(titulo=htmlmod.escape(titulo), fac=fac, descricao=htmlmod.escape(descricao),
                         unidade_longa=htmlmod.escape(curs[0].meta["unidade"].split(" · ")[0]),
                         ids=",".join(c.meta["id"] for c in curs), url_fonte=htmlmod.escape(curs[0].meta["fonte"]["url"]),
                         scripts="\n".join(scripts))
    open(os.path.join(pasta_abs, "index.html"), "w", encoding="utf-8").write(html)


MANUAIS = [  # currículos mantidos à mão (não gerados por este script)
    ("fc/bcc", "Bacharelado em Ciência da Computação", "Currículo 2105 · ingressantes a partir de 2023", True),
    ("fc/bsi", "Bacharelado em Sistemas de Informação", "Currículo 2804 · ingressantes a partir de 2023", True),
]
NOMES_FAC = OrderedDict([("fc", "Faculdade de Ciências (FC)"), ("faac", "Faculdade de Arquitetura, Artes, Comunicação e Design (FAAC)"), ("feb", "Faculdade de Engenharia de Bauru (FEB)")])


def escrever_indice():
    itens = defaultdict(list)
    for pasta, titulo, desc, previa in MANUAIS:
        itens["fc"].append((titulo, desc, pasta, previa))
    for pasta, titulo, desc, curs in CURSOS:
        itens[pasta.split("/")[0]].append((titulo, desc, pasta, False))
    blocos = []
    total = 0
    for fac, nome in NOMES_FAC.items():
        lis = []
        for titulo, desc, pasta, previa in sorted(itens[fac], key=lambda x: norm(x[0])):
            total += 1
            nav = f'<a href="{pasta}/index.html">Abrir a árvore</a>' + (f'<a href="{pasta}/previa-no-portal.html">Pré-visualizar no leiaute do portal</a>' if previa else "")
            lis.append(f'      <li>\n        <h4>{htmlmod.escape(titulo)}</h4>\n        <p>{htmlmod.escape(desc)}</p>\n        <nav>{nav}</nav>\n      </li>')
        blocos.append(f'    <section class="ag-secao">\n    <h3>{htmlmod.escape(nome)}</h3>\n    <ul class="ag-cursos">\n' + "\n".join(lis) + "\n    </ul>\n    </section>")
    html = INDICE.replace("{blocos}", "\n".join(blocos)).replace("{total}", str(total))
    open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8").write(html)


INDICE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Árvore de Grade · Cursos de graduação · Unesp Bauru</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/arvore-grade.css">
<style>
  .ag-cursos { list-style: none; margin: 12px 0 0; padding: 0; display: grid; gap: 14px; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }
  .ag-cursos li { border: 1px solid var(--ag-borda); border-top: 1.6px solid var(--ag-ciano); padding: 16px 18px; background: #fff; }
  .ag-cursos h4 { margin: 0; font-size: 18px; font-weight: 500; color: var(--ag-azul); line-height: 1.3; }
  .ag-cursos p { margin: 4px 0 10px; font-size: 14px; color: var(--ag-texto-2); }
  .ag-cursos nav { display: flex; gap: 6px 18px; flex-wrap: wrap; font-size: 14.5px; font-weight: 500; }
</style>
</head>
<body class="ag-pagina">
<main class="ag-container">
  <div class="ag">
    <header class="ag-cab">
      <p class="ag-sobretitulo">Unesp · Câmpus de Bauru</p>
      <h2 class="ag-titulo">Árvore de Grade</h2>
      <p class="ag-desc">Ferramenta de consulta às matrizes curriculares dos {total} cursos de graduação do câmpus, com as relações de pré-requisito entre as disciplinas. Cada curso é mantido em pasta própria, com seus arquivos de dados e sua página.</p>
    </header>
{blocos}
    <footer class="ag-rodape"><p><strong>Página de avaliação — não publicar.</strong> No portal, cada curso é incorporado pela sua própria página (ver README.md, seção 2).</p></footer>
  </div>
</main>
</body>
</html>
"""


def main():
    faac()
    fc()
    feb()
    relatorio = []
    for pasta, titulo, desc, curs in CURSOS:
        for cur in curs:
            cur.aplicar_correcoes()
            cur.resolver(getattr(cur, "_aliases", None))
            regras = {d["c"]: d["_regra"] for d in cur.disc if d.get("_regra")}
            if regras:
                cur.meta["regras"] = regras
            relatorio.append(verificar(cur))
        escrever(pasta, titulo, desc, curs)
    os.makedirs(os.path.join(RAIZ, "testes", "referencia"), exist_ok=True)
    json.dump({"gerado": ATUALIZADO, "cursos": relatorio}, open(os.path.join(RAIZ, "testes/referencia/verificacao.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump([{"pasta": p, "titulo": t, "descricao": d, "curriculos": [{"id": c.meta["id"], "rotulo": c.meta.get("rotuloSeletor") or c.meta["curso"]} for c in cs],
                "unidade": cs[0].meta["unidade"]} for p, t, d, cs in CURSOS],
              open(os.path.join(AQUI, "cursos-gerados.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    escrever_indice()
    # resumo no terminal
    for r in relatorio:
        print(f"{r['id']:<40} termos conferidos: {sum(1 for v in r['termos'].values() if v['confere'])}/{len(r['termos'])}"
              + (f"  DIVERGÊNCIAS: {r['divergencias']}" if r["divergencias"] else ""))
    for pasta, titulo, desc, curs in CURSOS:
        for cur in curs:
            for c in cur.correcoes:
                print(f"  [{cur.meta['id']}] corrigido: “{c['de']}” → “{c['para']}” ({c['motivo']})")
            for a in cur.avisos:
                print(f"  [{cur.meta['id']}] aviso: {a}")


if __name__ == "__main__":
    main()
