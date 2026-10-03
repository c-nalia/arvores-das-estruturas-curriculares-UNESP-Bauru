// Revisão: testes exploratórios de bugs (além de testes/e2e.mjs). Uso: node revisao/exploratorio.mjs
import { chromium } from "playwright";
import { fileURLToPath, pathToFileURL } from "node:url";
const raiz = fileURLToPath(new URL("..", import.meta.url));
const url = (p) => { const m = p.match(/^([^?#]*)(.*)$/); return pathToFileURL(raiz + m[1]).href + m[2]; };
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH });
const res = [];
async function t(id, nome, fn) { try { const r = await fn(); res.push([id, r === true ? "OK" : "FALHA", nome, r === true ? "" : String(r)]); } catch (e) { res.push([id, "ERRO", nome, e.message.split("\n")[0]]); } }
const nova = async (w = 1280, h = 900) => { const c = await b.newContext({ viewport: { width: w, height: h } }); const p = await c.newPage(); p.erros = []; p.on("pageerror", (e) => p.erros.push(e.message)); return p; };

await t("X01", "iframe: após trocar de currículo várias vezes e redimensionar, a altura informada = altura real do conteúdo", async () => {
  const pg = await nova(1200, 800);
  await pg.goto(url("index.html"));
  await pg.evaluate((src) => {
    document.body.innerHTML = '<iframe class="arvore-grade" src="' + src + '" style="width:100%;border:0;height:600px"></iframe>';
    window.__alturas = [];
    window.addEventListener("message", (e) => { if (e.data && e.data.tipo === "arvore-grade:altura") { window.__alturas.push(e.data.altura); document.querySelector("iframe").style.height = e.data.altura + "px"; } });
  }, url("fc/fisica/index.html?embed=1"));
  await pg.waitForTimeout(1200);
  const fl = pg.frameLocator("iframe");
  for (const id of ["fisica-1606-materiais", "fisica-1606-computacional", "fisica-1606-licenciatura", "fisica-1606-materiais"]) { await fl.locator(`[data-curriculo="${id}"]`).click(); await pg.waitForTimeout(500); }
  await fl.locator('[data-vista="lista"]').click(); await pg.waitForTimeout(500);
  const f = pg.frames().find((x) => x !== pg.mainFrame());
  await pg.setViewportSize({ width: 900, height: 800 }); await pg.waitForTimeout(800);
  const real = await f.evaluate(() => Math.ceil(document.querySelector(".ag-container").getBoundingClientRect().bottom + scrollY + parseFloat(getComputedStyle(document.body).paddingBottom || 0)));
  const ifr = parseInt(await pg.$eval("iframe", (e) => e.style.height));
  const mins = await pg.evaluate(() => window.__alturas.filter((a) => a < 400));
  return (Math.abs(real - ifr) <= 4 && !mins.length) || `iframe ${ifr}px × conteúdo ${real}px; alturas anômalas enviadas: ${mins.join(",")}`;
});
await t("X02", "trocar de currículo não acumula instâncias ativas (ouvintes de resize/ResizeObserver)", async () => {
  const pg = await nova();
  await pg.addInitScript(() => { window.__resize = 0; const o = window.addEventListener; window.addEventListener = function (tp, ...a) { if (tp === "resize") window.__resize++; return o.call(this, tp, ...a); }; const r = window.removeEventListener; window.removeEventListener = function (tp, ...a) { if (tp === "resize") window.__resize--; return r.call(this, tp, ...a); }; });
  await pg.goto(url("fc/fisica/index.html")); await pg.waitForTimeout(300);
  const r0 = await pg.evaluate(() => window.__resize);
  for (let i = 0; i < 6; i++) { await pg.click(`[data-curriculo="${i % 2 ? "fisica-1606-licenciatura" : "fisica-1606-materiais"}"]`); await pg.waitForTimeout(100); }
  const r1 = await pg.evaluate(() => window.__resize);
  return r1 === r0 || `ouvintes de resize: ${r0} → ${r1} após 6 trocas (instâncias antigas continuam ativas)`;
});
await t("X03", "busca pelo código como impresso no documento (com espaço: “ART-E 01”, “RTVI-E 35”)", async () => {
  const pg = await nova(); await pg.goto(url("faac/artes-visuais/index.html")); await pg.waitForTimeout(300);
  await pg.fill('input[type="search"]', "ART-E 01"); const n = await pg.locator(".ag-card.achado").count();
  return n === 1 || `“ART-E 01” encontrou ${n} disciplina(s)`;
});
await t("X04", "simulação: disciplina com requisito não resolvido (Micrometeorologia exige “Física II”) não pode aparecer como apta", async () => {
  const pg = await nova(); await pg.goto(url("fc/meteorologia/index.html")); await pg.waitForTimeout(300);
  await pg.click('[data-acao="simular"]');
  for (const c of ["7000", "7003", "7008", "7042", "7043", "7044", "7005", "7046", "7047", "7048", "7049", "7050", "7010", "7013", "7051", "7052", "7053", "7054", "49183", "7023", "7055", "7056", "7057", "7058"]) await pg.locator(`input[data-concluir="${c}"]`).check({ force: true });
  const cls = await pg.getAttribute('.ag-card[data-c="7034"]', "class");
  return !cls.includes(" apta") || "7034 aparece “apta para matrícula” embora o requisito “Física II” não possa ser verificado";
});
await t("X05", "Psicologia: total da simulação não conta os 4 programas de estágio (o aluno faz 3)", async () => {
  const pg = await nova(); await pg.goto(url("fc/psicologia/index.html")); await pg.waitForTimeout(300);
  await pg.click('[data-acao="simular"]'); const s = await pg.locator(".ag-sim-num").innerText();
  // documento: 3 dos 4 estágios (54 cr) + disciplinas obrigatórias dos semestres 1–8 sem as 2 optativas (210 cr) = 264 cr
  const m = s.match(/de (\d+) créditos/); return (m && +m[1] === 264) || `total da barra: ${s} (esperado 264: o aluno cursa 3 dos 4 programas de estágio)`;
});
await t("X06", "Educação Física: TCC II repetido em dois termos é tratado como disciplina anual (selo/aviso)", async () => {
  const pg = await nova(); await pg.goto(url("fc/educacao-fisica/index.html?curriculo=educacao-fisica-2610-bacharelado")); await pg.waitForTimeout(300);
  const s = await pg.locator('.ag-card[data-c="7.14"] .ag-selo').innerText(); const av = await pg.locator(".ag-avisos").innerText();
  return (/anual/i.test(s) || /Trabalho de Conclusão de Curso II/.test(av)) || `dois cartões “Trabalho de Conclusão de Curso II” (7º e 8º termos), selo “${s}”, sem indicação de anual nem aviso`;
});
await t("X07", "rota de portal (#!): seletor não altera o endereço", async () => {
  const pg = await nova(); await pg.goto(url("fc/quimica/index.html#!/cursos/quimica")); await pg.waitForTimeout(300);
  await pg.click('[data-curriculo="quimica-tecnologica-2023"]'); await pg.waitForTimeout(200);
  const h = await pg.evaluate(() => location.search + location.hash);
  return h === "#!/cursos/quimica" || `endereço virou ${h}`;
});
await t("X08", "regra percentual (Elétrica): base da regra = mesma base da contagem", async () => {
  const pg = await nova(); await pg.goto(url("feb/engenharia-eletrica/index.html")); await pg.waitForTimeout(300);
  await pg.click('[data-acao="simular"]'); const n = await pg.locator(".ag-sim-nota").first().innerText();
  return /60% da carga obrigatória \(1\.908 h\)/.test(n) || n;
});
await t("X09", "sem erros de script em nenhuma página ao trocar todas as opções do seletor", async () => {
  const erros = [];
  for (const p of ["fc/fisica", "fc/quimica", "fc/ciencias-biologicas", "fc/educacao-fisica", "faac/artes-visuais"]) {
    const pg = await nova(); await pg.goto(url(p + "/index.html")); await pg.waitForTimeout(300);
    for (const id of await pg.$$eval("[data-curriculo]", (bs) => bs.map((x) => x.dataset.curriculo))) { await pg.click(`[data-curriculo="${id}"]`); await pg.waitForTimeout(150); await pg.click(".ag-card-btn"); }
    erros.push(...pg.erros);
  }
  return !erros.length || erros.join(" | ");
});
await t("X10", "celular 360 px: seletor com rótulos longos não causa rolagem horizontal", async () => {
  const pg = await nova(360, 740); await pg.goto(url("fc/educacao-fisica/index.html")); await pg.waitForTimeout(300);
  const w = await pg.evaluate(() => document.documentElement.scrollWidth); return w <= 360 || `scrollWidth ${w}`;
});
await t("X11", "impressão com seletor: imprime só o currículo escolhido e oculta o seletor", async () => {
  const pg = await nova(); await pg.goto(url("fc/fisica/index.html")); await pg.waitForTimeout(300);
  await pg.emulateMedia({ media: "print" });
  const vis = await pg.evaluate(() => getComputedStyle(document.querySelector(".ag-seletor")).display);
  return vis === "none" || `seletor visível na impressão (${vis})`;
});
await t("X12", "Design (sem carga): lista por termo não mostra coluna “Carga” vazia", async () => {
  const pg = await nova(); await pg.goto(url("faac/design/index.html")); await pg.waitForTimeout(300);
  const th = await pg.$$eval(".ag-vista-lista thead th", (x) => x.map((e) => e.textContent));
  return !th.includes("Carga") || "tabela da lista tem coluna “Carga” sem nenhum valor";
});
await t("X13", "rodapé: correções da Química não apontam erro inexistente (“Cientifica”)", async () => {
  const pg = await nova(); await pg.goto(url("fc/quimica/index.html")); await pg.waitForTimeout(300);
  const tx = await pg.locator(".ag-rodape").textContent();
  return !/Cientifica/.test(tx) || "a página afirma que o documento grafa “Cientifica”, mas o documento grafa “Científica”";
});
await b.close();
for (const r of res) console.log(`${r[1].padEnd(5)} ${r[0]}  ${r[2]}${r[3] ? "\n        → " + r[3] : ""}`);
