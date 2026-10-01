#!/usr/bin/env python3
"""Gera, na pasta de cada curso, o arquivo "Correções necessárias.txt" (índice) e a pasta
"Correções necessárias/" com UM arquivo de texto por correção, a partir dos achados da revisão
(revisao/relatorio-de-revisao-expansao.md).

Uso: python3 revisao/gerar_correcoes.py [pasta-de-saida]   (padrão: a raiz do projeto)

Cada item diz ONDE corrigir:
  SITE       — arquivos deste projeto (dados, gerador, componente). Responsável: quem mantém o site.
  DOCUMENTO  — documento oficial do curso. Responsável: Conselho de Curso / Seção de Graduação.
  DECISÃO    — depende de uma escolha da coordenação antes de qualquer alteração.
"""
import json, os, re, sys, glob, subprocess, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = sys.argv[1] if len(sys.argv) > 1 else RAIZ
ITENS = {}   # pasta -> lista de dicts
ORDEM = {"CRÍTICA": 0, "ALTA": 1, "MÉDIA": 2, "BAIXA": 3}


def add(pasta, grav, onde, titulo, errado, evidencia, correcao, ref=""):
    ITENS.setdefault(pasta, []).append(dict(grav=grav, onde=onde, titulo=titulo, errado=errado, evidencia=evidencia, correcao=correcao, ref=ref))


def dados(p):
    if "/bcc/" in p or "/bsi/" in p:
        js = 'const vm=require("vm"),fs=require("fs");let D;vm.runInNewContext(fs.readFileSync(process.argv[1],"utf8"),{ArvoreGrade:{registrar:x=>D=x}});console.log(JSON.stringify(D))'
        return json.loads(subprocess.run(["node", "-e", js, os.path.join(RAIZ, p)], capture_output=True, text=True).stdout)
    t = open(os.path.join(RAIZ, p), encoding="utf-8").read()
    return json.loads(t[t.index("registrar(") + 10: t.rindex(");")])


# ------------------------------------------------------------------------------------------
# 1) Grafias já corrigidas no site: o erro continua no documento oficial (um arquivo por grafia)
# ------------------------------------------------------------------------------------------
FALSAS = {"Introdução à Metodologia da Pesquisa Cientifica"}           # tratadas à parte (A2)
DECISAO = ("Ecologia ", "Interação Biosfera", "Tópicos Especiais Aprendizado", "Processos de Produção e do", "História e Teorias e da")
vistos = {}
for arq in sorted(glob.glob(os.path.join(RAIZ, "f*", "*", "dados-*.js"))):
    rel = os.path.relpath(arq, RAIZ)
    pasta = os.path.dirname(rel)
    D = dados(rel)
    for c in D.get("correcoes", []):
        if c["de"] in FALSAS:
            continue
        chave = (pasta, c["de"], c["para"], c.get("campo"))
        vistos.setdefault(chave, {"curr": [], "c": c})["curr"].append(D.get("rotuloSeletor") or D["curso"])
for (pasta, de, para, campo), v in vistos.items():
    c = v["c"]
    dec = any(de.startswith(x) or x in de for x in DECISAO)
    onde_doc = "tabela de ementas da página do curso (Estrutura curricular)" if campo == "ementa" else "documento oficial da matriz curricular / cadastro da disciplina no Sistema de Graduação"
    alvo = f"ementa da disciplina {c.get('cod')}" if campo == "ementa" else (f"nome da disciplina {c['cod']}" if c.get("cod") else "nome da disciplina")
    add(pasta, "BAIXA", "DECISÃO" if dec else "DOCUMENTO",
        f"Grafia no documento - {de[:60]}",
        f"No {onde_doc}, o {alvo} está grafado:\n    “{de}”\nO site já exibe a forma corrigida:\n    “{para}”\nMotivo da correção: {c['motivo']}.",
        f"Currículo(s): {'; '.join(v['curr'])}.\nRegistro da correção: campo \"correcoes\" do arquivo de dados; aparece no rodapé da página (“Grafias corrigidas em relação ao documento”).",
        ("ANTES de manter a correção, a coordenação precisa confirmar que a forma corrigida é a desejada: esta alteração muda a redação do nome, não é só um erro de digitação. "
         if dec else "") + "Corrigir a grafia no documento oficial (ou no cadastro da disciplina). Depois disso, remover o registro em \"correcoes\" no site, para que o rodapé deixe de apontar a diferença.",
        "Relatório, seção 4 (M4)" if dec else "Relatório, seção 1 (correções registradas)")

# ------------------------------------------------------------------------------------------
# 2) Itens gerais do componente que afetam cursos específicos
# ------------------------------------------------------------------------------------------
for pasta in ("fc/ciencias-biologicas", "fc/educacao-fisica", "fc/fisica", "fc/quimica", "faac/artes-visuais"):
    add(pasta, "CRÍTICA", "SITE", "Iframe fica com altura zero ao trocar de currículo",
        "Esta página tem seletor de currículos. Quando ela está dentro de um iframe com o script de ajuste automático de altura (README, Opção A), basta trocar de currículo uma vez: a árvore anterior, já removida da tela, envia “altura: 0” e o iframe encolhe para 0 px. A ferramenta some da página do portal.",
        "revisao/exploratorio.mjs, teste X01. Mensagens registradas: “fisica-1606-materiais:2228” seguida de “fisica-1606-licenciatura:0”. Os cliques seguintes falham porque o iframe está com 0 px.",
        "Em assets/arvore-grade.js: (1) a função montar deve devolver uma rotina de desmontagem que remova ouvintes e observadores; (2) montarSeletor deve chamá-la antes de montar o currículo seguinte; (3) avisarAltura não deve enviar nada quando raiz.isConnected for falso.",
        "Relatório, C2")
    add(pasta, "MÉDIA", "SITE", "Instâncias antigas continuam ativas a cada troca de currículo",
        "A cada troca no seletor, a árvore anterior não é desmontada: o ouvinte de “resize”, o ResizeObserver e o envio de altura continuam ativos. O consumo cresce a cada troca e é a causa do erro do iframe com altura zero.",
        "revisao/exploratorio.mjs, teste X02: ouvintes de “resize” passam de 1 para 7 depois de 6 trocas.",
        "Mesma correção do item do iframe: desmontar a instância anterior (remover ouvintes e desconectar o ResizeObserver) antes de montar a nova.",
        "Relatório, C2")

for pasta, ex in (("faac/artes-visuais", "ART-E 01"), ("faac/comunicacao-audiovisual", "RTVI-E 35"), ("faac/relacoes-publicas", "RP-E 01"),
                  ("faac/arquitetura-e-urbanismo", "ARQ-E 56"), ("faac/jornalismo", "JOR-E 01")):
    add(pasta, "MÉDIA", "SITE", "Busca não encontra o código como está no documento",
        f"Digitar o código da disciplina como ele aparece no documento e no cartão (com espaço, ex.: “{ex}”) não encontra nada. A busca compara com o identificador interno, sem espaço (“{ex.replace(' ', '')}”), e ignora o código exibido.",
        "revisao/exploratorio.mjs, teste X03: “ART-E 01” retorna 0 disciplinas.",
        "Em assets/arvore-grade.js, função aplicarBusca: comparar também com o campo “cod” (código exibido), ignorando espaços e hifens.",
        "Relatório, M2")

for pasta in ("feb/engenharia-civil", "feb/engenharia-eletrica", "feb/engenharia-mecanica", "feb/engenharia-de-producao"):
    add(pasta, "BAIXA", "SITE", "Nome da unidade redundante",
        "A ficha do curso mostra a unidade como “Faculdade de Engenharia de Bauru · Câmpus de Bauru”: “de Bauru” aparece duas vezes.",
        "Campo “unidade” do arquivo de dados; definido em ferramentas/construir.py (UNIDADES[\"FEB\"]).",
        "Usar “Faculdade de Engenharia · Câmpus de Bauru” (ou “Faculdade de Engenharia de Bauru (FEB)”) e regerar.",
        "Relatório, B2")

# ------------------------------------------------------------------------------------------
# 3) Itens por curso
# ------------------------------------------------------------------------------------------
# ---- FEB · Engenharia de Produção
P = "feb/engenharia-de-producao"
add(P, "CRÍTICA", "SITE", "Correquisito de Gestão de Custos atribuído à disciplina errada",
    "No documento, “Correquisito: EP3206P23 - Gestão de Custos” pertence a EP3207P23 - Projeto Integrado em Engenharia de Produção III (optativa), do 6º termo.\nNo site, esse correquisito aparece em DP4102P23 - Gestão de Pessoas (7º termo), que não tem requisito nenhum no documento. E EP3207P23 fica sem ele.",
    "PDF eproducao.pdf, fim da pág. 3 e topo da pág. 4: a linha “Correquisito: EP3206P23 - Gestão de Custos” vem antes de “Total de Carga Horária: 450.0” do 6º termo.\nConferido pela leitura visual independente (revisao/transcricoes-independentes/feb-producao.json) e por revisao/comparar_feb.py (2 diferenças).",
    "1) Em ferramentas/fontes_sg.py (ler_pdf_sg), ligar ao último registro da página anterior todo bloco de requisitos que vier antes do primeiro código da página e antes do “Total” do termo.\n2) Regerar (python3 ferramentas/construir.py).\n3) Conferir: EP3207P23 com 6 correquisitos (EP3201P23, EP3202P23, AG3203P23, EP3204P23, EP3205P23, EP3206P23) e DP4102P23 sem requisitos; revisao/comparar_feb.py deve dar 0 diferenças.",
    "Relatório, C1")
add(P, "ALTA", "SITE", "Quadro de integralização e exigência de optativas ausentes",
    "O documento traz, em imagem, a tabela “Componentes curriculares da estrutura proposta”. O site não mostra o quadro-resumo nem a carga de optativas exigida.",
    "Valores lidos da imagem (revisao/transcricoes-independentes/feb-producao.json): Disciplinas obrigatórias 214 créditos / 3.210 h; Disciplinas optativas 12 / 180; Atividades curriculares de Extensão Universitária 4 / 60; Estágio Supervisionado 12 / 180; Trabalho de Conclusão de Curso 2 / 30; Atividades Complementares 4 / 60; TOTAL 248 / 3.720.",
    "Transcrever a tabela em ferramentas/transcricoes.py, incluir como quadroResumo e como exigência de optativas (180 h) em construir.py e regerar. Conferir os valores na imagem antes de publicar.",
    "Relatório, A3")
add(P, "BAIXA", "DOCUMENTO", "Total do 2º termo não inclui a CH ACEU",
    "No 2º termo (Série 1 - Período 2), o “Total de Carga Horária: 354.0” soma só a coluna Carga Horária. As disciplinas do termo têm ainda 156 h de CH ACEU (12 + 6 + 6 + 120 + 12), que ficaram fora do total.",
    "eproducao.pdf, pág. 1. O site mantém os números do documento e mostra aviso.",
    "A Seção de Graduação deve confirmar se o total do termo deve incluir a CH ACEU (510 h) e corrigir o relatório do Sistema de Graduação.",
    "Relatório, seção 6")
add(P, "BAIXA", "DOCUMENTO", "Total do 5º termo não inclui a CH ACEU",
    "No 5º termo (Série 3 - Período 1), o “Total de Carga Horária: 384.0” soma só a coluna Carga Horária. As disciplinas do termo têm ainda 186 h de CH ACEU, que ficaram fora do total.",
    "eproducao.pdf, pág. 3. O site mantém os números do documento e mostra aviso.",
    "A Seção de Graduação deve confirmar se o total do termo deve incluir a CH ACEU (570 h) e corrigir o relatório do Sistema de Graduação.",
    "Relatório, seção 6")
add(P, "BAIXA", "DOCUMENTO", "AG3203P23 sem a coluna Duração preenchida",
    "A disciplina AG3203P23 - Ergonomia e Segurança do Trabalho está com a coluna “Duração” em branco; todas as outras trazem “Semestral”.",
    "eproducao.pdf, 6º termo (leitura visual independente, observações).",
    "Preencher a duração no cadastro da disciplina.", "Relatório, seção 6")
add(P, "BAIXA", "DOCUMENTO", "PDF publicado com colunas de edição (Alterar e Excluir)",
    "O cabeçalho da tabela do 8º termo traz as colunas “Alterar” e “Excluir”, que são botões da tela de edição do sistema, não informação do currículo.",
    "eproducao.pdf, pág. 4, tabela “Série: 4 - Período: 2”.",
    "Gerar o PDF de novo pela tela de consulta (sem as colunas de edição) e republicar.", "Relatório, seção 6")
add(P, "BAIXA", "DOCUMENTO", "Coluna de equivalências sem cabeçalho no 5º termo",
    "No 5º termo aparece, entre “Requisitos” e “Duração”, uma coluna sem cabeçalho com textos como “1: 0002412 - … (Não integraliza CH de ACEU)”. Pelo conteúdo são equivalências, mas o documento não diz.",
    "eproducao.pdf, pág. 3.",
    "Incluir o cabeçalho “Equivalências” ou retirar a coluna do PDF publicado.", "Relatório, seção 6")

# ---- FEB · Civil / Mecânica / Elétrica
add("feb/engenharia-civil", "ALTA", "SITE", "Quadro de integralização e exigência de optativas ausentes",
    "O documento traz, em imagem, a tabela “Componentes curriculares da estrutura proposta”. O site não mostra o quadro-resumo nem a carga de optativas exigida (150 h).",
    "Imagem na pág. 4 de ecivil.pdf (conferida visualmente): Disciplinas obrigatórias 225 créditos / 3.375 h; Disciplinas optativas 10 / 150; Atividades curriculares de Extensão Universitária 28 / 420; Estágio Supervisionado 11 / 165; Trabalho de Conclusão de Curso 2 / 30; Atividades Complementares 1 / 15; TOTAL 277 / 4.155.",
    "Transcrever a tabela em ferramentas/transcricoes.py, incluir como quadroResumo e como exigência de optativas em construir.py e regerar.",
    "Relatório, A3")
add("feb/engenharia-civil", "BAIXA", "DOCUMENTO", "Cabeçalho de coluna “Exclir” no PDF",
    "A tabela do 6º termo (Série 3 - Período 2) tem uma coluna extra, vazia, com o cabeçalho “Exclir” (botão “Excluir” da tela de edição, cortado).",
    "ecivil.pdf, pág. 3.", "Gerar o PDF de novo pela tela de consulta e republicar.", "Relatório, seção 6")
add("feb/engenharia-civil", "BAIXA", "DOCUMENTO", "Numerais romanos gravados com a letra l no texto do PDF",
    "Na camada de texto do PDF, vários numerais romanos estão digitados com a letra “l” minúscula no lugar de “I” (ex.: “Hidráulica l”, “Estruturas de Concreto lI”, “lsostática”). Na tela não se nota, mas quem copia o texto ou usa leitor de tela recebe o nome errado. Cada nome afetado tem o seu próprio arquivo nesta pasta.",
    "pdftotext de ecivil.pdf; 12 nomes com “l” e “lsostática”.",
    "Corrigir os nomes no cadastro das disciplinas (digitar “I” maiúsculo) e gerar o PDF de novo.", "Relatório, seção 7")
add("feb/engenharia-mecanica", "ALTA", "SITE", "Quadro de integralização e exigência de optativas ausentes",
    "O documento traz, em imagem, a tabela “Componentes curriculares da estrutura proposta”. O site não mostra o quadro-resumo nem a carga de optativas exigida (240 h).",
    "Valores lidos da imagem (revisao/transcricoes-independentes/feb-mecanica.json): Disciplinas obrigatórias 207 créditos / 3.105 h; Disciplinas optativas 16 / 240; Atividades curriculares de Extensão Universitária 27 / 405; Estágio Supervisionado 11 / 165; Trabalho de Conclusão de Curso 4 / 60; Atividades Complementares 4 / 60; TOTAL 269 / 4.035.",
    "Transcrever a tabela, incluir como quadroResumo e exigência de optativas e regerar. Conferir os valores na imagem antes de publicar.",
    "Relatório, A3")
add("feb/engenharia-mecanica", "BAIXA", "DOCUMENTO", "PDF publicado mostra o nome de usuário de quem o gerou",
    "O cabeçalho da pág. 1 do PDF traz o nome de usuário do Sistema de Graduação de quem gerou o relatório (“amanda.peron”). É um dado pessoal num documento público.",
    "emecanica.pdf, pág. 1, primeira linha (“Sistema de Graduação … amanda.peron”). O site não reproduz esse dado.",
    "Gerar o PDF de novo sem o cabeçalho de sessão (ou recortá-lo) e republicar.", "Relatório, seção 6")
add("feb/engenharia-eletrica", "ALTA", "SITE", "Quadro de integralização incompleto",
    "O site mostra só as duas linhas de texto do documento (obrigatórias 3.180 h; optativas 240 h). A tabela em imagem “Componentes curriculares da estrutura proposta” traz também estágio, TCC, ACEU e os totais, que ficaram de fora.",
    "Valores lidos da imagem (revisao/transcricoes-independentes/feb-eletrica.json): Disciplinas Obrigatórias 212 créditos / 3.180 h; Disciplinas Optativas 16 / 240; Estágio Curricular Obrigatório 11 / 165; TCC 4 / 60; TOTAL (sem extensão) 243 / 3.645; ACEU 27 / 405; TOTAL (com extensão) 270 / 4.050.",
    "Transcrever a tabela, substituir o quadroResumo atual e regerar. Conferir os valores na imagem antes de publicar.",
    "Relatório, A3")
add("feb/engenharia-eletrica", "BAIXA", "DECISÃO", "Base da regra “Percentual do Curso Exigido 60%” não está definida",
    "Quatro disciplinas (EP0002F23, EE4202E23, EP0001F23, EP4201E23) exigem “Percentual do Curso Exigido: 60.0%”. O documento não diz 60% de quê. A simulação usa a carga das disciplinas da grade (3.180 h → 1.908 h). Se a base for o total do curso com extensão (4.050 h), o valor seria 2.430 h.",
    "eeletrica.pdf (coluna Requisitos); revisao/exploratorio.mjs, teste X08.",
    "O Conselho de Curso deve informar a base do percentual. Depois, ajustar a regra no site ou acrescentar um aviso dizendo qual base a simulação usa.",
    "Relatório, B3")

# ---- FAAC · Arquitetura
A = "faac/arquitetura-e-urbanismo"
add(A, "ALTA", "DECISÃO", "Paisagismo V - carga de 60 h no site e 30 h na Resolução",
    "ARQ-E 56 - Paisagismo V - Ecologia da Paisagem aparece no site com 60 h (como na relação do Sistema de Graduação publicada na página do curso). O anexo da Resolução Unesp 123/2023 dá 2 créditos (30 h).",
    "Resolução Unesp 123/2023, anexo, pág. 2: “Paisagismo V - Ecologia da Paisagem 2”. Relação do SG (página do curso): “ARQ-E 56 … 60.0”. As outras 68 disciplinas do anexo conferem com o site.",
    "O Conselho de Curso deve dizer qual fonte prevalece. O site NÃO deve mudar o número por conta própria: até a decisão, manter 60 h e exibir um aviso da divergência.",
    "Relatório, A1")
add(A, "ALTA", "DECISÃO", "Totais do curso diferem entre a Resolução e a página",
    "Disciplinas obrigatórias: 3.570 h no quadro da página (exibido no site) × 236 créditos = 3.540 h na Resolução. Total do curso: 4.230 h na página × 280 créditos = 4.200 h na Resolução. A diferença de 30 h é a de Paisagismo V.",
    "Resolução Unesp 123/2023, art. 1º (parágrafo único) e art. 2º; quadro “Componentes Curriculares” da página do curso.",
    "Decidir a fonte e alinhar a página do curso ou o cadastro do Sistema de Graduação. No site, exibir aviso enquanto houver divergência.",
    "Relatório, A1")
add(A, "ALTA", "SITE", "Documento oficial citado não é a origem dos números",
    "A ficha do curso mostra “Documento oficial: Estrutura curricular - Resolução Unesp nº 123/2023”, mas os números exibidos (cargas, termos, tipos, requisitos, quadro) vêm da relação do Sistema de Graduação publicada na página do curso. As duas fontes divergem.",
    "Campo “fonte” de dados-arquitetura-urbanismo-2023.js; ferramentas/construir.py (função faac).",
    "Citar as duas fontes: a relação do Sistema de Graduação (origem dos dados) e a Resolução (ato legal), com aviso da divergência.",
    "Relatório, A1")
add(A, "ALTA", "SITE", "Número do currículo omitido (Estrutura 2011)",
    "A página oficial informa “Ingressantes a partir de 2023 - Estrutura 2011 - Resolução Unesp 123/2023”. O site não mostra o número e ainda traz o aviso “O documento publicado não informa o número do currículo”, que é falso.",
    "planos de ensino/FAAC/DAUP/Arquitetura_e_Urbanismo/matriz-curricular-arquitetura-e-urbanismo.html (texto fora da tabela).",
    "Em construir.py: curriculo=\"2011\" e remover o aviso. Regerar (o nome do arquivo de dados e o id passam a poder incluir 2011).",
    "Relatório, A4")
RES = [("ARQ-E 01", "Laboratório de Arquitetura, Urbanismo e Paisagismo I: Percepção", "Laboratório de Arquitetura, Urbanismo e Paisagismo I – Percepção"),
       ("ARQ-E 02", "Arquitetura I: Percepção do Espaço Construído", "Arquitetura I – Percepção do Espaço Construído"),
       ("ARQ-E 03", "Urbanismo I: Percepção do Espaço", "Urbanismo I – Percepção do Espaço"),
       ("ARQ-E 04", "Paisagismo I: Percepção da Paisagem", "Paisagismo I – Percepção da Paisagem"),
       ("ARQ-E 05", "História da Arquitetura I - Da Antiguidade ao Barroco", "História da Arquitetura I – Da Antiguidade ao Barroco"),
       ("ARQ-E 08", "Fundamentos Socioeconômicos I: Cidade e Cidadania", "Fundamentos Socioeconômicos I – Cidade e Cidadania"),
       ("ARQ-E 10", "Laboratório de Arquitetura, Urbanismo e Paisagismo II: Composição e Forma", "Laboratório de Arquitetura, Urbanismo e Paisagismo II – Composição e Forma"),
       ("ARQ-E 32", "Atelier Vertical I: Modos de Habitar a Cidade", "Atelier Vertical I: Modos de habitar a cidade"),
       ("ARQ-E 40", "Urbanismo IV: Estudos Urbanos e Cidade Contemporânea", "Urbanismo IV - Estudos Urbanos e Cidade Contemporânea"),
       ("ARQ-E 48", "Atelier Vertical II: Habitar a Paisagem", "Atelier Vertical II: Habitar a paisagem"),
       ("ARQ-E 65", "Atelier Vertical III: Cultura e Cidade Inclusiva", "Atelier Vertical III: Cultura e cidade inclusiva")]
for cod, sg, res in RES:
    add(A, "BAIXA", "DOCUMENTO", f"Nome diferente entre SG e Resolução - {cod}",
        f"O nome da disciplina {cod} não é igual nos dois documentos oficiais:\n    Sistema de Graduação (usado no site): “{sg}”\n    Resolução Unesp 123/2023:              “{res}”\nA diferença é de pontuação (dois-pontos, hífen, travessão) ou de maiúsculas.",
        "revisao/relatorio-de-revisao-expansao.md, A1; comparação do anexo da Resolução (69 disciplinas) com os dados.",
        "Padronizar o nome nos dois documentos. O site segue o Sistema de Graduação e acompanha a forma que for adotada.", "Relatório, A1")

# ---- FAAC · RP, RTVI, AV, Design
add("faac/relacoes-publicas", "ALTA", "SITE", "Número do currículo omitido (Estrutura 2402)",
    "A página oficial informa “Ingressantes a partir de 2023 - Estrutura 2402”. O site não mostra o número e traz o aviso “O documento publicado não informa o número do currículo”, que é falso.",
    "planos de ensino/FAAC/DARP/Relacoes_Publicas/matriz-curricular-relacoes-publicas.html (texto fora da tabela).",
    "Em construir.py: curriculo=\"2402\" e remover o aviso. Regerar.", "Relatório, A4")
add("faac/comunicacao-audiovisual", "BAIXA", "DOCUMENTO", "Erro de ortografia na página do curso (engressaram)",
    "O título da tabela na página oficial diz: “Estrutura Curricular (para alunos que engressaram a partir de 2023)”. O correto é “ingressaram”.",
    "planos de ensino/FAAC/DARP/Comunicacao_Audiovisual/matriz-curricular-comunicacao-radio-televisao-e-internet.html. O site não reproduz essa frase.",
    "Corrigir o texto na página do curso no portal da FAAC.", "Novo (encontrado ao detalhar as correções)")
AV = "faac/artes-visuais"
add(AV, "BAIXA", "DOCUMENTO", "Total do 8º termo do núcleo básico não inclui a CH ACEU",
    "Na relação “Artes Visuais - Estrutura Curricular - Básico” (2504), o 8º termo (Série 4 - Período 2) traz “Total de Carga Horária: 93.0”, que soma só a coluna Carga Horária. Há ainda 27 h de CH ACEU no termo. Nos demais termos o total inclui a CH ACEU.",
    "artes-visuais-estrutura-curricular-basico.csv/.html. O site mantém os números e mostra aviso (Bacharelado e Licenciatura).",
    "A Seção de Graduação deve conferir o total do termo (93 h ou 120 h) e corrigir o relatório.", "Relatório, seção 6")
add(AV, "BAIXA", "DOCUMENTO", "Total do 8º termo da Licenciatura não inclui a CH ACEU",
    "Na relação da Licenciatura (2504L), o 8º termo traz “Total de Carga Horária: 174.0”, que soma só a coluna Carga Horária. Há ainda 6 h de CH ACEU no termo.",
    "artes-visuais-estrutura-curricular-licenciatura.csv/.html. O site mantém os números e mostra aviso.",
    "A Seção de Graduação deve conferir o total do termo (174 h ou 180 h) e corrigir o relatório.", "Relatório, seção 6")
add(AV, "BAIXA", "DOCUMENTO", "Linha solta “Total de Carga Horária 1242.0” no Bacharelado",
    "Depois do último termo, a relação do Bacharelado (2504B) traz uma segunda linha “Total de Carga Horária: 1242.0”, sem dizer a que se refere. Não corresponde à soma do bacharelado (240 h obrigatórias + 90 h de TCC) nem à do núcleo básico (1.680 h).",
    "artes-visuais-estrutura-curricular-bacharelado.csv, antes de “Total Carga Horária Obrigatória do Curso: 240.0”. O site ignora essa linha.",
    "A Seção de Graduação deve esclarecer ou retirar a linha do relatório.", "Novo (encontrado ao detalhar as correções)")
add(AV, "BAIXA", "DECISÃO", "Maiúsculas não uniformes - Antropologia visual",
    "ART-E 26 está grafada “Antropologia visual” (v minúsculo). As demais seguem maiúsculas nos nomes (“Antropologia da Arte”, “Sociologia da Arte”), e a própria equivalência do documento traz “Antropologia Visual”. O site corrigiu maiúsculas em outros cursos, mas não aqui.",
    "artes-visuais-estrutura-curricular-basico.csv, Série 2 - Período 2.",
    "Definir o critério de maiúsculas para todos os cursos. Se for uniformizar: corrigir para “Antropologia Visual” no cadastro e registrar a correção no site.",
    "Relatório, M3")
add("faac/design", "BAIXA", "SITE", "Lista por termo mostra a coluna Carga vazia",
    "O documento do Design não informa cargas. Mesmo assim, a visualização “Lista por termo” mantém a coluna “Carga”, sem nenhum valor.",
    "revisao/exploratorio.mjs, teste X12.",
    "Em assets/arvore-grade.js, não gerar a coluna “Carga” quando o currículo estiver marcado com semCarga.", "Relatório, B1")
add("faac/design", "MÉDIA", "DOCUMENTO", "Documento não informa cargas, códigos nem pré-requisitos",
    "A estrutura curricular publicada traz só os nomes dos componentes por termo. Sem cargas, códigos e requisitos, a árvore do Design não tem ligações, e a simulação conta componentes em vez de horas.",
    "matriz-curricular-2023-design-unesp.pdf (1 página). Conferido pela transcrição independente.",
    "A coordenação deve publicar a matriz completa (códigos, cargas horárias, pré-requisitos e relação de optativas). Com ela, o site pode ser gerado como o dos outros cursos.",
    "Relatório, seção 6")
add("faac/design", "BAIXA", "DOCUMENTO", "Ano diferente no título e nos metadados do PDF",
    "O título impresso é “ESTRUTURA CURRICULAR BACHARELADO DESIGN | FAAC | UNESP | 2023”; os metadados do arquivo dizem “Matriz Curricular 2024”; e a página do curso o apresenta como “Ingressantes a partir de 2024”.",
    "pdfinfo de matriz-curricular-2023-design-unesp.pdf; fonte.json do curso.",
    "Uniformizar o ano no documento e na página. No site, confirmar se “Currículo 2023” é a identificação correta.", "Relatório, seção 6")

# ---- FC · Química
Q = "fc/quimica"
for mod, pag in (("Licenciatura em Química", "pág. 3 (4º ano, 1º semestre)"), ("Bacharelado em Química Tecnológica", "pág. 5 (3º ano, 1º semestre)")):
    add(Q, "ALTA", "SITE", f"Correção de grafia falsa - {mod.split(' em ')[0]}",
        f"O rodapé da página ({mod}) afirma que o documento oficial grafa “Introdução à Metodologia da Pesquisa Cientifica” (sem acento) e que o site corrigiu para “Científica”. O documento JÁ grafa “Científica”, com acento. O erro foi da transcrição usada pelo gerador, e o site atribui ao documento um erro que ele não tem.",
        f"Imagem da matriz a 400 dpi, {pag}; transcrição independente (revisao/transcricoes-independentes/quimica.json); revisao/exploratorio.mjs, teste X13.",
        "Em ferramentas/transcricoes.py, trocar “Cientifica” por “Científica” (QUI_LIC e QUI_BACH) e regerar. O registro em “correcoes” deve desaparecer. O nome exibido não muda.",
        "Relatório, A2")
add(Q, "BAIXA", "SITE", "Rótulo “Currículo 2023” não consta do documento",
    "A ficha mostra “Currículo: 2023”. O documento não dá número de currículo: diz apenas que as estruturas são “vigentes a partir do ano letivo de 2023”. O rótulo pode ser lido como um código oficial que não existe.",
    "2-matrizes-e-ementario-quimica.pdf, pág. 6; campo “curriculo” dos dois arquivos de dados.",
    "Deixar o campo “curriculo” vazio (a vigência já informa o ano) ou obter o número do currículo com a coordenação. Regerar.",
    "Novo (encontrado ao detalhar as correções)")
add(Q, "MÉDIA", "DOCUMENTO", "Licenciatura - soma da matriz (3.705 h) diferente da carga declarada (3.735 h)",
    "O documento declara “Carga horária: 3735 horas (249 créditos)” para a Licenciatura. A soma das cargas impressas na matriz é 3.495 h + 210 h de Atividades Teórico-Práticas de Aprofundamento = 3.705 h. Faltam 30 h (2 créditos).",
    "Matriz das págs. 2–3; somas conferidas por duas transcrições independentes. No Bacharelado a soma fecha (3.450 h). O site mantém os números e mostra aviso.",
    "A coordenação deve localizar a diferença de 30 h (uma disciplina com carga impressa a menos ou a carga declarada a mais) e corrigir o documento.",
    "Relatório, seção 6")
for n in ("1", "2"):
    add(Q, "BAIXA", "DOCUMENTO", f"Ementário - “Analise Instrumental {n}” sem acento",
        f"No ementário, o título da ementa está grafado “Analise Instrumental {n}” (sem acento). Na matriz, o nome da disciplina é “Análise Instrumental {n}”.",
        "2-matrizes-e-ementario-quimica.pdf, pág. 6 (início do ementário). O site não exibe o ementário da Química.",
        "Corrigir o título no ementário.", "Novo (encontrado ao detalhar as correções)")

# ---- FC · Física
F = "fc/fisica"
add(F, "ALTA", "SITE", "Pré-requisito formal ausente - Introdução à Pesquisa em Ensino de Ciências",
    "Na Licenciatura, a ementa de “Introdução à Pesquisa em Ensino de Ciências” (7º termo) termina com “Pré-requisito: Metodologias e Práticas de Ensino de Física I, II, III e IV”. É um pré-requisito sem a palavra “recomendado”. O site mostra a disciplina sem requisito e sem ligações.",
    "grade-por-termo-com-ementa-e-objetivo-2.pdf, ementa da disciplina (“(Pré-requisito: Metodologias e Práticas de Ensino de Física I, II, III e IV – Seriação ideal: sétimo termo da Licenciatura em Física)”).",
    "Em ferramentas/transcricoes.py, incluir como pré-requisitos as quatro “Metodologia e Prática de Ensino de Física” (I a IV) e regerar. Confirmar com a coordenação que o requisito é obrigatório.",
    "Novo (encontrado ao detalhar as correções) - acrescentado ao relatório como A8")
add(F, "ALTA", "SITE", "Aviso falso - “pré-requisito recomendado” em só dois casos",
    "As três páginas da Física dizem: “O documento não estabelece pré-requisitos formais: as ementas indicam apenas a seriação ideal (e, em dois casos, um ‘pré-requisito recomendado’)”. Isso está errado: o documento traz “pré-requisito recomendado” (ou “recomentado”) em 47 ementas, e “Pré-requisito:” sem “recomendado” em 6 (as cinco de TCC, “ver regulamento geral do TCC”, e Introdução à Pesquisa em Ensino de Ciências).",
    "Contagem no texto do PDF: 22 ocorrências de “recomendado” + 25 de “recomentado”.",
    "Corrigir o aviso em ferramentas/construir.py e regerar.", "Novo - relatório, A8 (substitui M5)")
add(F, "MÉDIA", "SITE", "Pré-requisitos recomendados não aparecem nas disciplinas",
    "O documento indica um pré-requisito recomendado para quase todas as disciplinas (ex.: Cálculo Diferencial e Integral II ← Cálculo Diferencial e Integral I; Física Moderna II ← Física Moderna I; Simulações Computacionais II ← Simulações Computacionais I). O site não mostra nenhum, e a árvore da Física fica sem ligações.",
    "Ementas do PDF (texto entre parênteses ao fim de cada ementa).",
    "Transcrever a recomendação de cada disciplina e exibi-la como texto (“pré-requisito recomendado: …”), sem bloquear a simulação. A coordenação deve confirmar se as recomendações devem aparecer como ligações.",
    "Relatório, M5 / A8")
add(F, "MÉDIA", "SITE", "Requisito dos TCC (“ver regulamento geral do TCC”) não aparece",
    "As ementas dos Trabalhos de Conclusão de Curso (I, II e III da Licenciatura; I e II do Bacharelado) trazem “Pré-requisito: ver regulamento geral do TCC”. O site mostra os TCC sem nenhuma indicação de requisito.",
    "Ementas “Trabalho de Conclusão de Curso …” do PDF.",
    "Exibir o texto como requisito (campo preTexto) nos cinco TCC e regerar.", "Novo - relatório, A8")
add(F, "MÉDIA", "SITE", "Ementas que existem no documento não aparecem no site",
    "O documento traz ementa para estas disciplinas, mas o site as mostra sem ementa (o gerador só reconhece o título quando ele cabe numa linha e é igual ao nome da tabela):\n  Licenciatura: Tecnologia da Comunicação e Informação no Ensino de Física; Filosofia das Ciências; Estágio Supervisionado II; Trabalho de Conclusão de Curso I, II e III; Ciência, Sociedade, Ambiente e Desenvolvimento Humano; Libras, Educação Especial e Inclusiva.\n  Física de Materiais: Ciência, Sociedade, Ambiente e Desenvolvimento Humano; Trabalho de Conclusão de Curso I e II.\n  Física Computacional: Cálculo Numérico I; Ciência, Sociedade, Ambiente e Desenvolvimento Humano; Estágio - I; Computação Quântica; Estágio II.",
    "Títulos no PDF que quebram em duas linhas ou diferem do nome da tabela: “Cálculo Numérico I (4credidos – …)”, “Estágio Física Computacional - I”, “Estágio II da Física Computacional”, “Computação Quântica -”, “Trabalho de Conclusão de Curso I – bacharelado - I”.",
    "Em ferramentas/construir.py (ementas_fisica), aceitar títulos em duas linhas e mapear os títulos divergentes para os nomes da tabela. Regerar e conferir que só fica sem ementa o que o documento não traz.",
    "Novo (encontrado ao detalhar as correções)")
add(F, "BAIXA", "DOCUMENTO", "Química Geral II - 4 créditos na tabela e 2 na ementa",
    "“Química Geral II” tem “(4cd)” na tabela do terceiro termo e “(2 créditos – Primeiro Semestre – DQ)” no título da sua ementa. Os totais do termo só fecham com 4.",
    "PDF, tabela do terceiro termo e título da ementa. O site usa 4 e mostra aviso.",
    "Corrigir o título da ementa para 4 créditos (ou a tabela, se o correto for 2, refazendo os totais).", "Relatório, seção 6")
for err, certo, ctx in (("é divido em duas modalidades", "é dividido em duas modalidades", "1º parágrafo"),
                        ("para concluir estas habilidades individualmente", "para concluir estas habilitações individualmente", "1º parágrafo"),
                        ("De a acordo com a resolução", "De acordo com a resolução", "1º parágrafo"),
                        ("e do bacharelada tanto em Física de Materiais", "e do bacharelado tanto em Física de Materiais", "1º parágrafo"),
                        ("a que compões o tronco comum", "as que compõem o tronco comum", "4º parágrafo"),
                        ("Na ultima linha de cada tabela", "Na última linha de cada tabela", "5º parágrafo"),
                        ("Cálculo Numérico I (4credidos", "Cálculo Numérico I (4 créditos", "título da ementa de Cálculo Numérico I")):
    add(F, "BAIXA", "DOCUMENTO", f"Erro de digitação no documento - {err[:40]}",
        f"No documento “Grade das disciplinas por termos…”, {ctx}, está escrito:\n    “{err}”\nO correto é:\n    “{certo}”",
        "grade-por-termo-com-ementa-e-objetivo-2.pdf. O site não reproduz esse trecho.",
        "Corrigir o texto do documento.", "Novo (encontrado ao detalhar as correções)")
add(F, "BAIXA", "DOCUMENTO", "“recomentado” no lugar de “recomendado” (25 vezes)",
    "Em 25 ementas, a nota final está grafada “Pré-requisito recomentado” (com t).",
    "Contagem no texto do PDF: 25 ocorrências de “recomentado” e 22 de “recomendado”.",
    "Substituir “recomentado” por “recomendado” em todo o documento.", "Novo (encontrado ao detalhar as correções)")
add(F, "MÉDIA", "DOCUMENTO", "Pré-requisito recomendado “xxx” em cinco ementas",
    "Cinco ementas do Bacharelado em Física Computacional trazem “Pré-requisito recomendado: xxx”, um marcador que ficou sem ser preenchido: Simulações Computacionais I, Estruturas de Dados, Computação Quântica, Estágio II da Física Computacional e Introdução às Técnicas de Aprendizado de Máquina.",
    "Texto do PDF: 5 ocorrências de “xxx”.",
    "A coordenação deve informar o pré-requisito recomendado de cada uma (ou retirar a nota).", "Novo (encontrado ao detalhar as correções)")
add(F, "BAIXA", "DOCUMENTO", "Recomendações citam disciplinas que não existem na grade",
    "Algumas notas de pré-requisito recomendado citam nomes que não existem na grade: “Cálculo Básico” (duas vezes; a grade tem Pré-Cálculo e Cálculo Diferencial e Integral I–IV) e “Cálculo I a V” (duas vezes; a grade vai até o IV). Várias usam “Calculo” sem acento.",
    "Ementas de Probabilidade e Estatística, Física Matemática I e Mecânica Quântica I, entre outras.",
    "Trocar pelos nomes exatos das disciplinas da grade.", "Novo (encontrado ao detalhar as correções)")
add(F, "BAIXA", "DOCUMENTO", "Ciências dos Materiais II recomenda a si mesma",
    "A ementa de “Ciências dos Materiais II” termina com “Prérequisito recomentado: Ciências dos Materiais II”. Provavelmente deveria ser “Ciências dos Materiais I”.",
    "Ementa de Ciências dos Materiais II (oitavo termo do Bacharelado em Física de Materiais).",
    "Corrigir para “Ciências dos Materiais I” (confirmar com a coordenação).", "Novo (encontrado ao detalhar as correções)")
add(F, "BAIXA", "DOCUMENTO", "Nome da habilitação escrito de duas formas",
    "O documento usa “Física de Materiais” no texto e nas ementas, e “Física dos Materiais” no título e no cabeçalho das tabelas (“Bach. Física dos Materiais”). O título também cita só “licenciatura e bacharelado em Física dos Materiais”, embora o documento inclua a Física Computacional.",
    "Título e tabelas do PDF. O site usa “Física de Materiais”.",
    "Padronizar o nome da habilitação e incluir a Física Computacional no título.", "Novo (encontrado ao detalhar as correções)")
add(F, "BAIXA", "DOCUMENTO", "Nomes diferentes na tabela e no título da ementa",
    "Algumas disciplinas têm um nome na tabela do termo e outro no título da ementa:\n  “Estágio - I” × “Estágio Física Computacional - I”\n  “Estágio II” × “Estágio II da Física Computacional”\n  “Computação Quântica” × “Computação Quântica -”\n  “Trabalho de Conclusão de Curso I” × “Trabalho de Conclusão de Curso I – bacharelado - I” e “… I - Licenciatura”\n  “Trabalho de Conclusão de Curso III” × “Trabalho de Conclusão de Curso III- Licenciatura”",
    "Tabelas dos termos 7 a 10 e títulos das ementas.",
    "Usar o mesmo nome nos dois lugares.", "Novo (encontrado ao detalhar as correções)")

# ---- FC · Meteorologia
M = "fc/meteorologia"
add(M, "ALTA", "SITE", "Micrometeorologia aparece como apta sem o requisito “Física II”",
    "7034 - Micrometeorologia exige “Física II”, que não existe na grade com esse nome. O site guarda o requisito só como texto, e a simulação o ignora: a disciplina aparece como “apta para matrícula”.",
    "revisao/exploratorio.mjs, teste X04.",
    "Em assets/arvore-grade.js, disciplinas com requisito em texto (preTexto/coTexto) devem ficar num estado próprio (“requisito a confirmar com o Conselho de Curso”), não como aptas.",
    "Relatório, A6")
add(M, "MÉDIA", "DOCUMENTO", "Códigos 7005 e 7050 com o mesmo nome",
    "No 1º ano / 2º semestre, 7005 (6 créditos, 90 h) e 7050 (4 créditos, 60 h) têm o mesmo nome: “Energia e Sustentabilidade Ambiental”. Pela posição (entre Física I, 7000, e Física III, 7010) e pela carga, o 7005 provavelmente é “Física II”.",
    "Imagem da tabela do 1º ano / 2º semestre na página do curso; duas transcrições independentes. O site mantém os dois nomes e mostra aviso.",
    "A coordenação deve corrigir o nome do 7005 na página do curso. Depois, atualizar a transcrição e regerar: o requisito da Micrometeorologia passa a ter destino.",
    "Relatório, seção 6")
add(M, "MÉDIA", "DOCUMENTO", "Micrometeorologia exige “Física II”, que não existe na grade",
    "7034 - Micrometeorologia tem como pré-requisito “Física II”. Nenhuma disciplina da grade tem esse nome (ver o item dos códigos 7005 e 7050).",
    "Tabela do 3º ano / 1º semestre.", "Resolver junto com o nome do 7005.", "Relatório, seção 6")
add(M, "BAIXA", "DOCUMENTO", "Laboratório de Física II com departamento DM e 4 créditos",
    "7047 - Laboratório de Física II está com departamento “DM” e 4 créditos / 60 h. Os Laboratórios de Física I (7044) e III (7052) são do DFM, com 2 créditos / 30 h.",
    "Tabela do 1º ano / 2º semestre (transcrição independente, observações). O site reproduz o documento e não tem aviso para este ponto.",
    "A coordenação deve confirmar departamento e créditos do 7047 e corrigir a tabela se for o caso. No site, acrescentar aviso enquanto não houver confirmação.",
    "Relatório, seção 6")
add(M, "BAIXA", "DOCUMENTO", "Cálculo de Uma Variável com departamento DFM",
    "7046 - Cálculo Diferencial e Integral de Uma Variável está com departamento “DFM”. As demais disciplinas de Cálculo (7003, 7043, 7051, 7055, 7057) são do DM. Na mesma tabela, o Laboratório de Física II está como DM: os dois departamentos parecem trocados.",
    "Tabela do 1º ano / 2º semestre.", "Confirmar e corrigir os departamentos de 7046 e 7047.", "Relatório, seção 6")
add(M, "MÉDIA", "DOCUMENTO", "Soma da grade (197 créditos) diferente do resumo da página (187)",
    "A página informa: disciplinas obrigatórias 2.805 h (187 créditos), estágio 60 h (4), atividades complementares 195 h (13), total 3.150 h (210). As oito tabelas somam 197 créditos / 2.955 h; sem o estágio, 193 / 2.895. Sobram 6 créditos / 90 h, exatamente o tamanho do 7005.",
    "Somas conferidas por duas transcrições. O site mostra aviso.",
    "Resolver junto com o item do 7005 (uma das duas “Energia e Sustentabilidade Ambiental” pode estar sobrando) e corrigir o resumo ou a grade.",
    "Relatório, seção 6")
for nome in ("Meteorologia de Mesoescala", "Interação Solo-Vegetação-Atmosfera"):
    add(M, "BAIXA", "DOCUMENTO", f"Optativa sem código - {nome}",
        f"Na tabela de disciplinas optativas, “{nome}” está com a célula “Cód.” vazia.",
        "Imagem “Disciplinas Optativas” da página do curso. O site mostra “—” no lugar do código.",
        "Informar o código da disciplina na página do curso; depois, atualizar a transcrição e regerar.", "Relatório, seção 6")
for cod, nome, alvo in (("7055", "Cálculo Diferencial e Integral de várias variáveis II", "Cálculo Diferencial e Integral de Várias Variáveis II"),
                        ("49183", "Mecânica dos Fluidos para atmosfera", "Mecânica dos Fluidos para Atmosfera")):
    add(M, "BAIXA", "DECISÃO", f"Maiúsculas não uniformes - {cod}",
        f"{cod} está grafada “{nome}”. As demais disciplinas usam maiúsculas (ex.: “Cálculo Diferencial e Integral de Várias Variáveis I”). O site corrigiu maiúsculas em outros cursos, mas não aqui.",
        "Tabelas da página do curso.",
        f"Definir o critério de maiúsculas para todos os cursos. Se for uniformizar: “{alvo}” no documento e registro da correção no site.",
        "Relatório, M3")
for cod, txt in (("7010", "Física III tem “Física I” como correquisito (o esperado seria pré-requisito, já que Física I é do 1º semestre do curso)."),
                 ("7051", "Cálculo Diferencial e Integral de Várias Variáveis I tem “Pré-Cálculo” como correquisito, embora Pré-Cálculo seja do 1º semestre."),
                 ("7052", "Laboratório de Física III tem “Laboratório de Física I” como correquisito, embora este seja do 1º semestre."),
                 ("7030", "Meteorologia Física II tem como pré-requisito “Cálculo Diferencial e Integral de Uma Variável”, e não “Meteorologia Física I”.")):
    add(M, "BAIXA", "DOCUMENTO", f"Requisito a confirmar - {cod}",
        txt + " O site reproduz o documento como está.",
        "Tabelas da página do curso (colunas Correquisito e Pré-requisito); apontado pela transcrição independente.",
        "A coordenação deve confirmar se o requisito está na coluna certa e com a disciplina certa.", "Relatório, seção 6")

# ---- FC · Psicologia
S = "fc/psicologia"
add(S, "ALTA", "SITE", "Simulação conta 4 programas de estágio (o aluno cursa 3)",
    "O documento diz: “São contabilizadas apenas o referente a 3 opções de Estágio”. A simulação soma os quatro programas (18 créditos cada) e mostra “de 282 créditos”. O correto é 264 (210 das disciplinas dos semestres 1 a 8, sem as duas optativas, + 54 de três estágios). O percentual exibido fica menor do que o real.",
    "revisao/exploratorio.mjs, teste X05.",
    "Marcar os quatro estágios como grupo “cursar 3 de 4” (campo novo no arquivo de dados) e contar só os exigidos, em assets/arvore-grade.js e ferramentas/construir.py.",
    "Relatório, A5")
add(S, "ALTA", "SITE", "Disciplina aparece como apta com requisito não verificável",
    "“Análise do Comportamento Aplicada: Educação Especial e Inclusiva” tem um pré-requisito que o site guarda só como texto (“Análise do Comportamento Aplicada: Processos Educativos”, sem I ou II). A simulação ignora esse texto e pode mostrar a disciplina como “apta para matrícula”.",
    "Mesmo defeito do teste X04 (Meteorologia) em revisao/exploratorio.mjs.",
    "Em assets/arvore-grade.js, criar o estado “requisito a confirmar” para disciplinas com preTexto/coTexto.", "Relatório, A6")
add(S, "MÉDIA", "DECISÃO", "Erro de concordância não corrigido - Teorias Sistêmica e Complexa",
    "A disciplina do 2º semestre está grafada “Fundamentos das Teorias Sistêmica e Complexa”. O próprio documento, ao citá-la como pré-requisito, escreve “Fundamentos das Teorias Sistêmicas e Complexas”. O site corrigiu grafias em outros nomes, mas deixou este.",
    "grade-curricular-curso-de-psicologia-1212-1213.pdf, pág. 1 (nome) e pág. 2 (coluna Pré-Requisitos de “Teorias e Práticas Sistêmicas e Complexas”).",
    "Confirmar o nome com a coordenação. Se for “Sistêmicas e Complexas”: corrigir o documento e acrescentar a correção em CORRECOES (ferramentas/construir.py).",
    "Relatório, M3")
for n in ("Laboratório de Análise Experimental do Comportamento I", "Análise Experimental do Comportamento I"):
    add(S, "MÉDIA", "DOCUMENTO", f"Correquisito aponta para a própria disciplina - {n[:45]}",
        f"Na coluna Correquisitos de “{n}” está o nome da própria disciplina. No par II a relação é cruzada (Laboratório II ↔ Análise Experimental II); no par I os nomes parecem trocados.",
        "PDF, pág. 1, 2º semestre. O site mostra aviso e mantém o texto.",
        "Corrigir a coluna: o correquisito do Laboratório I deve ser “Análise Experimental do Comportamento I”, e vice-versa (confirmar com a coordenação). Depois, atualizar a transcrição e regerar.",
        "Relatório, seção 6")
add(S, "BAIXA", "DOCUMENTO", "Semestre dos estágios grafado “10 e 10”, “11 e 10” e “12 e 10”",
    "Os quatro programas de estágio são do 9º e 10º semestres (anuais). Só o primeiro está como “9 e 10 (Anual)”; os outros aparecem como “10 e 10”, “11 e 10” e “12 e 10”.",
    "PDF, pág. 5, coluna SEM. O site coloca os quatro no 9º termo e mostra aviso.",
    "Corrigir a coluna SEM para “9 e 10 (Anual)” nas quatro linhas.", "Relatório, seção 6")
add(S, "BAIXA", "DOCUMENTO", "Disciplina sem semestre - ACA Processos Educativos I",
    "“Análise do Comportamento Aplicada: Processos Educativos I” está com a coluna SEM vazia. Fica entre linhas do 4º semestre.",
    "PDF, pág. 2. O site a coloca no 4º termo e mostra aviso.", "Preencher o semestre (4) no documento.", "Relatório, seção 6")
add(S, "BAIXA", "DOCUMENTO", "Pré-requisito incompleto - “Processos Educativos” sem I ou II",
    "O pré-requisito de “Análise do Comportamento Aplicada: Educação Especial e Inclusiva” termina em “Análise do Comportamento Aplicada: Processos Educativos”, sem dizer se é I ou II.",
    "PDF, pág. 4. O site mantém como texto e mostra aviso.", "Completar com I ou II.", "Relatório, seção 6")
for n, det in (("Psicologia Social I", "“Fenômenos e processos Psicológicos: Psicologia Sócio-Histórica II, Políticas Públicas, Instituições e Saúde”"),
               ("Psicologia Organizacional e do Trabalho II", "“Psicologia Organizacional e do Trabalho I”")):
    add(S, "MÉDIA", "DOCUMENTO", f"Requisito na coluna de correquisitos - {n}",
        f"“{n}” tem a coluna Pré-Requisitos vazia e, na coluna Correquisitos, {det}. As disciplinas citadas são de semestres anteriores: pelo conteúdo, parecem pré-requisitos digitados na coluna errada.",
        "PDF, págs. 3 e 5 (conferido nas imagens). O site reproduz como correquisito, sem aviso.",
        "A coordenação deve confirmar a coluna correta. No site, acrescentar aviso enquanto não houver confirmação.", "Relatório, seção 6")
add(S, "BAIXA", "DOCUMENTO", "Pré-requisito do mesmo semestre",
    "“Atividades Extensionistas em Educação e Sociedade I” (5º semestre) tem como pré-requisito “Análise do comportamento Aplicada: Delineamentos Culturais”, que também é do 5º semestre.",
    "PDF, pág. 3. O site mantém e mostra aviso.", "Confirmar se é pré-requisito ou correquisito.", "Relatório, seção 7")
for err, certo in (("Avaliação psicológica I", "Avaliação Psicológica I"), ("Introdução à extensão", "Introdução à Extensão"),
                   ("Análise do comportamento Aplicada", "Análise do Comportamento Aplicada"), ("Fenômenos e processos Psicológicos: Psicologia Sócio-Histórica II", "Fenômenos e Processos Psicológicos: Psicologia Sócio-histórica II")):
    add(S, "BAIXA", "DOCUMENTO", f"Nome citado com grafia diferente - {err[:38]}",
        f"Nas colunas de requisitos, a disciplina é citada como “{err}”; o nome na coluna DISCIPLINA é “{certo}”.",
        "PDF, colunas Pré-Requisitos/Correquisitos. O site liga o requisito à disciplina certa.",
        "Uniformizar a grafia no documento.", "Relatório, seção 6")
add(S, "BAIXA", "DOCUMENTO", "“SIM” e “Sim” na coluna Divisão de Turma",
    "A coluna “Divisão de Turma” usa “SIM” nas disciplinas e “Sim” nos estágios.", "PDF, págs. 1 a 5. O site não exibe essa coluna.",
    "Uniformizar.", "Novo (encontrado ao detalhar as correções)")

# ---- FC · Ciências Biológicas
B = "fc/ciencias-biologicas"
add(B, "ALTA", "SITE", "Metodologias e Práticas de Ensino aparecem como aptas sem o estágio correquisito",
    "Na Licenciatura (2711), as cinco “Metodologia e Prática de Ensino de Ciências e Biologia: …” têm como correquisito um “Estágio Supervisionado em Ensino de Ciências e Biologia: …” que não é disciplina da matriz. O site guarda o correquisito como texto, e a simulação o ignora.",
    "Avisos da página do 2711; mesmo defeito do teste X04 em revisao/exploratorio.mjs.",
    "Em assets/arvore-grade.js, criar o estado “requisito a confirmar” para disciplinas com preTexto/coTexto.", "Relatório, A6")
add(B, "MÉDIA", "DOCUMENTO", "2711 - estágios citados como correquisito não constam da matriz",
    "Cinco estágios supervisionados (Estudo da Realidade Escolar; Abordagens Didáticas e Recursos de Apoio; Sociedade, Escola e Ensino; Relações Ciência-Sociedade e Temas Ambientais; Currículo e Processos de Avaliação) são citados na coluna Correquisito, mas não aparecem como linhas em nenhum semestre. O quadro resumo só traz “Estágio curricular 27 créditos / 405 h”.",
    "curriculo-2711-licenciatura-noturno.pdf; transcrição independente.",
    "Incluir os estágios na planilha (semestre, créditos e horas de cada um).", "Relatório, seção 6")
for c in ("2710", "2711"):
    add(B, "BAIXA", "DOCUMENTO", f"{c} - asterisco sem nota em “Disciplinas Obrigatórias*”",
        f"No Quadro Resumo do currículo {c}, a linha “Disciplinas Obrigatórias* (incluindo {'390' if c == '2710' else '392'}h de ACEUs)” tem um asterisco, mas o documento não traz a nota correspondente. Também não informa em quais disciplinas estão as horas de ACEU.",
        f"curriculo-{c}-…pdf, Quadro Resumo.", "Incluir a nota do asterisco e a distribuição das horas de ACEU por disciplina.", "Relatório, seção 6")
add(B, "BAIXA", "DOCUMENTO", "2711 - Trabalho de Conclusão de Curso sem créditos no quadro",
    "No Quadro Resumo do 2711, “Trabalho de Conclusão de Curso” está com os créditos em branco (horas 0).",
    "curriculo-2711-licenciatura-noturno.pdf. O site mostra 0 créditos e “—” em horas.", "Preencher ou retirar a linha.", "Relatório, seção 6")
add(B, "BAIXA", "DOCUMENTO", "2710 - dois espaços em “Anatomia Geral e  Humana”",
    "No 1º ano / 1º semestre do 2710, o nome está digitado com dois espaços: “Anatomia Geral e  Humana”.",
    "Caracteres do PDF (transcrição independente). O site exibe com um espaço.", "Retirar o espaço a mais.", "Relatório, seção 6")
add(B, "BAIXA", "DOCUMENTO", "Cabeçalho “OP (optativa) / A (anual)” escondido nas tabelas",
    "No 2710 (3º e 4º anos) e no 2711 (3º ao 6º ano), a legenda “OP (optativa)” e “A (anual)” existe no arquivo, mas fica escondida atrás da primeira linha da tabela. Só se vê “OB (obrigatória)” e “S (semestral)”.",
    "Texto extraído dos PDFs × imagem.", "Ajustar a altura da linha de cabeçalho na planilha e gerar o PDF de novo.", "Relatório, seção 6")
add(B, "BAIXA", "DOCUMENTO", "Nome diferente entre 2710 e 2711 - Deuterostomia",
    "A mesma disciplina aparece como “Zoologia de Ecdysozoa e Deuterostomia” no 2710 e “Zoologia de Ecdysozoa e Deuterostomia Basais” no 2711.",
    "2º ano / 2º semestre dos dois PDFs.", "Confirmar o nome e uniformizar.", "Relatório, seção 6")

# ---- FC · Educação Física
E = "fc/educacao-fisica"
for cur, tt in (("2610 Bacharelado (integral)", "7º e 8º"), ("2610 Licenciatura (integral)", "7º e 8º"), ("2611 Bacharelado (noturno)", "9º e 10º"), ("2611 Licenciatura (noturno)", "9º e 10º")):
    add(E, "MÉDIA", "SITE", f"TCC II repetido sem indicação de anual - {cur}",
        f"No currículo {cur}, “Trabalho de Conclusão de Curso II” aparece em dois termos seguidos ({tt}), com 2 créditos em cada. O site mostra dois cartões iguais, sem selo “anual” e sem aviso; a simulação exige marcar os dois.",
        "revisao/exploratorio.mjs, teste X06; revisao/comparar_edf.py.",
        "Confirmar com a coordenação se a disciplina é anual. Se for, marcar as duas ocorrências como anual em ferramentas/construir.py (ler_edf) e acrescentar aviso. Regerar.",
        "Relatório, M1")
add(E, "BAIXA", "SITE", "Marca “A” da coluna Cód. descartada (2610 Licenciatura)",
    "No documento do 2610 Licenciatura, a linha do TCC II do 7º termo traz “A” na coluna Cód. (provavelmente “Anual”). O gerador ignora essa célula.",
    "curriculo-2610---licenciatura-integral-a-partir-de-2015.doc, 7º termo.",
    "Tratar “A” na coluna Cód. como indicação de disciplina anual (após confirmação da coordenação).", "Relatório, M1")
for cur in ("2610 Bacharelado", "2611 Bacharelado"):
    add(E, "BAIXA", "DECISÃO", f"Maiúsculas não uniformes - hipertensão e cardiovascular ({cur})",
        f"No {cur}, as disciplinas “Fisiopatologia e Tratamento pelo Exercício: hipertensão e cardiovascular - I/II” (e os estágios correspondentes) usam minúsculas depois dos dois-pontos; as demais usam maiúsculas (“Obesidade e Diabetes”, “Distúrbios do Aparelho Locomotor”). O site uniformizou “prescrição” → “Prescrição”, mas não este caso.",
        "Documento .doc do currículo.",
        "Definir o critério de maiúsculas. Se for uniformizar: “Hipertensão e Cardiovascular” no documento e registro da correção no site.", "Relatório, M3")
add(E, "MÉDIA", "DOCUMENTO", "2611 Bacharelado - total do 4º termo (22) diferente da soma (20)",
    "O 4º termo lista disciplinas que somam 20 créditos, mas a linha “Créditos” diz 22.",
    "curriculo-2611---bacharelado-noturno-a-partir-de-2015.doc; conferido por duas leituras. O site mostra aviso.",
    "Corrigir o total (os totais do 4º e do 5º termos parecem trocados).", "Relatório, seção 6")
add(E, "MÉDIA", "DOCUMENTO", "2611 Bacharelado - total do 5º termo (20) diferente da soma (22)",
    "O 5º termo lista disciplinas que somam 22 créditos, mas a linha “Créditos” diz 20.",
    "curriculo-2611---bacharelado-noturno-a-partir-de-2015.doc. O site mostra aviso.",
    "Corrigir o total (os totais do 4º e do 5º termos parecem trocados).", "Relatório, seção 6")
add(E, "MÉDIA", "DOCUMENTO", "2610 Bacharelado - “147 Créditos – 2005 H/A” no quadro",
    "O quadro final do 2610 Bacharelado diz “Créditos em Disciplinas do Currículo 147 Créditos – 2005 H/A”. 147 × 15 = 2.205; o 2611 Bacharelado traz 2205 para os mesmos 147 créditos.",
    "curriculo-2610---bacharelado-integral-a-partir-de-2015.doc. O site reproduz 2005 e mostra aviso.",
    "Corrigir para 2205 H/A no documento. Depois, regerar o site.", "Relatório, seção 6")
add(E, "BAIXA", "DOCUMENTO", "2611 Bacharelado - título “Licenciatura em Educação Física: Bacharelado”",
    "O quadro final do 2611 Bacharelado começa com “Licenciatura em Educação Física: Bacharelado”. Nos documentos do 2610 está “Graduação em Educação Física: Bacharelado”.",
    "curriculo-2611---bacharelado-noturno-a-partir-de-2015.doc. O site não reproduz esse título.",
    "Corrigir para “Graduação em Educação Física: Bacharelado”.", "Novo (encontrado ao detalhar as correções)")
add(E, "BAIXA", "DOCUMENTO", "Pré-requisitos indicados por siglas",
    "A coluna Pré-Requisito usa siglas sem legenda: “PPCCEF -I” e “FE - I”. O site as ligou a “Processos de Produção do Conhecimento Científico em Educação Física I” e “Fisiologia do Exercício I”, por dedução.",
    "Os quatro documentos .doc. O site mostra aviso com a interpretação.",
    "Escrever o nome completo das disciplinas (ou incluir legenda) e confirmar a interpretação usada no site.", "Relatório, seção 6")

# ---- FC · Pedagogia, Matemática
add("fc/pedagogia", "BAIXA", "SITE", "Rótulo “Currículo 2023” não consta do documento",
    "A ficha mostra “Currículo: 2023”. O documento não dá número de currículo: o título é “Estrutura Curricular do Curso Pedagogia – Proposta de Reestruturação 2023”.",
    "matriz-curricular-final---21-12-a-partir-de-2023.pdf; campo “curriculo” do arquivo de dados.",
    "Deixar “curriculo” vazio (a vigência já informa 2023) ou obter o número com a coordenação. Regerar.", "Novo (encontrado ao detalhar as correções)")
add("fc/pedagogia", "BAIXA", "DOCUMENTO", "Documento vigente ainda se intitula “Proposta de Reestruturação”",
    "A matriz publicada como vigente (ingressantes a partir de 2023) tem no título “Proposta de Reestruturação 2023”, o que sugere documento ainda não aprovado.",
    "Título do PDF.", "Publicar a versão aprovada, com o número do currículo.", "Novo (encontrado ao detalhar as correções)")
add("fc/pedagogia", "BAIXA", "DOCUMENTO", "Matriz sem códigos e sem pré-requisitos",
    "A matriz traz só nomes e créditos. Sem códigos e pré-requisitos, a árvore da Pedagogia não tem ligações.",
    "PDF de 1 página; transcrição independente.", "Publicar a relação com códigos e requisitos (por exemplo, a do Sistema de Graduação).", "Relatório, seção 6")
add("fc/pedagogia", "BAIXA", "DOCUMENTO", "Espaços a mais em dois nomes",
    "“Expressão Oral    e Escrita na Educação Infantil” e “Corporeidade   e Educação” estão digitados com vários espaços antes do “e”.",
    "Texto do PDF. O site exibe com um espaço.", "Retirar os espaços a mais.", "Novo (encontrado ao detalhar as correções)")
add("fc/matematica", "BAIXA", "DOCUMENTO", "8101A com 06 créditos no 5º termo e 07 no 6º",
    "O código 8101A - Estágio Curricular Supervisionado I (anual) aparece com 06 créditos no 5º termo e 07 no 6º termo.",
    "grade-curricular-1507 (página do curso). O site reproduz e mostra aviso.", "Confirmar se a diferença é intencional; se não for, corrigir a tabela.", "Relatório, seção 6")
add("fc/matematica", "BAIXA", "DOCUMENTO", "Nome abreviado - “Desenho Geométrico e Geom. Descritiva”",
    "5122A está grafada com abreviação: “Desenho Geométrico e Geom. Descritiva”.",
    "grade-curricular-1507, 5º termo.", "Escrever o nome por extenso (“Geometria Descritiva”).", "Novo (encontrado ao detalhar as correções)")

# ---- FC · BCC (documento)
add("fc/bcc", "BAIXA", "DOCUMENTO", "PDF do currículo grafa “A0lgebra Linear”",
    "No PDF oficial do currículo 2105, a disciplina 4609 está impressa como “A0lgebra Linear”. O site exibe “Álgebra Linear” (correção autorizada).",
    "bcc-curriculo-2105-com-quadro-resumo.pdf, 2º termo.", "Corrigir o PDF publicado.", "Relatório da 1ª revisão (correção autorizada 4609)")
add("fc/bcc", "BAIXA", "DOCUMENTO", "PDF do currículo grafa “Geometria AnalÍtica” nos requisitos",
    "Na coluna Pré-Requisito de 4616 - Métodos Numéricos Computacionais, o nome está como “Geometria AnalÍtica” (Í maiúsculo).",
    "bcc-curriculo-2105-com-quadro-resumo.pdf, 3º termo. O site liga o requisito à disciplina certa.", "Corrigir o PDF publicado.", "Relatório da 1ª revisão")
add("fc/bcc", "BAIXA", "DOCUMENTO", "PDF do currículo cita “Estrutura de Dados I” (sem s) nos requisitos",
    "Em duas linhas da coluna Pré-Requisito aparece “Estrutura de Dados I”; o nome da disciplina 4617 é “Estruturas de Dados I”.",
    "bcc-curriculo-2105-com-quadro-resumo.pdf (duas ocorrências). O site liga o requisito à disciplina certa.", "Corrigir o PDF publicado.", "Relatório da 1ª revisão")

# ------------------------------------------------------------------------------------------
# 4) Itens gerais do projeto (não pertencem a um curso)
# ------------------------------------------------------------------------------------------
G = "revisao/gerais-do-projeto"
add(G, "ALTA", "SITE", "Testes de fidelidade comparam o gerador com ele mesmo",
    "testes/conferir_fontes.py relê as fontes com o mesmo leitor (ferramentas/fontes_sg.py) e as mesmas transcrições (ferramentas/transcricoes.py) que geraram os dados. Por isso passou 6.250/6.250 sem detectar o requisito trocado da Produção nem a transcrição errada da Química. O README promete que ele “relê as fontes oficiais”.",
    "Relatório, seção 1.",
    "Levar para testes/ as leituras independentes de revisao/ (segunda_leitura_sg.py, comparar_feb.py, comparar_independente.py com transcricoes-independentes/, comparar_edf.py) e corrigir a descrição no README.",
    "Relatório, A7")
add(G, "BAIXA", "SITE", "README repete afirmações desmentidas pela revisão",
    "README.md: (a) abertura diz que há quadro de optativas “sempre que o documento traz … a exigência”, mas Civil, Mecânica e Produção ficaram sem; (b) seção 7 diz que Relações Públicas e Arquitetura não informam o número do currículo (informam: 2402 e 2011); (c) seção 8 descreve conferir_fontes.py como leitura independente.",
    "README.md, abertura e seções 7 e 8.", "Atualizar o README depois das correções A3, A4 e A7.", "Relatório, B4")
add(G, "BAIXA", "SITE", "Regra percentual usa bases diferentes para a meta e para o concluído",
    "Em assets/arvore-grade.js, a meta da regra percentual é calculada sobre a carga de OBR + TRA + EST, mas as horas concluídas contam só OBR. Hoje nenhum curso com regra percentual tem TRA/EST na grade, então o resultado está certo; fica errado no primeiro curso que tiver.",
    "Funções regraAtendida e horasConcluidas(true).", "Usar a mesma base nos dois lados.", "Relatório, B5")

# ------------------------------------------------------------------------------------------
# Escrita
# ------------------------------------------------------------------------------------------
def nome_arquivo(i, titulo):
    t = re.sub(r'[\\/:*?"<>|“”‘’]', "", titulo)
    t = re.sub(r"\s+", " ", t).strip(" .")
    return f"{i:02d} - {t[:90].strip()}.txt"


NOMES = {}
for arq in glob.glob(os.path.join(RAIZ, "ferramentas", "cursos-gerados.json")):
    for c in json.load(open(arq, encoding="utf-8")):
        NOMES[c["pasta"]] = c["titulo"]
NOMES.update({"fc/bcc": "Bacharelado em Ciência da Computação", "fc/bsi": "Bacharelado em Sistemas de Informação", G: "Itens gerais do projeto (não pertencem a um curso)"})
RESP = {"SITE": "quem mantém o site (arquivos deste projeto)", "DOCUMENTO": "Conselho de Curso / Seção Técnica de Graduação (documento oficial)",
        "DECISÃO": "Conselho de Curso decide; depois, quem mantém o site aplica"}
total = 0
resumo = []
for pasta in sorted(ITENS):
    itens = sorted(ITENS[pasta], key=lambda x: (ORDEM[x["grav"]], {"SITE": 0, "DECISÃO": 1, "DOCUMENTO": 2}[x["onde"]]))
    base = os.path.join(SAIDA, pasta)
    sub = os.path.join(base, "Correções necessárias")
    os.makedirs(sub, exist_ok=True)
    curso = NOMES.get(pasta, pasta)
    linhas = [f"CORREÇÕES NECESSÁRIAS — {curso}", f"Pasta: {pasta}", "Origem: revisão de 01/10/2026 (revisao/relatorio-de-revisao-expansao.md)", "",
              f"Total: {len(itens)} correção(ões). Cada uma tem o seu arquivo na pasta “Correções necessárias”.", "",
              "Onde corrigir:", "  SITE      = arquivos deste projeto (quem mantém o site)", "  DOCUMENTO = documento oficial do curso (Conselho de Curso / Seção de Graduação)",
              "  DECISÃO   = a coordenação precisa decidir antes de qualquer alteração", ""]
    cont = {}
    for i, it in enumerate(itens, 1):
        nome = nome_arquivo(i, it["titulo"])
        cont[it["grav"]] = cont.get(it["grav"], 0) + 1
        linhas.append(f"{i:02d}. [{it['grav']}] [{it['onde']}] {it['titulo']}")
        linhas.append(f"      arquivo: Correções necessárias/{nome}")
        corpo = [f"CORREÇÃO NECESSÁRIA nº {i:02d} de {len(itens)} — {curso}", "", f"Título: {it['titulo']}", f"Gravidade: {it['grav']}",
                 f"Onde corrigir: {it['onde']}", f"Responsável: {RESP[it['onde']]}", "", "O QUE ESTÁ ERRADO", it["errado"], "", "EVIDÊNCIA", it["evidencia"], "",
                 "CORREÇÃO NECESSÁRIA", it["correcao"], "", f"Referência: {it['ref']}", "Situação: pendente", ""]
        open(os.path.join(sub, nome), "w", encoding="utf-8", newline="\r\n").write("\n".join(corpo))
        total += 1
    linhas[4] = f"Total: {len(itens)} correção(ões) — " + ", ".join(f"{v} {k.lower()}(s)" for k, v in sorted(cont.items(), key=lambda kv: ORDEM[kv[0]])) + ". Cada uma tem o seu arquivo na pasta “Correções necessárias”."
    linhas += ["", "Observação: estes arquivos são de trabalho. Não publicar no portal junto com index.html e dados-*.js."]
    open(os.path.join(base, "Correções necessárias.txt"), "w", encoding="utf-8", newline="\r\n").write("\n".join(linhas) + "\n")
    resumo.append((pasta, len(itens), cont))
for p, n, c in resumo:
    print(f"{p:<34} {n:>3}  " + ", ".join(f"{v} {k}" for k, v in sorted(c.items(), key=lambda kv: ORDEM[kv[0]])))
print("total de arquivos de correção:", total, "em", len(resumo), "pastas")
