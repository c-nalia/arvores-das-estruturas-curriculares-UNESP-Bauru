// Validação estática dos arquivos de dados — sem dependências.
// Uso:  node testes/validar-dados.mjs
// Confere, para TODOS os currículos (fc/, faac/, feb/):
//   (1) a integridade estrutural do grafo (códigos únicos, termos, requisitos, ciclos);
//   (2) a coerência das correções de grafia registradas em "correcoes";
//   (3) as somas por termo × totais impressos nos documentos (testes/referencia/verificacao.json);
// e, para BCC e BSI, a fidelidade literal aos documentos oficiais (transcrições por coordenadas
// em testes/referencia/), em que só as correções registradas podem diferir do documento.
// A conferência número a número dos cursos gerados contra as fontes é feita por
// testes/conferir_fontes.py.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import vm from "node:vm";
const raiz = fileURLToPath(new URL("..", import.meta.url));
const ler = (p) => readFileSync(raiz + p, "utf8");

function carregar(arquivo) {
  let dados; const ctx = { ArvoreGrade: { registrar: (d) => (dados = d) } };
  vm.runInNewContext(ler(arquivo), ctx); return dados;
}
let falhas = 0, total = 0;
function ok(cond, msg) { total++; if (!cond) { falhas++; console.log("  FALHA  " + msg); } }
const esp = (s) => String(s).replace(/\s+/g, " ").trim();
const ord = (a) => [...a].sort().join("/");

function estrutura(D) {
  console.log(`\n[${D.id}] integridade estrutural`);
  const M = {}; D.disciplinas.forEach((d) => { ok(!M[d.c], `código duplicado ${d.c}`); M[d.c] = d; });
  D.disciplinas.forEach((d) => {
    ok(Number.isInteger(d.t) && d.t >= 1, `${d.c}: termo inválido`);
    ok(["OBR", "TRA", "EST", "OPT", "SLOT"].includes(d.tipo), `${d.c}: tipo desconhecido ${d.tipo}`);
    ok(typeof d.n === "string" && d.n.trim() === d.n && !/\s{2}/.test(d.n), `${d.c}: nome com espaços sobrando`);
    if (D.semCarga) ok(d.ch == null && d.cr == null, `${d.c}: carga num currículo marcado semCarga`);
    else ok(d.ch != null || d.cr != null || d.aceu != null, `${d.c}: sem carga nem créditos`);
    ok(!("rotulo" in d) && !("ext" in d), `${d.c}: campo fora do modelo (rotulo/ext)`);
    (d.pre || []).forEach((p) => {
      ok(!!M[p], `${d.c}: pré-requisito inexistente ${p}`);
      // pré-requisito no mesmo termo só é aceito quando o próprio documento o indica (registrado em avisos)
      if (M[p]) ok(M[p].t < d.t || (D.avisos || []).some((a) => a.includes("tem como pré-requisito “" + M[p].n + "”")), `${d.c} (termo ${d.t}) exige ${p} do termo ${M[p].t}`);
    });
    (d.co || []).forEach((p) => { ok(!!M[p], `${d.c}: co-requisito inexistente ${p}`); if (M[p]) ok(M[p].t <= d.t, `${d.c}: co-requisito ${p} em termo posterior`); });
    ok(!d.preTexto || typeof d.preTexto === "string", `${d.c}: preTexto inválido`);
    ok(!(d.pre || []).includes(d.c) && !(d.co || []).includes(d.c), `${d.c}: requisito de si mesma`);
  });
  const cor = {}; let ciclo = null;
  // ciclos só entre pré-requisitos: co-requisitos mútuos (cursar juntas) são legítimos
  const dfs = (c, cam) => { cor[c] = 1; for (const p of [...(M[c].pre || [])]) { if (!M[p]) continue; if (cor[p] === 1) ciclo = [...cam, p]; else if (!cor[p]) dfs(p, [...cam, p]); } cor[c] = 2; };
  D.disciplinas.forEach((d) => { if (!cor[d.c]) dfs(d.c, [d.c]); });
  ok(!ciclo, "ciclo de requisitos: " + (ciclo || []).join(" → "));
  const opt = D.optativas || { lista: [] };
  ok(!Array.isArray(opt), "optativas deve ser um objeto { lista, oferta?, fonte? }");
  const vistos = new Set();
  (opt.lista || []).forEach((o) => {
    ok(!vistos.has(o.c), `optativa duplicada ${o.c}`); vistos.add(o.c);
    ok(["OPT", "EXT"].includes(o.tipo), `optativa ${o.c}: tipo ${o.tipo}`);
    (o.pre || []).forEach((p) => ok(!!M[p], `optativa ${o.c}: requisito inexistente ${p}`));
    (o.co || []).forEach((p) => ok(!!M[p], `optativa ${o.c}: co-requisito inexistente ${p}`));
  });
  // correções de grafia: cada registro tem de estar aplicado (o "para" existe, o "de" não)
  const nomes = new Set([...D.disciplinas, ...(opt.lista || [])].map((d) => d.n));
  (D.correcoes || []).forEach((c) => {
    ok(c.de && c.para && c.de !== c.para && c.motivo, `correção malformada: ${JSON.stringify(c)}`);
    if (c.campo === "ementa") { const d = M[c.cod]; ok(d && d.ementa.includes(c.para) && (c.para.includes(c.de) || !d.ementa.includes(c.de)), `${c.cod}: correção de ementa não aplicada (${c.de})`); }
    else { ok(nomes.has(c.para), `correção sem disciplina correspondente: ${c.para}`); ok(!nomes.has(c.de), `nome original ainda presente: ${c.de}`); }
  });
  ok(!("rotuloTermo" in D) || ["serie-periodo", "ano-semestre"].includes(D.rotuloTermo), "rotuloTermo desconhecido");
  Object.keys(D.regras || {}).forEach((c) => ok(!!M[c], `regra para disciplina inexistente ${c}`));
  if (D.quadroResumo && D.id === "bcc-2105") {
    const obr = D.disciplinas.filter((d) => d.tipo === "OBR" && d.classificacao !== "extensao").reduce((s, d) => s + (d.ch || 0), 0);
    ok(obr === D.quadroResumo.linhas[0][2], `soma das obrigatórias (${obr} h) ≠ quadro-resumo (${D.quadroResumo.linhas[0][2]} h)`);
    const soma = D.quadroResumo.linhas.reduce((s, l) => [s[0] + l[1], s[1] + l[2]], [0, 0]);
    ok(soma[0] === D.quadroResumo.total[0] && soma[1] === D.quadroResumo.total[1], "linhas do quadro-resumo não fecham o total");
  }
  if (D.fonte) ok(/^https:\/\//.test(D.fonte.url), "fonte sem URL https");
  if (D.contato) ok(/^https:\/\//.test(D.contato.url), "contato sem URL https");
}

function fidelidadeBCC(D) {
  console.log(`\n[${D.id}] fidelidade literal ao PDF do currículo 2105, às ementas e aos horários`);
  const pdf = JSON.parse(ler("testes/referencia/bcc-2105-pdf.json"));
  const comp = JSON.parse(ler("testes/referencia/bcc-2105-complementos.json"));
  const C = Object.fromEntries(D.disciplinas.map((d) => [d.c, d]));
  const porNome = Object.fromEntries(D.disciplinas.map((d) => [esp(d.n).toLowerCase(), d]));
  const vistos = new Set();
  Object.entries(comp.classificacoesConfirmadas || {}).forEach(([c, x]) => ok(C[c] && C[c].classificacao === x.classificacao, `${c}: classificação confirmada "${x.classificacao}" ausente`));
  const alias = (s) => esp(s).toLowerCase().replace(/^estrutura de dados/, "estruturas de dados").replace("analÍtica", "analítica");
  for (const r of pdf) {
    const d = r.code ? C[r.code] : D.disciplinas.find((x) => x.tipo === "SLOT" && esp(x.n) === esp(r.name));
    ok(!!d, `linha do PDF sem correspondente: ${r.code} ${r.name}`); if (!d) continue; vistos.add(d.c);
    const corr = (comp.correcoesAutorizadas || {})[d.c];
    const reg = (D.correcoes || []).find((c) => c.cod === d.c && c.campo !== "ementa" && esp(c.de) === esp(r.name));
    const esperado = corr && esp(corr.pdf) === esp(r.name) ? corr.usar : reg ? reg.para : r.name;
    ok(esp(d.n) === esp(esperado), `${d.c}: nome "${d.n}" ≠ PDF "${r.name}"${corr ? " (correção autorizada: " + corr.usar + ")" : ""}`);
    ok(d.d === r.d, `${d.c}: departamento ${d.d} ≠ PDF ${r.d}`);
    ok(+r.term === d.t, `${d.c}: termo ${d.t} ≠ PDF ${r.term}`);
    ok(+r.h === d.ch, `${d.c}: horas ${d.ch} ≠ PDF ${r.h}`);
    ok(+r.cr * 15 === +r.h, `${d.c}: no PDF créditos×15 ≠ horas (exibição de créditos derivada ficaria errada)`);
    // requisitos: o PDF cita nomes (às vezes com grafia diferente da coluna Disciplina)
    const resolve = (nome) => porNome[alias(nome)] || D.disciplinas.find((x) => alias(x.n) === alias(nome)) || (alias(nome) === "álgebra linear" ? C["4609"] : null);
    const co = r.co.split(",").map(esp).filter(Boolean).map((n) => (resolve(n) || {}).c || "?" + n);
    ok(ord(co) === ord(d.co || []), `${d.c}: co-requisitos ${ord(d.co || [])} ≠ PDF ${ord(co)}`);
    if (/Ter cumprido/.test(r.pre)) { ok(!!(D.regras || {})[d.c] && esp(D.regras[d.c].texto) === esp(r.pre), `${d.c}: texto da regra ≠ PDF`); continue; }
    const pre = r.pre.split(",").map(esp).filter(Boolean).map((n) => (resolve(n) || {}).c || "?" + n);
    ok(ord(pre) === ord(d.pre || []), `${d.c}: pré-requisitos ${ord(d.pre || [])} ≠ PDF ${ord(pre)}`);
  }
  D.disciplinas.forEach((d) => ok(vistos.has(d.c), `${d.c} não existe no PDF`));
  // quadro-resumo literal
  const q = comp.quadroResumo;
  ok(JSON.stringify(D.quadroResumo.linhas) === JSON.stringify(q.linhas) && JSON.stringify(D.quadroResumo.total) === JSON.stringify(q.total), "quadro-resumo ≠ PDF");
  // ementas literais (tabela da página Estrutura curricular)
  ler("testes/referencia/bcc-2105-ementas-portal.txt").trim().split("\n").forEach((l) => {
    const [c, , ...e] = l.split("|"); const cod = c.trim(); let txt = e.join("|").trim();
    (D.correcoes || []).filter((x) => x.cod === cod && x.campo === "ementa").forEach((x) => { txt = txt.replace(x.de, x.para); });
    ok(C[cod] && C[cod].ementa === txt, `${cod}: ementa ≠ página do curso (após as correções registradas)`);
  });
  // oferta de optativas = horários oficiais
  const of = (D.optativas && D.optativas.oferta) || { itens: [] };
  ok(JSON.stringify(of.itens.map((o) => ({ c: o.c, d: o.d, n: o.n, cr: o.cr, termos: o.termos }))) === JSON.stringify(comp.oferta1sem2026), "oferta de optativas ≠ horários de 1º/2026");
  ok(Array.isArray(D.optativas.lista) && D.optativas.lista.length === 0, "BCC: lista de optativas preenchida sem fonte oficial");
}

function fidelidadeBSI(D) {
  console.log(`\n[${D.id}] fidelidade literal à relação do Sistema de Graduação (currículo 2804)`);
  const rows = JSON.parse(ler("testes/referencia/bsi-2804-sistema.json")).map((r) => ({ c: r[3], n: r[4], ch: r[5], aceu: r[6], tipo: r[7], pre: r[8] ? r[8].split("/") : [], co: r[9] ? r[9].split("/") : [] }));
  // início de cada Série/Período, conferido visualmente no documento
  const inicio = ["4700", "4705", "4710", "4715", "4720", "4725", "4729", "4733"]; let t = 0;
  rows.forEach((r) => { if (r.tipo === "OBR" || r.tipo === "TRA") { if (inicio.includes(r.c)) t++; r.t = t; } });
  const M = Object.fromEntries(D.disciplinas.map((d) => [d.c, d])), O = Object.fromEntries((D.optativas.lista || []).map((d) => [d.c, d]));
  for (const r of rows) {
    const opt = !r.t, d = opt ? O[r.c] : M[r.c];
    ok(!!d, `${r.c} consta do documento e não dos dados`); if (!d) continue;
    const reg = (D.correcoes || []).find((c) => c.cod === r.c && esp(c.de) === esp(r.n));
    ok(esp(d.n) === esp(reg ? reg.para : r.n), `${r.c}: nome "${d.n}" ≠ documento "${r.n}"${reg ? " (correção registrada: " + reg.para + ")" : ""}`);
    ok(d.tipo === r.tipo, `${r.c}: tipo ${d.tipo} ≠ documento ${r.tipo}`);
    if (!opt) ok(d.t === r.t, `${r.c}: termo ${d.t} ≠ documento ${r.t}`);
    ok((d.ch || 0) === r.ch && (d.aceu || 0) === r.aceu, `${r.c}: carga ${d.ch || 0} h / ACEU ${d.aceu || 0} h ≠ documento ${r.ch} h / ACEU ${r.aceu} h`);
    ok(ord(d.pre || []) === ord(r.pre), `${r.c}: pré-requisitos ≠ documento`);
    ok(ord(d.co || []) === ord(r.co), `${r.c}: co-requisitos ≠ documento`);
    ok(!("d" in d), `${r.c}: departamento não consta do documento 2804`);
  }
  ok(!("turno" in D), "turno não consta do documento 2804");
  const doc = new Set(rows.map((r) => r.c));
  [...D.disciplinas, ...(D.optativas.lista || [])].forEach((d) => ok(doc.has(d.c), `${d.c} nos dados e não no documento`));
}

function somasPorTermo() {
  console.log("\n[todos] somas por termo × totais impressos nos documentos");
  const v = JSON.parse(ler("testes/referencia/verificacao.json"));
  // divergências conhecidas da fonte (o documento soma errado); qualquer outra é falha
  const conhecidas = { "educacao-fisica-2611-bacharelado": ["4", "5"] };
  for (const c of v.cursos) for (const [t, x] of Object.entries(c.termos)) {
    const esperada = (conhecidas[c.id] || []).includes(t);
    ok(x.confere !== esperada, `${c.id}, ${t}º termo: documento ${x.documento} × dados ${x.dados}${esperada ? " (divergência conhecida deixou de ocorrer?)" : ""}`);
  }
}

const arquivos = [];
for (const fac of ["fc", "faac", "feb"]) for (const curso of readdirSync(raiz + fac)) {
  const pasta = `${fac}/${curso}`;
  if (!statSync(raiz + pasta).isDirectory()) continue;
  for (const f of readdirSync(raiz + pasta)) if (/^dados-.*\.js$/.test(f)) arquivos.push(`${pasta}/${f}`);
}
const ids = new Set();
for (const a of arquivos) {
  const D = carregar(a);
  ok(!ids.has(D.id), `id repetido entre arquivos: ${D.id}`); ids.add(D.id);
  ok(a.endsWith(`dados-${D.id}.js`), `${a}: nome do arquivo não corresponde ao id ${D.id}`);
  estrutura(D);
  if (D.id === "bcc-2105") fidelidadeBCC(D);
  if (D.id === "bsi-2804") fidelidadeBSI(D);
}
ok(arquivos.length >= 27, `esperados ao menos 27 currículos, encontrados ${arquivos.length}`);
somasPorTermo();
console.log(`\n${total - falhas}/${total} verificações aprovadas, ${falhas} falha(s).`);
process.exitCode = falhas ? 1 : 0;
