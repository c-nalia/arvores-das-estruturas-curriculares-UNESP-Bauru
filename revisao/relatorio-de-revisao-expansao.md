# Relatório de revisão — expansão da Árvore de Grade para os cursos de Bauru

**Versão revisada:** cópia de trabalho do repositório em 01/10/2026 (70 arquivos; conteúdo idêntico, arquivo a arquivo, ao que está na pasta do usuário — conferido por SHA-1), ainda sem commit sobre `47aa314`.
**Escopo:** 28 currículos de 20 cursos (FC, FAAC, FEB), 1.719 disciplinas/optativas, 63 correções de grafia, componente `assets/arvore-grade.js`, gerador `ferramentas/`, testes e documentação.
**Resultado:** **2 erros críticos, 7 altos, 5 médios, 5 baixos.** Nenhum número da grade foi alterado em relação aos documentos, salvo o requisito trocado da Engenharia de Produção (C1).

> **Recomendação:** não publicar antes de corrigir C1, C2, A1, A2, A3 e A4.

---

## 1. Como a revisão foi feita

Os testes do projeto (`validar-dados.mjs`, `conferir_fontes.py`, `e2e.mjs`) passam: 16.226/16.226, 6.250/6.250 e 173/173. Mas **dois deles comparam o gerador com ele mesmo**:

- `conferir_fontes.py` relê as fontes com o mesmo leitor que gerou os dados.
- As transcrições que ele usa são as mesmas do gerador.

Por isso esta revisão refez a leitura de cada documento **por um caminho diferente** e comparou com os dados:

| Cursos | Segunda leitura (independente do gerador) | Resultado |
|---|---|---|
| FAAC (6 cursos, 7 relações) | páginas **HTML** célula a célula com lxml (o gerador usa os CSV) | 0 diferenças em 322 linhas |
| FEB (4 cursos) | **transcrição visual** das 23 páginas a 200 dpi, às cegas, por dois revisores independentes | **1 requisito trocado (C1)**; o resto confere: 257 disciplinas, 207 requisitos, 4 regras percentuais |
| Arquitetura | anexo da **Resolução Unesp 123/2023** (documento legal citado como fonte) | **1 carga divergente entre fontes (A1)** |
| Meteorologia, Química, Psicologia, Pedagogia, Biologia (2), Design | **transcrição às cegas** das imagens/PDFs, sem acesso aos dados | 0 diferenças de número; **2 correções falsas (A2)** |
| Física (3 modalidades) | posição e **cor do texto** de cada disciplina no PDF (preto, azul, verde, roxo, laranja, vermelho) | confere com os dados |
| Educação Física (4) | `.doc` → **texto puro** (o gerador usa `.doc` → HTML) | 0 diferenças; o 4º/5º termo do 2611 bacharelado diverge no próprio documento, como já avisado |
| Matemática | página **HTML** × CSV × dados | 0 diferenças (49 disciplinas, anuais e requisitos) |
| BCC e BSI | PDFs do repositório × transcrições de referência | conferem (46 e 80 linhas) |
| Componente | 13 testes exploratórios novos em navegador (`revisao/exploratorio.mjs`) | **6 falhas** (C2, A5, A6, M1, M2, B1) |

Os scripts e as transcrições independentes estão em `revisao/` e podem ser reexecutados.

---

## 2. Erros críticos

### C1 — Engenharia de Produção: correquisito atribuído à disciplina errada

- **Onde:** `feb/engenharia-de-producao/dados-engenharia-de-producao-4403.js`
- **O que o documento diz:** "Correquisito: EP3206P23 – Gestão de Custos" pertence a **EP3207P23 – Projeto Integrado em Engenharia de Produção III (optativa)**, do 6º termo. A célula começa na pág. 3 e termina no topo da pág. 4, antes de "Total de Carga Horária: 450.0" (pdftotext, págs. 3–4).
- **O que os dados mostram:**
  - **DP4102P23 – Gestão de Pessoas**, do 7º termo, aparece com correquisito EP3206P23, que é falso.
  - EP3207P23 perde esse correquisito.
- **Efeito:** a árvore desenha uma aresta inexistente, e a simulação trata Gestão de Pessoas com uma condição que não existe.
- **Causa:** `ferramentas/fontes_sg.py` (`ler_pdf_sg`) liga cada bloco de requisitos ao registro mais próximo **na mesma página**. Linhas que continuam da página anterior caem no primeiro registro da página nova.
- **Correção proposta:** ligar ao último registro da página anterior todo bloco que vier antes do primeiro código da página e antes do "Total" do termo. Depois, regerar e conferir com `revisao/comparar_feb.py`.

### C2 — Seletor de currículos + iframe com ajuste de altura: a ferramenta some

- **Onde:** `assets/arvore-grade.js` (`montarSeletor` / `montar`)
- **Reprodução:** iframe com o script de altura do README (Opção A) → trocar de currículo uma vez.
- **Medição:** a instância antiga, já fora do documento, envia `altura: 0`. O iframe vai para **0 px**, e os cliques seguintes falham por tempo esgotado (`revisao/exploratorio.mjs`, X01).
  - Trace: `fisica-1606-materiais:2228` e logo depois `fisica-1606-licenciatura:0`.
- **Problema relacionado (X02):** cada troca deixa a instância anterior viva, com o ouvinte de `resize`, o ResizeObserver e o `postMessage`. Depois de 6 trocas, há 7 ouvintes de `resize`.
- **Correção proposta:** `montar` deve devolver uma função de desmontagem que remove ouvintes e observadores; `montarSeletor` a chama antes de montar o próximo currículo. Além disso, `avisarAltura` não deve enviar nada se `raiz.isConnected` for falso.

---

## 3. Erros altos

### A1 — Arquitetura e Urbanismo: números exibidos ≠ documento citado como fonte

- **Fonte indicada:** a página cita como "Documento oficial" a **Resolução Unesp 123/2023**. Os números exibidos, porém, vêm da relação do Sistema de Graduação, e as duas fontes divergem:

| Item | Resolução 123/2023 (anexo e art. 2º) | Página/SG (usada nos dados) |
|---|---|---|
| ARQ-E 56 Paisagismo V – Ecologia da Paisagem | **2 créditos (30 h)** | **60 h** |
| Disciplinas obrigatórias | 236 créditos = **3.540 h** | **3.570 h** |
| Total do curso | 280 créditos = **4.200 h** | **4.230 h** |

- As demais 68 disciplinas do anexo conferem com os dados (créditos × 15).
- **Proposta:** decidir com o Conselho de Curso qual fonte prevalece. Até lá, citar as duas fontes e exibir um aviso da divergência. Não alterar o número.

### A2 — Química: duas correções de grafia falsas

- **O que o arquivo diz:** os arquivos da Química registram a correção "Introdução à Metodologia da Pesquisa **Cientifica**" → "**Científica**", e o rodapé informa que o documento tinha o erro.
- **O que o documento diz:** na imagem a 400 dpi (págs. 3 e 5) está "**Científica**". A transcrição usada pelo gerador (`ferramentas/transcricoes.py`) leu errado.
- **Efeito:** o nome exibido está certo, mas a página atribui ao documento oficial um erro que ele não tem.
- **Proposta:** corrigir a transcrição e regerar. O registro de correções deve sumir dos dois currículos.

### A3 — FEB: quadros de integralização e exigência de optativas não incorporados

Os quatro PDFs da FEB trazem, em imagem, a tabela "Componentes curriculares da estrutura proposta" (conferida visualmente na Civil). O gerador lê só o texto e por isso a ignorou. Como o pedido incluía o quadro de optativas sempre que possível:

| Curso | Optativas exigidas no documento | Situação nos dados |
|---|---|---|
| Civil | 10 créditos (150 h) | sem quadro-resumo e sem exigência de optativas |
| Mecânica | 16 créditos (240 h) | sem quadro-resumo e sem exigência de optativas |
| Produção | 12 créditos (180 h) | sem quadro-resumo e sem exigência de optativas |
| Elétrica | 16 créditos (240 h) | só as duas linhas de texto; faltam estágio (165 h), TCC (60 h), ACEU (405 h) e o total (4.050 h) |

Valores completos em `revisao/transcricoes-independentes/feb-*.json`. Para a Civil: 225/3375, 10/150, 28/420, 11/165, 2/30, 1/15, total 277/4155.

### A4 — Número do currículo omitido, com aviso falso

As páginas oficiais informam o número do currículo, mas os dados dizem "O documento publicado não informa o número do currículo":

- **Relações Públicas:** "Ingressantes a partir de 2023 – **Estrutura 2402**"
- **Arquitetura e Urbanismo:** "**Estrutura 2011** – Resolução Unesp 123/2023"

### A5 — Psicologia: total da simulação inclui um estágio a mais

- **O documento:** "São contabilizadas apenas o referente a 3 opções de estágio", e o total é de 272 créditos.
- **A simulação:** soma os 4 programas e mostra "de **282** créditos".
- **O correto:** **264** créditos (210 nas disciplinas obrigatórias dos semestres 1–8 + 54 nos estágios). O percentual exibido fica subestimado.
- **Proposta:** marcar os estágios como "escolha 3 de 4" (campo novo, ex.: `grupo: {id, exigidos: 3}`) e contar só os exigidos.

### A6 — Simulação ignora requisitos que não correspondem a disciplinas da matriz

- **O problema:** disciplinas com `preTexto`/`coTexto` aparecem como "**apta para matrícula**" mesmo com um requisito que não pode ser verificado (X04).
- **Casos:**
  - Meteorologia 7034 (exige "Física II");
  - Psicologia "ACA: Educação Especial e Inclusiva";
  - as 5 Metodologias e Práticas de Ensino da Biologia 2711 (correquisitos de estágio).
- **Proposta:** novo estado "requisito a confirmar com o Conselho de Curso", em vez de "apta".

### A7 — Testes de fidelidade circulares

- **Limitação 1:** `testes/conferir_fontes.py` usa o mesmo leitor (`fontes_sg.py`) e as mesmas transcrições (`transcricoes.py`) do gerador. Por isso não detecta erro de leitura (não pegou C1) nem de transcrição (não pegou A2). O README promete o contrário ("relê as fontes oficiais").
- **Limitação 2:** `validar-dados.mjs` confere as somas por termo, mas compara com `verificacao.json`, que também é produzido pelo gerador.
- **Proposta:**
  - Incorporar a `testes/` as leituras independentes desta revisão: `revisao/segunda_leitura_sg.py`, `revisao/comparar_feb.py`, `revisao/comparar_independente.py` com `transcricoes-independentes/` e `revisao/comparar_edf.py`.
  - Corrigir a descrição no README.

### A8 — Física: requisitos e ementas do documento ausentes; aviso falso

*(Achado acrescentado em 01/10/2026, ao detalhar as correções por curso. Substitui a redação anterior do item M5.)*

- **Aviso falso:** o site diz que o "pré-requisito recomendado" aparece "em dois casos". O documento traz a expressão em cerca de 47 ementas (22 como "recomendado" e 25 como "recomentado").
- **Pré-requisitos formais ignorados:** 6 ementas trazem "Pré-requisito:" sem o "recomendado":
  - Introdução à Pesquisa em Ensino de Ciências ← Metodologias e Práticas de Ensino de Física I a IV;
  - cinco TCC ← "ver regulamento geral do TCC".
- **Ementas ausentes no site** embora existam no documento (falha na leitura do cabeçalho): Tecnologia da Comunicação…, Filosofia das Ciências, ES II, os TCC, CSADH, Libras, Cálculo Numérico I ("4credidos"), Estágio - I/II, Computação Quântica.
- **Erros do próprio documento** (para o Conselho de Curso): "recomentado" ×25, "xxx" ×5, "divido", "De a acordo", "bacharelada", "compões", "ultima", "Cálculo Básico" e "Cálculo I a V" (nomes que não existem na matriz), Ciências dos Materiais II recomenda a si mesma, "Física dos Materiais" × "de Materiais".
- **Detalhe por item:** `fc/fisica/Correções necessárias/`.

---

## 4. Erros médios

### M1 — Educação Física: TCC II repetido sem indicação de disciplina anual

- **O que aparece:** nos quatro currículos, "Trabalho de Conclusão de Curso II" aparece em dois termos seguidos: 7º/8º no 2610 e 9º/10º no 2611.
- **O que falta:**
  - não tem selo "anual" nem aviso;
  - o "A" que o documento traz na coluna Cód. (2610 licenciatura) foi descartado.
- **Efeito:** o aluno vê duas disciplinas com o mesmo nome.

### M2 — Busca não encontra o código como impresso no documento

Buscar "ART-E 01" ou "RTVI-E 35", como está no documento, dá **0 resultados** (X03). A busca compara com o identificador interno (`ART-E01`), não com o código exibido (`cod`). Isso afeta os 6 cursos da FAAC.

### M3 — Erros de grafia não corrigidos e critério desigual

- **Concordância não corrigida:** Psicologia "Fundamentos das Teorias **Sistêmica e Complexa**". O próprio documento grafa "Sistêmicas e Complexas" quando a cita como requisito.
- **Maiúsculas:** o gerador uniformizou "prescrição" → "Prescrição" na Educação Física, mas deixou:
  - "Cálculo Diferencial e Integral de **várias variáveis** II" e "Mecânica dos Fluidos para **atmosfera**" (Meteorologia);
  - "Antropologia **visual**" (Artes Visuais);
  - "Fisiopatologia… **hipertensão e cardiovascular**" (Educação Física).
- **Proposta:** definir o critério (só ortografia/acentuação/concordância, ou também maiúsculas) e aplicar a todos os cursos.

### M4 — Correções que alteram a forma do nome (pedem aprovação das coordenações)

Não são erros de digitação inequívocos, e sim escolhas de redação:

- "Ecologia Comunidades/Populações/Ecossistemas" → "Ecologia **de** …" (Biologia, 4 nomes);
- "Interação Biosfera Atmosfera" → "Biosfera**-**Atmosfera";
- "Tópicos Especiais Aprendizado…" → "Tópicos Especiais **em** Aprendizado…" (BSI);
- "Processos de Produção **e** do Conhecimento…" → sem o "e" (Educação Física);
- "História e Teorias **e** da Arquitetura" → sem o "e". A Resolução 123/2023 também grafa com o "e".

Ficam registradas no rodapé, mas convém o aval de cada coordenação.

### M5 — Física: "pré-requisito recomendado" omitido

Reclassificado e ampliado: ver **A8**. A afirmação anterior deste item ("duas disciplinas") estava errada.

---

## 5. Erros baixos

- **B1:** Design (sem carga) — a lista por termo mantém a coluna "Carga" vazia (X12).
- **B2:** FEB — a unidade aparece como "Faculdade de Engenharia de Bauru · Câmpus de Bauru" (redundante).
- **B3:** Elétrica — a regra "Percentual do Curso Exigido: 60%" usa como base a carga da grade (3.180 h → 1.908 h). O documento não define a base (total do curso = 4.050 h com ACEU). Documentar a premissa no aviso.
- **B4:** README — as seções 1, 7 e 8 repetem as afirmações desmentidas em A3, A4 e A7.
- **B5:** a regra percentual compara horas concluídas só de OBR com uma base que inclui TRA/EST. Hoje não afeta nenhum curso, mas fica inconsistente se um curso com TRA/EST tiver regra percentual.

---

## 6. Particularidades dos documentos oficiais (para os Conselhos de Curso)

Encontradas nas leituras independentes. Os dados seguem o documento; algumas ainda não aparecem como aviso:

| Curso | Particularidade | Aviso na página? |
|---|---|---|
| Meteorologia | 7005 e 7050 com o mesmo nome; o 7005 provavelmente é "Física II", exigida pela 7034 | sim |
| Meteorologia | 7047 Laboratório de Física II com departamento DM e 4 cr / 60 h; os Laboratórios I e III têm 2 cr / 30 h | **não** |
| Psicologia | "Psicologia Social I" e "Psicologia Organizacional e do Trabalho II" só têm texto na coluna Correquisitos; pelo conteúdo, parecem pré-requisitos | **não** |
| Psicologia | correquisitos que apontam para a própria disciplina; semestres "10 e 10", "11 e 10", "12 e 10" | sim |
| Arquitetura | 60 h × 30 h em Paisagismo V (A1) | **não** |
| Química | soma da Licenciatura 3.705 h × 3.735 h declaradas (confirmada às cegas) | sim |
| Educação Física 2611 (bacharelado) | totais do 4º e 5º termos trocados | sim |
| Biologia | "Disciplinas Obrigatórias*" com asterisco sem nota | **não** |
| Design | o título diz 2023; os metadados do PDF dizem "Matriz Curricular 2024" | **não** |
| Mecânica (PDF) | o cabeçalho da pág. 1 traz um nome de usuário do sistema ("amanda.peron") | — (não reproduzido) |

---

## 7. O que foi conferido e está correto

- **FAAC:** os 6 cursos conferem com as páginas HTML: termo, nome, carga, CH ACEU, tipo e todo código citado em requisitos (322 linhas).
- **FEB:** fora C1, termos, cargas, tipos, 207 requisitos e as 4 regras percentuais da Elétrica conferem com a leitura visual. Os nomes com "l" no lugar de "I" estão de fato assim na camada de texto, então as correções estão certas.
- **Imagens e PDFs sem códigos:** Biologia (2710 e 2711), Pedagogia, Psicologia, Meteorologia, Química e Design conferem com as transcrições às cegas em nome, termo, créditos, horas, anuais, requisitos e colunas extraclasse/extensão.
- **Física:** a distribuição por modalidade confere com a posição e a cor do texto no PDF.
- **Educação Física, Matemática, BCC e BSI:** conferem pelas segundas leituras.
- **Somas por termo:** batem com os totais impressos, exceto nos casos já avisados.
- **Componente:** sem erros de script ao percorrer todos os currículos. Seletor sem rolagem horizontal a 360 px, oculto na impressão e sem alterar o endereço em rotas `#!` do portal (X07, X09, X10, X11).

## 8. Ordem sugerida de correção

1. **C1** (leitor de PDF) e **A2** (transcrição da Química) → regerar → rodar `revisao/comparar_feb.py` e `revisao/comparar_independente.py`, que devem dar 0 diferenças, salvo o alias documentado da Psicologia.
2. **C2** (desmontagem de instâncias) → rodar `revisao/exploratorio.mjs`.
3. **A1, A3, A4** (fontes e quadros) → validar os textos com as coordenações.
4. **A5, A6, M1, M2** (simulação e busca).
5. **A7** (testes independentes em `testes/`) e README.

---

## 9. Arquivos "Correções necessárias" por curso

Gerados por `revisao/gerar_correcoes.py` em 01/10/2026: 197 arquivos em 21 pastas (20 cursos + `revisao/gerais-do-projeto`). Cada pasta de curso tem `Correções necessárias.txt` (índice) e a subpasta `Correções necessárias/` com um arquivo por item. Incluem achados menores não listados acima (erros de digitação dos documentos oficiais, rótulos, totais por termo). São arquivos de trabalho: não publicar no portal.
