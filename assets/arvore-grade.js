/* =====================================================================
   Árvore de Grade — Unesp · Câmpus de Bauru
   Componente sem dependências. Uso:

     <div data-arvore-grade="bcc-2105"></div>
     <script src="assets/arvore-grade.js"></script>
     <script src="fc/bcc/dados-bcc-2105.js"></script>

   Vários currículos do mesmo curso (modalidades, turnos) numa só página:
     <div data-arvore-grade="fisica-1606-licenciatura,fisica-1606-materiais"></div>
   mostra um seletor acima da árvore; ?curriculo=<id> abre um currículo específico.

   Cada arquivo de dados chama ArvoreGrade.registrar({...}). Todo elemento
   [data-arvore-grade] é montado com o curso de mesmo id — no carregamento da
   página, quando o curso é registrado e sempre que um elemento novo aparece no
   documento (páginas de aplicação única, como o Portal Unesp).
   Atributos opcionais no elemento:
     data-titulo="nao"   oculta o título (quando a página hospedeira já exibe o seu)
     data-link="nao"     não altera o endereço (#d=código) ao selecionar disciplina
   Parâmetro de endereço ?embed=1 equivale a data-titulo="nao".
   API: ArvoreGrade.registrar(dados) · ArvoreGrade.iniciar([elemento]) ·
        ArvoreGrade.montar(elemento, dados, opcoes)
   ===================================================================== */
(function () {
  "use strict";

  var REGISTRO = {};
  var instancias = 0;

  function registrar(dados) {
    REGISTRO[dados.id] = dados;
    if (document.readyState !== "loading") iniciar();
  }

  /* ---------- utilitários ---------- */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }
  function norm(s) { return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  function horas(h) { return Number(h).toLocaleString("pt-BR") + " h"; }
  function numCr(h) { var c = h / 15; return c % 1 === 0 ? String(c) : c.toFixed(1).replace(".", ","); }
  function termoOrdinal(t) { return t + "º termo"; }
  function plural(n, um, varios) { return n + " " + (n === 1 ? um : varios); }
  function lerArmazenado(chave, padrao) {
    try { var v = localStorage.getItem(chave); return v == null ? padrao : JSON.parse(v); } catch (e) { return padrao; }
  }
  function gravar(chave, valor) { try { localStorage.setItem(chave, JSON.stringify(valor)); } catch (e) { /* armazenamento indisponível */ } }
  function dataBR(iso) { if (!iso) return ""; var p = iso.split("-"); return p[2] + "/" + p[1] + "/" + p[0]; }

  var ROTULOS_TERMO = {
    "serie-periodo": function (t) { return "Série " + Math.ceil(t / 2) + " · Período " + (t % 2 === 1 ? 1 : 2); },
    "ano-semestre": function (t) { return Math.ceil(t / 2) + "º ano · " + (t % 2 === 1 ? 1 : 2) + "º semestre"; }
  };

  var ICONES = {
    arvore: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3" y="4" width="6" height="4" rx="1"/><rect x="15" y="4" width="6" height="4" rx="1"/><rect x="15" y="16" width="6" height="4" rx="1"/><path d="M9 6h6M18 8v8M9 6c3 0 3 12 6 12"/></svg>',
    simular: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="2"/><path d="m8 12 3 3 5-6"/></svg>',
    imprimir: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M7 9V3h10v6M7 17H4v-7h16v7h-3"/><rect x="7" y="14" width="10" height="7"/></svg>',
    fechar: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    rolar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 12h16M8 8l-4 4 4 4M16 8l4 4-4 4"/></svg>'
  };

  /* ---------- montagem ---------- */
  function montar(raiz, dados, opcoes) {
    opcoes = opcoes || {};
    var n = ++instancias;
    var pfx = "ag" + n;
    var params = new URLSearchParams(location.search);
    var comTitulo = opcoes.titulo !== false && raiz.getAttribute("data-titulo") !== "nao" && params.get("embed") !== "1";
    // Nunca altera o endereço quando a página hospedeira usa rotas "#!" (Portal Unesp)
    var linkProfundo = opcoes.linkProfundo !== false && raiz.getAttribute("data-link") !== "nao" && location.hash.indexOf("#!") !== 0;
    var chave = "arvore-grade:" + dados.id;
    var mostraCr = !!dados.creditosNoDocumento;
    var mostraTipo = !!dados.tiposNoDocumento || dados.disciplinas.some(function (d) { return d.tipo === "TRA"; });

    /* modelo */
    var lista = dados.disciplinas.map(function (d) {
      var x = Object.assign({ pre: [], co: [], aceu: 0 }, d);
      if (d.ext && !d.aceu) x.aceu = d.ext; // compatibilidade com o formato anterior
      return x;
    });
    var M = {};
    lista.forEach(function (d) { M[d.c] = d; d.filhos = []; });
    var arestas = [];
    lista.forEach(function (d) {
      d.pre.forEach(function (p) {
        if (!M[p]) { console.warn("[Árvore de Grade] " + d.c + ": pré-requisito desconhecido " + p); return; }
        M[p].filhos.push(d.c); arestas.push({ de: p, para: d.c, co: false });
      });
      d.co.forEach(function (p) {
        if (!M[p]) { console.warn("[Árvore de Grade] " + d.c + ": co-requisito desconhecido " + p); return; }
        M[p].filhos.push(d.c); arestas.push({ de: p, para: d.c, co: true });
      });
    });
    var opt = Array.isArray(dados.optativas) ? { lista: dados.optativas } : (dados.optativas || { lista: [] });
    var optLista = (opt.lista || []).map(function (o) { return Object.assign({ pre: [], ch: 0 }, o); });
    var optPorReq = {};
    optLista.forEach(function (o) { o.pre.forEach(function (p) { (optPorReq[p] = optPorReq[p] || []).push(o); }); });
    var slots = lista.filter(function (d) { return d.tipo === "SLOT"; });
    function reqOptativa(o) {
      var r = o.pre.map(function (p) { return M[p] ? esc(M[p].n) + (cod(M[p]) ? " (" + esc(cod(M[p])) + ")" : "") : esc(p); });
      (o.co || []).forEach(function (p) { if (M[p]) r.push("co-requisito: " + esc(M[p].n) + (cod(M[p]) ? " (" + esc(cod(M[p])) + ")" : "")); });
      if (o.preTexto) r.push(esc(o.preTexto));
      return r.length ? r.join("; ") : '<span class="ag-vazio">—</span>';
    }
    var temSecaoOpt = !!(optLista.length || (opt.oferta && opt.oferta.itens.length) || slots.length || (opt.exigencia && opt.exigencia.length));
    var termos = [];
    lista.forEach(function (d) { if (termos.indexOf(d.t) < 0) termos.push(d.t); });
    termos.sort(function (a, b) { return a - b; });
    var regras = dados.regras || {};
    var fnTermo = typeof dados.rotuloTermo === "function" ? dados.rotuloTermo : ROTULOS_TERMO[dados.rotuloTermo];

    // Carga que conta para o progresso: obrigatórias (e TRA), exceto as classificadas como extensão
    // horas de uma disciplina: a carga impressa ou, na falta dela, créditos × 15
    function hc(d) { return typeof d.ch === "number" ? d.ch : (d.cr != null ? d.cr * 15 : 0); }
    function contaNoProgresso(d) { return (d.tipo === "OBR" || d.tipo === "TRA" || d.tipo === "EST") && d.classificacao !== "extensao"; }
    function numero(v) { return (v % 1 === 0 ? String(v) : String(v).replace(".", ",")); }
    var qr = dados.quadroResumo || null;
    var colunasQR = qr ? (qr.colunas || ["Créditos", "Horas"]) : [];
    var iHoras = colunasQR.indexOf("Horas") + 1; // posição na linha [rótulo, ...valores]
    function horasLinha(l) { return iHoras > 0 && typeof l[iHoras] === "number" ? l[iHoras] : null; }
    var linhaObrig = qr && qr.linhas.filter(function (l) { return /obrigat/i.test(l[0]) && !/optativ/i.test(l[0]) && horasLinha(l) != null; })[0];
    var linhaOpt = qr && qr.linhas.filter(function (l) { return /optativ/i.test(l[0]) && horasLinha(l); })[0];
    // unidade de medida: horas, créditos ou (quando o documento não informa carga) componentes
    var somaEmHoras = !dados.semCarga && lista.every(function (d) { return d.tipo === "SLOT" || typeof d.ch === "number"; });
    var modo = dados.semCarga ? "n" : somaEmHoras ? "h" : "cr";
    function valorProg(d) { return modo === "h" ? hc(d) : modo === "cr" ? (d.cr || 0) : 1; }
    function fmtProg(v) { return modo === "h" ? horas(v) : modo === "cr" ? numero(v) + (v === 1 ? " crédito" : " créditos") : plural(v, "componente", "componentes"); }
    var somaProgresso = lista.filter(contaNoProgresso).reduce(function (s, d) { return s + valorProg(d); }, 0);
    var totalObrig = dados.horasObrigatorias || somaProgresso;
    var baseRegra = totalObrig;
    var temTRA = lista.some(function (d) { return d.tipo === "TRA" || d.tipo === "EST"; });
    var rotuloProgresso = modo === "n" ? "da matriz" : temTRA ? "em disciplinas obrigatórias, TCC e estágios da matriz" : "em disciplinas obrigatórias da matriz";
    function cod(d) { return d.tipo === "SLOT" ? "" : d.semCodigo ? "" : (d.cod || d.c); }
    function somaTermo(ds) {
      if (modo === "n") return plural(ds.length, "componente", "componentes");
      if (somaEmHoras) return horas(ds.reduce(function (s, d) { return s + (d.ch || 0) + (d.aceu || 0); }, 0));
      var cr = ds.reduce(function (s, d) { return s + (d.cr != null ? d.cr : 0); }, 0);
      return numero(cr) + " créditos";
    }

    function rotuloTermo(t) { return fnTermo ? fnTermo(t) : ""; }
    function chListada(d) { return (d.ch || 0) + (d.aceu || 0); }
    function metaTexto(d, longo) {
      var partes = [];
      var temCh = typeof d.ch === "number";
      var cr = d.cr != null ? d.cr : (mostraCr && temCh && d.ch ? d.ch / 15 : null);
      var txtCr = cr != null ? numero(cr) + (longo ? (cr === 1 ? " crédito" : " créditos") : " cr") : "";
      if (temCh && (d.ch || !d.aceu)) partes.push(horas(d.ch) + (txtCr ? " · " + txtCr : ""));
      else if (txtCr) partes.push(txtCr);
      if (d.aceu) partes.push("CH ACEU " + horas(d.aceu));
      (d.extras || []).forEach(function (x) { partes.push(esc(x[0]) + (longo ? ": " : " ") + numero(x[1]) + (x[2] === "cr" ? (longo ? (x[1] === 1 ? " crédito" : " créditos") : " cr") : " h")); });
      return partes.join(" · ") || (dados.semCarga ? "" : "—");
    }
    function selo(d) { return d.tipoDoc ? d.tipoDoc : (d.tipo === "TRA" || d.tipo === "EXT" || d.tipo === "EST" || d.tipo === "OPT") ? d.tipo + (d.anual ? " · anual" : "") : d.anual ? "Anual" : ""; }

    /* estado */
    var sel = null, busca = "";
    var vista = lerArmazenado(chave + ":vista", null) || (window.innerWidth < 640 ? "lista" : "arvore");
    var simulando = !!lerArmazenado(chave + ":simulando", false);
    var concluidas = new Set(lerArmazenado(chave + ":concluidas", []));

    /* ---------- HTML ---------- */
    var h = [];
    h.push('<div class="ag' + (simulando ? " simulando" : "") + '" data-curso="' + esc(dados.id) + '">');
    h.push('<p class="ag-sr" aria-live="polite" data-anuncio></p>');

    h.push('<header class="ag-cab">');
    if (comTitulo) {
      h.push('<p class="ag-sobretitulo">' + esc(dados.curso) + (dados.curriculo ? " · Currículo " + esc(dados.curriculo) : "") + "</p>");
      h.push('<h2 class="ag-titulo">Árvore de Pré-requisitos</h2>');
    }
    var temEmenta = lista.some(function (d) { return d.ementa; });
    h.push('<p class="ag-desc' + (comTitulo ? "" : " sem-titulo") + '">Representação da matriz curricular organizada por termo, com as relações de pré-requisito e co-requisito entre as disciplinas. Selecione uma disciplina para consultar ' + (temEmenta ? "sua ementa, " : "") + "a cadeia de disciplinas que a antecede e aquelas que dela dependem.</p>");
    h.push('<dl class="ag-ficha">');
    h.push("<div><dt>Curso</dt><dd>" + esc(dados.sigla) + (dados.turno ? " · " + esc(dados.turno) : "") + "</dd></div>");
    if (dados.curriculo) h.push("<div><dt>Currículo</dt><dd>" + esc(dados.curriculo) + "</dd></div>");
    h.push("<div><dt>Vigência</dt><dd>" + esc(dados.vigencia) + "</dd></div>");
    if (qr && qr.total) {
      var tot = colunasQR.map(function (c, i) { var v = qr.total[i]; return v == null ? "" : (c === "Horas" ? horas(v) : numero(v) + " " + c.toLowerCase()); }).filter(Boolean);
      h.push("<div><dt>Carga horária total</dt><dd>" + tot[tot.length - 1] + (tot.length > 1 ? " (" + tot.slice(0, -1).join(", ") + ")" : "") + "</dd></div>");
    } else {
      h.push("<div><dt>" + (modo === "n" ? "Componentes listados" : somaEmHoras ? "Carga das disciplinas listadas" : "Créditos das disciplinas listadas") + "</dt><dd>" + somaTermo(lista.filter(function (d) { return d.tipo !== "SLOT" || modo !== "h"; })) + "</dd></div>");
    }
    if (dados.fonte) h.push('<div><dt>Documento oficial</dt><dd><a href="' + esc(dados.fonte.url) + '" target="_blank" rel="noopener">' + esc(dados.fonte.titulo) + (/\.pdf$/i.test(dados.fonte.url) ? " (PDF)" : "") + "</a></dd></div>");
    h.push("</dl>");
    if (dados.avisos && dados.avisos.length) {
      h.push('<ul class="ag-avisos">' + dados.avisos.map(function (a) { return "<li>" + esc(a) + "</li>"; }).join("") + "</ul>");
    }
    h.push("</header>");

    h.push('<div class="ag-barra">');
    h.push('<div class="ag-busca"><label class="ag-rotulo" for="' + pfx + '-busca">Localizar disciplina</label>');
    h.push('<div class="ag-busca-linha"><input id="' + pfx + '-busca" type="search" autocomplete="off" placeholder="Nome ou código da disciplina">');
    h.push('<span class="ag-busca-res" aria-live="polite"></span></div></div>');
    h.push('<div class="ag-grupo"><span class="ag-rotulo" id="' + pfx + '-vis">Visualização</span><div class="ag-seg" role="group" aria-labelledby="' + pfx + '-vis">');
    h.push('<button type="button" data-vista="arvore">Árvore</button><button type="button" data-vista="lista">Lista por termo</button></div></div>');
    h.push('<div class="ag-acoes">');
    h.push('<button type="button" class="ag-btn" data-acao="simular" aria-pressed="' + simulando + '">' + ICONES.simular + "Simular percurso</button>");
    h.push('<button type="button" class="ag-btn" data-acao="imprimir">' + ICONES.imprimir + "Imprimir</button>");
    h.push("</div></div>");

    h.push('<section class="ag-sim" aria-label="Simulação de percurso"' + (simulando ? "" : " hidden") + "></section>");
    h.push('<section class="ag-detalhe" aria-label="Detalhes da disciplina"></section>');

    // árvore
    h.push('<div class="ag-vista ag-vista-arvore">');
    h.push('<p class="ag-dica">' + ICONES.rolar + "Deslize horizontalmente para percorrer os " + termos.length + " termos.</p>");
    h.push('<div class="ag-rolagem" tabindex="0" role="region" aria-label="Árvore de pré-requisitos por termo"><div class="ag-tela">');
    h.push('<svg class="ag-arestas" aria-hidden="true" focusable="false"><defs>' +
      marcador(pfx + "-s", "#8792a0") + marcador(pfx + "-sa", "#1e3b50") + marcador(pfx + "-sd", "#00acfa") +
      '</defs><g class="ag-arestas-g"></g></svg>');
    termos.forEach(function (t) {
      var ds = lista.filter(function (d) { return d.t === t; });
      var idCab = pfx + "-t" + t;
      h.push('<div class="ag-col">');
      h.push('<div class="ag-col-cab" id="' + idCab + '"><strong>' + termoOrdinal(t) + "</strong><span>" + (rotuloTermo(t) ? esc(rotuloTermo(t)) + " · " : "") + somaTermo(ds) + "</span></div>");
      h.push('<div class="ag-col-lista" role="list" aria-labelledby="' + idCab + '">');
      ds.forEach(function (d) {
        var s = selo(d);
        h.push('<div class="ag-card" role="listitem" data-c="' + esc(d.c) + '" data-tipo="' + esc(d.tipo) + '">');
        h.push('<button type="button" class="ag-card-btn" aria-pressed="false">');
        h.push('<span class="ag-card-topo"><span>' + (d.tipo === "SLOT" ? "optativa" : esc(cod(d))) + "</span>" + (d.d ? '<span class="ag-dep" title="Departamento">' + esc(d.d) + "</span>" : "") + "</span>");
        h.push('<span class="ag-nome">' + esc(d.n) + "</span>");
        if (s) h.push('<span class="ag-selo" title="Tipo no Sistema de Graduação">' + esc(s) + "</span>");
        h.push('<span class="ag-meta"><span>' + metaTexto(d) + "</span>" + (d.filhos.length ? '<span class="ag-libera">libera ' + d.filhos.length + "</span>" : "") + "</span>");
        h.push('<span class="ag-rel"></span><span class="ag-estado"></span>');
        h.push("</button>");
        h.push('<label class="ag-check"><input type="checkbox" data-concluir="' + esc(d.c) + '"' + (concluidas.has(d.c) ? " checked" : "") + '><span></span><span class="ag-sr">Marcar ' + esc(d.n) + " como concluída</span></label>");
        h.push("</div>");
      });
      h.push("</div></div>");
    });
    h.push("</div></div>");
    h.push('<ul class="ag-legenda">' +
      '<li><span class="ag-amostra ant"></span>Cadeia de pré-requisitos da disciplina selecionada</li>' +
      '<li><span class="ag-amostra dep"></span>Disciplinas que dependem da selecionada</li>' +
      '<li><span class="ag-amostra-linha"></span>Pré-requisito</li>' +
      '<li><span class="ag-amostra-linha co"></span>Co-requisito</li>' +
      (slots.length ? '<li><span class="ag-amostra slot"></span>Vaga de disciplina optativa</li>' : "") +
      '<li><span class="ag-libera ag-legenda-libera">libera N</span>disciplinas que a exigem diretamente</li>' +
      (mostraTipo ? '<li><span class="ag-selo">TRA</span>tipo informado pelo Sistema de Graduação</li>' : "") +
      "</ul>");
    h.push("</div>");

    // lista
    h.push('<div class="ag-vista ag-vista-lista">');
    termos.forEach(function (t) {
      var ds = lista.filter(function (d) { return d.t === t; });
      h.push('<section class="ag-lista-termo"><h3>' + termoOrdinal(t) + "<span>" + (rotuloTermo(t) ? esc(rotuloTermo(t)) + " · " : "") + somaTermo(ds) + "</span></h3>");
      h.push('<div class="ag-tabela-wrap"><table class="ag-tabela"><thead><tr><th scope="col">Código</th><th scope="col">Disciplina</th><th scope="col">Carga</th><th scope="col">Pré-requisitos</th><th scope="col">Libera</th></tr></thead><tbody>');
      ds.forEach(function (d) {
        var req = [];
        var rc = function (p) { return cod(M[p]) ? " (" + esc(cod(M[p])) + ")" : ""; };
        d.pre.forEach(function (p) { if (M[p]) req.push(esc(M[p].n) + rc(p)); });
        d.co.forEach(function (p) { if (M[p]) req.push("co-requisito: " + esc(M[p].n) + rc(p)); });
        if (regras[d.c]) req.push(esc(regras[d.c].texto));
        if (d.preTexto) req.push(esc(d.preTexto));
        if (d.coTexto) req.push("co-requisito: " + esc(d.coTexto));
        var lib = d.filhos.map(function (f) { return esc(M[f].n); });
        h.push('<tr data-c="' + esc(d.c) + '"><td>' + (cod(d) ? esc(cod(d)) : "—") + '</td><td class="nome"><button type="button" data-selecionar="' + esc(d.c) + '">' + esc(d.n) + "</button>" + (selo(d) ? ' <span class="ag-selo">' + esc(selo(d)) + "</span>" : "") + "</td>");
        h.push('<td class="num" data-rot="Carga">' + metaTexto(d) + "</td>");
        h.push('<td class="req" data-rot="Pré-requisitos">' + (req.length ? req.join("; ") : '<span class="ag-vazio">—</span>') + "</td>");
        h.push('<td class="req" data-rot="Libera">' + (lib.length ? lib.join("; ") : '<span class="ag-vazio">—</span>') + "</td></tr>");
      });
      h.push("</tbody></table></div></section>");
    });
    h.push("</div>");

    // quadro de optativas
    if (temSecaoOpt) {
      h.push('<section class="ag-secao" id="' + pfx + '-optativas"><h3>Disciplinas optativas</h3>');
      (opt.exigencia || []).forEach(function (t) { h.push("<p>" + esc(t) + "</p>"); });
      var exig = [];
      if (linhaOpt && !opt.exigencia) {
        var vals = colunasQR.map(function (c, i) { var v = linhaOpt[i + 1]; return v == null ? null : (c === "Horas" ? horas(v) : numero(v) + " " + c.toLowerCase()); }).filter(Boolean);
        exig.push("O quadro-resumo do currículo " + esc(dados.curriculo) + " exige " + (vals.length > 1 ? vals[0] + " (" + vals.slice(1).join(", ") + ")" : vals[0]) + " em disciplinas optativas");
      }
      if (slots.length && !opt.exigencia) exig.push((exig.length ? ", previstos" : "A matriz prevê") + " como " + slots.map(function (s) { return esc(s.n) + " (" + termoOrdinal(s.t) + ")"; }).join(" e "));
      if (exig.length) h.push("<p>" + exig.join("") + ".</p>");
      if (opt.nota) h.push('<p class="ag-aviso">' + esc(opt.nota) + "</p>");
      if (optLista.length) {
        var tipos = {}; optLista.forEach(function (o) { tipos[o.tipo] = 1; });
        h.push("<p>Relação de disciplinas optativas" + (dados.curriculo ? " do currículo " + esc(dados.curriculo) : "") + ", conforme o documento oficial" +
          (opt.fonte ? ' (<a href="' + esc(opt.fonte.url) + '" target="_blank" rel="noopener">' + esc(opt.fonte.titulo) + "</a>)" : "") + ".</p>");
        h.push('<div class="ag-tabela-wrap"><table class="ag-tabela ag-tabela-opt"><thead><tr><th scope="col">Código</th><th scope="col">Disciplina</th><th scope="col">Carga horária</th>' + (Object.keys(tipos).length > 1 ? '<th scope="col">Tipo</th>' : "") + '<th scope="col">Pré-requisitos</th></tr></thead><tbody>');
        optLista.forEach(function (o) {
          h.push("<tr><td>" + (o.semCodigo ? "—" : esc(o.cod || o.c)) + '</td><td class="nome-opt">' + esc(o.n) + (o.d ? ' <span class="ag-dep" title="Departamento">' + esc(o.d) + "</span>" : "") + '</td><td class="num" data-rot="Carga">' + metaTexto(o) + "</td>" +
            (Object.keys(tipos).length > 1 ? '<td data-rot="Tipo">' + esc(o.tipo) + "</td>" : "") +
            '<td class="req" data-rot="Pré-requisitos">' + reqOptativa(o) + "</td></tr>");
        });
        h.push("</tbody></table></div>");
      } else if (!opt.nota && !opt.exigencia) {
        h.push('<p class="ag-aviso">A relação de optativas' + (dados.curriculo ? " do currículo " + esc(dados.curriculo) : "") + " não consta dos documentos publicados do curso. Ela será incluída aqui quando for disponibilizada pelo Conselho de Curso.</p>");
      }
      if (opt.oferta && opt.oferta.itens.length) {
        var of = opt.oferta;
        h.push('<h4 class="ag-subtitulo">Optativas ofertadas — ' + esc(of.periodo) + "</h4>");
        h.push("<p>Conforme os horários de aula publicados" + (of.fonte ? ' (<a href="' + esc(of.fonte.url) + '" target="_top">' + esc(of.fonte.titulo) + "</a>)" : "") + ". A oferta varia a cada semestre.</p>");
        h.push('<div class="ag-tabela-wrap"><table class="ag-tabela ag-tabela-opt"><thead><tr><th scope="col">Código</th><th scope="col">Depto.</th><th scope="col">Disciplina</th><th scope="col">Créditos</th><th scope="col">Consta no horário do</th></tr></thead><tbody>');
        of.itens.forEach(function (o) {
          h.push("<tr><td>" + esc(o.c) + '</td><td data-rot="Depto.">' + esc(o.d || "—") + '</td><td class="nome-opt">' + esc(o.n) + '</td><td class="num" data-rot="Créditos">' + (o.cr != null ? esc(o.cr) : "—") + '</td><td data-rot="Horário">' + (o.termos || []).map(termoOrdinal).join(", ") + "</td></tr>");
        });
        h.push("</tbody></table></div>");
      }
      h.push("</section>");
    }

    // quadro-resumo
    if (qr) {
      h.push('<section class="ag-secao"><h3>' + esc(qr.titulo || "Quadro-resumo da integralização") + "</h3>");
      h.push('<div class="ag-tabela-wrap"><table class="ag-quadro"><thead><tr><th scope="col">' + esc(qr.cabecalho || "Componentes curriculares") + "</th>" + colunasQR.map(function (c) { return '<th scope="col">' + esc(c) + "</th>"; }).join("") + "</tr></thead><tbody>");
      var cel = function (v) { return v == null ? "—" : typeof v === "number" ? v.toLocaleString("pt-BR") : esc(v); };
      qr.linhas.forEach(function (l) { h.push("<tr><td>" + esc(l[0]) + "</td>" + colunasQR.map(function (c, i) { return "<td>" + cel(l[i + 1]) + "</td>"; }).join("") + "</tr>"); });
      h.push("</tbody>" + (qr.total ? "<tfoot><tr><td>" + esc(qr.rotuloTotal || "TOTAL") + "</td>" + colunasQR.map(function (c, i) { return "<td>" + cel(qr.total[i]) + "</td>"; }).join("") + "</tr></tfoot>" : "") + "</table></div>");
      if (qr.nota) h.push('<p class="ag-nota">' + esc(qr.nota) + "</p>");
      h.push("</section>");
    }

    // rodapé
    h.push('<footer class="ag-rodape">');
    if (dados.fonte) h.push('<p><strong>Fonte:</strong> <a href="' + esc(dados.fonte.url) + '" target="_blank" rel="noopener">' + esc(dados.fonte.titulo) + "</a>" + (dados.atualizadoEm ? ". Dados conferidos em " + dataBR(dados.atualizadoEm) + "." : "") + "</p>");
    h.push("<p>Ferramenta de caráter informativo. Em caso de divergência, prevalece o currículo oficial homologado. Questões sobre matrícula, equivalências e quebra de pré-requisito devem ser encaminhadas ao Conselho de Curso" +
      (dados.contato ? ' (<a href="' + esc(dados.contato.url) + '" target="_top">' + esc(dados.contato.titulo) + "</a>)" : "") + ".</p>");
    if (dados.correcoes && dados.correcoes.length) {
      h.push('<details class="ag-correcoes"><summary>Grafias corrigidas em relação ao documento (' + dados.correcoes.length + ")</summary><ul>" +
        dados.correcoes.map(function (c) { return "<li>" + (c.cod ? esc(c.cod) + (c.campo === "ementa" ? " (ementa)" : "") + ": " : "") + "“" + esc(c.de) + "” → “" + esc(c.para) + "” <small>(" + esc(c.motivo) + ")</small></li>"; }).join("") +
        "</ul><p>Códigos, créditos e cargas horárias não foram alterados.</p></details>");
    }
    h.push("<p>A simulação de percurso é armazenada somente neste navegador e não substitui o histórico escolar.</p>");
    h.push("</footer>");
    h.push("</div>");

    raiz.innerHTML = h.join("");

    /* ---------- referências ---------- */
    var ag = raiz.querySelector(".ag");
    var tela = ag.querySelector(".ag-tela");
    var rolagem = ag.querySelector(".ag-rolagem");
    var svg = ag.querySelector(".ag-arestas");
    var gArestas = ag.querySelector(".ag-arestas-g");
    var detalhe = ag.querySelector(".ag-detalhe");
    var simBox = ag.querySelector(".ag-sim");
    var anuncio = ag.querySelector("[data-anuncio]");
    var campoBusca = ag.querySelector("#" + pfx + "-busca");
    var resBusca = ag.querySelector(".ag-busca-res");
    var vistaArvore = ag.querySelector(".ag-vista-arvore");
    var cards = {};
    ag.querySelectorAll(".ag-card").forEach(function (el) { cards[el.getAttribute("data-c")] = el; });
    var linhas = {};
    ag.querySelectorAll(".ag-vista-lista tr[data-c]").forEach(function (el) { linhas[el.getAttribute("data-c")] = el; });

    /* ---------- grafos ---------- */
    function antecessores(c) {
      var vis = new Set(), pilha = [c];
      while (pilha.length) { var x = M[pilha.pop()]; x.pre.concat(x.co).forEach(function (p) { if (M[p] && !vis.has(p)) { vis.add(p); pilha.push(p); } }); }
      vis.delete(c); // co-requisitos mútuos: a própria disciplina não entra na sua cadeia
      return vis;
    }
    function dependentes(c) {
      var vis = new Set(), pilha = [c];
      while (pilha.length) { M[pilha.pop()].filhos.forEach(function (f) { if (!vis.has(f)) { vis.add(f); pilha.push(f); } }); }
      vis.delete(c);
      return vis;
    }

    /* ---------- desenho das arestas ---------- */
    function marcador(id, cor) {
      return '<marker id="' + id + '" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0.5 7.5 4 0 7.5z" fill="' + cor + '" stroke="none"/></marker>';
    }
    function desenhar() {
      if (vistaArvore.hidden) return;
      var base = tela.getBoundingClientRect();
      var w = tela.scrollWidth, hh = tela.scrollHeight;
      svg.setAttribute("width", w); svg.setAttribute("height", hh); svg.setAttribute("viewBox", "0 0 " + w + " " + hh);
      var ant = sel ? antecessores(sel) : null, dep = sel ? dependentes(sel) : null;
      var out = [];
      arestas.forEach(function (a) {
        var ra = cards[a.de].getBoundingClientRect(), rb = cards[a.para].getBoundingClientRect();
        var classe = a.co ? "co" : "", marca = pfx + "-s";
        if (sel) {
          if ((a.para === sel || ant.has(a.para)) && ant.has(a.de)) { classe += " hl-ant"; marca = pfx + "-sa"; }
          else if ((a.de === sel || dep.has(a.de)) && dep.has(a.para)) { classe += " hl-dep"; marca = pfx + "-sd"; }
        }
        var d;
        if (M[a.de].t === M[a.para].t) {
          var x = ra.right - base.left, y1 = ra.top - base.top + ra.height / 2, y2 = rb.top - base.top + rb.height / 2;
          var bx = x + 16;
          d = "M" + x + " " + y1 + " C" + bx + " " + y1 + " " + bx + " " + y2 + " " + (x + 2) + " " + y2;
        } else {
          var x1 = ra.right - base.left, ya = ra.top - base.top + ra.height / 2;
          var x2 = rb.left - base.left - 2, yb = rb.top - base.top + rb.height / 2;
          var dx = Math.max(24, (x2 - x1) * 0.5);
          d = "M" + x1 + " " + ya + " C" + (x1 + dx) + " " + ya + " " + (x2 - dx) + " " + yb + " " + x2 + " " + yb;
        }
        out.push('<path class="' + classe.trim() + '" d="' + d + '" marker-end="url(#' + marca + ')"/>');
      });
      out.sort(function (p, q) { return (p.indexOf("hl-") > -1) - (q.indexOf("hl-") > -1); });
      gArestas.innerHTML = out.join("");
    }

    /* ---------- seleção ---------- */
    function rotuloRelacao(x) {
      var s = M[sel];
      if (s.co.indexOf(x) > -1) return "co-requisito";
      if (s.pre.indexOf(x) > -1) return "pré-requisito direto";
      if (M[x].co.indexOf(sel) > -1) return "tem esta como co-requisito";
      if (s.filhos.indexOf(x) > -1) return "requer esta disciplina";
      return null;
    }
    function escreverEndereco() {
      if (!linkProfundo) return;
      var atual = location.hash;
      // só mexe no endereço quando há seleção ou quando o hash atual é da própria ferramenta
      if (!sel && atual.indexOf("#d=") !== 0) return;
      try { history.replaceState(null, "", sel ? "#d=" + encodeURIComponent(sel) : location.pathname + location.search); } catch (e) { }
    }
    function aplicarSelecao() {
      var ant = sel ? antecessores(sel) : new Set(), dep = sel ? dependentes(sel) : new Set();
      tela.classList.toggle("com-selecao", !!sel);
      Object.keys(cards).forEach(function (c) {
        var el = cards[c];
        var eAnt = ant.has(c), eDep = dep.has(c) && !eAnt;
        el.classList.toggle("sel", c === sel);
        el.classList.toggle("ant", eAnt);
        el.classList.toggle("dep", eDep);
        el.classList.toggle("ativo", c === sel || eAnt || eDep);
        el.querySelector(".ag-card-btn").setAttribute("aria-pressed", c === sel ? "true" : "false");
        el.querySelector(".ag-rel").textContent = eAnt ? (rotuloRelacao(c) || "pré-requisito indireto") : eDep ? (rotuloRelacao(c) || "dependente indireta") : "";
      });
      renderDetalhe(ant, dep);
      anuncio.textContent = sel ? "Selecionada: " + M[sel].n + ". " + plural(ant.size, "disciplina anterior", "disciplinas anteriores") + " na cadeia; " + plural(dep.size, "disciplina dependente", "disciplinas dependentes") + "." : "";
      desenhar();
      escreverEndereco();
      avisarAltura();
    }
    function selecionar(c, rolar) {
      sel = (c && M[c]) ? c : null;
      aplicarSelecao();
      if (sel && rolar && !vistaArvore.hidden) {
        var el = cards[sel];
        var alvo = el.offsetLeft - rolagem.clientWidth / 2 + el.offsetWidth / 2;
        rolagem.scrollTo({ left: Math.max(0, alvo), behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
      }
    }
    function focarSelecao() {
      // mantém o foco do teclado num ponto útil depois que o painel é recriado
      if (sel && !vistaArvore.hidden) { cards[sel].querySelector(".ag-card-btn").focus({ preventScroll: true }); return; }
      var t = detalhe.querySelector(".ag-det-nome, .ag-detalhe-vazio p");
      if (t) { t.setAttribute("tabindex", "-1"); t.focus({ preventScroll: true }); }
    }

    function chip(c, classe, extra) {
      var d = M[c];
      return '<li><button type="button" class="ag-chip ' + classe + '" data-selecionar="' + esc(c) + '">' + esc(d.n) + (cod(d) ? " <small>" + esc(cod(d)) + "</small>" : "") + (extra ? " <small>" + extra + "</small>" : "") + "</button></li>";
    }
    function renderDetalhe(ant, dep) {
      if (!sel) {
        detalhe.innerHTML = '<div class="ag-detalhe-vazio">' + ICONES.arvore +
          "<p>Selecione uma disciplina para consultar " + (temEmenta ? "sua ementa, " : "") +
          "seus pré-requisitos e as disciplinas que dependem dela. A cadeia anterior é destacada em azul-escuro; as disciplinas dependentes, em azul-claro.</p></div>";
        return;
      }
      var d = M[sel];
      var meta = [(d.tipo === "SLOT" ? "<b>Optativa</b>" : cod(d) ? "<b>" + esc(cod(d)) + "</b>" : ""), termoOrdinal(d.t)].filter(Boolean);
      if (rotuloTermo(d.t)) meta.push(esc(rotuloTermo(d.t)));
      meta.push(metaTexto(d, true));
      if (d.d) meta.push("Depto. " + esc(d.d));
      if (mostraTipo && d.tipo !== "SLOT") meta.push("Tipo " + esc(d.tipo));
      var x = [];
      x.push('<div class="ag-det-topo"><div><div class="ag-det-meta">' + meta.join(" · ") + '</div><h3 class="ag-det-nome">' + esc(d.n) + "</h3></div>");
      x.push('<button type="button" class="ag-det-fechar" data-acao="limpar" aria-label="Limpar seleção" title="Limpar seleção">' + ICONES.fechar + "</button></div>");
      if (d.tipo === "SLOT") {
        x.push('<p class="ag-det-ementa">Vaga destinada a disciplina optativa' + (temSecaoOpt ? ' — consulte o <a href="#' + pfx + '-optativas">quadro de disciplinas optativas</a>' : "") + ".</p>");
      } else if (d.ementa) {
        x.push('<p class="ag-det-ementa"><b>Ementa.</b> ' + esc(d.ementa) + "</p>");
      }
      x.push('<div class="ag-det-grade">');
      x.push('<div><h4>Pré-requisitos</h4><ul class="ag-lista-chips">');
      if (regras[sel]) x.push('<li><span class="ag-chip neutro pre">' + esc(regras[sel].texto) + "</span></li>");
      d.pre.forEach(function (p) { if (M[p]) x.push(chip(p, "pre")); });
      if (d.preTexto) x.push('<li><span class="ag-chip neutro pre">' + esc(d.preTexto) + "</span></li>");
      if (!d.pre.length && !regras[sel] && !d.preTexto) x.push('<li><span class="ag-chip neutro">Nenhum</span></li>');
      x.push("</ul></div>");
      if (d.co.length || d.coTexto) {
        x.push('<div><h4>Co-requisitos</h4><ul class="ag-lista-chips">');
        d.co.forEach(function (p) { if (M[p]) x.push(chip(p, "co")); });
        if (d.coTexto) x.push('<li><span class="ag-chip neutro co">' + esc(d.coTexto) + "</span></li>");
        x.push("</ul></div>");
      }
      x.push('<div><h4>Disciplinas que dependem desta</h4><ul class="ag-lista-chips">');
      if (d.filhos.length) d.filhos.forEach(function (f) { x.push(chip(f, "pos", M[f].co.indexOf(sel) > -1 ? "co-req." : "")); });
      else x.push('<li><span class="ag-chip neutro">Nenhuma</span></li>');
      x.push("</ul></div>");
      if (optPorReq[sel]) {
        x.push('<div><h4>Optativas que a exigem</h4><ul class="ag-lista-chips">');
        optPorReq[sel].forEach(function (o) { x.push('<li><span class="ag-chip neutro">' + esc(o.n) + " <small>" + esc(o.c) + "</small></span></li>"); });
        x.push("</ul></div>");
      }
      x.push("</div>");
      if (d.tipo !== "SLOT") {
        x.push('<p class="ag-det-rodape">Cadeia anterior completa: ' + plural(ant.size, "disciplina", "disciplinas") +
          " · Dependentes diretas e indiretas: " + plural(dep.size, "disciplina", "disciplinas") + ".</p>");
      }
      detalhe.innerHTML = x.join("");
    }

    /* ---------- busca ---------- */
    function aplicarBusca() {
      var q = norm(busca.trim());
      var nres = 0;
      tela.classList.toggle("com-busca", !!q);
      lista.forEach(function (d) {
        var ok = !!q && (norm(d.n).indexOf(q) > -1 || norm(d.c).indexOf(q) > -1);
        if (ok) nres++;
        cards[d.c].classList.toggle("achado", ok);
        linhas[d.c].classList.toggle("oculta", !!q && !ok);
      });
      resBusca.textContent = q ? (nres === 0 ? "Nenhum resultado" : nres === 1 ? "1 resultado" : nres + " resultados") : "";
      ag.querySelectorAll(".ag-lista-termo").forEach(function (sec) {
        sec.classList.toggle("sem-resultado", !!q && !sec.querySelector("tr[data-c]:not(.oculta)"));
      });
      avisarAltura();
      return q ? lista.filter(function (d) { return cards[d.c].classList.contains("achado"); }) : [];
    }

    /* ---------- simulação ---------- */
    function horasConcluidas(soBaseRegra) {
      return lista.filter(function (d) {
        if (!concluidas.has(d.c) || !contaNoProgresso(d)) return false;
        return soBaseRegra ? d.tipo === "OBR" : true;
      }).reduce(function (s, d) { return s + valorProg(d); }, 0);
    }
    function regraAtendida(d) {
      var r = regras[d.c];
      if (!r || r.tipo !== "percentualObrigatorias") return true;
      return horasConcluidas(true) >= r.valor * baseRegra;
    }
    // apta = pré-requisitos concluídos + regra atendida + cada co-requisito concluído ou, ele próprio, apto
    function podeCursar(c, visitando) {
      var d = M[c];
      if (concluidas.has(c)) return true;
      if (!d.pre.every(function (p) { return concluidas.has(p); })) return false;
      if (!regraAtendida(d)) return false;
      visitando = visitando || new Set([c]);
      return d.co.every(function (p) {
        if (concluidas.has(p)) return true;
        if (visitando.has(p)) return true;
        visitando.add(p);
        return podeCursar(p, visitando);
      });
    }
    function estadoDe(d) {
      if (d.tipo === "SLOT") return concluidas.has(d.c) ? "concluida" : "apta";
      if (concluidas.has(d.c)) {
        var faltam = d.pre.filter(function (p) { return !concluidas.has(p); });
        return faltam.length ? "inconsistente" : "concluida";
      }
      return podeCursar(d.c) ? "apta" : "bloqueada";
    }
    var TEXTO_ESTADO = { concluida: "concluída", apta: "apta para matrícula", bloqueada: "pré-requisitos pendentes", inconsistente: "concluída sem pré-requisito marcado" };
    function aplicarSimulacao() {
      ag.classList.toggle("simulando", simulando);
      simBox.hidden = !simulando;
      ag.querySelector('[data-acao="simular"]').setAttribute("aria-pressed", simulando ? "true" : "false");
      var cont = { concluida: 0, apta: 0, bloqueada: 0, inconsistente: 0 };
      lista.forEach(function (d) {
        var el = cards[d.c];
        var e = estadoDe(d);
        if (d.tipo !== "SLOT") cont[e]++;
        ["concluida", "apta", "bloqueada", "inconsistente"].forEach(function (k) {
          el.classList.toggle(k, e === k || (k === "concluida" && e === "inconsistente"));
        });
        el.querySelector(".ag-estado").textContent = TEXTO_ESTADO[e];
        var cb = el.querySelector("input[data-concluir]"); if (cb) cb.checked = concluidas.has(d.c);
      });
      if (!simulando) { avisarAltura(); return; }
      var feitas = horasConcluidas(false);
      var pct = totalObrig ? feitas / totalObrig : 0;
      var s = [];
      s.push('<div class="ag-sim-topo"><div class="ag-sim-num"><strong>' + fmtProg(feitas) + "</strong> de " + fmtProg(totalObrig) + " " + rotuloProgresso + " (" + Math.round(pct * 100) + "%)</div>");
      s.push('<div class="ag-sim-contagem">' + plural(cont.concluida + cont.inconsistente, "concluída", "concluídas") + " · " + cont.apta + (cont.apta === 1 ? " apta" : " aptas") + " para matrícula · " + cont.bloqueada + " com pré-requisitos pendentes</div></div>");
      var marcas = "", notas = [];
      Object.keys(regras).forEach(function (c) {
        var r = regras[c];
        if (r.tipo !== "percentualObrigatorias" || !M[c]) return;
        var alvo = r.valor * baseRegra, feitasBase = horasConcluidas(true);
        marcas += '<span class="ag-trilho-marca" style="left:' + (alvo / totalObrig * 100).toFixed(2) + '%" title="' + esc(M[c].n) + '"></span>';
        notas.push("<strong>" + esc(c) + " — " + esc(M[c].n) + ":</strong> exige " + Math.round(r.valor * 100) + "% da carga obrigatória (" + fmtProg(Math.ceil(alvo)) + "). " +
          (feitasBase >= alvo ? "Requisito atendido na simulação." : "Faltam " + fmtProg(Math.ceil(alvo - feitasBase)) + "."));
      });
      s.push('<div class="ag-trilho" role="progressbar" aria-label="Carga horária obrigatória concluída" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + Math.round(pct * 100) + '"><span class="ag-trilho-fill" style="width:' + Math.min(100, pct * 100).toFixed(2) + '%"></span>' + marcas + "</div>");
      notas.forEach(function (t) { s.push('<p class="ag-sim-nota">' + t + "</p>"); });
      if (cont.inconsistente) {
        s.push('<p class="ag-sim-nota ag-sim-alerta">' + plural(cont.inconsistente, "disciplina marcada como concluída tem", "disciplinas marcadas como concluídas têm") + " pré-requisito não marcado. Revise as marcações destacadas.</p>");
      }
      s.push('<div class="ag-sim-rodape"><p class="ag-sim-nota">Marque as disciplinas concluídas diretamente na árvore. As marcações permanecem apenas neste navegador.</p>');
      s.push('<button type="button" class="ag-btn" data-acao="zerar">Limpar marcações</button></div>');
      simBox.innerHTML = s.join("");
      avisarAltura();
    }

    /* ---------- vista ---------- */
    function aplicarVista() {
      vistaArvore.hidden = vista !== "arvore";
      ag.querySelector(".ag-vista-lista").hidden = vista !== "lista";
      ag.querySelectorAll("[data-vista]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-vista") === vista ? "true" : "false"); });
      if (vista === "arvore") requestAnimationFrame(desenhar);
      avisarAltura();
    }

    /* ---------- altura para iframe ---------- */
    var ultimaAltura = 0;
    function alturaConteudo() {
      // mede o conteúdo, não a janela: scrollHeight nunca fica menor que a altura do iframe
      var alvo = raiz.closest(".ag-container") || raiz;
      var r = alvo.getBoundingClientRect();
      var cs = getComputedStyle(document.body);
      return Math.ceil(r.bottom + window.scrollY + parseFloat(cs.marginBottom || 0) + parseFloat(cs.paddingBottom || 0));
    }
    function avisarAltura() {
      if (window.parent === window) return;
      requestAnimationFrame(function () {
        var a = alturaConteudo();
        if (a !== ultimaAltura) { ultimaAltura = a; window.parent.postMessage({ tipo: "arvore-grade:altura", id: dados.id, altura: a }, "*"); }
      });
    }

    /* ---------- eventos ---------- */
    ag.addEventListener("click", function (ev) {
      var alvo = ev.target.closest("[data-selecionar],[data-acao],[data-vista],.ag-card-btn");
      if (!alvo || !ag.contains(alvo)) return;
      if (alvo.classList.contains("ag-card-btn")) {
        var c = alvo.closest(".ag-card").getAttribute("data-c");
        selecionar(sel === c ? null : c, false);
      } else if (alvo.hasAttribute("data-selecionar")) {
        var veioDoPainel = detalhe.contains(alvo);
        selecionar(alvo.getAttribute("data-selecionar"), true);
        if (vista === "lista") detalhe.scrollIntoView({ block: "nearest", behavior: "smooth" });
        if (veioDoPainel || vista === "lista") focarSelecao();
      } else if (alvo.hasAttribute("data-vista")) {
        vista = alvo.getAttribute("data-vista"); gravar(chave + ":vista", vista); aplicarVista();
      } else {
        var acao = alvo.getAttribute("data-acao");
        if (acao === "limpar") { var ant = sel; selecionar(null); if (ant && cards[ant] && !vistaArvore.hidden) cards[ant].querySelector(".ag-card-btn").focus({ preventScroll: true }); }
        else if (acao === "simular") { simulando = !simulando; gravar(chave + ":simulando", simulando); aplicarSimulacao(); requestAnimationFrame(desenhar); }
        else if (acao === "zerar") { concluidas.clear(); gravar(chave + ":concluidas", []); aplicarSimulacao(); }
        else if (acao === "imprimir") window.print();
      }
    });
    ag.addEventListener("change", function (ev) {
      var cb = ev.target.closest("input[data-concluir]");
      if (!cb) return;
      var c = cb.getAttribute("data-concluir");
      if (cb.checked) concluidas.add(c); else concluidas.delete(c);
      gravar(chave + ":concluidas", Array.from(concluidas));
      aplicarSimulacao();
    });
    campoBusca.addEventListener("input", function () { busca = campoBusca.value; aplicarBusca(); });
    campoBusca.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter") { var r = aplicarBusca(); if (r.length) selecionar(r[0].c, true); }
      if (ev.key === "Escape") { campoBusca.value = ""; busca = ""; aplicarBusca(); }
    });
    ag.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && sel && ev.target !== campoBusca) selecionar(null);
    });

    var agendado = false;
    function redesenharDepois() { if (agendado) return; agendado = true; requestAnimationFrame(function () { agendado = false; desenhar(); avisarAltura(); }); }
    window.addEventListener("resize", redesenharDepois);
    if (window.ResizeObserver) { var ro = new ResizeObserver(redesenharDepois); ro.observe(tela); ro.observe(ag); }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(redesenharDepois);

    /* ---------- estado inicial ---------- */
    aplicarVista();
    aplicarSimulacao();
    var inicial = null;
    if (linkProfundo) { var m = /^#d=([^&]+)/.exec(location.hash); if (m) inicial = decodeURIComponent(m[1]); }
    selecionar(inicial, !!inicial);

    return { selecionar: selecionar, dados: dados };
  }

  /* ---------- inicialização automática ---------- */
  function iniciar(escopo) {
    (escopo || document).querySelectorAll("[data-arvore-grade]:not([data-ag-montado])").forEach(function (el) {
      var ids = el.getAttribute("data-arvore-grade").split(",").map(function (x) { return x.trim(); }).filter(Boolean);
      if (!ids.length || !ids.every(function (id) { return REGISTRO[id]; })) return;
      el.setAttribute("data-ag-montado", "");
      if (ids.length === 1) montar(el, REGISTRO[ids[0]]);
      else montarSeletor(el, ids);
    });
  }

  /* ---------- seletor de currículos (modalidades e turnos de um mesmo curso) ---------- */
  function montarSeletor(el, ids) {
    var params = new URLSearchParams(location.search);
    var chave = "arvore-grade:seletor:" + ids.join(",");
    var atual = params.get("curriculo");
    if (ids.indexOf(atual) < 0) atual = lerArmazenado(chave, null);
    if (ids.indexOf(atual) < 0) atual = ids[0];
    var n = ++instancias;
    var caixa = document.createElement("div");
    caixa.className = "ag ag-seletor";
    caixa.innerHTML = '<span class="ag-rotulo" id="ag-sel' + n + '">Currículo</span><div class="ag-seg ag-seg-quebra" role="group" aria-labelledby="ag-sel' + n + '">' +
      ids.map(function (id) { var d = REGISTRO[id]; return '<button type="button" data-curriculo="' + esc(id) + '">' + esc(d.rotuloSeletor || d.curso) + "</button>"; }).join("") + "</div>";
    var alvo = document.createElement("div");
    el.innerHTML = "";
    el.appendChild(caixa);
    el.appendChild(alvo);
    function abrir(id, foco) {
      atual = id;
      gravar(chave, id);
      caixa.querySelectorAll("[data-curriculo]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-curriculo") === id ? "true" : "false"); });
      var box = document.createElement("div");
      alvo.innerHTML = "";
      alvo.appendChild(box);
      montar(box, REGISTRO[id]);
      if (location.hash.indexOf("#!") !== 0) {
        var p = new URLSearchParams(location.search);
        p.set("curriculo", id);
        try { history.replaceState(null, "", location.pathname + "?" + p.toString() + (foco ? "" : location.hash)); } catch (e) { }
      }
      if (foco) caixa.querySelector('[data-curriculo="' + id + '"]').focus();
    }
    caixa.addEventListener("click", function (ev) {
      var b = ev.target.closest("[data-curriculo]");
      if (b && b.getAttribute("data-curriculo") !== atual) abrir(b.getAttribute("data-curriculo"), true);
    });
    abrir(atual, false);
  }
  var observador = null;
  function observar() {
    iniciar();
    if (observador || !window.MutationObserver || !document.body) return;
    observador = new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) { if (muts[i].addedNodes.length) { iniciar(); return; } }
    });
    observador.observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", observar);
  else observar();

  window.ArvoreGrade = { registrar: registrar, montar: montar, iniciar: iniciar, cursos: REGISTRO };
})();
