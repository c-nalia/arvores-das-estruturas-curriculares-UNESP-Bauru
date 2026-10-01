"""Leitura das relações de disciplinas emitidas pelo Sistema de Graduação da Unesp
(exportadas em CSV a partir das páginas das faculdades).

Cada linha de disciplina tem a forma  "CÓDIGO - Nome", seguida de carga (e CH ACEU, quando
houver), tipo (OBR, TRA, EST, OPT), requisitos e equivalências. Requisitos longos continuam
em linhas cuja primeira coluna está vazia.
"""
import csv, re

RE_SERIE = re.compile(r"^S[ée]rie:\s*(\d+)\s*-\s*Per[ií]odo:\s*(\d+)")
RE_COD = re.compile(r"^((?:[A-Z]{2,5}-E\s?\d{1,3})|(?:[A-Z]{3,}\d{2,})|(?:\d{4,}[A-Z]?))\s+-\s+(.+)$")
RE_REQ = re.compile(r"(Pr[ée]-Requisito|Correquisito|Co-Requisito)\s*:\s*((?:[A-Z]{2,5}-E\s?\d{1,3})|(?:[A-Z]{3,}\d{2,})|(?:\d{4,}[A-Z]?))")
RE_TOTAL = re.compile(r"^Total de Carga Hor[aá]ria:\s*([\d.]+)(?:\s*\(sendo\s*([\d.]+)\s*em aceus\))?")


def _num(v):
    v = (v or "").strip()
    if not v:
        return None
    f = float(v.replace(",", "."))
    return int(f) if f == int(f) else f


def ler_csv_sg(caminho):
    """Retorna dict com: cabecalho, disciplinas (lista), optativas, totais_termo, resumo (linhas literais)."""
    linhas = list(csv.reader(open(caminho, encoding="utf-8-sig")))
    out = {"cabecalho": None, "disciplinas": [], "optativas": [], "totais_termo": {}, "resumo": []}
    cols = None
    termo = None
    atual = None
    pos_totais = False  # depois dos totais do curso, a tabela que vem é de optativas
    for row in linhas:
        if not row or not any(c.strip() for c in row):
            continue
        a = row[0].strip()
        m = RE_SERIE.match(a)
        if m:
            s, p = int(m.group(1)), int(m.group(2))
            termo = (s - 1) * 2 + p
            continue
        if a == "Disciplina":
            cols = [c.strip() for c in row]
            continue
        mt = RE_TOTAL.match(a)
        if mt:
            if termo is not None and not pos_totais:
                out["totais_termo"].setdefault(termo, []).append((_num(mt.group(1)), _num(mt.group(2)) or 0))
            continue
        if a.startswith("Total "):
            out["resumo"].append(a)
            pos_totais = True
            termo = None
            continue
        if a.startswith("*"):
            out["resumo"].append(a)
            continue
        if out["cabecalho"] is None and cols is None:
            out["cabecalho"] = a
            continue
        if cols is None:
            continue
        reg = dict(zip(cols, row + [""] * (len(cols) - len(row))))
        req_txt = " ".join(v for k, v in reg.items() if k in ("Requisitos", "Pré-Requisito"))
        m = RE_COD.match(a)
        if not m:
            # continuação de requisitos (primeira coluna vazia) ou de equivalências ("2: ...")
            if atual is not None and not a:
                _anexa_req(atual, reg, cols)
            continue
        cod, nome = m.group(1).strip(), m.group(2).strip()
        d = {
            "cod": cod, "n": nome,
            "ch": _num(reg.get("Carga Horária")) or 0,
            "aceu": _num(reg.get("CH Aceu")) or 0,
            "tipo": (reg.get("Tipo") or "").strip() or "OBR",
            "pre": [], "co": [], "t": termo, "_req_bruto": [],
        }
        _anexa_req(d, reg, cols)
        if pos_totais or termo is None:
            out["optativas"].append(d)
        else:
            out["disciplinas"].append(d)
        atual = d
    return out


def _anexa_req(d, reg, cols):
    if "Requisitos" in cols:
        txt = (reg.get("Requisitos") or "").strip()
        if not txt:
            return
        d["_req_bruto"].append(txt)
        for tipo, cod in RE_REQ.findall(txt):
            (d["co"] if tipo.lower().startswith("co") else d["pre"]).append(cod.strip())
    elif "Pré-Requisito" in cols:
        txt = (reg.get("Pré-Requisito") or "").strip()
        if not txt:
            return
        d["_req_bruto"].append(txt)
        m = RE_COD.match(txt)
        if m:
            d["pre"].append(m.group(1).strip())


# ---------------------------------------------------------------------------
# Relação do Sistema de Graduação em PDF (FEB): leitura por coordenadas
# ---------------------------------------------------------------------------
RE_COD_PDF = re.compile(r"^([A-Z]{2}\d{4}[A-Z]\d{2}|[A-Z]{2,5}-E\s?\d{1,3}|\d{7}|[A-Z]{2,}\d{3,}[A-Z]?\d*)\s*-\s*(.*)$")
RE_REQ_PDF = re.compile(r"(Pr[ée]-Requisito|Correquisito)\s*:\s*([A-Z]{2}\d{4}[A-Z]\d{2}|\d{7}|[A-Z]{2,}\d{3,}[A-Z]?\d*)")


def _linhas_pdf(pagina, tol=2.5):
    palavras = pagina.extract_words(keep_blank_chars=False, use_text_flow=False, x_tolerance=1.5)
    palavras.sort(key=lambda w: (round(w["top"]), w["x0"]))
    linhas = []
    for w in palavras:
        if linhas and abs(linhas[-1]["top"] - w["top"]) <= tol:
            linhas[-1]["words"].append(w)
        else:
            linhas.append({"top": w["top"], "words": [w]})
    return linhas


def ler_pdf_sg(caminho):
    import pdfplumber
    out = {"cabecalho": None, "disciplinas": [], "optativas": [], "totais_termo": {}, "resumo": []}
    termo = None
    pos_totais = False
    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            linhas = _linhas_pdf(pagina)
            # colunas pelo cabeçalho da tabela
            cab = None
            for i, ln in enumerate(linhas):
                t = " ".join(w["text"] for w in ln["words"])
                if t.startswith("Disciplina") and "Tipo" in t:
                    cab = {}
                    for ln2 in linhas[max(0, i - 2): i + 3]:
                        if abs(ln2["top"] - ln["top"]) <= 12:
                            for w in ln2["words"]:
                                cab.setdefault(w["text"], w["x0"])
                    break
            if cab is None:
                # página sem cabeçalho (ex.: só optativas continuação): reaproveita o último
                cab = getattr(ler_pdf_sg, "_cab", None)
            if cab is None:
                continue
            ler_pdf_sg._cab = cab
            x_ch = min(cab.get("Carga", 1e9), cab.get("Horária", 1e9)) - 6
            x_aceu = min(cab.get("CH", 1e9), cab.get("Aceu", 1e9), x_ch - 20) - 6
            x_tipo = cab["Tipo"] - 4
            x_req = cab["Requisitos"] - 40
            x_dur = cab.get("Duração", 10_000) - 10
            registros = []
            itens_ch, itens_tipo, itens_req = [], [], []
            for ln in linhas:
                texto = " ".join(w["text"] for w in ln["words"])
                ms = RE_SERIE.match(texto)
                if ms:
                    termo = (int(ms.group(1)) - 1) * 2 + int(ms.group(2))
                    continue
                mt = RE_TOTAL.match(texto)
                if mt:
                    if termo is not None and not pos_totais:
                        out["totais_termo"].setdefault(termo, []).append((_num(mt.group(1)), _num(mt.group(2)) or 0))
                    continue
                if texto.startswith("Total "):
                    out["resumo"].append(texto); pos_totais = True; termo = None
                    continue
                if texto.startswith("Disciplina") or texto.startswith("Sistema de Gradua") or texto.startswith("Faculdade de"):
                    continue
                if re.match(r"^\d{4}\s*-\s*Curso:", texto):
                    out["cabecalho"] = out["cabecalho"] or texto
                    continue
                disc = [w for w in ln["words"] if w["x0"] < x_aceu]
                if disc:
                    td = " ".join(w["text"] for w in disc)
                    m = RE_COD_PDF.match(td)
                    if m:
                        registros.append({"cod": m.group(1), "partes": [m.group(2)], "ys": [ln["top"]], "t": termo, "opt": pos_totais or termo is None})
                    elif registros:
                        registros[-1]["partes"].append(td); registros[-1]["ys"].append(ln["top"])
                for w in ln["words"]:
                    if x_ch <= w["x0"] < x_tipo and re.match(r"^\d+\.\d$", w["text"]):
                        itens_ch.append((ln["top"], _num(w["text"]), "ch"))
                    elif x_aceu <= w["x0"] < x_ch and re.match(r"^\d+\.\d$", w["text"]):
                        itens_ch.append((ln["top"], _num(w["text"]), "aceu"))
                    elif x_tipo <= w["x0"] < x_tipo + 25 and w["text"] in ("OBR", "TRA", "EST", "OPT", "EXT"):
                        itens_tipo.append((ln["top"], w["text"]))
                req = " ".join(w["text"] for w in ln["words"] if x_req <= w["x0"] < x_dur and not (x_tipo <= w["x0"] < x_tipo + 25 and w["text"] in ("OBR", "TRA", "EST", "OPT", "EXT")))
                if req:
                    itens_req.append((ln["top"], req))
            # centro vertical de cada registro
            for r in registros:
                r["cy"] = (min(r["ys"]) + max(r["ys"])) / 2
            def perto(y):
                return min(registros, key=lambda r: abs(r["cy"] - y)) if registros else None
            for y, v, k in itens_ch:
                r = perto(y)
                if r is not None:
                    r.setdefault(k, v)
            for y, v in itens_tipo:
                r = perto(y)
                if r is not None:
                    r.setdefault("tipo", v)
            # requisitos: blocos contíguos, atribuídos pelo centro do bloco
            blocos = []
            for y, t in sorted(itens_req):
                if blocos and y - blocos[-1]["ys"][-1] <= 12.5:
                    blocos[-1]["ys"].append(y); blocos[-1]["txt"].append(t)
                else:
                    blocos.append({"ys": [y], "txt": [t]})
            for b in blocos:
                cy = (b["ys"][0] + b["ys"][-1]) / 2
                r = perto(cy)
                if r is not None:
                    r.setdefault("req", []).extend(b["txt"])
            for r in registros:
                txt = " ".join(r.get("req", []))
                d = {"cod": r["cod"], "n": re.sub(r"\s+", " ", " ".join(r["partes"])).strip(),
                     "ch": r.get("ch", 0), "aceu": r.get("aceu", 0), "tipo": r.get("tipo", "OBR"),
                     "pre": [], "co": [], "t": r["t"], "_req_bruto": [txt] if txt else []}
                for tipo, cod in RE_REQ_PDF.findall(txt):
                    (d["co"] if tipo.startswith("Co") else d["pre"]).append(cod)
                (out["optativas"] if r["opt"] else out["disciplinas"]).append(d)
    ler_pdf_sg._cab = None
    return out
