"""Transcrições das matrizes publicadas como imagem, tabela de PDF sem códigos ou texto corrido.

Cada disciplina é transcrita com os números EXATAMENTE como constam do documento (créditos,
horas, códigos). Nomes ficam como no documento; correções de grafia são aplicadas depois, em
construir.py, e registradas em cada arquivo de dados (campo "correcoes").

Requisitos são indicados pelo NOME citado no documento; construir.py os resolve para a
disciplina correspondente e registra qualquer requisito que não corresponda a uma disciplina
da matriz (fica como texto, em "preTexto").
"""


def D(t, n, cr=None, ch=None, **kw):
    d = {"t": t, "n": n}
    if cr is not None:
        d["cr"] = cr
    if ch is not None:
        d["ch"] = ch
    d.update(kw)
    return d


# ---------------------------------------------------------------------------
# Ciências Biológicas — currículos 2710 (Bacharelado, integral) e 2711 (Licenciatura, noturno)
# Fonte: planilhas por ano/semestre (créditos e horas). "A (anual)": a disciplina aparece nos
# dois semestres do ano, com os créditos contados em cada um (é assim que os totais fecham).
# ---------------------------------------------------------------------------
BIO_1 = [
    D(1, "Anatomia Geral e Humana", 3, 45), D(1, "Biologia Celular e Molecular", 4, 60),
    D(1, "Geologia", 2, 30), D(1, "Sistemática Biológica", 2, 30), D(1, "Química Geral", 2, 30),
    D(1, "Física Geral", 3, 45), D(1, "Morfologia Vegetal: Órgãos Vegetativos", 4, 60),
]

BIO_2710 = BIO_1 + [
    D(2, "Histologia Básica e Comparada", 3, 45), D(2, "Embriologia Comparada", 3, 45),
    D(2, "Biofísica Geral", 4, 60), D(2, "Matemática", 4, 60), D(2, "Química Orgânica", 2, 30),
    D(2, "Morfologia Vegetal: Órgãos Reprodutivos", 4, 60), D(2, "Protistas e Fungos", 4, 60),
    D(2, "Direito, Legislação e Ética", 2, 30), D(2, "Fundamentos de Extensão Universitária", 2, 30),

    D(3, "Bioquímica", 4, 60), D(3, "Genética Geral", 3, 45),
    D(3, "Fisiologia Geral e Comparada: Regulação", 4, 60),
    D(3, "Zoologia dos Metazoa Basais e Lophotrochozoa", 4, 60),
    D(3, "Sistemática de Primoplantae sem sementes", 4, 60), D(3, "Imunologia Geral", 2, 30),
    D(3, "Microbiologia Básica", 3, 45), D(3, "Bioquímica Experimental", 1, 15, co=["Bioquímica"]),
    D(3, "Projeto Integrador 1", 4, 60, anual=True),

    D(4, "Metodologia Científica", 2, 30), D(4, "Fisiologia Geral e Comparada: Sistemas", 2, 30),
    D(4, "Zoologia de Ecdysozoa e Deuterostomia", 4, 60), D(4, "Sistemática de Spermatophyta", 4, 60),
    D(4, "Parasitologia Geral e Humana", 3, 45), D(4, "Biologia Molecular", 4, 60),
    D(4, "Ecologia de Populações", 4, 60), D(4, "Nanobiotecnologia", 2, 30), D(4, "Biossegurança", 2, 30),
    D(4, "Projeto Integrador 1", 4, 60, anual=True),

    D(5, "Zoologia de Anamniota", 4, 60), D(5, "Paleontologia", 4, 60),
    D(5, "Fisiologia Vegetal: Metabolismo", 4, 60), D(5, "Educação Ambiental", 2, 30),
    D(5, "Genética Molecular", 3, 45), D(5, "Conservação e Manejo", 2, 30), D(5, "Bioestatística", 4, 60),
    D(5, "Projeto Integrador 2", 4, 60, anual=True),

    D(6, "Zoologia de Amniota", 4, 60), D(6, "Fisiologia Vegetal: Desenvolvimento", 4, 60),
    D(6, "Evolução", 4, 60), D(6, "Ecologia Comunidades", 3, 45), D(6, "Paleoecologia Evolutiva", 4, 60),
    D(6, "Biodiversidade Animal", 4, 60), D(6, "Bioindicadores", 4, 60),
    D(6, "Planejamento e Gestão Ambiental", 4, 60), D(6, "Projeto Integrador 2", 4, 60, anual=True),

    D(7, "Ecologia de Ecossistemas", 3, 45), D(7, "Biogeografia", 2, 30), D(7, "Ecologia de Campo", 4, 60),
    D(7, "Gestão Ambiental de Resíduos Sólidos", 4, 60), D(7, "Legislação do Profissional Biólogo", 2, 30),
    D(7, "Projeto Integrador 3", 4, 60, anual=True),

    D(8, "Fundamentos de Ciências Humanas", 2, 30),
    D(8, "Impacto das Mudanças Climáticas na Biodiversidade", 4, 60),
    D(8, "Produção Vegetal Sustentável", 4, 60), D(8, "Evolução da Diversidade Biológica", 2, 30),
    D(8, "Projeto Integrador 3", 4, 60, anual=True),
]
BIO_2710_TOTAIS = {1: (20, 300), 2: (28, 420), 3: (29, 435), 4: (31, 465), 5: (27, 405), 6: (35, 525), 7: (19, 285), 8: (16, 240)}
BIO_2710_QUADRO = [
    ["Disciplinas Obrigatórias* (incluindo 390h de ACEUs)", 205, 3075],
    ["Estágio curricular", 24, 360],
    ["Trabalho de Conclusão de Curso", 4, 60],
    ["Atividades Complementares", 14, 210],
]

EST_BIO = "Estágio Supervisionado em Ensino de Ciências e Biologia: "
MPE_BIO = "Metodologia e Prática de Ensino de Ciências e Biologia: "
BIO_2711 = BIO_1 + [
    D(2, "Histologia Básica e Comparada", 3, 45), D(2, "Embriologia Comparada", 3, 45),
    D(2, "Biofísica Geral", 4, 60), D(2, "Morfologia Vegetal: Órgãos Reprodutivos", 4, 60),
    D(2, "Direito, Legislação e Ética", 2, 30), D(2, "Química Orgânica", 2, 30),
    D(2, "Protistas e Fungos", 4, 60), D(2, "Fundamentos de Extensão Universitária", 2, 30),

    D(3, "Bioquímica", 4, 60), D(3, "Sistemática de Primoplantae sem sementes", 4, 60),
    D(3, "Zoologia dos Metazoa Basais e Lophotrochozoa", 4, 60), D(3, "Microbiologia Básica", 3, 45),
    D(3, "Genética Geral", 3, 45), D(3, "Políticas Públicas Em Educação", 4, 60),
    D(3, "Projeto Integrador 1", 4, 60, anual=True),

    D(4, "Zoologia de Ecdysozoa e Deuterostomia Basais", 4, 60), D(4, "Matemática", 4, 60),
    D(4, "Sistemática de Spermatophyta", 4, 60),
    D(4, "Metodologia Ciêntifica Aplicada ao Ensino e a pesquisa", 2, 30),
    D(4, "Psicologia da Educação", 4, 60), D(4, "Fundamentos de Educação", 4, 60),
    D(4, "Projeto Integrador 1", 4, 60, anual=True),

    D(5, "Zoologia de Anamniota", 4, 60), D(5, "Fisiologia Vegetal: Metabolismo", 4, 60),
    D(5, "Educação Ambiental", 2, 30), D(5, "Imunologia Geral", 2, 30),
    D(5, "Didática e Metodologia do Ensino de Ciências Naturais", 4, 60),
    D(5, "Sociologia da Educação", 4, 60), D(5, "Projeto Integrador 2", 4, 60, anual=True),

    D(6, "Zoologia de Amniota", 4, 60), D(6, "Fisiologia Vegetal: Desenvolvimento", 4, 60),
    D(6, "Ecologia Populações", 4, 60), D(6, "Parasitologia Geral e Humana", 3, 45),
    D(6, MPE_BIO + "Estudo da Realidade Escolar", 4, 60, co=[EST_BIO + "Estudo da Realidade Escolar"]),
    D(6, "Projeto Integrador 2", 4, 60, anual=True),

    D(7, "Genética Molecular", 3, 45), D(7, "Paleontologia", 4, 60),
    D(7, "Educação Especial e Inclusiva", 4, 60), D(7, "História e Filosofia das Ciências Naturais", 4, 60),
    D(7, MPE_BIO + "Abordagens Didáticas e Recursos de Apoio", 4, 60, co=[EST_BIO + "Abordagens Didáticas e Recursos de Apoio"]),
    D(7, "Projeto Integrador 3", 4, 60, anual=True),

    D(8, "Biologia Molecular", 4, 60), D(8, "Ecologia Comunidades", 3, 45), D(8, "Evolução", 4, 60),
    D(8, MPE_BIO + "Sociedade, Escola e Ensino", 4, 60, co=[EST_BIO + "Sociedade, Escola e Ensino"]),
    D(8, "Projeto Integrador 3", 4, 60, anual=True),

    D(9, "Fisiologia Geral e Comparada: Regulação", 4, 60), D(9, "Ecologia Ecossistemas", 3, 45),
    D(9, "Libras, Educação Especial e Inclusiva", 4, 60),
    D(9, MPE_BIO + "Relações Ciência-Sociedade e Temas Ambientais", 4, 60, co=[EST_BIO + "Relações Ciência-Sociedade e Temas Ambientais"]),

    D(10, "Fisiologia Geral e Comparada: Sistemas", 2, 30), D(10, "Elaboração de Material Didático", 4, 60),
    D(10, "História da Educação Brasileira", 4, 60),
    D(10, MPE_BIO + "Currículo e Processos de Avaliação", 4, 60, co=[EST_BIO + "Currículo e Processos de Avaliação"]),
]
BIO_2711_TOTAIS = {1: (20, 300), 2: (24, 360), 3: (26, 390), 4: (26, 390), 5: (24, 360), 6: (23, 345), 7: (23, 345), 8: (19, 285), 9: (15, 225), 10: (14, 210)}
BIO_2711_QUADRO = [
    ["Disciplinas Obrigatórias* (incluindo 392h de ACEUs)", 214, 3210],
    ["Estágio curricular", 27, 405],
    ["Trabalho de Conclusão de Curso", 0, None],
    ["Atividades Teórico-práticas de aprofundamento", 14, 210],
]

# ---------------------------------------------------------------------------
# Pedagogia — matriz para ingressantes a partir de 2023 (créditos; carga por termo em horas)
# ---------------------------------------------------------------------------
PEDAGOGIA = [
    D(1, "História da Educação", 4), D(1, "Filosofia da Educação I", 4), D(1, "Psicologia da Educação I", 4),
    D(1, "Fundamentos da Educação", 4), D(1, "Sociologia da Educação I", 4),

    D(2, "História da Educação Brasileira", 4), D(2, "Filosofia da Educação II", 4),
    D(2, "Psicologia da Educação II", 4), D(2, "Leitura e Produção de Textos", 4), D(2, "Sociologia da Educação II", 4),

    D(3, "Política Educacional e Legislação de Ensino", 4), D(3, "Metodologia da Pesquisa Científica I", 2),
    D(3, "História da Infância", 2), D(3, "Expressão Oral e Escrita na Educação Infantil", 4),
    D(3, "Currículos, Programas e Projetos", 4), D(3, "Didática I", 4),

    D(4, "Didática II", 4), D(4, "Metodologia da Pesquisa Científica II", 2), D(4, "Ludicidade e Educação", 2),
    D(4, "Alfabetização e Letramento", 4), D(4, "Corporeidade e Educação", 4),
    D(4, "Educação Especial e Inclusiva", 4), D(4, "Introdução à LIBRAS", 4),

    D(5, "Língua Portuguesa: conteúdos e metodologias I", 4),
    D(5, "Políticas Públicas para a Infância e Juventude", 4),
    D(5, "Educação Física: conteúdos e metodologias", 4), D(5, "Matemática: conteúdos e metodologias I", 4),
    D(5, "Organização do Trabalho Pedagógico na Educação Infantil", 4), D(5, "Práxis Pedagógica I", 4),
    D(5, "Estágio Curricular Supervisionado na Educação Básica I", 9, 135, tipo="EST"),

    D(6, "Língua Portuguesa: conteúdos e metodologias II", 4), D(6, "Geografia: conteúdos e metodologias", 4),
    D(6, "Arte: conteúdos e metodologias", 4), D(6, "Matemática: conteúdos e metodologias II", 4),
    D(6, "Organização do Trabalho Pedagógico no Ensino Fundamental – anos iniciais", 4),
    D(6, "Práxis Pedagógica II", 4),
    D(6, "Estágio Curricular Supervisionado na Educação Básica II", 9, 135, tipo="EST"),

    D(7, "História: conteúdos e metodologias", 4), D(7, "Trabalho de Conclusão de Curso I", 2, tipo="TRA"),
    D(7, "Problemas de aprendizagem escolar I", 2), D(7, "Ciências da natureza: conteúdos e metodologias", 4),
    D(7, "Literatura Infantojuvenil", 4), D(7, "Gestão da Educação Básica", 4), D(7, "Práxis Pedagógica III", 4),
    D(7, "Estágio Curricular Supervisionado na Educação Básica III", 10, 150, tipo="EST"),

    D(8, "Cultura e Educação", 4), D(8, "Trabalho de Conclusão de Curso II", 2, tipo="TRA"),
    D(8, "Problemas de aprendizagem escolar II", 2), D(8, "Tecnologias digitais na prática pedagógica", 4),
    D(8, "Organização do Trabalho na escola e a Coordenação Pedagógica", 4),
    D(8, "Organização do Trabalho Pedagógico na Educação de Jovens e Adultos", 4),
]
# "C.H." por termo, como impresso (disciplinas + estágio)
PEDAGOGIA_CH = {1: "300 horas", 2: "300 horas", 3: "300 horas", 4: "360 horas", 5: "360 horas + 135 horas", 6: "360 horas + 135 horas", 7: "360 horas + 150 horas", 8: "300 horas"}

# ---------------------------------------------------------------------------
# Psicologia — currículo 1212/1213 (integral e noturno), ingressantes a partir de 2023
# Colunas: Créditos · Atividade Extraclasse ou Prática · Extensão · Pré-Requisitos · Correquisitos
# ---------------------------------------------------------------------------
AEC = "Análise Experimental do Comportamento"
ACA = "Análise do Comportamento Aplicada"
FPP = "Fenômenos e Processos Psicológicos: Psicologia Sócio-histórica"
PSICOLOGIA = [
    D(1, "Introdução à Psicologia como Ciência e Profissão", 2),
    D(1, "Constituição Histórica da Psicologia", 4), D(1, "Psicologia do Desenvolvimento: Ciclo Vital", 4),
    D(1, "Bases Biológicas do Comportamento", 4), D(1, "Sociologia", 4, xc=2), D(1, "Filosofia", 4),
    D(1, "Metodologia Científica I", 2), D(1, "Fundamentos da Análise do Comportamento", 2),

    D(2, "Neurofisiologia", 4), D(2, "Estatística Aplicada à Psicologia", 4),
    D(2, "Metodologia Científica II", 4, xc=2, pre=["Metodologia Científica I"]),
    D(2, "Antropologia I", 2),
    D(2, "Laboratório de " + AEC + " I", 4, xc=2, pre=["Fundamentos da Análise do Comportamento"],
      co=["Laboratório de " + AEC + " I"]),
    D(2, AEC + " I", 4, pre=["Fundamentos da Análise do Comportamento"], co=[AEC + " I"]),
    D(2, "Análise Histórico-Social do Desenvolvimento Humano", 2),
    D(2, "Fundamentos Epistemológicos da Psicologia Sócio-histórica", 2),
    D(2, "Fundamentos das Teorias Sistêmica e Complexa", 2),

    D(3, "Antropologia II", 2, pre=["Antropologia I"]),
    D(3, "Estágio Básico - Pesquisa 1", 2, xc=2, pre=["Metodologia Científica II"]),
    D(3, "Introdução à Extensão", 4, ext=4),
    D(3, "Análise do Comportamento Verbal", 2, pre=[AEC + " I"], co=[AEC + " II"]),
    D(3, "Laboratório de " + AEC + " II", 4, xc=2, pre=[AEC + " I"], co=[AEC + " II"]),
    D(3, AEC + " II", 2, pre=[AEC + " I"], co=["Laboratório de " + AEC + " II"]),
    D(3, FPP + " I", 4, pre=["Fundamentos Epistemológicos da Psicologia Sócio- histórica", "Análise Histórico-Social do Desenvolvimento Humano"]),
    D(3, "Psicologia da Educação: Fundamentos Filosóficos", 4, pre=["Fundamentos Epistemológicos da Psicologia Sócio- histórica", "Análise Histórico-Social do Desenvolvimento Humano"]),
    D(3, "Teorias e Práticas Sistêmicas e Complexas", 4, ext=1, pre=["Fundamentos das Teorias Sistêmicas e Complexas"]),
    D(3, "Fundamentos da Psicanálise", 2),

    D(4, "Avaliação Psicológica I", 4, xc=2),
    D(4, "Estágio Básico - Pesquisa 2", 2, xc=2),
    D(4, "Análise Comportamental do Desenvolvimento Humano", 2, pre=[AEC + " II", "Análise do Comportamento Verbal"]),
    D(4, ACA + ": Processos Educativos I", 2, pre=[AEC + " II", "Laboratório de " + AEC + " II"], semSemestre=True),
    D(4, FPP + " II", 6, ext=2, pre=[FPP + " I"], co=["Introdução à extensão"]),
    D(4, "Políticas Públicas, Instituições e Saúde", 4),
    D(4, "Psicologia Escolar I", 4, pre=["Psicologia da Educação: Fundamentos Filosóficos"]),
    D(4, "Teorias Psicanalíticas I", 4, pre=["Fundamentos da Psicanálise"]),

    D(5, "Avaliação Psicológica II", 4, xc=2, pre=["Avaliação psicológica I"]),
    D(5, ACA + ": Processos Educativos II", 2, pre=[ACA + ": Processos Educativos I"]),
    D(5, ACA + ": Delineamentos Culturais", 2, pre=[AEC + " II"]),
    D(5, "Atividades Extensionistas em Educação e Sociedade I", 2, ext=2,
      pre=["Análise do comportamento Aplicada: Processos Educativos I", "Análise do comportamento Aplicada: Delineamentos Culturais"],
      co=[ACA + ": Processos Educativos II"]),
    D(5, "Psicologia Escolar II", 6, ext=2, pre=["Psicologia Escolar I"]),
    D(5, "Psicologia Social I", 4, co=["Fenômenos e processos Psicológicos: Psicologia Sócio-Histórica II", "Políticas Públicas, Instituições e Saúde"]),
    D(5, "Teorias Psicanalíticas II", 4, pre=["Teorias Psicanalíticas I"]),
    D(5, "Orientação Profissional I", 2, pre=["Teorias e Práticas Sistêmicas e Complexas", "Avaliação Psicológica I"]),

    D(6, "Psicopatologia", 4, pre=["Teorias Psicanalíticas II", "Psicologia do Desenvolvimento: Ciclo Vital"],
      co=["Terapia Comportamental", "Clínica Psicanalítica I"]),
    D(6, "Terapia Comportamental", 4, pre=["Análise Comportamental do Desenvolvimento Humano", "Avaliação Psicológica II"],
      co=["Psicopatologia"]),
    D(6, ACA + ": Educação Especial e Inclusiva", 4,
      pre=["Análise Comportamental do Desenvolvimento Humano", ACA + ": Processos Educativos"], co=["Psicopatologia"]),
    D(6, "Atividades Extensionistas em Educação e Sociedade II", 2, ext=2,
      pre=["Atividades Extensionistas em Educação e Sociedade I"], co=["Análise do comportamento Aplicada: Educação Especial e Inclusiva"]),
    D(6, "Psicologia Social II", 4, pre=["Psicologia Social I"]),
    D(6, "Orientação Profissional II", 2),
    D(6, "Clínica Psicanalítica I", 4, ext=2, pre=["Políticas Públicas, Instituições e Saúde", "Teorias Psicanalíticas II"], co=["Psicopatologia"]),
    D(6, "Optativa", 4, xc=2, tipo="SLOT"),

    D(7, ACA + " à Saúde", 4, pre=["Terapia Comportamental"]),
    D(7, "Atividades Extensionistas em Clínica e Saúde I", 2, ext=2, pre=["Terapia Comportamental"]),
    D(7, "Psicologia e Inclusão", 2), D(7, "Intervenção e Processos Grupais", 2),
    D(7, "Psicologia e Comunidade", 4, ext=2), D(7, "Psicologia Organizacional e do Trabalho I", 4),
    D(7, "Clínica Psicanalítica II", 4, ext=2, pre=["Clínica Psicanalítica I", "Psicopatologia"]),
    D(7, "Optativa", 4, xc=2, tipo="SLOT"),

    D(8, "Desenvolvimento e Educação Sexual", 4, pre=["Psicologia do Desenvolvimento: Ciclo Vital", "Psicologia Escolar I"]),
    D(8, "Psicopatologia e Clínica Existencial", 4, pre=["Psicopatologia"], co=["Clínica Psicanalítica III"]),
    D(8, "Ética Profissional", 4),
    D(8, "Laboratório de " + ACA + " aos Processos Clínicos", 2, pre=[ACA + " à Saúde"]),
    D(8, "Atividades Extensionistas em Clínica e Saúde II", 2, ext=2, pre=["Atividades Extensionistas em Clínica e Saúde I"]),
    D(8, "Psicologia Organizacional e do Trabalho II", 4, co=["Psicologia Organizacional e do Trabalho I"]),
    D(8, "Clínica Psicanalítica III", 4, pre=["Clínica Psicanalítica II"], co=["Psicopatologia e Clínica Existencial"]),
    D(8, "Atividades Complementares", 2, xc=2, tipo="AC"),

    D(9, "Disciplinas do Programa de Estágio Supervisionado em Psicologia Clínica e da Saúde*", 18, xc=8, ext=2, tipo="EST", anual=True, semestreImpresso="9 e 10 (Anual)"),
    D(9, "Disciplinas do Programa de Estágio Supervisionado em Psicologia e Educação*", 18, xc=8, ext=2, tipo="EST", anual=True, semestreImpresso="10 e 10 (Anual)"),
    D(9, "Disciplinas do Programa de Estágio Supervisionado em Psicologia Organizacional e do Trabalho*", 18, xc=8, ext=2, tipo="EST", anual=True, semestreImpresso="11 e 10 (Anual)"),
    D(9, "DIsciplinas do Programa de Estágio Supervisionado em Psicologia Social*", 18, xc=8, ext=2, tipo="EST", anual=True, semestreImpresso="12 e 10 (Anual)"),
]
PSICOLOGIA_OBS = "*São Contabilizadas Apenas o Referente a 3 opções de Estágio"
PSICOLOGIA_QUADRO = {
    "titulo": "Carga horária segundo as DCN (ajuste do PPP)",
    "colunas": ["Créditos", "Horas"],
    "linhas": [
        ["Práticas (EST+AACC)", 54, 810],
        ["Aula (Sala +AE)", 189, 2835],
        ["Extensão", 29, 435],
    ],
    "total": [272, 4080],
    "detalhamento": [
        ["Disciplinas teóricas e teórico-práticas", 189, 2835],
        ["Em Sala de Aula", 143, 2145], ["Em Atividade Extra-Classe", 46, 690],
        ["Práticas", 54, 810], ["Estágio Básico", 4, 60], ["Estágio Específico", 48, 720], ["AACC", 2, 30],
        ["Extensão", 29, 435],
    ],
}

# ---------------------------------------------------------------------------
# Química — Licenciatura em Química e Bacharelado em Química Tecnológica (matrizes 2023)
# Fonte: matrizes publicadas como imagem (carga horária por disciplina). Disciplinas que
# ocupam dois semestres aparecem nos dois, como na matriz.
# ---------------------------------------------------------------------------
QUI_ANO1 = [
    D(1, "Química Geral 1", ch=60), D(1, "Química Geral Experimental 1", ch=60), D(1, "Pré-Cálculo", ch=60),
    D(1, "História e Filosofia da Ciência e Ensino de Ciências", ch=60), D(1, "Prática de Leitura e Escrita", ch=60),
    D(2, "Química Geral 2", ch=60), D(2, "Química Geral Experimental 2", ch=60),
    D(2, "Cálculo – Derivadas e Integrais em Uma Variável", ch=60), D(2, "Cálculo Vetorial e Geometria Analítica", ch=60),
    D(2, "Biologia Geral", ch=60), D(2, "Extensão Universitária: diretrizes e princípios", ch=30),
    D(3, "Química Inorgânica 1", ch=60), D(3, "Química Inorgânica Experimental 1", ch=30),
    D(3, "Fundamentos de Mineralogia e Cristalografia", ch=30), D(3, "Cálculo – Derivadas Múltiplas", ch=60),
    D(3, "Física 1", ch=60), D(3, "Física Experimental 1", ch=30),
    D(3, "Atividades Orientadas de Extensão Universitária 1", ch=60, anual=True),
]
QUI_LIC = QUI_ANO1 + [
    D(4, "Atividades Orientadas de Extensão Universitária 1", ch=60, anual=True), D(4, "Química Inorgânica 2", ch=60),
    D(4, "Química Inorgânica Experimental 2", ch=30), D(4, "Físico-Química 1", ch=60),
    D(4, "Fundamentos da Educação", ch=30), D(4, "Física 2", ch=60), D(4, "Física Experimental 2", ch=30),

    D(5, "Físico-Química 2", ch=60), D(5, "Físico-Química Experimental 1", ch=30), D(5, "Química Ambiental 1", ch=30),
    D(5, "Física 3", ch=60), D(5, "Psicologia da Educação", ch=60),
    D(5, "Política Educacional Brasileira para o Ensino Fundamental e Médio", ch=60),
    D(5, "Atividades Orientadas de Extensão Universitária 2", ch=60, anual=True),

    D(6, "Atividades Orientadas de Extensão Universitária 2", ch=60, anual=True), D(6, "Físico-Química 3", ch=60),
    D(6, "Físico-Química Experimental 2", ch=30), D(6, "Química Analítica Qualitativa", ch=30),
    D(6, "Química Analítica Qualitativa Experimental", ch=60), D(6, "Didática das Ciências da Natureza", ch=60),
    D(6, "Metodologia e Prática de Ensino de Ciências", ch=30),
    D(6, "Estágio Supervisionado em Ensino de Ciências para o Ensino Fundamental", ch=45, tipo="EST"),

    D(7, "Química Analítica Quantitativa", ch=30), D(7, "Química Analítica Quantitativa Experimental", ch=60),
    D(7, "Introdução à Metodologia da Pesquisa Cientifica", ch=30),
    D(7, "Elaboração de Material Didático para o Ensino de Química e Ciências", ch=60),
    D(7, "Metodologia e Prática de Ensino de Química 1", ch=60),
    D(7, "Estágio Supervisionado em Ensino de Química 1", ch=90, tipo="EST"),

    D(8, "Química Orgânica 1", ch=60), D(8, "Química Orgânica Experimental 1", ch=30),
    D(8, "Instrumentação para o Ensino de Química e Ciências", ch=60),
    D(8, "Metodologia e Prática de Ensino de Química 2", ch=60),
    D(8, "Estágio Supervisionado em Ensino de Química 2", ch=60, tipo="EST"),
    D(8, "Desenvolvimento da Pesquisa em Ensino de Química e Ciências", ch=30, anual=True),

    D(9, "Desenvolvimento da Pesquisa em Ensino de Química e Ciências", ch=30, anual=True),
    D(9, "Química Orgânica 2", ch=60), D(9, "Química Orgânica Experimental 2", ch=60),
    D(9, "História da Educação", ch=30), D(9, "Metodologia e Prática de Ensino de Química 3", ch=30),
    D(9, "Estágio Supervisionado em Ensino de Química 3", ch=90, tipo="EST"),
    D(9, "LIBRAS, Educação Especial e Inclusiva", ch=60),
    D(9, "Monografia", ch=60, anual=True, tipo="TRA"),

    D(10, "Monografia", ch=60, anual=True, tipo="TRA"), D(10, "Bioquímica", ch=60), D(10, "Bioquímica Experimental", ch=60),
    D(10, "Ensino de Ciências da Natureza: contextos éticos, educacionais, sociais e tecnológicos", ch=90),
    D(10, "Orientações Curriculares Oficiais para o Ensino de Ciências e Química", ch=30),
    D(10, "Metodologia e Prática de Ensino de Química 4", ch=30),
    D(10, "Estágio Supervisionado em Ensino de Química 4", ch=90, tipo="EST"),
]
QUI_LIC_FORA = [["Atividades Teórico-Práticas de Aprofundamento", 210]]
QUI_LIC_DECLARADO = (3735, 249)

QUI_BACH = QUI_ANO1 + [
    D(4, "Atividades Orientadas de Extensão Universitária 1", ch=60, anual=True), D(4, "Química Inorgânica 2", ch=60),
    D(4, "Química Inorgânica Experimental 2", ch=30), D(4, "Físico-Química 1", ch=60),
    D(4, "Cálculo – Integrais Múltiplas", ch=60), D(4, "Física 2", ch=60), D(4, "Física Experimental 2", ch=30),

    D(5, "Química Inorgânica 3", ch=30), D(5, "Físico-Química 2", ch=60), D(5, "Físico-Química Experimental 1", ch=30),
    D(5, "Química Ambiental 1", ch=30), D(5, "Introdução à Metodologia da Pesquisa Cientifica", ch=30),
    D(5, "Física 3", ch=60), D(5, "Fundamentos de Estatística", ch=60),
    D(5, "Atividades Orientadas de Extensão Universitária 2", ch=60, anual=True),

    D(6, "Atividades Orientadas de Extensão Universitária 2", ch=60, anual=True), D(6, "Físico-Química 3", ch=60),
    D(6, "Físico-Química Experimental 2", ch=30), D(6, "Química Ambiental 2", ch=30),
    D(6, "Química Analítica Qualitativa", ch=30), D(6, "Química Analítica Qualitativa Experimental", ch=60),
    D(6, "Química Orgânica 1", ch=60), D(6, "Química Orgânica Experimental 1", ch=30),

    D(7, "Físico-Química 4", ch=30), D(7, "Química Orgânica 2", ch=60), D(7, "Química Orgânica Experimental 2", ch=60),
    D(7, "Química Analítica Quantitativa", ch=30), D(7, "Química Analítica Quantitativa Experimental", ch=60),
    D(7, "Análise Instrumental 1", ch=30), D(7, "Análise Instrumental Experimental 1", ch=30),

    D(8, "Química Orgânica 3", ch=30), D(8, "Análise Instrumental 2", ch=60),
    D(8, "Análise Instrumental Experimental 2", ch=30), D(8, "Bioquímica", ch=60),
    D(8, "Bioquímica Experimental", ch=60), D(8, "Tratamento e Descarte de Resíduos Químicos", ch=30),

    D(9, "Microbiologia Industrial", ch=60), D(9, "Processos Industriais Orgânicos", ch=60),
    D(9, "Processos Industriais Inorgânicos", ch=60), D(9, "Higiene e Segurança Industrial", ch=30),
    D(9, "Operações Unitárias", ch=90, anual=True), D(9, "Estágio em Indústria", ch=150, anual=True, tipo="EST"),

    D(10, "Operações Unitárias", ch=90, anual=True), D(10, "Estágio em Indústria", ch=150, anual=True, tipo="EST"),
    D(10, "Processos Industriais Biotecnológicos", ch=60), D(10, "Noções de Desenho Técnico na Indústria", ch=60),
]
QUI_BACH_FORA = [["Atividades Complementares", 30]]
QUI_BACH_DECLARADO = (3450, 230)

# ---------------------------------------------------------------------------
# Física — estrutura curricular 1606 (Licenciatura; Bacharelado em Física de Materiais;
# Bacharelado em Física Computacional). Créditos ("cd") por termo, como nas tabelas.
# Chaves: L = Licenciatura, M = Física de Materiais, C = Física Computacional.
# ---------------------------------------------------------------------------
def _fis(t, n, cr, mods, **kw):
    return dict(D(t, n, cr, **kw), mods=mods)

FISICA = [
    _fis(1, "Análise Computacional Elementar", 2, "LMC"), _fis(1, "Evolução Histórica e Conceitual da Física", 2, "LMC"),
    _fis(1, "Física Básica", 4, "LMC"), _fis(1, "Fundamentos da Extensão Universitária", 2, "LMC"),
    _fis(1, "Fundamentos de Física Experimental", 2, "LMC"), _fis(1, "Pré-Cálculo", 4, "LMC"),
    _fis(1, "Química Geral I", 4, "LMC"),

    _fis(2, "Cálculo Diferencial e Integral I", 4, "LMC"), _fis(2, "Cálculo Vetorial e Geometria Analítica", 4, "LMC"),
    _fis(2, "Física Geral e Experimental I", 6, "LMC"), _fis(2, "Laboratório de Química I", 2, "LM"),
    _fis(2, "Astronomia: Terra e Universo", 4, "L"), _fis(2, "Introdução à Linguagem de Programação", 6, "MC"),

    _fis(3, "Cálculo Diferencial e Integral II", 4, "LMC"), _fis(3, "Física Geral e Experimental II", 6, "LMC"),
    _fis(3, "Química Geral II", 4, "LM"), _fis(3, "Metodologia e Prática de Ensino de Física I", 4, "L"),
    _fis(3, "Tecnologia da Comunicação e Informação no Ensino de Física", 4, "L"),
    _fis(3, "Optativa de Física dos Materiais", 4, "M", tipo="SLOT"),
    _fis(3, "Cálculo Numérico I", 4, "C"), _fis(3, "Probabilidade e Estatística", 4, "C"),

    _fis(4, "Cálculo Diferencial e Integral III", 4, "LMC"), _fis(4, "Elementos de Álgebra Linear", 4, "LMC"),
    _fis(4, "Física Geral e Experimental III", 6, "LMC"), _fis(4, "Laboratório de Química II", 2, "LM"),
    _fis(4, "Metodologia e Prática de Ensino de Física II", 4, "L"), _fis(4, "Termodinâmica", 4, "MC"),
    _fis(4, "Ciência, Sociedade, Ambiente e Desenvolvimento Humano", 4, "M"), _fis(4, "Cálculo Numérico II", 4, "C"),

    _fis(5, "Cálculo Diferencial e Integral IV", 4, "LMC"), _fis(5, "Física Geral e Experimental IV", 6, "LMC"),
    _fis(5, "História da Ciência", 4, "L"), _fis(5, "Metodologia e Prática de Ensino de Física III", 4, "L"),
    _fis(5, "Física Matemática I", 4, "MC"), _fis(5, "Física Moderna I", 4, "MC"),
    _fis(5, "Simulações Computacionais I", 4, "C"),

    _fis(6, "Filosofia das Ciências", 4, "L"), _fis(6, "Metodologia e Prática de Ensino de Física IV", 4, "L"),
    _fis(6, "Optativa livre", 4, "L", tipo="SLOT"), _fis(6, "Políticas Educacionais Brasileiras", 4, "L"),
    _fis(6, "Termodinâmica", 4, "L"),
    _fis(6, "Física Matemática II", 4, "MC"), _fis(6, "Física Moderna II", 4, "MC"), _fis(6, "Mecânica Clássica", 4, "MC"),
    _fis(6, "Física da Matéria Condensada I", 4, "M"), _fis(6, "Laboratório de Física Moderna", 4, "M"),
    _fis(6, "Ciência, Sociedade, Ambiente e Desenvolvimento Humano", 4, "C"),
    _fis(6, "Simulações Computacionais II", 4, "C"), _fis(6, "Optativa Livre", 4, "C", tipo="SLOT"),

    _fis(7, "Estágio Supervisionado I: A Realidade Escolar", 4, "L", tipo="EST"), _fis(7, "Física Moderna I", 4, "L"),
    _fis(7, "Introdução à Pesquisa em Ensino de Ciências", 4, "L"),
    _fis(7, "Metodologia e Prática de Ensino de Física V", 4, "L"), _fis(7, "Psicologia da Educação", 4, "L"),
    _fis(7, "Eletromagnetismo I", 6, "MC"), _fis(7, "Física Estatística", 4, "MC"), _fis(7, "Mecânica Quântica I", 6, "MC"),
    _fis(7, "Ciências dos Materiais I", 4, "M"), _fis(7, "Trabalho de Conclusão de Curso I", 4, "M", tipo="TRA"),
    _fis(7, "Estágio - I", 4, "C", tipo="EST"), _fis(7, "Estruturas de Dados", 4, "C"),

    _fis(8, "Estágio Supervisionado II: A Estrutura e a Organização Institucional da Escola de Ensino Médio", 8, "L", tipo="EST"),
    _fis(8, "Física Moderna II", 4, "L"), _fis(8, "Instrumentação para o Ensino de Física I", 4, "L"),
    _fis(8, "Laboratório de Física Moderna", 4, "L"), _fis(8, "Trabalho de Conclusão de Curso I", 4, "L", tipo="TRA"),
    _fis(8, "Caracterização de Materiais", 4, "M"), _fis(8, "Ciências dos Materiais II", 4, "M"),
    _fis(8, "Nanomateriais e Nanotecnologia", 4, "M"), _fis(8, "Trabalho de Conclusão de Curso II", 4, "M", tipo="TRA"),
    _fis(8, "Optativa de Física dos Materiais", 4, "M", tipo="SLOT"),
    _fis(8, "Computação Quântica", 4, "C"), _fis(8, "Estágio II", 4, "C", tipo="EST"),
    _fis(8, "Introdução às Técnicas de Aprendizado de Máquina", 4, "C"),
    _fis(8, "Optativa de Física Computacional", 4, "C", tipo="SLOT"),

    _fis(9, "Didática das Ciências", 4, "L"),
    _fis(9, "Estágio Supervisionado III: Projeto interdisciplinar de Ensino de Ciências e Física", 5, "L", tipo="EST"),
    _fis(9, "Instrumentação para o Ensino de Física II", 4, "L"), _fis(9, "Trabalho de Conclusão de Curso II", 6, "L", tipo="TRA"),
    _fis(9, "Optativa de Licenciatura em Física", 4, "L", tipo="SLOT"),

    _fis(10, "Ciência, Sociedade, Ambiente e Desenvolvimento Humano", 4, "L"),
    _fis(10, "Estágio Supervisionado IV: Atividades de Regência em Unidade Escolar", 10, "L", tipo="EST"),
    _fis(10, "Libras, Educação Especial e Inclusiva", 4, "L"), _fis(10, "Mecânica Clássica", 4, "L"),
    _fis(10, "Trabalho de Conclusão de Curso III", 4, "L", tipo="TRA"),
]
FISICA_TOTAIS = {
    "L": {1: 20, 2: 20, 3: 22, 4: 20, 5: 18, 6: 20, 7: 20, 8: 24, 9: 23, 10: 26},
    "M": {1: 20, 2: 22, 3: 18, 4: 24, 5: 18, 6: 20, 7: 24, 8: 20},
    "C": {1: 20, 2: 20, 3: 18, 4: 22, 5: 22, 6: 24, 7: 24, 8: 16},
}
FISICA_DECLARADO = {"L": (3195, 213), "M": (2490, 166), "C": (2490, 166)}

# ---------------------------------------------------------------------------
# Meteorologia — Bacharelado, currículo 1702 (tabelas publicadas como imagem na página do curso)
# ---------------------------------------------------------------------------
def _met(t, cod, dep, n, cr, ch, co=(), pre=()):
    return D(t, n, cr, ch, cod=cod, d=dep, co=list(co), pre=list(pre))

METEOROLOGIA = [
    _met(1, "7000", "DFM", "Física I", 6, 90), _met(1, "7003", "DM", "Cálculo Vetorial e Geometria Analítica", 4, 60),
    _met(1, "7008", "DFM", "Meteorologia Básica", 6, 90), _met(1, "7042", "DFM", "Meteorologia e Sociedade", 2, 30),
    _met(1, "7043", "DM", "Pré-Cálculo", 4, 60), _met(1, "7044", "DFM", "Laboratório de Física I", 2, 30),

    _met(2, "7005", "DFM", "Energia e Sustentabilidade Ambiental", 6, 90),
    _met(2, "7046", "DFM", "Cálculo Diferencial e Integral de Uma Variável", 4, 60),
    _met(2, "7047", "DM", "Laboratório de Física II", 4, 60), _met(2, "7048", "DFM", "Observações Meteorológicas", 2, 30),
    _met(2, "7049", "DFM", "Atividades Orientadas de Extensão Universitária I", 6, 90),
    _met(2, "7050", "DFM", "Energia e Sustentabilidade Ambiental", 4, 60),

    _met(3, "7010", "DFM", "Física III", 6, 90, co=["Física I"]), _met(3, "7013", "EP", "Estatística Aplicada", 4, 60),
    _met(3, "7051", "DM", "Cálculo Diferencial e Integral de Várias Variáveis I", 4, 60, co=["Pré-Cálculo"]),
    _met(3, "7052", "DFM", "Laboratório de Física III", 2, 30, co=["Laboratório de Física I"]),
    _met(3, "7053", "DFM", "Introdução às Linguagens de Programação", 6, 90),
    _met(3, "7054", "DFM", "Atividades Orientadas de Extensão Universitária II", 2, 30),
    _met(3, "49183", "DFM", "Mecânica dos Fluidos para atmosfera", 4, 60,
         co=["Cálculo Diferencial e Integral de Várias Variáveis I"], pre=["Cálculo Vetorial e Geometria Analítica"]),

    _met(4, "7023", "DFM", "Meteorologia Física I", 4, 60),
    _met(4, "7055", "DM", "Cálculo Diferencial e Integral de várias variáveis II", 4, 60),
    _met(4, "7056", "DFM", "Métodos Matemáticos em Meteorologia e Climatologia", 6, 90,
         pre=["Cálculo Vetorial e Geometria Analítica", "Cálculo Diferencial e Integral de Várias Variáveis I"]),
    _met(4, "7057", "DM", "Séries e Equações Diferenciais", 4, 60, pre=["Cálculo Diferencial e Integral de Várias Variáveis I"]),
    _met(4, "7058", "DFM", "Atividades Orientadas de Extensão Universitária III", 6, 90),

    _met(5, "7021", "DFM", "Meteorologia Dinâmica I", 6, 90, pre=["Métodos Matemáticos em Meteorologia e Climatologia"]),
    _met(5, "7030", "DFM", "Meteorologia Física II", 4, 60, pre=["Cálculo Diferencial e Integral de Uma Variável"]),
    _met(5, "7034", "DFM", "Micrometeorologia", 4, 60, co=["Meteorologia Dinâmica I"], pre=["Física II"]),
    _met(5, "7036", "DFM", "Métodos Estatísticos em Meteorologia e Climatologia", 6, 90,
         co=["Climatologia"], pre=["Estatística Aplicada"]),
    _met(5, "7059", "DFM", "Climatologia", 6, 90, co=["Estatística Aplicada"], pre=["Meteorologia Básica", "Meteorologia Física I"]),
    _met(5, "7060", "DFM", "Atividades Orientadas de Extensão Universitária IV", 2, 30),

    _met(6, "7026", "DFM", "Meteorologia Dinâmica II", 6, 90, pre=["Meteorologia Dinâmica I"]),
    _met(6, "7027", "DFM", "Meteorologia Sinótica I", 6, 90, co=["Meteorologia Dinâmica II"],
         pre=["Meteorologia Física I", "Meteorologia Dinâmica I"]),
    _met(6, "7038", "DFM", "Meteorologia com Radar e Satélite", 6, 90, pre=["Meteorologia Física II"]),
    _met(6, "7061", "DFM", "Hidrologia e Hidrometeorologia", 4, 60, pre=["Estatística Aplicada", "Meteorologia Básica"]),
    _met(6, "7062", "DFM", "Atividades Orientadas de Extensão Universitária V", 5, 75),

    _met(7, "7031", "DFM", "Poluição Atmosférica", 4, 60, pre=["Meteorologia Física I", "Micrometeorologia"]),
    _met(7, "7032", "DFM", "Meteorologia Sinótica II", 6, 90, pre=["Meteorologia Sinótica I", "Meteorologia Dinâmica II"]),
    _met(7, "7063", "DE", "Metodologia da Pesquisa Científica", 2, 30),
    _met(7, "7064", "DFM", "Modelagem Numérica", 6, 90, pre=["Meteorologia Dinâmica II"]),
    _met(7, "7065", "DFM", "Trabalho de Conclusão de Curso I", 2, 30, co=["Metodologia da Pesquisa Científica"]),
    _met(7, "7066", "DFM", "Atividades Orientadas de Extensão Universitária VI", 2, 30),

    _met(8, "7028", "DFM", "Meteorologia Tropical", 4, 60, pre=["Meteorologia Física I"]),
    _met(8, "7039", "DFM", "Técnicas de Comunicação Oral e Escrita em Meteorologia", 2, 30,
         pre=["Meteorologia Básica", "Meteorologia e Sociedade"]),
    _met(8, "7041", "DFM", "Estágio Profissionalizante", 4, 60),
    _met(8, "7067", "DFM", "Agrometeorologia", 4, 60, pre=["Micrometeorologia"]),
    _met(8, "7068", "DFM", "Trabalho de Conclusão de Curso II", 4, 60, co=["Trabalho de Conclusão de Curso I"]),
]
METEOROLOGIA_TOTAIS = {1: (24, 360), 2: (26, 390), 3: (28, 420), 4: (24, 360), 5: (28, 420), 6: (27, 405), 7: (22, 330), 8: (18, 270)}
METEOROLOGIA_OPT = [
    _met(0, "4209", "DQ", "Química Geral e Inorgânica", 4, 60), _met(0, "4210", "DQ", "Laboratório de Química Geral e Inorgânica", 2, 30),
    _met(0, "4220", "DFM", "Termodinâmica", 4, 60), _met(0, "4246", "DFM", "Físico-Química", 4, 60),
    _met(0, "4918", "DCo", "Animação em 3D", 4, 60), _met(0, "4981", "DFM", "Fundamentos de Astronomia", 2, 30),
    _met(0, "4983", "DFM", "Produção de Textos Científicos", 2, 30), _met(0, "49112", "DFM", "Tópicos em Biometeorologia", 2, 30),
    _met(0, "49131", "DFM", "Tópicos Especiais em Mudanças Climáticas e Modelagem de Clima", 4, 60),
    _met(0, "49132", "DFM", "Interação Oceano-Atmosfera", 4, 60), _met(0, "49160", "DFM", "Interação Biosfera Atmosfera", 4, 60),
    _met(0, "49189", "DFM", "Matemática Básica para Meteorologia", 4, 60),
    _met(0, None, "DFM", "Meteorologia de Mesoescala", 4, 60, co=["Meteorologia Sinótica II"],
         pre=["Meteorologia Sinótica I", "Meteorologia Dinâmica II"]),
    _met(0, None, "DFM", "Interação Solo-Vegetação-Atmosfera", 2, 30, pre=["Observações Meteorológicas", "Estatística Aplicada"]),
]

# ---------------------------------------------------------------------------
# Design — estrutura curricular do Bacharelado (2023; ingressantes a partir de 2024).
# O documento lista apenas os componentes por termo: não informa carga, códigos nem requisitos.
# ---------------------------------------------------------------------------
_LAB = "Laboratório Transdisciplinar de Ensino, Extensão e Pesquisa "
DESIGN = [
    (1, ["Projeto Interdisciplinar 1", _LAB + "1", "Design e Cultura 1", "Expressão e Representação",
         "Processos e Construção da Imagem", "Tecnologia dos Materiais"]),
    (2, ["Projeto Interdisciplinar 2", _LAB + "2", "Design e Cultura 2", "Desenho de Observação e Ilustração",
         "Estudo das Linguagens", "Tipografia", "Tecnologias dos Processos 1"]),
    (3, ["Projeto Interdisciplinar 3", _LAB + "3", "Psicologia: Percepção e Cognição no Design", "Expressão Gráfica",
         "Linguagens Complexas", "Planejamento Gráfico e Visual", "Tecnologias dos Processos 2"]),
    (4, ["Projeto Interdisciplinar 4", _LAB + "4", "Sociologia e Design", "Representação Gráfica",
         "Design da Informação", "Design Ergonômico", "Tecnologias e Processos Digitais"]),
    (5, ["Projeto Interdisciplinar 5", _LAB + "5", "Filosofia: Estética e Design", "Antropologia Cultural e Design",
         "Representação Digital", "Design e Experiência do Usuário", "Design Inclusivo", "Tecnologias Sociais"]),
    (6, ["Projeto Interdisciplinar 6", _LAB + "6", "Comunicação de Marketing", "Processos Criativos e Expressivos",
         "Design de Serviços", "Design de Animação e Games", "Tecnologias Assistivas"]),
    (7, ["TCC 1", _LAB + "7", "OPTATIVA 1", "Gestão do Design", "Planejamento Estratégico"]),
    (8, ["TCC 2", "OPTATIVA 2", "OPTATIVA 3"]),
]
