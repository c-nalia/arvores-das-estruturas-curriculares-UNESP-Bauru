/*
 * Árvore de Grade — dados do curso
 * Bacharelado em Sistemas de Informação (BSI) · Currículo 2804
 * Faculdade de Ciências · Unesp · Câmpus de Bauru
 *
 * Fonte única: relação de disciplinas do currículo 2804 (ingressantes a partir de 2023),
 * emitida pelo Sistema de Graduação em 19/02/2026 e publicada na página "Grade Curricular"
 * do curso. Nomes, códigos, cargas, tipos, requisitos e Série/Período foram transcritos
 * literalmente desse documento. As únicas alterações são as correções de grafia listadas em
 * "correcoes" (ex.: "Computacão" → "Computação"); nenhum código ou carga foi alterado.
 *
 * O documento não informa departamento, turno nem créditos; por isso esses campos não existem
 * aqui. Os créditos não são calculados para exibição.
 *
 * Campos (ver README.md, "Formato dos dados"):
 *   c     código (sem os zeros à esquerda do sistema)   t     termo (Série/Período em sequência)
 *   n     nome, como no documento                        ch    coluna "Carga Horária" (h)
 *   aceu  coluna "CH ACEU" (h)                            tipo  coluna "Tipo": OBR | TRA | OPT | EXT
 *   pre   "Pré-Requisito" (códigos)                       co    "Correquisito" (códigos)
 */
ArvoreGrade.registrar({
  id: "bsi-2804",
  sigla: "BSI",
  curso: "Bacharelado em Sistemas de Informação",
  curriculo: "2804",
  vigencia: "Ingressantes a partir de 2023",
  unidade: "Faculdade de Ciências · Câmpus de Bauru",
  departamento: "Departamento de Computação",
  atualizadoEm: "2026-09-30",
  correcoes: [
      {
          "cod": "4623",
          "de": "Teoria da Computacão e Linguagens Formais",
          "para": "Teoria da Computação e Linguagens Formais",
          "motivo": "ortografia (cedilha)"
      },
      {
          "cod": "49225",
          "de": "Aprendizado de Máquina Aplicado à Sistemas de Informação",
          "para": "Aprendizado de Máquina Aplicado a Sistemas de Informação",
          "motivo": "crase indevida antes de palavra no plural"
      },
      {
          "cod": "49130",
          "de": "Tópicos Especiais Aprendizado de Máquina",
          "para": "Tópicos Especiais em Aprendizado de Máquina",
          "motivo": "preposição ausente"
      }
  ],
  rotuloTermo: "serie-periodo",
  tiposNoDocumento: true,
  fonte: {
    titulo: "Currículo 2804 (para ingressantes a partir de 2023)",
    url: "https://www.fc.unesp.br/Home/Departamentos/Computacao/bachareladoemsistemasdeinformacao/bsi-curriculo-2804v2.pdf"
  },
  contato: {
    titulo: "página do Conselho de Curso",
    url: "https://www.fc.unesp.br/#!/departamentos/computacao/cursos-de-graduao/bacharelado-em-sistemas-de-informacao/conselho-do-curso/"
  },
  disciplinas: [
    { c: "4700", t: 1, ch: 60, tipo: "OBR", n: "Algoritmos I" },
    { c: "4703", t: 1, ch: 60, tipo: "OBR", n: "Lógica Computacional" },
    { c: "4736", t: 1, ch: 60, tipo: "OBR", n: "Geometria Analítica" },
    { c: "4737", t: 1, ch: 60, tipo: "OBR", n: "Cálculo I" },
    { c: "4740", t: 1, ch: 60, tipo: "OBR", n: "Administração de Empresas" },

    { c: "4705", t: 2, ch: 60, tipo: "OBR", n: "Algoritmos II" },
    { c: "4706", t: 2, ch: 60, tipo: "OBR", n: "Cálculo II" },
    { c: "4739", t: 2, ch: 60, tipo: "OBR", n: "Álgebra Linear" },
    { c: "4741", t: 2, ch: 60, tipo: "OBR", n: "Probabilidade e Estatística" },
    { c: "4751", t: 2, ch: 60, tipo: "OBR", n: "Introdução à Tecnologia da Informação" },

    { c: "4710", t: 3, ch: 60, tipo: "OBR", n: "Estruturas de Dados I", pre: ["4700", "4705"] },
    { c: "4711", t: 3, ch: 60, tipo: "OBR", n: "Técnicas de Programação", pre: ["4700", "4705"] },
    { c: "4713", t: 3, ch: 60, tipo: "OBR", n: "Métodos Numéricos Computacionais", pre: ["4700", "4736", "4737"] },
    { c: "4742", t: 3, ch: 30, tipo: "OBR", n: "Metodologia da Pesquisa" },
    { c: "4745", t: 3, ch: 60, tipo: "OBR", n: "Fundamentos de Sistemas de Informação", pre: ["4740"] },
    { c: "4746", t: 3, ch: 0, aceu: 60, tipo: "OBR", n: "Fundamentos e Metodologia da Extensão Universitária" },

    { c: "4715", t: 4, ch: 60, tipo: "OBR", n: "Estruturas de Dados II", pre: ["4700", "4705"] },
    { c: "4717", t: 4, ch: 60, tipo: "OBR", n: "Engenharia de Software I", pre: ["4711", "4751"] },
    { c: "4718", t: 4, ch: 60, tipo: "OBR", n: "Arquitetura de Computadores", pre: ["4703", "4751"] },
    { c: "4719", t: 4, ch: 60, tipo: "OBR", n: "Pesquisa Operacional", pre: ["4700", "4737", "4739"] },
    { c: "4747", t: 4, ch: 60, tipo: "OBR", n: "Estratégias de Sistemas de Informação", pre: ["4740"] },

    { c: "4720", t: 5, ch: 60, tipo: "OBR", n: "Banco de Dados I", pre: ["4705", "4710"] },
    { c: "4722", t: 5, ch: 60, tipo: "OBR", n: "Engenharia de Software II", pre: ["4710", "4711", "4751"] },
    { c: "4723", t: 5, ch: 60, tipo: "OBR", n: "Sistemas Operacionais", pre: ["4710"] },
    { c: "4724", t: 5, ch: 60, tipo: "OBR", n: "Redes de Computadores", pre: ["4718"], co: ["4723"] },
    { c: "4748", t: 5, ch: 60, tipo: "OBR", n: "Gestão de Projetos", pre: ["4745"] },

    { c: "4725", t: 6, ch: 60, tipo: "OBR", n: "Banco de Dados II", pre: ["4715"] },
    { c: "4727", t: 6, ch: 60, tipo: "OBR", n: "Segurança em Sistemas de Informação", pre: ["4718", "4723"] },
    { c: "4749", t: 6, ch: 60, tipo: "OBR", n: "Projeto e Implementação de Sistemas", pre: ["4745", "4747"] },
    { c: "4750", t: 6, ch: 60, tipo: "OBR", n: "Inteligência Artificial", pre: ["4705"] },

    { c: "4729", t: 7, ch: 60, tipo: "OBR", n: "Gestão de Tecnologia da Informação", pre: ["4748"] },
    { c: "4730", t: 7, ch: 60, tipo: "OBR", n: "Projeto de Redes de Computadores", pre: ["4724"] },
    { c: "4732", t: 7, ch: 60, tipo: "OBR", n: "Engenharia Econômica" },
    { c: "4743", t: 7, ch: 90, tipo: "TRA", n: "Trabalho de Conclusão de Curso I", pre: ["4717", "4720", "4723", "4724"] },

    { c: "4733", t: 8, ch: 60, tipo: "OBR", n: "Empreendedorismo" },
    { c: "4734", t: 8, ch: 120, tipo: "TRA", n: "Trabalho de Conclusão de Curso II", pre: ["4722", "4743"] },
    { c: "4735", t: 8, ch: 60, tipo: "OBR", n: "Direito, Legislação e Ética" },
    { c: "4744", t: 8, ch: 60, tipo: "OBR", n: "Métodos Contemporâneos de Gestão" }
  ],
  optativas: {
    fonte: {
      titulo: "Currículo 2804 (para ingressantes a partir de 2023)",
      url: "https://www.fc.unesp.br/Home/Departamentos/Computacao/bachareladoemsistemasdeinformacao/bsi-curriculo-2804v2.pdf"
    },
    lista: [
      { c: "4552", ch: 60, tipo: "OPT", n: "Processamento de Imagens Digitais" },
      { c: "4556", ch: 60, tipo: "OPT", n: "Sistemas Distribuídos" },
      { c: "4561", ch: 60, tipo: "OPT", n: "Tópicos Avançados em Computação IV" },
      { c: "4572", ch: 60, tipo: "OPT", n: "Tópicos Avançados em Tecnologia da Informação III" },
      { c: "4605", ch: 30, tipo: "OPT", n: "Fundamentos de Computação" },
      { c: "4606", ch: 60, tipo: "OPT", n: "Dispositivos e Circuitos Eletrônicos" },
      { c: "4613", ch: 60, tipo: "OPT", n: "Circuitos Digitais" },
      { c: "4614", ch: 60, tipo: "OPT", n: "Laboratório de Circuitos Digitais" },
      { c: "4623", ch: 60, tipo: "OPT", n: "Teoria da Computação e Linguagens Formais" },
      { c: "4627", ch: 60, tipo: "OPT", n: "Pesquisa Operacional II" },
      { c: "4628", ch: 60, tipo: "OPT", n: "Compiladores" },
      { c: "4632", ch: 60, tipo: "OPT", n: "Microcontroladores" },
      { c: "4633", ch: 60, tipo: "OPT", n: "Computação Gráfica" },
      { c: "4648", ch: 60, tipo: "OPT", n: "Análise de Algoritmos" },
      { c: "4931", ch: 60, tipo: "OPT", n: "Programação Avançada para Windows" },
      { c: "4935", ch: 60, tipo: "OPT", n: "Complexidade de Algoritmos" },
      { c: "4944", ch: 60, tipo: "OPT", n: "Programação para Web" },
      { c: "4979", ch: 60, tipo: "OPT", n: "Web Semântica" },
      { c: "49108", ch: 60, tipo: "OPT", n: "Redes Neurais, Cognição e Sistemas Computacionais" },
      { c: "49125", ch: 60, tipo: "OPT", n: "Realidade Aumentada" },
      { c: "49130", ch: 60, tipo: "OPT", n: "Tópicos Especiais em Aprendizado de Máquina" },
      { c: "49141", ch: 60, tipo: "OPT", n: "Modelagem e Simulação Computacional" },
      { c: "49187", ch: 60, tipo: "OPT", n: "Ciência de Dados" },
      { c: "49190", ch: 60, tipo: "OPT", n: "Ciência de Dados Aplicada" },
      { c: "49191", ch: 60, tipo: "OPT", n: "Programação Competitiva I" },
      { c: "49193", ch: 60, tipo: "OPT", n: "Projeto de Data Warehouse" },
      { c: "49194", ch: 60, tipo: "OPT", n: "Administração de Banco de Dados" },
      { c: "49195", ch: 60, tipo: "OPT", n: "Otimização e Balanceamento de Banco de Dados" },
      { c: "49196", ch: 60, tipo: "OPT", n: "Laboratório de Programação" },
      { c: "49202", ch: 30, tipo: "OPT", n: "Informação Profissional e Acadêmica" },
      { c: "49203", ch: 60, tipo: "OPT", n: "Laboratório de Programação Competitiva" },
      { c: "49208", ch: 60, tipo: "OPT", n: "Laboratório de Programação Competitiva II" },
      { c: "49210", ch: 60, tipo: "OPT", n: "Introdução à Análise Exploratória de Dados" },
      { c: "49215", ch: 60, tipo: "OPT", n: "Técnicas de Otimização de Códigos" },
      { c: "49218", ch: 60, tipo: "OPT", n: "Acessibilidade e Inclusão" },
      { c: "49222", ch: 60, tipo: "OPT", n: "Fundamentos de Matemática Discreta" },
      { c: "49223", ch: 60, tipo: "OPT", n: "Introdução ao Desenvolvimento Web Moderno", pre: ["4700"] },
      { c: "49225", ch: 60, tipo: "OPT", n: "Aprendizado de Máquina Aplicado a Sistemas de Informação" },
      { c: "49300", ch: 60, tipo: "OPT", n: "Computação Científica e Sistemas Embarcados", pre: ["4700", "4705"] },
      { c: "49301", ch: 60, tipo: "OPT", n: "Cibersegurança para Análise de Ataques", pre: ["4723", "4724"] },
      { c: "DPA001", ch: 75, tipo: "EXT", n: "Disciplina Paulista de Acessibilidade e Inclusão" },
      { c: "INTJOR001", ch: 60, tipo: "OPT", n: "Educação Midiática: uso e apropriação da informação" }
    ]
  }
});
