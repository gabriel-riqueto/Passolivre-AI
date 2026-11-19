# PassoLivre AI

Projeto acadêmico de inteligência artificial generativa voltado a perguntas sobre acessibilidade urbana, utilizando uma base de conhecimento textual e um modelo de linguagem executado localmente.

## Equipe

| Integrante | RM |
| --- | --- |
| Leticia Resina | 98069 |
| Sabrina Flores | 550781 |
| Gabriel Riqueto | 98685 |

## Funcionalidades e escopo

O sistema recebe perguntas em português e retorna uma resposta estruturada com o texto gerado, os identificadores das fontes utilizadas e um indicador de recusa. A interface de acesso é uma API local desenvolvida com FastAPI.

A base de conhecimento contém 17 trechos: dez registros ou políticas simuladas e sete paráfrases de fontes públicas identificadas por referência e origem.

| Modo | Comportamento |
| --- | --- |
| `puro` | Consulta a LLM sem apresentar trechos da base de conhecimento. |
| `rag` | Recupera até três trechos relevantes com TF-IDF e os apresenta ao modelo. |
| `agente` | Combina recuperação textual, consulta exata por identificador de ocorrência e regras de abstenção e validação. |

A adaptação ao domínio foi realizada por prompts, ferramentas e regras. Não houve fine-tuning, LoRA ou treinamento de pesos. A recuperação de informações é lexical, baseada em TF-IDF de palavras e caracteres, e não utiliza embeddings ou um banco de dados vetorial.

### Limitações do protótipo

O projeto não realiza identificação automática de obstáculos em fotografias, cadastro de usuários, armazenamento de imagens, mapas ou vistorias reais. As ocorrências e os endereços usados na demonstração são fictícios.

## Tecnologias

- Python 3.11
- FastAPI e Pydantic
- scikit-learn (recuperação TF-IDF)
- Ollama
- Modelo `qwen2.5:3b-instruct-q4_K_M`
- Pytest para testes automatizados

O modelo é executado localmente. O tempo de geração varia conforme o hardware; a aceleração por GPU pode ser utilizada quando disponível e compatível com o Ollama.

## Como executar o projeto

As instruções abaixo consideram Windows com PowerShell. Execute os comandos na ordem indicada. Cada comando ocupa uma única linha.

### 1. Pré-requisitos

Tenha instalados o Git, o Python 3.11 (com o comando `py` disponível) e o Ollama. É necessário ter acesso à internet para baixar as dependências e o modelo na primeira execução.

### 2. Baixar o código

Abra o PowerShell na pasta onde deseja salvar o projeto e execute:

```powershell
git clone https://github.com/gabriel-riqueto/Passolivre-AI.git
cd .\Passolivre-AI
```

Todos os comandos a seguir devem ser executados na raiz da pasta clonada, onde está o arquivo `requirements.txt`.

### 3. Preparar o ambiente Python

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os comandos utilizam o Python do ambiente virtual diretamente; não é necessário ativá-lo no terminal.

### 4. Iniciar o Ollama e baixar o modelo

Com o Ollama instalado e em execução, abra um terminal e execute:

```powershell
ollama pull qwen2.5:3b-instruct-q4_K_M
ollama list
```

Confirme que `qwen2.5:3b-instruct-q4_K_M` aparece na listagem. Normalmente o Ollama funciona em `http://127.0.0.1:11434`. Se o serviço não estiver em execução, abra outro terminal e execute:

```powershell
ollama serve
```

Por padrão, o código utiliza o modelo `qwen2.5:3b-instruct-q4_K_M`. Caso você já tenha definido a variável de ambiente `PASSOLIVRE_MODEL` com outro valor no seu computador, ajuste-a no terminal que iniciará a API:

```powershell
$env:PASSOLIVRE_MODEL = "qwen2.5:3b-instruct-q4_K_M"
```

### 5. Executar os testes automatizados

Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Na execução documentada do projeto, 27 testes foram aprovados. Os testes verificam comportamentos do código, mas não substituem a revisão humana da precisão factual das respostas.

### 6. Iniciar a API

Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Com a API em execução, abra no navegador:

**http://127.0.0.1:8000/docs**

A página contém o Swagger, que permite experimentar os endpoints. Para testar uma pergunta, expanda POST `/perguntar`, clique em Try it out, insira o JSON e depois clique em Execute:

```json
{
  "pergunta": "A ocorrência OC002 já foi resolvida?",
  "modo": "agente"
}
```

A resposta apresenta o texto gerado, as fontes utilizadas e informações de validação. Também estão disponíveis:

| Endpoint | Finalidade |
| --- | --- |
| `GET /health` | Verificar se a API está em funcionamento; não testa a conexão com o Ollama. |
| `GET /fontes` | Listar as fontes presentes na base de conhecimento. |
| `GET /buscar` | Consultar os trechos recuperados pela busca lexical. |
| `POST /perguntar` | Enviar uma pergunta, selecionando `puro`, `rag` ou `agente`. |

> **Observação:** a primeira geração pode ser mais lenta por causa do carregamento do modelo na memória.

### Problemas comuns

| Situação | Verificação sugerida |
| --- | --- |
| `py -3.11` não funciona | Confira a instalação do Python 3.11 e o Python Launcher do Windows. |
| A API informa indisponibilidade do Ollama (HTTP 503) | Confira se o Ollama está aberto e se o modelo aparece em `ollama list`. |
| O modelo não é encontrado | Execute novamente `ollama pull qwen2.5:3b-instruct-q4_K_M` e confira `PASSOLIVRE_MODEL`. |
| A porta 8000 está ocupada | Feche o processo que a utiliza ou inicie a API em outra porta e abra o `/docs` nessa porta. |

## Metodologia de avaliação

Foi realizada uma avaliação exploratória de 32 perguntas nos três modos, seguida de retestes dirigidos de cinco erros (Q04, Q07, Q13, Q20 e Q24) e de um conjunto distinto de 16 perguntas. As 48 respostas do conjunto distinto passaram por revisão humana conforme `avaliacao/rubrica_humana.md`.

A recuperação foi avaliada por **Recall@1** e **Recall@3**. A correção factual e a ocorrência de alucinações foram classificadas separadamente: uma citação com ID válido não garante que a afirmação esteja sustentada pelo trecho citado.

### Resultados da avaliação independente

| Métrica | Puro | RAG | Agente |
| --- | ---: | ---: | ---: |
| Respostas auditadas | 16 | 16 | 16 |
| Correção humana | 18,75% | 68,75% | 75,00% |
| Taxa de alucinação | 25,00% | 6,25% | 12,50% |
| Recusas conforme gabarito | 68,75% | 75,00% | 93,75% |
| JSON válido nas gerações | 100% | 100% | 100% |

| Conjunto | Recall@1 | Recall@3 |
| --- | ---: | ---: |
| Avaliação original (24 questões com fonte relevante) | 89,58% | 97,92% |
| Avaliação independente (12 questões com fonte relevante) | 75,00% | 83,33% |

Os valores representam apenas os conjuntos e a base avaliados e não comprovam generalização para situações reais.

### Reproduzir as métricas

Para avaliar a recuperação no conjunto independente, *em realizar chamadas à LLM:

```powershell
.\.venv\Scripts\python.exe scripts\avaliar.py --perguntas avaliacao/perguntas_novas.json
```

Para gerar o placar a partir da auditoria humana concluída, também sem consultar a LLM:

```powershell
.\.venv\Scripts\python.exe scripts\placar.py --csv "avaliacao/rodadas/avaliacao_independente_e68b6315fca6/resultados_revisados_v2.csv" --perguntas avaliacao/perguntas_novas.json
```

Os registros e resultados encontram-se em `avaliacao/rodadas/`. A pasta `avaliacao_independente_e68b6315fca6` contém o placar final e as respostas revisadas; `reteste_cinco_erros_254bce103d96` registra os retestes dirigidos.

## Estrutura do projeto

```text
Passolivre-AI/
├── app/               # API, LLM, recuperação e regras do agente
├── base/              # Trechos do corpus e documentação da base
├── avaliacao/         # Perguntas, rubrica, métricas e resultados
├── docs/              # Relatório técnico e análise de erros
├── notebooks/         # Auditoria da base e comparação de métodos
├── scripts/           # Scripts de avaliação e geração do placar
├── tests/             # Testes automatizados
├── .env.example       # Exemplos opcionais de variáveis de ambiente
├── requirements.txt
└── README.md
```

## Documentação complementar

- [Relatório técnico](docs/relatorio_tecnico.docx)
- [Cinco erros e correções](docs/erros_e_correcoes.md)
- [Rubrica de auditoria](avaliacao/rubrica_humana.md)
- [Base de conhecimento](base/trechos.json)
- [Placar](rodadas/avaliacao_independente_e68b6315fca6/placar.json)

## Privacidade e limitações de uso

O conjunto de demonstração contém dados simulados e não inclui fotografias, localizações reais ou cadastros pessoais. Como a API recebe texto livre, não se deve inserir dados pessoais reais sem controles apropriados. As respostas produzidas não substituem vistorias técnicas nem podem certificar a segurança de um percurso.

## Referências

As fontes, suas naturezas, suas referências e seus endereços estão documentados em `base/trechos.json`. Incluem a Lei Brasileira de Inclusão (Lei nº 13.146/2015), orientações da Prefeitura de São Paulo sobre calçadas e o Decreto municipal nº 59.671/2020. Os textos públicos são paráfrases e devem ser verificados nas fontes oficiais para uso fora do experimento acadêmico.
