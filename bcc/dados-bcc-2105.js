/*
 * Árvore de Grade — dados do curso
 * Bacharelado em Ciência da Computação (BCC) · Currículo 2105
 * Faculdade de Ciências · Unesp · Câmpus de Bauru
 *
 * Fontes (transcritas LITERALMENTE; não corrigir grafias aqui):
 *   - "Bacharelado em Ciência da Computação — Currículo 2105 – para ingressantes a partir
 *     de 2023" (PDF da página Estrutura Curricular): códigos, departamentos, nomes, créditos,
 *     horas, termos, co-requisitos, pré-requisitos e quadro-resumo;
 *   - tabela "Ementas de disciplinas obrigatórias do Currículo 2105" da mesma página: ementas;
 *   - PDFs "BCC Horário Nº Termo 1º semestre de 2026" (página Horário de aulas): optativas
 *     ofertadas no semestre.
 *
 * O PDF do currículo imprime créditos e horas; como créditos = horas ÷ 15 em todas as linhas,
 * guarda-se só a carga horária e "creditosNoDocumento" autoriza a exibição dos créditos.
 *
 * Campos (ver README.md, "Formato dos dados"):
 *   c     código                          t      termo (1 a 8)
 *   n     nome, como no documento         ch     horas, como no documento
 *   d     departamento, como no documento tipo   OBR (grade) | SLOT (linha "Optativa")
 *   pre   pré-requisitos (códigos)        co     co-requisitos (códigos)
 *   ementa texto da página do curso      classificacao "extensao" = fora da soma das obrigatórias
 */
ArvoreGrade.registrar({
  id: "bcc-2105",
  sigla: "BCC",
  curso: "Bacharelado em Ciência da Computação",
  curriculo: "2105",
  vigencia: "Ingressantes a partir de 2023",
  unidade: "Faculdade de Ciências · Câmpus de Bauru",
  departamento: "Departamento de Computação",
  atualizadoEm: "2026-09-30",
  creditosNoDocumento: true,
  fonte: {
    titulo: "Currículo 2105 (a partir de 2023)",
    url: "https://www.fc.unesp.br/Home/Departamentos/Computacao/bachareladoemcienciadacomputacao/bcc-curriculo-2105-com-quadro-resumo.pdf"
  },
  contato: {
    titulo: "Conselho de Curso",
    url: "https://www.fc.unesp.br/#!/departamentos/computacao/cursos-de-graduao/bacharelado-em-ciencia-da-computacao/conselho-de-curso/"
  },
  quadroResumo: {
    linhas: [
      ["Disciplinas obrigatórias", 178, 2670],
      ["Disciplinas optativas", 8, 120],
      ["Estágio, Iniciação Científica ou Monitoria", 0, 0],
      ["Atividades curriculares de Extensão Universitária", 22, 330],
      ["Atividades Complementares", 6, 90]
    ],
    total: [214, 3210]
  },
  regras: {
    "4650": {
      tipo: "percentualObrigatorias",
      valor: 0.70,
      texto: "Ter cumprido 70% do total de créditos referentes às disciplinas obrigatórias"
    }
  },
  disciplinas: [
    { c: "4600", t: 1, d: "MAT", ch: 60, tipo: "OBR", n: "Cálculo I",
      ementa: "Função real de uma variável real. Limites. Derivadas. Aplicações de Derivadas." },
    { c: "4601", t: 1, d: "MAT", ch: 60, tipo: "OBR", n: "Geometria Analítica",
      ementa: "Vetores. A Reta. O Plano. Distância e Ângulos. Curvas Planas." },
    { c: "4602", t: 1, d: "MAT", ch: 60, tipo: "OBR", n: "Lógica Computacional",
      ementa: "Lógica proposicional; lógica quantificacional; álgebra dos conjuntos; sistemas booleanos, sistemas fuzzy." },
    { c: "4604", t: 1, d: "COM", ch: 60, tipo: "OBR", n: "Algoritmos I",
      ementa: "Metodologia para o desenvolvimento de programas. Estruturas básicas: tipos, constantes e variáveis. Expressões: aritméticas e lógicas. Estruturas de controle. Modularização. Manipulação de Cadeias de Caracteres. Estruturas de Dados Compostas Homogêneas." },
    { c: "4605", t: 1, d: "COM", ch: 30, tipo: "OBR", n: "Fundamentos de Computação",
      ementa: "Sistemas de Numeração. Representação interna de dados. Arquitetura de Computadores. Conceitos de linguagens de programação. Tecnologia da Informação." },
    { c: "4606", t: 1, d: "COM", ch: 60, tipo: "OBR", n: "Dispositivos e Circuitos Eletrônicos",
      ementa: "Analise de Circuitos. Teoria dos Semicondutores. Transistor de Junção Bipolar. Transistor de Efeito de Campo de Junção (JFET). Transistor de Efeito de Campo de Metal Oxido Semicondutor (MOSFET). Chaveamento com Transistores. Amplificadores Operacionais. Outros Circuitos Integrados Lineares." },
    { c: "49202", t: 1, d: "COM", ch: 30, tipo: "OBR", n: "Informação Profissional e Acadêmica",
      ementa: "Definição de Ciência da Computação. Perspectivas profissionais. Necessidades de formação. Apresentação do curso de Ciência da Computação. Relacionamento entre as disciplinas do currículo e Formação profissional. A vida acadêmica universitária." },

    { c: "4608", t: 2, d: "MAT", ch: 60, tipo: "OBR", n: "Cálculo II",
      ementa: "Integral Indefinida e Técnicas de Integração. Coordenadas Polares. Integral Definida e Aplicações. Integral Imprópria." },
    { c: "4609", t: 2, d: "MAT", ch: 60, tipo: "OBR", n: "Álgebra Linear", // PDF imprime "A0lgebra Linear" (falha de acento); correção autorizada em 30/09/2026
      ementa: "Matrizes. Sistemas Lineares. Espaços Vetoriais. Transformações Lineares." },
    { c: "4611", t: 2, d: "COM", ch: 60, tipo: "OBR", n: "Algoritmos II",
      ementa: "Estruturas de dados compostas heterogêneas. Arquivos. Recursividade. Complexidade de Algoritmos. Algoritmos de Busca. Algoritmos de Ordenação Interna. Listas Lineares." },
    { c: "4613", t: 2, d: "COM", ch: 60, tipo: "OBR", n: "Circuitos Digitais",
      ementa: "Circuitos Lógicos. Codificadores e Decodificadores. Multiplexadores e Demultiplexadores. Circuitos Aritméticos. Introdução a Lógica Seqüencial. Flip-Flops. Registradores de Deslocamento. Contadores e Divisores. Famílias Lógicas e Circuitos Integrados. Memórias Semicondutoras. Interface com o Mundo analógico. Dispositivos de Lógica Programável. Introdução ao Microprocessador e ao Microcomputador." },
    { c: "4614", t: 2, d: "COM", ch: 60, tipo: "OBR", n: "Laboratório de Circuitos Digitais", co: ["4613"],
      ementa: "Experimentos com Portas Lógicas. Experimentos com Circuitos Lógicos. Experimentos com Circuitos Codificadores e Decodificadores. Experimentos com Circuitos Multiplex e Demultiplex. Experimentos com Circuitos Aritméticos.Experimentos com Flip-Flops. Multivibradores Ástavel e Monoestável. Experimentos com Registradores de Deslocamento. Experimentos com Contadores Digitais. Experimentos com Memórias Semicondutoras. Conversores Digitais.Dispositivos de Lógica Programável." },
    { c: "49196", t: 2, d: "COM", ch: 60, tipo: "OBR", n: "Laboratório de Programação",
      ementa: "A disciplina tem caráter de laboratório, com intensa atividade de programação. Todos os programas criados pelos alunos são submetidos a \"juízes eletrônicos\". Os problemas de programação podem cobrir tópicos clássicos de Ciência da Computação, tais como estruturas de dados básicas, ordenação, problemas básicos de matemática, entre outros." },
    // 4652: carga de extensão universitária (confirmado em 30/09/2026) — exibida como no PDF, fora da soma das obrigatórias
    { c: "4652", t: 2, d: "COM", ch: 60, tipo: "OBR", classificacao: "extensao", n: "Fundamentos e Metodologia da Extensão Universitária",
      ementa: "Conceitua, numa perspectiva histórico-filosófica, estudos referentes à Universidade Pública e à Extensão Universitária e a sua função acadêmica e social. Analisa as concepções, a legislação e as tendências da Extensão Universitária nas Universidades Públicas Brasileiras. Aborda os procedimentos pedagógicos, metodológicos e técnico-científicos de projetos e atividades de extensão universitária, articulados ao ensino de graduação e à pesquisa. Elabora propostas de atividades de Extensão Universitária numa abordagem multi e interdisciplinar. Divulga o conhecimento científico produzido às comunidades acadêmicas e grupos sociais." },

    { c: "4603", t: 3, d: "DEP", ch: 60, tipo: "OBR", n: "Probabilidade e Estatística",
      ementa: "Estatística Descritiva. Probabilidades. Variáveis Aleatórias. Amostragem. Estimação de Parâmetros. Testes de Hipóteses. Correlação e Regressão." },
    { c: "4615", t: 3, d: "MAT", ch: 60, tipo: "OBR", n: "Cálculo III", pre: ["4600"],
      ementa: "Funções reais de duas ou mais variáveis reais. Limites. Derivadas Parciais. Aplicações de Derivadas Parciais - Máximos e Mínimos. Fórmula de Taylor." },
    { c: "4616", t: 3, d: "COM", ch: 60, tipo: "OBR", n: "Métodos Numéricos Computacionais", pre: ["4600", "4601", "4604"],
      ementa: "Algoritmos Numéricos. Cálculo de Zero de Funções. Solução de Sistemas Algébricos Lineares. Interpolação de Funções. Ajuste de Curvas. Diferenciação Numérica. Integração Numérica. Solução de Sistemas de Equações Não Lineares." },
    { c: "4617", t: 3, d: "COM", ch: 60, tipo: "OBR", n: "Estruturas de Dados I", pre: ["4602", "4604", "4611"],
      ementa: "Tipo Abstrato de Dados e Abstração. Pilhas. Filas. Árvores. Coleta e compactação. Heap. Hashing." },
    { c: "4619", t: 3, d: "COM", ch: 60, tipo: "OBR", n: "Arquitetura de Computadores",
      ementa: "Fundamentos sobre arquitetura e organização de computadores. Organização de processsadores, memórias, barramentos e dispositivos de Entrada e Saída. Análise de sistemas paralelos. Análise de tópicos avançados em arquitetura e organização de computadores." },
    { c: "4623", t: 3, d: "COM", ch: 60, tipo: "OBR", n: "Teoria da Computação e Linguagens Formais", pre: ["4611"],
      ementa: "Introdução e conceitos básicos. Autômatos finitos. Linguagens e gramáticas regulares. Linguagem livre de contexto (LLC). Autômatos a Pilha. Máquinas de Turing (MT). Hierarquia das Linguagens Formais. Limites da computação algorítmica." },
    { c: "4644", t: 3, d: "COM", ch: 60, tipo: "OBR", n: "Programação Orientada a Objetos", pre: ["4604", "4611"], co: ["4617"],
      ementa: "Conceitos de programação orientada a objetos (POO), classes, instâncias herança, sobrecarga de operadores e funções, sobreposição (override), tipos genéricos. Aplicações com exemplos, oferecendo ao aluno meios para desenvolver programas completos com linhas de execução concorrentes (threads), banco de dados e comunicação por rede em programas cliente-servidor." },

    { c: "4624", t: 4, d: "COM", ch: 60, tipo: "OBR", n: "Estruturas de Dados II", pre: ["4604", "4611"],
      ementa: "Organização e Acesso em Memória Auxiliar. Árvores B. Ordenação Externa. Grafos." },
    { c: "4626", t: 4, d: "COM", ch: 60, tipo: "OBR", n: "Sistemas Operacionais I", pre: ["4617"],
      ementa: "Introdução. Processos e Threads. Gerenciamento de Memória." },
    { c: "4632", t: 4, d: "COM", ch: 60, tipo: "OBR", n: "Microcontroladores", pre: ["4619"],
      ementa: "Arquitetura de Microcontroladores. Programação de Microcontroladores. Desenvolvimento de Projetos." },
    { c: "4645", t: 4, d: "FIS", ch: 60, tipo: "OBR", n: "Física",
      ementa: "Cargas elétricas. Campos elétricos. Potencial elétrico. Capacitância. Corrente elétrica. Bandas de energia." },
    { c: "4646", t: 4, d: "COM", ch: 60, tipo: "OBR", n: "Pesquisa Operacional", pre: ["4600", "4601", "4604", "4609", "4611"],
      ementa: "Aplicações de Pesquisa Operacional. Modelos lineares, inteiros, não lineares e dinâmicos. Programação Linear. Método Simplex e Método Simplex de Duas Fases. Programação Linear Inteira: Técnica de Bifurcação e Limite, Método de Cortes, Transportes, Produção e Alocação." },
    { c: "4647", t: 4, d: "MAT", ch: 60, tipo: "OBR", n: "Séries e Equações Diferenciais Ordinárias", pre: ["4615"],
      ementa: "Sequências e séries. Equações diferenciais ordinárias de primeira e segunda ordem." },
    { c: "4653", t: 4, d: "COM", ch: 60, tipo: "OBR", n: "Engenharia de Software I", pre: ["4605", "4617", "4644"],
      ementa: "Natureza e importancia do software. Processo e modelo de processo de software. Engenharia de software agil, Aspectos humanos do software. Requisitos de software. Modelagem de software. Metricas de software. Qualidade e melhoria de software. Estimativas de esforco de projetos de software. Gestao de projeto de software. Tendencias emergentes na Engenharia de Software." },

    { c: "4610", t: 5, d: "EDU", ch: 30, tipo: "OBR", n: "Metodologia da Pesquisa Científica",
      ementa: "Planejamento e desenvolvimento da pesquisa científica: as etapas da pesquisa, pesquisa bibliográfica, experimental, correlacional e de campo. Metodologia de observação e registro do comportamento. Técnicas de Pesquisa Bibliográfica: itens básicos para a elaboração e apresentação de trabalho científico. Normalização de referência bibliográfica." },
    { c: "4628", t: 5, d: "COM", ch: 60, tipo: "OBR", n: "Compiladores", pre: ["4617", "4623"],
      ementa: "Introdução à compilação. Analisador léxico. Analisador sintático descendente. Analisador sintático ascendente. Análise Semântica. Sistema de Execução básico de uma linguagem de programação. Organização do Computador." },
    { c: "4629", t: 5, d: "COM", ch: 60, tipo: "OBR", n: "Banco de Dados I", pre: ["4611", "4617"],
      ementa: "Introdução aos sistemas de banco de dados. Modelagem de dados. Linguagem de definição, manipulação e consulta de dados. Projeto de banco de dados" },
    { c: "4631", t: 5, d: "COM", ch: 60, tipo: "OBR", n: "Sistemas Operacionais II", pre: ["4617"],
      ementa: "Gerenciamento de Memória Virtual. Gerenciamento de Entrada e Saída. Deadlocks. Sistemas de Arquivos. Projeto e Implementação de Sistemas Operacionais" },
    { c: "4648", t: 5, d: "COM", ch: 60, tipo: "OBR", n: "Análise de Algoritmos", pre: ["4611", "4617"],
      ementa: "Algoritmos. Conceitos de complexidade algorítmica no tempo/espaço. Estratégias recursivas e interativas. Ordenação e estatísticas de ordem. Programação dinâmica. Algoritmos gulosos. Análise de algoritmos para grafos." },
    { c: "4654", t: 5, d: "COM", ch: 60, tipo: "OBR", n: "Engenharia de Software II", pre: ["4605", "4617", "4644"],
      ementa: "Fundamentos do projeto de software. Elementos do projeto de software. Estrategias de teste de software. Tecnicas de teste de software. Manutencao de software. Gestao de configuracao de software. Seguranca na Engenharia de Software. Engenharia de software baseada na nuvem" },

    { c: "4633", t: 6, d: "COM", ch: 60, tipo: "OBR", n: "Computação Gráfica", pre: ["4601", "4609", "4611", "4617"],
      ementa: "Conceitos Básicos de Computação Gráfica; Fundamentos da Imagem Digital; Dispositivos Gráficos; Transformações Geométricas 2D e 3D; Transformações para Visualização; Modelos Geométricos; Rasterização; Mecanismos de Visualização 3D; Modelos de Iluminação e Tonalização." },
    { c: "4635", t: 6, d: "COM", ch: 60, tipo: "OBR", n: "Banco de Dados II", pre: ["4624"],
      ementa: "Transações. Controle de Concorrência. Recuperação de falhas. Bancos de Dados Distribuídos. Segurança e Integridade. Banco de dados orientado a objetos e objetorelacionais. Tecnologias emergentes em banco de dados." },
    { c: "4637", t: 6, d: "COM", ch: 60, tipo: "OBR", n: "Redes de Computadores", pre: ["4619"],
      ementa: "Introdução. Conceitos Básicos em Redes de Computadores. Modelo OSI. A rede Mundial Internet. Arquitetura TCP/IP. Segurança e Gerenciamento de Redes." },
    { c: "4655", t: 6, d: "COM", ch: 60, tipo: "OBR", n: "Inteligência Artificial", pre: ["4611"],
      ementa: "Introdução, Agentes Inteligentes, Computação Evolutiva, Redes Neurais Artificiais, Aprendizagem de Máquina" },
    { c: "4656", t: 6, d: "COM", ch: 60, tipo: "OBR", n: "Fundamentos de Sistemas de Informação",
      ementa: "Conceitos e princípios da teoria geral dos sistemas. Introdução aos sistemas de informação. Sistemas de informação nas empresas. Solução de problemas empresariais com sistemas de informação. Tipos de sistemas de informação. O papel estratégico dos sistemas de informação. Planejamento e decisão de sistemas de informação. Abordagens para construção de sistemas de informação. Exemplos de aplicações de sistemas de informação. Ética em sistemas de informação." },

    { c: "4649", t: 7, d: "COM", ch: 60, tipo: "OBR", n: "Segurança da Informação", pre: ["4626", "4631"],
      ementa: "Revisão dos conceitos de redes de computadores. Protocolos TCP/IP. Conceitos em segurança de redes de computadores. Vulnerabilidade e exposição. Ataques cibernéticos. Códigos maliciosos. Dispositivos de defesa em redes de computadores. Firewalls, Sistemas de Detecção de Intrusos, Sistemas de autenticação. Fundamentos de criptografia. Conceitos básicos de programação segura. Conceitos sobre gerenciamento, monitoração e auditoria de redes de computadores. Plano de segurança de sistemas." },
    { c: "4650", t: 7, d: "COM", ch: 240, tipo: "OBR", n: "Projeto e Implementação de Sistemas (TCC-disciplina anual)",
      ementa: "Apresentação de pré-proposta de desenvolvimento do projeto. Revisão bibliográfica e estudo de produtos ou projetos similares. Apresentação de proposta definitiva em comum acordo com o orientador do projeto. Desenvolvimento do projeto, apresentação de palestras, seminários e relatórios sobre o desenvolvimento do projeto. Documentação do projeto. Apresentação pública do projeto." },
    { c: "4651", t: 7, d: "CHU", ch: 60, tipo: "OBR", n: "Direito, Legislação e Ética",
      ementa: "Introdução ao Estudo do Direito. Noções de ética profissional. Legislação aplicada à Computação. Direito e novas tecnologias." },
    { c: "OPT-I", t: 7, d: "COM", ch: 60, tipo: "SLOT", n: "Optativa I" },

    { c: "4642", t: 8, d: "COM", ch: 60, tipo: "OBR", n: "Projeto de Redes de Computadores", pre: ["4637"],
      ementa: "Introdução ao Projeto de Redes. Identificação das necessidades. Projeto Lógico da Rede. Projeto Físico da Rede. Exemplos de projeto de redes." },
    { c: "4657", t: 8, d: "COM", ch: 60, tipo: "OBR", n: "Empreendedorismo",
      ementa: "Fundamentos de Administracao de Empresas. Empreendedorismo. Planos de Negocios." },
    { c: "OPT-II", t: 8, d: "COM", ch: 60, tipo: "SLOT", n: "Optativa II" }
  ],
  optativas: {
    // O PDF do currículo 2105 prevê "Optativa I" (7º termo) e "Optativa II" (8º termo) e, no
    // quadro-resumo, 8 créditos / 120 h em disciplinas optativas, mas não publica a relação de
    // optativas. Enquanto essa relação não for disponibilizada, "lista" permanece vazia e o
    // quadro mostra a oferta registrada nos horários oficiais do semestre.
    lista: [],
    oferta: {
      periodo: "1º semestre de 2026",
      fonte: {
        titulo: "BCC – Horário de aulas (1º semestre de 2026)",
        url: "https://www.fc.unesp.br/#!/departamentos/computacao/cursos-de-graduao/bacharelado-em-ciencia-da-computacao/horrios-de-aula/"
      },
      itens: [
        // Nos horários o nome vem seguido de "(op)", marcador de disciplina optativa.
        { c: "49203", d: "COM", n: "Laboratório de Programação Competitiva", cr: 4, termos: [3, 5] },
        { c: "49187", d: "COM", n: "Ciência de Dados", cr: 4, termos: [5, 7] }
      ]
    }
  }
});
