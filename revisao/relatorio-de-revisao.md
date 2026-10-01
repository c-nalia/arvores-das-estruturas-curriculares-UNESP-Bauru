# Relatório de revisão técnica — Árvore de Grade

**Objeto:** pasta `arvore-de-grade/` (componente, dados do BCC 2105 e do BSI 2804, páginas, prévias e README).
**Data:** 30/09/2026.
**Situação atual:** todos os achados foram corrigidos — ver seção 7.
**Escopo:** fidelidade dos dados às fontes oficiais, correção do comportamento, acessibilidade e coerência interna do projeto.
Não foram avaliados o mérito nem os eventuais erros das grades oficiais em si.

## Resumo

| Severidade | Qtd. | Achados |
|---|---|---|
| Alta | 2 | B1 impressão vazia · B3 co-requisito ignorado na simulação |
| Média | 8 | D1 nome errado (BSI 4742) · B2 impressão com busca · B4 altura do iframe só cresce · B5 alturas fixas do README · B6 Opção B inviável no portal · A1 perda de foco · A3 contraste · P1 README afirma o que não ocorre |
| Baixa | 13 | D2, D4, B7–B10, A2, A4, P2–P6 |

**Os dados estão corretos, com uma exceção.** Todas as 46 linhas do PDF do BCC conferem com o
grafo: código, nome, termo, horas, pré-requisitos, co-requisitos e a regra de 70% do TCC. As 43
ementas do BCC são idênticas às do portal. No BSI, as 38 disciplinas da matriz conferem em
termo, tipo, carga, pré e co-requisitos, e as 42 optativas estão todas presentes. Há um nome
incorreto (D1) e uma inconsistência de modelagem (D2).

**Os defeitos estão no comportamento, não no grafo.** O desenho das arestas e o destaque da
cadeia foram verificados exaustivamente e estão corretos (T02, T03). Os problemas mais sérios
são a impressão, que sai vazia, e a simulação, que aponta como "apta" uma disciplina cujo
co-requisito não pode ser cursado.

---

## 1. Método

1. **Referências independentes.** As fontes oficiais foram lidas outra vez, por coordenadas, e
   não a partir da transcrição que originou os dados:
   - **BCC:** o PDF do currículo 2105 foi extraído com `pdftotext -bbox`, e cada palavra
     atribuída à coluna pela posição x (Código, Disciplina, Créditos, Horas, Co-Requisito,
     Pré-Requisito).
   - **BSI:** o PDF do currículo 2804 foi baixado do portal e extraído com pdf.js, também por
     posição. Os requisitos foram agrupados em blocos verticais centrados na linha da
     disciplina.
   - **Termos do BSI:** os cabeçalhos "Série x – Período y" não são texto no PDF. Por isso
     foram conferidos visualmente, página a página, e confirmados pelos totais de carga
     impressos (300, 300, 330, 300, 300, 240, 270, 300 h).
   - Essas transcrições estão em `testes/referencia/`. Um controle negativo confirmou que o
     comparador detecta divergências: um pré-requisito e um termo foram alterados de propósito,
     e ambos foram apontados.
2. **Validação estática** (`testes/validar-dados.mjs`, sem dependências): 1.529 verificações de
   integridade (códigos únicos, requisitos existentes e em termo anterior, ausência de ciclos,
   quadro-resumo fechando) e de fidelidade às referências.
3. **Testes em navegador** (`testes/e2e.mjs`, Playwright/Chromium): 32 casos cobrindo desenho,
   seleção, busca, simulação, impressão, iframe, link profundo, armazenamento bloqueado, teclado,
   ARIA, celular, duas instâncias, injeção de HTML e montagem tardia.
4. **Revisão de código** de `arvore-grade.js` e `arvore-grade.css`, e cálculo de contraste
   WCAG 2.1 dos pares de cor usados.
5. **Confronto com o portal ao vivo.** Os endereços do menu lateral do BSI foram lidos no
   próprio www.fc.unesp.br.

Resultado bruto: validação de dados **1.527/1.529**; testes em navegador **17/32** (anexo).

---

## 2. Fidelidade dos dados

### D1 — Nome incorreto: BSI 4742 · Média
- **Onde:** `bsi/dados-bsi-2804.js:52`.
- **Evidência:** o documento 2804 traz "0004742 - Metodologia da Pesquisa". O dado diz
  "Metodologia da Pesquisa Científica".
- **Causa provável:** a palavra "Científica" que aparece logo abaixo pertence à coluna de
  Equivalências ("0071132 - Introdução à Metodologia da Pesquisa Científica") e foi lida como
  continuação do nome.
- **Correção:** `n: "Metodologia da Pesquisa"`.

### D2 — DPA001 modelada de forma diferente da fonte · Baixa
- **Onde:** `bsi/dados-bsi-2804.js:124`.
- **Evidência:** no documento, os 75 h estão na coluna *Carga Horária* com tipo `EXT`. No dado,
  foram registrados como `ch: 0, ext: 75`.
- **Incoerência:** a 4746, que o documento põe na coluna *CH ACEU*, também está em `ext`. Assim,
  o mesmo campo representa duas colunas diferentes da fonte.
- **Correção:** adotar `ch: 75, tipo/rotulo: "EXT"`, ou documentar que `ext` significa
  "de natureza extensionista" independentemente da coluna.

### D3 — BCC · conferido
46/46 linhas idênticas ao PDF. Ementas 43/43 idênticas às do portal. Nenhuma divergência.

### D4 — Dados exibidos que não vêm do documento 2804 · Baixa
- **O que:** o turno "Noturno" e os departamentos (MAT, COM…) do BSI foram herdados do
  currículo 2803.
- **Situação:** o README já declara isso. Mesmo assim, a página exibe esses dados como se fossem
  do 2804.
- **Recomendação:** não exibir até a confirmação.

---

## 3. Defeitos funcionais

### B1 — Impressão a partir da vista "Árvore" sai vazia · Alta
- **Teste:** T04-bcc e T04-bsi. Linhas visíveis na impressão: 0 de 46 e 0 de 38.
- **Causa:** `arvore-grade.css:39`, `.ag [hidden]{display:none!important}` (especificidade
  0,2,0), vence `.ag-vista-lista{display:block!important}` (0,1,0) do `@media print`
  (linha 317). A lista continua com o atributo `hidden`.
- **Consequência:** o botão "Imprimir" gera uma página só com cabeçalho, quadro e rodapé.
- **Correção:** no bloco de impressão, usar `.ag .ag-vista-lista[hidden]{display:block!important}`,
  ou remover o atributo no evento `beforeprint`.

### B2 — Impressão com busca ativa omite termos · Média
- **Teste:** T05. 25 de 46 linhas.
- **Causa:** `aplicarBusca` esconde seções inteiras com `sec.hidden` (`arvore-grade.js:417`). O
  CSS de impressão só reexibe as linhas (`tr.oculta`), não as seções.
- **Correção:** limpar a busca em `beforeprint` ou reexibir `.ag-lista-termo[hidden]` na
  impressão.

### B3 — Simulação ignora co-requisitos ao marcar "apta para matrícula" · Alta
- **Teste:** T19.
- **Onde:** `arvore-grade.js:424–426`. `estadoDe` só testa `d.pre`.
- **Exemplo no BCC:** com Algoritmos I e II concluídas e Lógica pendente, Estruturas de Dados I
  fica bloqueada. Mesmo assim, Programação Orientada a Objetos aparece como apta, embora exija
  cursar EDI no mesmo período.
- **Exemplo no BSI:** o mesmo ocorre com Redes (4724) em relação a Sistemas Operacionais
  (4723).
- **Correção:** apta ⇔ todos os `pre` concluídos **e** cada `co` concluído ou, ele próprio, apto.

### B4 — A altura do iframe só aumenta · Média
- **Teste:** T14, na prévia do BSI: árvore 2.835 px → lista 5.130 px → árvore **5.130 px**.
- **Causa:** `arvore-grade.js:487` mede `document.documentElement.scrollHeight`. Dentro de um
  iframe, esse valor nunca é menor que a altura atual do próprio iframe.
- **Consequência:** depois de abrir a lista, a seleção ou a simulação, a página do portal fica
  com cerca de 2.300 px de espaço em branco.
- **Correção:** medir `document.querySelector(".ag-container").getBoundingClientRect().height`,
  ou `document.body` com `html{height:auto}`.

### B5 — As alturas fixas sugeridas no README cortam o conteúdo no celular · Média
- **Teste:** T20. Com 360 px de largura, abre-se a lista por termo: o BCC mede 9.342 px e o BSI
  11.239 px, contra os 2.200 e 2.900 px sugeridos (README, linha 78).
- **Correção:** sem script de redimensionamento, oferecer no celular um link "abrir em página
  própria". Alternativa: iframe de altura limitada com rolagem interna, sinalizada.

### B6 — "Opção B — incorporação direta" não funciona no portal · Média
- O conteúdo das páginas do Portal Unesp é injetado pelo AngularJS, e `<script>` inserido dessa
  forma não é executado.
- Mesmo que fosse, o componente só procura elementos `[data-arvore-grade]` no
  `DOMContentLoaded` (`arvore-grade.js:553`). Ao navegar entre rotas `#!`, o elemento reinserido
  não é montado (T16).
- **Correção:** retirar a opção do README, ou expor `ArvoreGrade.iniciar()` com um
  `MutationObserver` e condicioná-la a um recurso do CMS que aceite scripts.

### B7 — Âncora existente é apagada ao abrir a página · Baixa
- **Teste:** T18.
- **Causa:** sem seleção, `aplicarSelecao` reescreve o endereço para `pathname+search`
  (`arvore-grade.js:335`), apagando qualquer `#…` que não seja `#d=`.
- **Correção:** só reescrever quando o hash atual começa com `#d=`.

### B8 — Escurecimento inconsistente com seleção e simulação ativas · Baixa
- **Teste:** T12. Fora da cadeia selecionada, as opacidades ficam em 0,26 e 0,55 ao mesmo tempo.
- **Causa:** `.ag.simulando .ag-card.bloqueada:not(.ativo)` (linha 221) tem especificidade maior
  que `.ag-tela.com-selecao .ag-card` (linha 193). O mesmo ocorre com a busca.
- **Correção:** qualificar a regra da simulação com `.ag-tela:not(.com-selecao):not(.com-busca)`.

### B9 — Na simulação, cartões concluídos perdem a cor da cadeia · Baixa (por inspeção)
`.ag.simulando .ag-card.concluida` (0,4,0) sobrepõe `.ag-card.ant` e `.ag-card.dep` (0,2,0). A
relação continua indicada em texto, mas a cor some.

### B10 — Estados impossíveis na simulação · Baixa
- **O que:** é possível marcar como concluída uma disciplina cujos pré-requisitos não estão
  concluídos (ex.: Compiladores sem EDI).
- **Consequência:** as dependentes passam a aparecer como aptas.
- **Correção:** avisar ou marcar a inconsistência.

---

## 4. Acessibilidade

### A1 — Foco do teclado perdido ao navegar pelo painel · Média
- **Teste:** T08.
- **Causa:** ativar uma disciplina dentro do painel recria o painel via `innerHTML`
  (`arvore-grade.js:401`), e o foco vai para o `<body>`. Quem navega por teclado ou leitor de
  tela volta ao início da página.
- **Correção:** após renderizar, focar o título do painel (`tabindex="-1"`) ou o cartão
  selecionado.

### A2 — Estrutura ARIA inválida · Baixa
- **Teste:** T09. Cada coluna é `role="list"` (linha 162), mas contém o cabeçalho do termo como
  filho, o que dá 8 filhos inválidos por curso.
- **Correção:** tirar o cabeçalho da lista e referenciá-lo por `aria-labelledby`.

### A3 — Contraste abaixo do declarado · Média
O README afirma "Contraste de texto ≥ 4,5:1" (linha 134). Medido pela WCAG 2.1:

| Par | Razão | Mínimo |
|---|---|---|
| `--ag-texto-3` #69727b em #f5f5f5 (rótulos da ficha, 11 px) | 4,49 | 4,5 |
| #69727b em #eaf0f5 (código nos chips de pré-requisito) | 4,26 | 4,5 |
| #69727b em #e7f6fe (código nos chips de dependentes) | 4,43 | 4,5 |
| #69727b em #ebf5ec (cartão concluído) | 4,38 | 4,5 |
| Borda do campo de busca e da caixa de seleção #d7dce1 em branco | 1,38 | 3,0 (WCAG 1.4.11) |
| Arestas #b9c3cc em branco | 1,79 | 3,0 (objeto gráfico) |

- **Correção:** `--ag-texto-3: #5f6871` (≥ 4,93 em todos os fundos), e bordas de controles
  `#8792a0` (3,16 em branco).
- **Observação:** os cartões fora da cadeia, a 26% de opacidade, ficam ilegíveis de propósito. O
  README deveria mencionar isso.

### A4 — Região `aria-live` extensa · Baixa
O painel inteiro é `aria-live="polite"`, então cada seleção faz o leitor de tela ler toda a
ementa e as listas. Sugere-se anunciar apenas "Selecionada: <nome>" numa região própria.

---

## 5. Incoerências do projeto e da documentação

### P1 — O README afirma comportamentos que não se verificam · Média
Linha 134 (contraste, ver A3). Linha 135, "Impressão gera a lista por termo completa" (ver B1 e
B2). Linha 78, alturas fixas (ver B5). Seção "Opção B" (ver B6). Linha 132: a lista só é
"ativada automaticamente em telas estreitas" na primeira visita, pois uma preferência salva
prevalece e redimensionar a janela não reavalia.

### P2 — Menu lateral da prévia do BSI com endereços inventados · Baixa
- **Onde:** `bsi/previa-no-portal.html`.
- **Endereços errados:** comparado com o portal ao vivo,
  - `…/aacc-e-atividades-complementares/` → o correto é `…/aacc/`;
  - `…/conselho-de-curso/` → o correto é `…/conselho-do-curso/`.
- **Falta um item:** "Identidade Visual do Curso" (`…/identidade-visual-do-curso/`).

### P3 — O link de contato não leva ao Conselho de Curso · Baixa
- **Onde:** `contato.url` nos dois arquivos de dados.
- **O que acontece:** o rodapé diz "encaminhadas ao Conselho de Curso", mas o link aponta para
  a raiz do curso.
- **Correção no BSI:** a página existe em `…/bacharelado-em-sistemas-de-informacao/conselho-do-curso/`.

### P4 — A página de entrada aponta para arquivos que não serão publicados · Baixa
- **Onde:** `index.html:31,36,39`.
- **O que acontece:** ela liga para `previa-no-portal.html` e para `README.md`, mas o README
  manda publicar sem os arquivos `previa-*`. Em produção, os links quebram.

### P5 — Modelagem do TCC e das somas de carga incoerente entre telas e cursos · Baixa
- **Tipo do TCC:** no BCC, o TCC (4650) é `OBR`; no BSI, os TCCs são `TRA`.
- **Rótulo da simulação:** a barra do BSI diz "em disciplinas obrigatórias", mas inclui os TCCs.
- **Distribuição da carga:** o 4650 é anual, mas aparece só no 7º termo. O cabeçalho mostra
  420 h no 7º e 180 h no 8º, sem indicar que parte da carga cai no 8º.
- **Definições diferentes de "carga":** o cabeçalho de cada termo soma vagas de optativa e
  horas de extensão; a barra de progresso exclui as duas.
- **Recomendação:** definir e documentar uma única convenção.

### P6 — Função dentro do arquivo de dados · Baixa
- **Onde:** `bsi/dados-bsi-2804.js:35` (`rotuloTermo`).
- **Problema:** por ser uma função, o arquivo não pode ser serializado como JSON nem gerado
  automaticamente a partir do Sistema de Graduação. Isso pesa se o componente for adotado por
  outros cursos da Unesp.
- **Correção:** trocar por um campo declarativo, por exemplo `"rotuloTermo": "serie-periodo"`.

---

## 6. Verificado e correto

- **Arestas (T02):** as 45 do BCC e as 41 do BSI partem da borda do cartão de origem e chegam à
  do destino. Os co-requisitos do mesmo termo são desenhados pela lateral.
- **Destaque da cadeia (T03):** para cada uma das 84 disciplinas, a cadeia anterior e as
  dependentes destacadas são exatamente o fecho transitivo calculado, e o número "libera N"
  confere.
- **Regra de 70% (T13):** a disciplina 4650 passa a apta exatamente ao atingir 1.869 h
  (124,6 créditos).
- **Robustez:**
  - funciona com `localStorage` lançando exceção (T06);
  - o link profundo `#d=` funciona, e um código inválido não quebra a página (T07);
  - duas instâncias na mesma página não geram ids duplicados (T15);
  - conteúdo HTML nos dados é escapado (T17);
  - não há rolagem horizontal no celular (T11);
  - a busca ignora acentos, Enter seleciona o primeiro resultado e Esc limpa (T10).
- **Integridade dos dados:** todos os requisitos apontam para disciplinas existentes em termos
  anteriores, não há ciclos, e o quadro-resumo do BCC fecha (178 créditos obrigatórios =
  2.670 h; total 214 = 3.210 h).

---

## 7. Situação após as correções (30/09/2026)

Todos os achados foram tratados. Regra adotada nas correções: nomes e dados dos documentos
oficiais são reproduzidos literalmente, mesmo quando parecem incompletos ou incorretos.

| ID | Situação | O que foi feito |
|---|---|---|
| D1 | Corrigido | 4742 passa a "Metodologia da Pesquisa", como no documento 2804. |
| D2 | Corrigido | DPA001 com `ch: 75`, `tipo: "EXT"`, como no documento. O campo `ext` foi substituído por `aceu`, que espelha só a coluna "CH ACEU". |
| D4 | Corrigido | Turno e departamentos do BSI, ausentes do documento 2804, foram removidos. |
| — | Novo | Revisão literal de todos os nomes. O PDF do BCC imprime "A0lgebra Linear" na coluna Disciplina, e assim ficou (pendência 1 do README). "Teoria da Computacão…" (BSI) foi mantida. O nome completo "Projeto e Implementação de Sistemas (TCC-disciplina anual)" substituiu o rótulo parafraseado. O texto da regra de 70% agora é literal. |
| B1, B2 | Corrigido | A impressão reexibe a lista e todas as seções, qualquer que seja a vista ou a busca. As seções sem resultado passam a ser ocultadas por classe, e não por `hidden`. |
| B3 | Corrigido | Uma disciplina só fica "apta" se os pré-requisitos estiverem concluídos e cada co-requisito estiver concluído ou apto. |
| B4 | Corrigido | A altura enviada ao iframe é a do conteúdo, e não o `scrollHeight` da janela. Um `ResizeObserver` na raiz reenvia a altura a cada mudança. |
| B5 | Corrigido | O README não recomenda mais alturas fixas: o padrão é `85vh` com rolagem interna, mais um link para a página própria. |
| B6 | Corrigido | `ArvoreGrade.iniciar()` é público e um `MutationObserver` monta elementos inseridos depois do carregamento. O README explica que scripts no conteúdo AngularJS não rodam. |
| B7 | Corrigido | O endereço só é reescrito quando há seleção ou quando o hash é `#d=`. |
| B8, B9 | Corrigido | Com seleção ativa, todos os cartões fora da cadeia ficam a 0,26, e a cor da cadeia prevalece sobre a da simulação. |
| B10 | Corrigido | Uma disciplina marcada como concluída sem o pré-requisito marcado recebe borda vermelha, o texto "concluída sem pré-requisito marcado" e um aviso na barra da simulação. |
| A1 | Corrigido | Ao escolher uma disciplina no painel, o foco vai para o cartão correspondente (ou para o título do painel, na lista). "Limpar seleção" devolve o foco ao cartão. |
| A2 | Corrigido | O cabeçalho do termo saiu da lista; cada lista é rotulada por `aria-labelledby`. |
| A3 | Corrigido | `--ag-texto-3` passou a #5f6871 (≥ 4,93:1). Controles e arestas passaram a #8792a0 (3,16:1). |
| A4 | Corrigido | O painel deixou de ser `aria-live`; uma região discreta anuncia apenas a seleção e os totais. |
| P1 | Corrigido | O README foi reescrito, com afirmações verificadas pelos testes. |
| P2 | Corrigido | O menu lateral das duas prévias usa os itens e endereços lidos no portal, inclusive "Identidade Visual do Curso". |
| P3 | Corrigido | O contato leva a `…/conselho-de-curso/` (BCC) e `…/conselho-do-curso/` (BSI). |
| P4 | Corrigido | A página de entrada foi marcada como "página de avaliação — não publicar", e o README lista exatamente o que publicar. |
| P5 | Corrigido | As convenções de carga estão documentadas. O rótulo da barra do BSI passou a "em disciplinas OBR e TRA", e a do BCC usa o quadro-resumo. Os tipos aparecem literalmente (TRA, EXT), sem tradução. |
| P6 | Corrigido | `rotuloTermo: "serie-periodo"` é declarativo. A forma antiga, com função, continua aceita. |

**Acréscimo pedido:** quadro de disciplinas optativas também no BCC.

- **Fonte:** o PDF do currículo 2105 não publica a relação de optativas. O quadro do BCC mostra
  a exigência do quadro-resumo (8 créditos / 120 h), as vagas Optativa I (7º termo) e Optativa
  II (8º termo), e as optativas ofertadas no 1º semestre de 2026, conforme os PDFs de horário
  (49203 e 49187).
- **Aviso:** o quadro informa que a relação completa será incluída quando publicada.
- **BSI:** a lista virou tabela, com coluna de tipo (OPT/EXT).

**Decisões de 30/09/2026:** a 4609 passa a "Álgebra Linear" (correção autorizada da falha de
acento do PDF), e a 4652 fica confirmada como carga de extensão.

Resultado após as correções: validação de dados **1.916/1.916**; testes em navegador **37/37**.

## 8. Como reproduzir

```
node testes/validar-dados.mjs              # sem dependências
npm i -D playwright && npx playwright install chromium
node testes/e2e.mjs
```

Os resultados da primeira execução (antes das correções) estão no anexo abaixo.

## Anexo — saída dos testes antes das correções
```
validar-dados.mjs
  FALHA  4742: nome "Metodologia da Pesquisa Científica" ≠ documento "Metodologia da Pesquisa"
  FALHA  DPA001: carga ch 0/ext 75 ≠ documento ch 75/ext 0
  1527/1529 verificações aprovadas, 2 falha(s).

e2e.mjs
  OK    T01-bcc  carrega sem erros de script nem avisos de dados
  OK    T02-bcc  cada aresta liga a borda do cartão de origem à do destino
  OK    T03-bcc  destaque da seleção = fecho transitivo calculado (todas as disciplinas)
  FALHA T04-bcc  impressão a partir da vista Árvore mostra a lista por termo
          → linhas visíveis na impressão: 0 de 46
  FALHA T05-bcc  impressão com busca ativa mostra a lista completa
          → linhas visíveis na impressão: 25 de 46
  OK    T06-bcc  funciona com localStorage bloqueado (lança exceção)
  OK    T07-bcc  link profundo #d=<código> abre com a disciplina selecionada; código inválido não quebra
  FALHA T08-bcc  foco do teclado é preservado após clicar em disciplina do painel
          → foco voltou para <body> (usuário de teclado perde a posição)
  FALHA T09-bcc  estrutura ARIA: role=list contém apenas listitem
          → 8 filhos inválidos dentro de role=list
  OK    T10-bcc  busca ignora acentos, Enter seleciona o 1º resultado, Esc limpa
  OK    T11-bcc  mobile 390 px: sem rolagem horizontal da página
  FALHA T12-bcc  dimming consistente: seleção + simulação escurecem igualmente os cartões fora da cadeia
          → opacidades diferentes fora da cadeia: 0.26, 0.55
  OK    T01-bsi  carrega sem erros de script nem avisos de dados
  OK    T02-bsi  cada aresta liga a borda do cartão de origem à do destino
  OK    T03-bsi  destaque da seleção = fecho transitivo calculado (todas as disciplinas)
  FALHA T04-bsi  impressão a partir da vista Árvore mostra a lista por termo
          → linhas visíveis na impressão: 0 de 38
  FALHA T05-bsi  impressão com busca ativa mostra a lista completa
          → linhas visíveis na impressão: 20 de 38
  OK    T06-bsi  funciona com localStorage bloqueado (lança exceção)
  OK    T07-bsi  link profundo #d=<código> abre com a disciplina selecionada; código inválido não quebra
  FALHA T08-bsi  foco do teclado é preservado após clicar em disciplina do painel
          → foco voltou para <body> (usuário de teclado perde a posição)
  FALHA T09-bsi  estrutura ARIA: role=list contém apenas listitem
          → 8 filhos inválidos dentro de role=list
  OK    T10-bsi  busca ignora acentos, Enter seleciona o 1º resultado, Esc limpa
  OK    T11-bsi  mobile 390 px: sem rolagem horizontal da página
  FALHA T12-bsi  dimming consistente: seleção + simulação escurecem igualmente os cartões fora da cadeia
          → opacidades diferentes fora da cadeia: 0.26, 0.55
  OK    T13-bcc  regra do TCC (70%): 4650 fica apta exatamente ao atingir 1.869 h obrigatórias
  FALHA T14      iframe da prévia encolhe quando o conteúdo diminui
          → árvore 2835px → lista 5130px → árvore 5130px
  OK    T15      duas instâncias na mesma página: ids únicos e ambas funcionais
  FALHA T16      montagem tardia (conteúdo injetado depois do carregamento, como em SPA)
          → elemento inserido após o carregamento não é montado (não há API pública de reinicialização nem observador)
  OK    T17      dados com HTML são escapados (sem injeção)
  FALHA T18      hash pré-existente não relacionado é preservado ao abrir a página
          → hash "#topo" foi apagado (ficou "")
  FALHA T19-bcc  co-requisito: disciplina não fica 'apta' se o co-requisito também não puder ser cursado
          → POO aparece 'apta para matrícula' embora seu co-requisito (EDI) esteja bloqueado
  FALHA T20      altura fixa sugerida no README (sem script) comporta o conteúdo no celular
          → bcc: conteúdo 9342px > 2200px; bsi: conteúdo 11239px > 2900px
  
  17/32 testes aprovados.
```
