// Testes de comportamento em navegador (Chromium via Playwright).
// Uso:  npm i -D playwright  &&  npx playwright install chromium  &&  node testes/e2e.mjs
// Cada teste imprime OK ou FALHA com o identificador usado no relatório de revisão.
// T01–T03, T09 e T11 rodam em TODOS os currículos (fc/, faac/, feb/); os demais, em BCC e BSI.
import { chromium } from "playwright";
import { readFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
const raiz = fileURLToPath(new URL("..", import.meta.url));
const url = (p) => { const m = p.match(/^([^?#]*)(.*)$/); return pathToFileURL(raiz + m[1]).href + m[2]; };
const resultados = [];
async function teste(id, nome, fn) {
  try { const r = await fn(); resultados.push([id, r === true || r === undefined ? "OK" : "FALHA", nome, r === true || r === undefined ? "" : String(r)]); }
  catch (e) { resultados.push([id, "ERRO", nome, e.message.split("\n")[0]]); }
}
const exe = process.env.CHROMIUM_PATH || undefined;
const browser = await chromium.launch({ executablePath: exe });
const nova = async (w = 1280, h = 900) => { const ctx = await browser.newContext({ viewport: { width: w, height: h } }); const pg = await ctx.newPage(); pg.erros = []; pg.on("pageerror", (e) => pg.erros.push(e.message)); pg.on("console", (m) => { if (m.type() === "warning" || (m.type() === "error" && !/ERR_|Failed to load resource/.test(m.text()))) pg.erros.push(m.text()); }); return pg; };

// todos os currículos: [rótulo, página, ?curriculo=]
const gerados = JSON.parse(readFileSync(raiz + "ferramentas/cursos-gerados.json", "utf8"));
const todos = [["bcc", "fc/bcc/index.html", ""], ["bsi", "fc/bsi/index.html", ""]];
for (const g of gerados) for (const c of g.curriculos) todos.push([c.id, g.pasta + "/index.html", g.curriculos.length > 1 ? "?curriculo=" + c.id : ""]);
for (const [curso, pagina, q] of todos) {
  const arq = pagina + q;
  const base = curso === "bcc" || curso === "bsi";
  await teste(`T01-${curso}`, "carrega sem erros de script nem avisos de dados", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(400);
    const n = await pg.locator(".ag-card").count();
    return pg.erros.length ? pg.erros.join(" | ") : n > 0 || "nenhum cartão";
  });
  await teste(`T02-${curso}`, "cada aresta liga a borda do cartão de origem à do destino", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(400);
    return pg.evaluate(() => {
      const d = ArvoreGrade.cursos[document.querySelector(".ag[data-curso]").dataset.curso], M = Object.fromEntries(d.disciplinas.map((x) => [x.c, x]));
      const esperadas = d.disciplinas.reduce((s, x) => s + (x.pre || []).length + (x.co || []).length, 0);
      const paths = [...document.querySelectorAll(".ag-arestas-g path")];
      if (paths.length !== esperadas) return `arestas desenhadas ${paths.length} ≠ esperadas ${esperadas}`;
      const tela = document.querySelector(".ag-tela").getBoundingClientRect();
      const ret = (c) => { const r = document.querySelector(`.ag-card[data-c="${c}"]`).getBoundingClientRect(); return { l: r.left - tela.left, r: r.right - tela.left, t: r.top - tela.top, b: r.bottom - tela.top }; };
      const pares = []; d.disciplinas.forEach((x) => { (x.pre || []).forEach((p) => pares.push([p, x.c])); (x.co || []).forEach((p) => pares.push([p, x.c])); });
      const ruins = [];
      paths.forEach((p, i) => {
        const nums = p.getAttribute("d").match(/-?[\d.]+/g).map(Number);
        const [x1, y1] = nums, [x2, y2] = nums.slice(-2);
        const ok = pares.some(([a, b]) => { const A = ret(a), B = ret(b); return Math.abs(x1 - A.r) < 3 && y1 > A.t && y1 < A.b && y2 > B.t && y2 < B.b && (Math.abs(x2 - B.l) < 4 || Math.abs(x2 - B.r) < 4); });
        if (!ok) ruins.push(i);
      });
      return ruins.length ? `${ruins.length} arestas sem par origem/destino` : true;
    });
  });
  await teste(`T03-${curso}`, "destaque da seleção = fecho transitivo calculado (todas as disciplinas)", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(300);
    return pg.evaluate(async () => {
      const d = ArvoreGrade.cursos[document.querySelector(".ag[data-curso]").dataset.curso], M = Object.fromEntries(d.disciplinas.map((x) => [x.c, x]));
      const up = (c, s = new Set()) => { [...(M[c].pre || []), ...(M[c].co || [])].forEach((p) => { if (!s.has(p)) { s.add(p); up(p, s); } }); return s; };
      const filhos = (c) => d.disciplinas.filter((x) => (x.pre || []).includes(c) || (x.co || []).includes(c)).map((x) => x.c);
      const down = (c, s = new Set()) => { filhos(c).forEach((f) => { if (!s.has(f)) { s.add(f); down(f, s); } }); return s; };
      const erros = [];
      for (const x of d.disciplinas) {
        document.querySelector(`.ag-card[data-c="${x.c}"] .ag-card-btn`).click();
        const ant = [...document.querySelectorAll(".ag-card.ant")].map((e) => e.dataset.c).sort().join();
        const dep = [...document.querySelectorAll(".ag-card.dep")].map((e) => e.dataset.c).sort().join();
        // co-requisitos mútuos: quem está nas duas cadeias aparece como anterior (e a própria disciplina, como selecionada)
        const U = up(x.c); U.delete(x.c); const D = new Set([...down(x.c)].filter((c) => !U.has(c) && c !== x.c));
        if (ant !== [...U].sort().join() || dep !== [...D].sort().join()) erros.push(x.c);
        const lib = document.querySelector(`.ag-card[data-c="${x.c}"] .ag-libera`);
        if ((lib ? +lib.textContent.match(/\d+/)[0] : 0) !== filhos(x.c).length) erros.push(x.c + "(libera)");
        document.querySelector(`.ag-card[data-c="${x.c}"] .ag-card-btn`).click();
      }
      return erros.length ? "divergências: " + erros.join(", ") : true;
    });
  });
  if (base) await teste(`T04-${curso}`, "impressão a partir da vista Árvore mostra a lista por termo", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(300);
    await pg.evaluate(() => { try { localStorage.clear(); } catch (e) {} }); await pg.reload(); await pg.waitForTimeout(300);
    await pg.emulateMedia({ media: "print" });
    const vis = await pg.evaluate(() => [...document.querySelectorAll(".ag-tabela tr[data-c]")].filter((r) => r.getClientRects().length).length);
    const total = await pg.locator(".ag-tabela tr[data-c]").count();
    return vis === total || `linhas visíveis na impressão: ${vis} de ${total}`;
  });
  if (base) await teste(`T05-${curso}`, "impressão com busca ativa mostra a lista completa", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(300);
    await pg.click('[data-vista="lista"]'); await pg.fill('input[type="search"]', "dados");
    await pg.emulateMedia({ media: "print" });
    const vis = await pg.evaluate(() => [...document.querySelectorAll(".ag-tabela tr[data-c]")].filter((r) => r.getClientRects().length).length);
    const total = await pg.locator(".ag-tabela tr[data-c]").count();
    return vis === total || `linhas visíveis na impressão: ${vis} de ${total}`;
  });
  if (base) await teste(`T06-${curso}`, "funciona com localStorage bloqueado (lança exceção)", async () => {
    const pg = await nova();
    await pg.addInitScript(() => { Object.defineProperty(window, "localStorage", { get() { throw new DOMException("bloqueado", "SecurityError"); } }); });
    await pg.goto(url(arq)); await pg.waitForTimeout(300);
    await pg.click('[data-acao="simular"]'); await pg.locator("input[data-concluir]").first().check({ force: true });
    return pg.erros.length ? pg.erros.join(" | ") : (await pg.locator(".ag-card.concluida").count()) === 1 || "simulação não marcou";
  });
  if (base) await teste(`T07-${curso}`, "link profundo #d=<código> abre com a disciplina selecionada; código inválido não quebra", async () => {
    const d = curso === "bcc" ? "4617" : "4710";
    const pg = await nova(); await pg.goto(url(arq) + "#d=" + d); await pg.waitForTimeout(300);
    const sel = await pg.locator(".ag-card.sel").getAttribute("data-c");
    await pg.goto(url(arq) + "#d=XXXX"); await pg.waitForTimeout(200); await pg.reload(); await pg.waitForTimeout(300);
    return sel === d && pg.erros.length === 0 || `selecionada=${sel} erros=${pg.erros.join("|")}`;
  });
  if (base) await teste(`T08-${curso}`, "foco do teclado é preservado após clicar em disciplina do painel", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(300);
    const c = curso === "bcc" ? "4617" : "4710";
    await pg.focus(`.ag-card[data-c="${c}"] .ag-card-btn`); await pg.keyboard.press("Enter");
    await pg.locator(".ag-detalhe .ag-chip[data-selecionar]").first().focus(); await pg.keyboard.press("Enter"); await pg.waitForTimeout(100);
    const foco = await pg.evaluate(() => document.activeElement === document.body ? "body" : document.activeElement.className);
    return foco !== "body" || "foco voltou para <body> (usuário de teclado perde a posição)";
  });
  await teste(`T09-${curso}`, "estrutura ARIA: role=list contém apenas listitem", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(200);
    const n = await pg.evaluate(() => [...document.querySelectorAll('[role="list"]')].reduce((s, l) => s + [...l.children].filter((c) => c.getAttribute("role") !== "listitem").length, 0));
    return n === 0 || `${n} filhos inválidos dentro de role=list`;
  });
  if (base) await teste(`T10-${curso}`, "busca ignora acentos, Enter seleciona o 1º resultado, Esc limpa", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(200);
    await pg.fill('input[type="search"]', "calculo"); const n = await pg.locator(".ag-card.achado").count();
    await pg.press('input[type="search"]', "Enter"); const s = await pg.locator(".ag-card.sel").count();
    await pg.press('input[type="search"]', "Escape"); const n2 = await pg.locator(".ag-card.achado").count();
    return (n >= 2 && s === 1 && n2 === 0) || `achados=${n} selecionada=${s} após Esc=${n2}`;
  });
  await teste(`T11-${curso}`, "mobile 390 px: sem rolagem horizontal da página", async () => {
    const pg = await nova(390, 844); await pg.goto(url(arq)); await pg.waitForTimeout(300);
    const w = await pg.evaluate(() => document.documentElement.scrollWidth); return w <= 390 || `scrollWidth ${w}`;
  });
  if (base) await teste(`T12-${curso}`, "dimming consistente: seleção + simulação escurecem igualmente os cartões fora da cadeia", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(200);
    await pg.click('[data-acao="simular"]'); const c = curso === "bcc" ? "4600" : "4737";
    await pg.click(`.ag-card[data-c="${c}"] .ag-card-btn`); await pg.waitForTimeout(250);
    const ops = await pg.evaluate(() => [...new Set([...document.querySelectorAll(".ag-card:not(.ativo)")].map((e) => getComputedStyle(e).opacity))]);
    return ops.length === 1 || `opacidades diferentes fora da cadeia: ${ops.join(", ")}`;
  });
}

await teste("T13-bcc", "regra do TCC (70%): 4650 fica apta exatamente ao atingir 1.869 h obrigatórias", async () => {
  const pg = await nova(); await pg.goto(url("fc/bcc/index.html")); await pg.waitForTimeout(200);
  await pg.click('[data-acao="simular"]');
  return pg.evaluate(() => {
    const d = ArvoreGrade.cursos["bcc-2105"]; const obr = d.disciplinas.filter((x) => x.tipo === "OBR" && x.c !== "4650" && x.ch && x.classificacao !== "extensao").sort((a, b) => a.t - b.t);
    let h = 0; const marcar = (c) => { const i = document.querySelector(`input[data-concluir="${c}"]`); i.checked = true; i.dispatchEvent(new Event("change", { bubbles: true })); };
    let antes = null;
    for (const x of obr) { if (h + x.ch >= 1869 && antes === null) { antes = document.querySelector('.ag-card[data-c="4650"]').classList.contains("apta"); } marcar(x.c); h += x.ch; if (h >= 1869) break; }
    const depois = document.querySelector('.ag-card[data-c="4650"]').classList.contains("apta");
    return (antes === false && depois === true) || `antes=${antes} depois=${depois} (h=${h})`;
  });
});
await teste("T14", "iframe da prévia encolhe quando o conteúdo diminui", async () => {
  const pg = await nova(); await pg.goto(url("fc/bsi/previa-no-portal.html")); await pg.waitForTimeout(1200);
  const f = pg.frameLocator("iframe.arvore-grade");
  const h0 = parseInt(await pg.$eval("iframe.arvore-grade", (e) => e.style.height));
  await f.locator('[data-vista="lista"]').click(); await pg.waitForTimeout(600);
  const h1 = parseInt(await pg.$eval("iframe.arvore-grade", (e) => e.style.height));
  await f.locator('[data-vista="arvore"]').click(); await pg.waitForTimeout(600);
  const h2 = parseInt(await pg.$eval("iframe.arvore-grade", (e) => e.style.height));
  return (h1 > h0 && h2 < h1) || `árvore ${h0}px → lista ${h1}px → árvore ${h2}px`;
});
await teste("T15", "duas instâncias na mesma página: ids únicos e ambas funcionais", async () => {
  const pg = await nova(); await pg.goto(url("index.html"));
  await pg.setContent(`<!doctype html><link rel="stylesheet" href="${url("assets/arvore-grade.css")}"><div data-arvore-grade="bcc-2105"></div><div data-arvore-grade="bsi-2804"></div><script src="${url("assets/arvore-grade.js")}"></script><script src="${url("fc/bcc/dados-bcc-2105.js")}"></script><script src="${url("fc/bsi/dados-bsi-2804.js")}"></script>`);
  await pg.waitForTimeout(400);
  const dup = await pg.evaluate(() => { const ids = [...document.querySelectorAll("[id]")].map((e) => e.id); return ids.filter((x, i) => ids.indexOf(x) !== i); });
  const n = await pg.locator(".ag").count();
  return (dup.length === 0 && n === 2) || `instâncias=${n} ids duplicados=${dup.join(",")}`;
});
await teste("T16", "montagem tardia (conteúdo injetado depois do carregamento, como em SPA)", async () => {
  const pg = await nova(); await pg.goto(url("fc/bcc/index.html")); await pg.waitForTimeout(300);
  await pg.evaluate(() => { const d = document.createElement("div"); d.setAttribute("data-arvore-grade", "bcc-2105"); d.id = "tardio"; document.body.appendChild(d); });
  await pg.waitForTimeout(300);
  return (await pg.locator("#tardio .ag").count()) === 1 || "elemento inserido após o carregamento não é montado (não há API pública de reinicialização nem observador)";
});
await teste("T17", "dados com HTML são escapados (sem injeção)", async () => {
  const pg = await nova(); await pg.goto(url("fc/bcc/index.html")); await pg.waitForTimeout(200);
  return pg.evaluate(() => { const el = document.createElement("div"); document.body.appendChild(el);
    window.__xss = 0; ArvoreGrade.montar(el, { id: "x", curso: "<img src=x onerror=__xss=1>", sigla: "X", curriculo: "1", vigencia: "v", disciplinas: [{ c: "1", t: 1, n: "<img src=x onerror=__xss=1>", ch: 60, tipo: "OBR", ementa: "<b>x</b>" }] });
    return new Promise((r) => setTimeout(() => r(window.__xss === 0 && !el.querySelector("img") || "HTML interpretado"), 200)); });
});
await teste("T18", "hash pré-existente não relacionado é preservado ao abrir a página", async () => {
  const pg = await nova(); await pg.goto(url("fc/bcc/index.html") + "#topo"); await pg.waitForTimeout(300);
  const h = await pg.evaluate(() => location.hash); return h === "#topo" || `hash "#topo" foi apagado (ficou "${h}")`;
});

await teste("T19-bcc", "co-requisito: disciplina não fica 'apta' se o co-requisito também não puder ser cursado", async () => {
  const pg = await nova(); await pg.goto(url("fc/bcc/index.html")); await pg.waitForTimeout(200);
  await pg.click('[data-acao="simular"]');
  // Algoritmos I e II concluídas, Lógica Computacional não: EDI (4617) fica bloqueada; POO (4644) exige EDI como co-requisito
  for (const c of ["4604", "4611"]) await pg.locator(`input[data-concluir="${c}"]`).check({ force: true });
  const edi = await pg.getAttribute('.ag-card[data-c="4617"]', "class"), poo = await pg.getAttribute('.ag-card[data-c="4644"]', "class");
  return !(edi.includes("bloqueada") && poo.includes("apta")) || "POO aparece 'apta para matrícula' embora seu co-requisito (EDI) esteja bloqueado";
});
await teste("T19-bsi", "co-requisito no BSI: Redes (4724) não fica apta com Sistemas Operacionais (4723) bloqueada", async () => {
  const pg = await nova(); await pg.goto(url("fc/bsi/index.html")); await pg.waitForTimeout(200);
  await pg.click('[data-acao="simular"]');
  // Arquitetura (4718) exige 4703 e 4751; SO (4723) exige EDI (4710), que fica pendente
  for (const c of ["4703", "4751", "4718"]) await pg.locator(`input[data-concluir="${c}"]`).check({ force: true });
  const so = await pg.getAttribute('.ag-card[data-c="4723"]', "class"), redes = await pg.getAttribute('.ag-card[data-c="4724"]', "class");
  return (so.includes("bloqueada") && redes.includes("bloqueada")) || `SO: ${so.includes("bloqueada") ? "bloqueada" : "apta"} · Redes: ${redes.includes("apta") ? "apta" : "bloqueada"}`;
});
for (const [curso, arq] of [["bcc", "fc/bcc/index.html"], ["bsi", "fc/bsi/index.html"]]) {
  await teste(`T20-${curso}`, "nomes exibidos (árvore, lista e optativas) são exatamente os dos dados", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(200);
    return pg.evaluate(() => {
      const d = ArvoreGrade.cursos[document.querySelector(".ag[data-curso]").dataset.curso], erros = [];
      d.disciplinas.forEach((x) => {
        const card = document.querySelector(`.ag-card[data-c="${x.c}"] .ag-nome`).textContent;
        const lin = document.querySelector(`.ag-vista-lista tr[data-c="${x.c}"] td.nome button`).textContent;
        if (card !== x.n || lin !== x.n) erros.push(x.c);
      });
      const opt = d.optativas || {}; const nomesTab = [...document.querySelectorAll(".ag-tabela-opt td.nome-opt")].map((e) => e.textContent);
      [...(opt.lista || []), ...((opt.oferta && opt.oferta.itens) || [])].forEach((o) => { if (!nomesTab.includes(o.n)) erros.push("opt " + o.c); });
      return erros.length ? "divergem: " + erros.join(", ") : true;
    });
  });
  await teste(`T21-${curso}`, "quadro de optativas presente, com exigência do currículo e vagas da matriz", async () => {
    const pg = await nova(); await pg.goto(url(arq)); await pg.waitForTimeout(200);
    const sec = pg.locator(".ag-secao[id$='-optativas']");
    if (!(await sec.count())) return "seção ausente";
    const linhas = await sec.locator("tbody tr").count();
    const txt = await sec.innerText();
    if (curso === "bcc") return (linhas === 2 && /8 créditos \(120 h\)/.test(txt) && /Optativa I \(7º termo\) e Optativa II \(8º termo\)/.test(txt) && /não consta dos documentos publicados/.test(txt)) || `linhas=${linhas} texto=${txt.slice(0, 160)}`;
    return linhas === 42 || `linhas=${linhas}`;
  });
}
await teste("T22", "iframe sem o script de ajuste: conteúdo alcançável por rolagem interna", async () => {
  const pg = await nova(390, 800); await pg.goto(url("index.html"));
  await pg.evaluate((src) => { document.body.innerHTML = `<iframe src="${src}" style="width:100%;height:85vh;border:0"></iframe>`; }, url("fc/bcc/index.html") + "?embed=1");
  await pg.waitForTimeout(1000);
  const f = pg.frames().find((fr) => fr !== pg.mainFrame());
  return f.evaluate(() => { const el = document.scrollingElement; el.scrollTop = 1e6; return el.scrollTop > 0 || "sem rolagem interna"; });
});

await teste("T23", "seletor de currículos: troca a árvore, marca o botão e grava ?curriculo=", async () => {
  const pg = await nova(); await pg.goto(url("fc/fisica/index.html")); await pg.waitForTimeout(300);
  const ini = await pg.getAttribute(".ag[data-curso]", "data-curso");
  await pg.click('[data-curriculo="fisica-1606-computacional"]'); await pg.waitForTimeout(300);
  const fim = await pg.getAttribute(".ag[data-curso]", "data-curso");
  const prs = await pg.getAttribute('[data-curriculo="fisica-1606-computacional"]', "aria-pressed");
  const q = await pg.evaluate(() => new URLSearchParams(location.search).get("curriculo"));
  const n = await pg.locator(".ag[data-curso]").count();
  return (ini === "fisica-1606-licenciatura" && fim === "fisica-1606-computacional" && prs === "true" && q === fim && n === 1 && !pg.erros.length) || `ini=${ini} fim=${fim} pressed=${prs} q=${q} instâncias=${n} erros=${pg.erros.join("|")}`;
});
await teste("T24", "currículo sem cargas (Design): termos contam componentes e cartões sem “—”", async () => {
  const pg = await nova(); await pg.goto(url("faac/design/index.html")); await pg.waitForTimeout(300);
  const cab = await pg.locator(".ag-col-cab span").first().innerText();
  const tracos = await pg.evaluate(() => [...document.querySelectorAll(".ag-card .ag-meta")].filter((e) => e.textContent.includes("—")).length);
  await pg.click('[data-acao="simular"]');
  const sim = await pg.locator(".ag-sim-num").innerText();
  return (/6 componentes/.test(cab) && tracos === 0 && /componentes/.test(sim)) || `cab=${cab} tracos=${tracos} sim=${sim}`;
});
await teste("T25", "currículo em créditos (Física): simulação conta créditos, não horas", async () => {
  const pg = await nova(); await pg.goto(url("fc/fisica/index.html?curriculo=fisica-1606-licenciatura")); await pg.waitForTimeout(300);
  await pg.click('[data-acao="simular"]'); await pg.locator('input[data-concluir="1.3"]').check({ force: true }); await pg.waitForTimeout(100);
  const sim = await pg.locator(".ag-sim-num").innerText();
  return /^4 créditos de \d+ créditos/.test(sim) || sim;
});
await teste("T26", "correções de grafia listadas no rodapé, com o nome original e o corrigido", async () => {
  const pg = await nova(); await pg.goto(url("feb/engenharia-civil/index.html")); await pg.waitForTimeout(300);
  const txt = await pg.locator(".ag-correcoes").textContent().catch(() => "");
  const card = await pg.locator('.ag-card[data-c="EC2103C23"] .ag-nome').innerText();
  return (/lsostática/.test(txt) && card === "Isostática") || `rodapé=${txt.slice(0, 80)} cartão=${card}`;
});
await teste("T27", "requisito sem disciplina correspondente aparece como texto (Meteorologia 7034 → “Física II”)", async () => {
  const pg = await nova(); await pg.goto(url("fc/meteorologia/index.html#d=7034")); await pg.waitForTimeout(300);
  const det = await pg.locator(".ag-detalhe").innerText();
  return (/Física II/.test(det) && /Meteorologia Dinâmica I/.test(det)) || det.slice(0, 200);
});
await teste("T28", "índice lista os 20 cursos e todos os links levam a páginas existentes", async () => {
  const pg = await nova(); await pg.goto(url("index.html")); await pg.waitForTimeout(200);
  const links = await pg.$$eval(".ag-cursos a", (as) => as.map((a) => a.getAttribute("href")));
  const cursos = await pg.locator(".ag-cursos li").count();
  const { existsSync } = await import("node:fs");
  const faltam = links.filter((h) => !existsSync(raiz + h));
  return (cursos === 20 && !faltam.length) || `cursos=${cursos} faltam=${faltam.join(", ")}`;
});

await browser.close();
const w = Math.max(...resultados.map((r) => r[0].length));
resultados.forEach(([id, st, nome, det]) => console.log(`${st.padEnd(5)} ${id.padEnd(w)}  ${nome}${det ? "\n        → " + det : ""}`));
const f = resultados.filter((r) => r[1] !== "OK").length;
console.log(`\n${resultados.length - f}/${resultados.length} testes aprovados.`);
process.exitCode = f ? 1 : 0;
