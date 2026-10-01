# Árvores de Grade dos cursos da UNESP de Bauru
OBS: Este não é um repositório institucional nem oficial. É uma base para uma sugestão 

Ferramenta de consulta às matrizes curriculares dos cursos de graduação do Câmpus de Bauru, com as
relações de pré-requisito e co-requisito entre as disciplinas. Esta versão cobre **20 cursos
(28 currículos)** das três unidades do câmpus:

| Unidade | Curso | Currículo(s) | Pasta |
|---|---|---|---|
| FC | Ciência da Computação | 2105 | `fc/bcc/` |
| FC | Sistemas de Informação | 2804 | `fc/bsi/` |
| FC | Ciências Biológicas | 2710 (bacharelado, integral) · 2711 (licenciatura, noturno) | `fc/ciencias-biologicas/` |
| FC | Educação Física | 2610 (integral) · 2611 (noturno), bacharelado e licenciatura | `fc/educacao-fisica/` |
| FC | Física | 1606: licenciatura · bacharelado em Física de Materiais · bacharelado em Física Computacional | `fc/fisica/` |
| FC | Matemática (licenciatura) | 1507 | `fc/matematica/` |
| FC | Meteorologia | 1702 | `fc/meteorologia/` |
| FC | Pedagogia | matriz 2023 | `fc/pedagogia/` |
| FC | Psicologia | 1212/1213 | `fc/psicologia/` |
| FC | Química | licenciatura · bacharelado em Química Tecnológica (matrizes 2023) | `fc/quimica/` |
| FAAC | Arquitetura e Urbanismo | ingressantes a partir de 2023 | `faac/arquitetura-e-urbanismo/` |
| FAAC | Artes Visuais | 2504 (núcleo básico) + bacharelado / licenciatura | `faac/artes-visuais/` |
| FAAC | Comunicação: Rádio, TV e Internet | 1104I | `faac/comunicacao-audiovisual/` |
| FAAC | Design | estrutura 2023 (ingressantes a partir de 2024) | `faac/design/` |
| FAAC | Jornalismo | 2205 | `faac/jornalismo/` |
| FAAC | Relações Públicas | ingressantes a partir de 2023 | `faac/relacoes-publicas/` |
| FEB | Engenharia Civil | 0104 | `feb/engenharia-civil/` |
| FEB | Engenharia de Produção | 4403 | `feb/engenharia-de-producao/` |
| FEB | Engenharia Elétrica | 0304 | `feb/engenharia-eletrica/` |
| FEB | Engenharia Mecânica | 0204 | `feb/engenharia-mecanica/` |

Funcionalidades:

- árvore por termo, com destaque da cadeia de pré-requisitos e das disciplinas dependentes;
- painel com ementa (quando publicada), pré-requisitos, co-requisitos e dependentes;
- busca por nome ou código;
- lista por termo: é a visualização acessível e a que se imprime, e é o padrão em telas estreitas;
- simulação de percurso, em horas, créditos ou componentes, conforme o que o documento informa;
- **seletor de currículos** quando o curso tem modalidades ou turnos (Física, Química, Biologia,
  Educação Física, Artes Visuais);
- **quadro de optativas** sempre que o documento traz a relação (BSI, Meteorologia, Rádio-TV) ou a
  exigência de carga optativa (BCC, Arquitetura, Artes Visuais, Engenharia Elétrica, Educação
  Física, Psicologia, Design, Física);
- quadro-resumo da integralização, quando o documento o apresenta;
- avisos sobre divergências do próprio documento (totais que não fecham, requisitos que não
  correspondem a nenhuma disciplina, nomes repetidos).

**Regras dos dados.**

1. **Nenhum número é alterado.** Códigos, créditos, cargas horárias, termos e tipos são os do
   documento oficial, mesmo quando o documento soma errado. Divergências viram aviso na página.
2. **Erros de grafia são corrigidos e registrados.** Cada correção (ex.: `lsostática` →
   `Isostática`, `Computacão` → `Computação`, `ll` → `II`) fica no campo `correcoes` do arquivo de
   dados, com o texto original e o motivo, e aparece no rodapé da página ("Grafias corrigidas em
   relação ao documento"). A tabela de correções está em `ferramentas/construir.py`.
3. **O que a fonte não traz, o arquivo não inventa.** Sem código no documento, a disciplina fica sem
   código; sem requisito, sem aresta; sem carga (Design), a árvore conta componentes.

---

## 1. Estrutura de pastas

```
├── index.html                    página de avaliação (lista os 20 cursos) — não publicar
├── README.md
├── assets/
│   ├── arvore-grade.js           componente (sem dependências)
│   ├── arvore-grade.css          estilos, todos escopados em .ag
│   └── previa-portal.css         SOMENTE pré-visualização
├── fc/   faac/   feb/            uma pasta por curso:
│   └── <curso>/
│       ├── dados-<id>.js         dados de cada currículo
│       ├── index.html            página da árvore (autônoma ou dentro de iframe)
│       └── previa-no-portal.html só BCC e BSI — pré-visualização, não publicar
├── ferramentas/
│   ├── construir.py              gera os dados e as páginas a partir de "planos de ensino/"
│   ├── fontes_sg.py              leitura dos CSV/PDF do Sistema de Graduação
│   ├── transcricoes.py           matrizes publicadas como imagem ou tabela sem códigos
│   └── fontes.json               endereço oficial de cada documento
├── planos de ensino/             documentos oficiais baixados (fonte de tudo)
└── testes/
    ├── validar-dados.mjs         integridade e fidelidade dos dados (Node, sem dependências)
    ├── conferir_fontes.py        confere os dados gerados, número a número, com as fontes
    ├── e2e.mjs                   testes em navegador (Playwright)
    └── referencia/               transcrições independentes e totais por termo
```

**O que publicar:** `assets/arvore-grade.js`, `assets/arvore-grade.css` e, de cada curso,
`index.html` e os `dados-*.js` da pasta. O restante serve à avaliação e à manutenção.

**BCC e BSI** são mantidos à mão (foram conferidos linha a linha na revisão anterior).
**Os demais cursos são gerados** por `python3 ferramentas/construir.py`: não edite os `dados-*.js`
gerados; corrija a fonte, a transcrição ou a tabela de correções e gere de novo.

## 2. Publicação no Portal Unesp

As páginas de curso dos portais (www.fc, www.faac, www.feb) são rotas `#!/…` de uma aplicação
AngularJS (Portal Unesp 2.9). Cada curso ganha uma página "Árvore de grade" no seu menu, por
exemplo:

- `https://www.fc.unesp.br/#!/departamentos/computacao/cursos-de-graduao/bacharelado-em-ciencia-da-computacao/arvore-de-grade/`
- `https://www.feb.unesp.br/#!/graduacao/secao-de-graduacao/cursos-de-graduacao/engenharia-civil/arvore-de-grade/`

### Opção A — iframe (recomendada)

1. Enviar `assets/` e a pasta do curso para a área de arquivos do site, mantendo a estrutura
   (ex.: `https://www.fc.unesp.br/Home/arvore-de-grade/fc/bcc/`). A viabilidade de hospedar HTML
   nessa área deve ser confirmada com a equipe do portal. Um único local pode servir aos três
   portais.
2. Criar a página "Árvore de grade" no menu do curso.
3. Inserir no conteúdo da página (trocar o caminho do curso):

```html
<iframe class="arvore-grade"
        src="/Home/arvore-de-grade/fc/bcc/index.html?embed=1"
        title="Árvore de pré-requisitos do curso"
        style="display:block;width:100%;height:85vh;min-height:640px;border:0"></iframe>
<p><a href="/Home/arvore-de-grade/fc/bcc/index.html" target="_blank">Abrir a árvore em página própria</a></p>
```

`?embed=1` oculta o título interno. Em cursos com mais de um currículo, `?curriculo=<id>` abre
direto num deles (ex.: `fc/fisica/index.html?embed=1&curriculo=fisica-1606-computacional`), o que
permite que cada modalidade tenha sua própria página no portal.

**Ajuste automático de altura (opcional).** Se o portal permitir scripts no *modelo* da página
(não no conteúdo editável, onde scripts não rodam), a altura do iframe pode acompanhar o conteúdo:

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

### Opção B — incorporação direta (depende de acesso ao modelo do portal)

```html
<link rel="stylesheet" href="/Home/arvore-de-grade/assets/arvore-grade.css">
<script src="/Home/arvore-de-grade/assets/arvore-grade.js"></script>
<script src="/Home/arvore-de-grade/fc/fisica/dados-fisica-1606-licenciatura.js"></script>
<script src="/Home/arvore-de-grade/fc/fisica/dados-fisica-1606-materiais.js"></script>
```

No conteúdo: `<div data-arvore-grade="fisica-1606-licenciatura,fisica-1606-materiais" data-titulo="nao"></div>`.
Um id só monta um currículo; vários ids separados por vírgula mostram o seletor. O componente
monta o elemento sempre que a rota `#!` o insere e não altera o endereço em rotas `#!`.

### Opção C — link direto

Toda `index.html` funciona como página autônoma e aceita `#d=<código>` para abrir com uma
disciplina selecionada (ex.: `fc/bcc/index.html#d=4617`; em matrizes sem código, o identificador
é `termo.posição`, ex.: `#d=3.2`).

### Pré-visualização

`fc/bcc/previa-no-portal.html` e `fc/bsi/previa-no-portal.html` mostram a ferramenta dentro de uma
reprodução simplificada do leiaute do portal. **Não publicar.**

## 3. Identidade visual

Valores medidos em www.fc.unesp.br (setembro/2026), os mesmos dos portais da FAAC e da FEB:

| Elemento | Valor no portal | Uso na ferramenta |
|---|---|---|
| Fonte | Raleway | toda a interface, com algarismos alinhados e tabulares |
| Azul institucional | `#1e3b50` | títulos, cabeçalhos de termo, cadeia de pré-requisitos |
| Ciano | `#00acfa` | filetes e disciplinas dependentes; em texto usa-se `#0070a6` (contraste AA) |
| Cinza de menu | `#f5f5f5` | ficha do curso, cabeçalhos de tabela, avisos |
| Texto | `#1a1a1a` | corpo; texto secundário `#4d4d4d` e `#5f6871` |

## 4. Acessibilidade

- **Teclado:** toda a interface é operável por teclado (Tab, Enter/Espaço; Esc limpa a seleção
  ou a busca), inclusive o seletor de currículos.
- **Não depende só de cor:** a relação de cada cartão com a disciplina selecionada também é
  informada em texto.
- **Leitor de tela:** a lista por termo apresenta o mesmo conteúdo em tabelas; a seleção e a busca
  são anunciadas.
- **Contraste:** texto ≥ 4,5:1; contornos e arestas ≥ 3:1.
- **Impressão:** gera a lista por termo completa, com a lista de correções aberta.

## 5. Formato dos dados

```js
ArvoreGrade.registrar({
  id: "xxx-0000",                 // único; é o valor de data-arvore-grade
  sigla: "Nome curto",
  rotuloSeletor: "Licenciatura",  // texto do botão no seletor de currículos
  curso: "Nome completo do curso",
  curriculo: "0000",              // opcional (omitido quando o documento não informa)
  vigencia: "Ingressantes a partir de 20XX",
  unidade: "Faculdade de … · Câmpus de Bauru",
  atualizadoEm: "AAAA-MM-DD",
  fonte:   { titulo: "...", url: "..." },        // documento oficial
  pagina:  { titulo: "página do curso", url: "..." },
  contato: { titulo: "...", url: "..." },
  creditosNoDocumento: true,      // exibe créditos só se a fonte os imprime
  tiposNoDocumento: true,         // exibe o tipo (OBR/TRA/…) só se a fonte o informa
  rotuloTermo: "serie-periodo",   // ou "ano-semestre"
  semCarga: true,                 // a fonte não informa cargas: a árvore conta componentes
  quadroResumo: { titulo, cabecalho, colunas: ["Créditos", "Horas"], linhas: [[rótulo, ...valores]], total, nota },
  regras: { "CÓDIGO": { tipo: "percentualObrigatorias", valor: 0.70, texto: "texto literal" } },
  disciplinas: [
    { c: "4600", cod: "…", semCodigo: true, t: 1, n: "Cálculo I", ch: 60, cr: 4, aceu: 0, tipo: "OBR",
      d: "MAT", pre: ["..."], co: ["..."], preTexto: "...", coTexto: "...", anual: true,
      extras: [["Extensão", 2, "cr"]], ementa: "...", classificacao: "extensao", tipoDoc: "ACE" }
  ],
  optativas: { fonte, exigencia: ["texto"], nota, lista: [ { c, n, ch, cr, tipo: "OPT", d, pre, co } ], oferta },
  avisos: ["divergências e particularidades do documento"],
  correcoes: [ { cod, campo, de: "texto original", para: "texto corrigido", motivo } ]
});
```

| Campo | Significado |
|---|---|
| `c` / `cod` | identificador / código exibido. Sem código no documento: `semCodigo` e `c` = `termo.posição` |
| `t` | termo (Série/Período ou ano/semestre em sequência: 1º ano · 1º semestre = 1, …) |
| `ch` / `cr` | horas / créditos, como no documento (um ou outro, ou ambos) |
| `aceu` | coluna "CH ACEU" (horas de extensão) |
| `tipo` | `OBR`, `TRA`, `EST`, `OPT` (como no documento) ou `SLOT` (vaga de optativa da matriz) |
| `tipoDoc` | tipo literal quando não é um dos acima (ex.: `ACE`, `ACEU` na Arquitetura) |
| `pre` / `co` | requisitos que correspondem a disciplinas da matriz |
| `preTexto` / `coTexto` | requisitos citados que **não** correspondem a disciplina da matriz |
| `anual` | disciplina anual; aparece nos dois termos, como no documento |
| `extras` | colunas adicionais de carga (Psicologia: extraclasse e extensão) |

## 6. Gerar os dados

```
python3 ferramentas/construir.py
```

Requer Python 3 com `pdfplumber` e `pandas`, `pdftotext` (poppler) e, para os `.doc` da Educação
Física, LibreOffice (`soffice`). O script imprime, por currículo, quantos termos conferem com os
totais do documento, e lista cada correção de grafia e cada aviso.

**Fontes por tipo de documento:**

- **Sistema de Graduação (CSV da FAAC, PDF da FEB):** lidos automaticamente (`fontes_sg.py`).
- **PDF com tabela de texto (Psicologia, Pedagogia, Biologia, Física, Design):** transcritos em
  `transcricoes.py`, com as somas conferidas com os totais impressos.
- **Imagem (Química, Meteorologia):** transcritos em `transcricoes.py` a partir das imagens.
- **DOC (Educação Física):** convertidos pelo LibreOffice e lidos automaticamente.
- **CSV da página (Matemática):** lido automaticamente.

## 7. Divergências encontradas nos documentos

Mantidas como publicadas (os números não foram alterados) e exibidas como aviso na página de cada
curso:

- **Educação Física 2611 (bacharelado):** 4º termo soma 20 créditos e o documento diz 22; 5º soma
  22 e o documento diz 20. No quadro do 2610 (bacharelado), "147 Créditos – 2005 H/A" (147 × 15 = 2205).
- **Química:** a soma da matriz da licenciatura (3705 h) difere da carga declarada (3735 h).
- **Meteorologia:** dois códigos com o mesmo nome (7005 e 7050, "Energia e Sustentabilidade
  Ambiental"); a Micrometeorologia exige "Física II", que não existe na grade; a soma da grade
  (197 créditos) difere do total de obrigatórias da página (187).
- **Física:** "Química Geral II" tem 4 créditos na tabela e 2 no cabeçalho da ementa.
- **Psicologia:** duas disciplinas citam a si mesmas como co-requisito; os semestres dos estágios
  aparecem como "10 e 10", "11 e 10", "12 e 10"; um requisito cita "Processos Educativos" sem
  número; uma disciplina sem semestre informado; um pré-requisito no mesmo semestre.
- **Engenharia de Produção (2º e 5º termos) e Artes Visuais (8º termo):** o total impresso não
  inclui a CH ACEU, ao contrário dos demais termos.
- **Biologia 2711:** os co-requisitos das Metodologias e Práticas de Ensino são estágios que não
  constam da matriz.
- **Design:** o documento não informa cargas, códigos nem requisitos.
- **Relações Públicas, Arquitetura:** o documento não informa o número do currículo.

## 8. Testes

```
node testes/validar-dados.mjs                             # sem dependências
python3 testes/conferir_fontes.py                         # relê as fontes oficiais
npm i -D playwright && npx playwright install chromium
node testes/e2e.mjs
```

- **`validar-dados.mjs`:** integridade do grafo de todos os currículos, coerência das correções
  registradas, somas por termo × documento e, para BCC e BSI, comparação caractere a caractere com
  as transcrições em `testes/referencia/`.
- **`conferir_fontes.py`:** confere cada código (termo, carga, CH ACEU, tipo, requisitos) contra os
  CSV/PDF do Sistema de Graduação e cada disciplina transcrita contra a transcrição.
- **`e2e.mjs`:** arestas, destaque da cadeia e acessibilidade em todos os currículos; impressão,
  simulação, link profundo, teclado e iframe em BCC e BSI; seletor de currículos, modo créditos,
  modo componentes, correções e índice.

## 9. Privacidade e dependências externas

- Nenhum dado é enviado a servidores. A simulação e as preferências ficam apenas no `localStorage`
  do navegador.
- Sem ferramentas de análise ou rastreamento.
- Única dependência externa: a fonte Raleway via Google Fonts, a mesma usada pelos portais.

## 10. Manutenção

- **Mudança de currículo:** baixar o novo documento para `planos de ensino/`, ajustar
  `construir.py` (ou a transcrição) e gerar de novo, preservando o arquivo do currículo anterior.
- **Nova correção de grafia:** acrescentar à lista `CORRECOES` em `construir.py`; nunca editar o
  número de nada.
- **Após cada conferência:** atualizar `ATUALIZADO` em `construir.py` e rodar os três testes.
- **Oferta de optativas do BCC:** atualizar a cada semestre com os horários publicados.
