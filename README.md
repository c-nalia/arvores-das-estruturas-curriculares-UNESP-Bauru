# Árvore de Grade — Departamento de Computação · FC/Unesp Bauru

Ferramenta de consulta às matrizes curriculares dos cursos de graduação, com as relações de
pré-requisito e co-requisito entre as disciplinas. Nesta versão estão implementados:

| Curso | Currículo | Vigência | Pasta |
|---|---|---|---|
| Bacharelado em Ciência da Computação (BCC) | 2105 | ingressantes a partir de 2023 | `bcc/` |
| Bacharelado em Sistemas de Informação (BSI) | 2804 | ingressantes a partir de 2023 | `bsi/` |

Funcionalidades:

- árvore por termo, com destaque da cadeia de pré-requisitos e das disciplinas dependentes;
- painel com ementa (quando publicada), pré-requisitos, co-requisitos e dependentes;
- busca por nome ou código;
- lista por termo: é a visualização acessível e a que se imprime, e é o padrão em telas estreitas;
- simulação de percurso, com as disciplinas aptas para matrícula, os co-requisitos, o requisito
  percentual do TCC do BCC e aviso de marcações inconsistentes;
- quadro de disciplinas optativas nos dois cursos;
- quadro-resumo da integralização (BCC).

**Regra de fidelidade.** Nomes, códigos, cargas, tipos, requisitos e textos são transcritos
literalmente dos documentos oficiais, inclusive grafias que pareçam incorretas. A única exceção é
uma correção autorizada e registrada em `testes/referencia/` (hoje, apenas a 4609). Correções de nome
devem ser feitas primeiro na fonte oficial e só depois nos dados. `testes/validar-dados.mjs`
compara os dados, caractere a caractere, com transcrições independentes dessas fontes.

---

## 1. Estrutura de pastas

```
arvore-de-grade/
├── index.html                  página de avaliação (lista os cursos) — não publicar
├── README.md
├── assets/
│   ├── arvore-grade.js         componente (sem dependências)
│   ├── arvore-grade.css        estilos, todos escopados em .ag
│   └── previa-portal.css       SOMENTE pré-visualização
├── bcc/
│   ├── dados-bcc-2105.js       dados do currículo 2105
│   ├── index.html              página da árvore (autônoma ou dentro de iframe)
│   └── previa-no-portal.html   pré-visualização no leiaute do portal — não publicar
├── bsi/
│   ├── dados-bsi-2804.js
│   ├── index.html
│   └── previa-no-portal.html
├── testes/
│   ├── validar-dados.mjs       integridade e fidelidade dos dados (Node, sem dependências)
│   ├── e2e.mjs                 testes em navegador (Playwright)
│   └── referencia/             transcrições independentes das fontes oficiais
└── revisao/
    └── relatorio-de-revisao.md achados da revisão técnica e situação de cada um
```

**O que publicar:** `assets/arvore-grade.js`, `assets/arvore-grade.css`, `bcc/index.html`,
`bcc/dados-bcc-2105.js`, `bsi/index.html` e `bsi/dados-bsi-2804.js`. Os demais arquivos servem à
avaliação e à manutenção.

## 2. Publicação no Portal Unesp

As páginas de curso do portal são rotas `#!/…` de uma aplicação AngularJS (Portal Unesp 2.9).
Endereços propostos:

- `https://www.fc.unesp.br/#!/departamentos/computacao/cursos-de-graduao/bacharelado-em-ciencia-da-computacao/arvore-de-grade/`
- `https://www.fc.unesp.br/#!/departamentos/computacao/cursos-de-graduao/bacharelado-em-sistemas-de-informacao/arvore-de-grade/`

### Opção A — iframe (recomendada)

1. Enviar os arquivos listados acima para a área de arquivos do site, mantendo a estrutura de
   pastas. Exemplo: `https://www.fc.unesp.br/Home/Departamentos/Computacao/arvore-de-grade/`,
   o mesmo local dos PDFs de currículo. A viabilidade de hospedar HTML nessa área deve ser
   confirmada com a equipe do portal.
2. Criar a página "Árvore de grade" no menu lateral de cada curso.
3. Inserir no conteúdo da página:

```html
<iframe class="arvore-grade"
        src="/Home/Departamentos/Computacao/arvore-de-grade/bcc/index.html?embed=1"
        title="Árvore de pré-requisitos do Bacharelado em Ciência da Computação"
        style="display:block;width:100%;height:85vh;min-height:640px;border:0"></iframe>
<p><a href="/Home/Departamentos/Computacao/arvore-de-grade/bcc/index.html" target="_blank">Abrir a árvore em página própria</a></p>
```

`?embed=1` oculta o título interno, pois a página do portal já exibe o seu. Com altura em `vh`,
o conteúdo rola dentro do quadro em qualquer tamanho de tela. O link abaixo do quadro atende quem
prefere a página inteira, sobretudo no celular.

**Ajuste automático de altura (opcional).** Se o portal permitir scripts no *modelo* da página
(e não apenas no conteúdo editável), a altura do iframe pode acompanhar o conteúdo. Nesse caso,
use `style="…;height:auto;min-height:640px"` e o script abaixo:

```html
<script>
  window.addEventListener("message", function (e) {
    if (!e.data || e.data.tipo !== "arvore-grade:altura") return;
    document.querySelectorAll("iframe.arvore-grade").forEach(function (f) {
      if (f.contentWindow === e.source) f.style.height = e.data.altura + "px";
    });
  });
</script>
```

O componente informa a altura real do conteúdo, que aumenta e diminui conforme a vista, a
seleção e a simulação.

Um `<script>` colocado no conteúdo de uma página AngularJS **não é executado**. Por isso a altura
em `vh` é o padrão.

### Opção B — incorporação direta (depende de acesso ao modelo do portal)

Só é viável se o arquivo JavaScript puder ser carregado pelo modelo do site. O mesmo vale para o
script da Opção A: scripts inseridos no conteúdo editável não rodam. Nesse cenário:

```html
<link rel="stylesheet" href="/Home/Departamentos/Computacao/arvore-de-grade/assets/arvore-grade.css">
<script src="/Home/Departamentos/Computacao/arvore-de-grade/assets/arvore-grade.js"></script>
<script src="/Home/Departamentos/Computacao/arvore-de-grade/bcc/dados-bcc-2105.js"></script>
```

No conteúdo da página, basta então `<div data-arvore-grade="bcc-2105" data-titulo="nao"></div>`.
O componente observa o documento e monta o elemento sempre que a rota `#!` o insere, inclusive
ao navegar entre páginas. Ele também não altera o endereço em rotas `#!`. Os estilos são
escopados em `.ag`, mas o CSS global do portal (Bootstrap) pode interferir. Por isso a Opção A
continua preferível.

### Opção C — link direto

`bcc/index.html` e `bsi/index.html` funcionam como páginas autônomas e aceitam `#d=<código>` para
abrir com uma disciplina selecionada (ex.: `bcc/index.html#d=4617`). Âncoras de outro tipo são
preservadas.

### Pré-visualização

`bcc/previa-no-portal.html` e `bsi/previa-no-portal.html` mostram a ferramenta dentro de uma
reprodução simplificada do leiaute do portal. O menu lateral usa os itens e endereços reais de
cada curso. As páginas trazem aviso de que não são oficiais e um espaço reservado no lugar do
logotipo. **Não publicar.**

## 3. Identidade visual

Valores medidos em www.fc.unesp.br (setembro/2026):

| Elemento | Valor no portal | Uso na ferramenta |
|---|---|---|
| Fonte | Raleway | toda a interface, com algarismos alinhados e tabulares |
| Azul institucional | `#1e3b50` | títulos, cabeçalhos de termo, cadeia de pré-requisitos |
| Ciano | `#00acfa` | filetes e disciplinas dependentes; em texto usa-se `#0070a6` (contraste AA) |
| Cinza de menu | `#f5f5f5` | ficha do curso, cabeçalhos de tabela |
| Texto | `#1a1a1a` | corpo; texto secundário `#4d4d4d` e `#5f6871` |

Não há modo escuro: o portal é exclusivamente claro e a ferramenta acompanha a página hospedeira.

## 4. Acessibilidade

- **Teclado:** toda a interface é operável por teclado (Tab, Enter/Espaço; Esc limpa a seleção
  ou a busca). Ao escolher uma disciplina no painel, o foco vai para o cartão correspondente.
  Na lista por termo, vai para o título do painel.
- **Não depende só de cor:** a relação de cada cartão com a disciplina selecionada é informada
  também em texto ("pré-requisito direto", "requer esta disciplina", "co-requisito").
- **Leitor de tela:**
  - a lista por termo apresenta o mesmo conteúdo em tabelas;
  - cada termo é uma lista rotulada pelo seu cabeçalho;
  - a seleção é anunciada numa região discreta ("Selecionada: … N disciplinas anteriores…");
  - a busca anuncia o número de resultados.
- **Contraste:** o texto tem ≥ 4,5:1 em todos os fundos usados. Contornos de campos, caixas de
  seleção e arestas do grafo têm ≥ 3:1. Os cartões fora da cadeia selecionada ficam
  esmaecidos de propósito, para destacar a cadeia; a mesma informação está disponível, com
  contraste pleno, na lista por termo.
- **Movimento:** `prefers-reduced-motion` é respeitado.
- **Impressão:** gera a lista por termo completa, independentemente da vista ou da busca ativas.

## 5. Formato dos dados

Cada curso tem um arquivo `dados-<curso>-<currículo>.js`. Os campos espelham as colunas do
documento-fonte: o que a fonte não traz, o arquivo não inventa.

```js
ArvoreGrade.registrar({
  id: "xxx-0000",                 // único; é o valor de data-arvore-grade
  sigla: "XXX",
  curso: "Nome completo do curso",
  curriculo: "0000",
  vigencia: "Ingressantes a partir de 20XX",
  atualizadoEm: "AAAA-MM-DD",     // data da última conferência
  fonte:   { titulo: "...", url: "..." },                 // documento oficial
  contato: { titulo: "Conselho de Curso", url: "..." },   // página do Conselho
  creditosNoDocumento: true,      // exibe créditos (= horas ÷ 15) só se a fonte os imprime
  tiposNoDocumento: true,         // exibe o tipo (OBR/TRA/…) só se a fonte o informa
  rotuloTermo: "serie-periodo",   // opcional: "Série x · Período y" sob cada termo
  quadroResumo: { linhas: [["Componente", créditos, horas], ...], total: [créditos, horas] },
  regras: { "CÓDIGO": { tipo: "percentualObrigatorias", valor: 0.70, texto: "texto literal" } },
  disciplinas: [
    { c: "4600", t: 1, n: "Cálculo I", ch: 60, tipo: "OBR", d: "MAT",
      pre: ["..."], co: ["..."], aceu: 0, ementa: "...", classificacao: "extensao" }
  ],
  optativas: {
    fonte: { titulo: "...", url: "..." },
    lista: [ { c: "4552", n: "...", ch: 60, tipo: "OPT", pre: ["..."] } ],
    oferta: { periodo: "1º semestre de 2026", fonte: {...},
              itens: [ { c: "49187", d: "COM", n: "...", cr: 4, termos: [5, 7] } ] }
  }
});
```

| Campo | Significado |
|---|---|
| `c` | código (vagas de optativa usam um identificador, ex.: `OPT-I`) |
| `t` | termo; no BSI, Série/Período em sequência (Série 1 · Período 1 = 1, …) |
| `n` | nome, **como no documento** |
| `ch` | carga horária, como no documento (coluna "Horas" ou "Carga Horária") |
| `aceu` | coluna "CH ACEU" do Sistema de Graduação (horas de extensão) |
| `tipo` | `OBR`, `TRA` (literal da fonte), ou `SLOT` para a linha "Optativa" da matriz |
| `d` | departamento, só quando a fonte informa |
| `pre` / `co` | códigos de pré-requisitos e co-requisitos |
| `ementa` | ementa publicada (opcional) |
| `classificacao` | `"extensao"`: fica fora da soma das obrigatórias na simulação, sem mudar a exibição |

**Convenções de carga.**

- **Cabeçalho de cada termo:** soma o que o documento lista no termo, incluindo vagas de optativa
  e CH ACEU.
- **Barra da simulação:** usa as horas obrigatórias do quadro-resumo, quando existe. Sem ele,
  soma as disciplinas OBR e TRA, excluindo as classificadas como extensão.

O componente registra no console qualquer requisito que aponte para código inexistente e qualquer
diferença entre a soma das obrigatórias e o quadro-resumo.

## 6. Testes

```
node testes/validar-dados.mjs                             # sem dependências
npm i -D playwright && npx playwright install chromium
node testes/e2e.mjs
```

- **`validar-dados.mjs`:** confere a integridade do grafo e compara nomes, cargas, tipos, termos,
  requisitos, texto da regra do TCC, quadro-resumo, ementas e oferta de optativas com as
  transcrições em `testes/referencia/`.
- **`e2e.mjs`:** cobre desenho das arestas, destaque da cadeia, impressão, simulação (inclusive
  co-requisitos e regra de 70%), altura do iframe, montagem tardia, teclado, ARIA, celular e
  injeção de HTML.

## 7. Privacidade e dependências externas

- Nenhum dado é enviado a servidores. A simulação e a preferência de visualização ficam apenas no
  `localStorage` do navegador do usuário.
- Sem ferramentas de análise ou rastreamento.
- Única dependência externa: a fonte Raleway via Google Fonts, a mesma usada pelo portal.

## 8. Manutenção

- **Mudança de currículo:** criar um novo arquivo de dados (ex.: `dados-bcc-2106.js`) em vez de
  editar o anterior, preservando a árvore dos ingressantes antigos.
- **Após cada conferência:** atualizar `atualizadoEm` e rodar `node testes/validar-dados.mjs`.
- **Oferta de optativas:** atualizar a cada semestre com os horários publicados.
