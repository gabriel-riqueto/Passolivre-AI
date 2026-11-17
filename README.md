# PassoLivre AI
## Equipe

| Integrante | RM |
| --- | --- |
| Leticia Resina | 98069 |
| Sabrina Flores | 550781 |
| Gabriel Riqueto | 98685 |

## Funcionalidades e escopo

O sistema recebe perguntas em português e retorna uma resposta estruturada contendo o texto, os IDs das fontes utilizadas e um indicador de recusa. Possui uma API local construída com FastAPI e uma base textual de 17 trechos: dez registros ou políticas simuladas e sete paráfrases de fontes públicas com referência e origem.

Os modos disponíveis são:

| Modo | Comportamento |
| --- | --- |
| `puro` | Consulta a LLM sem fornecer trechos da base. |
| `rag` | Recupera até três trechos com TF-IDF e os fornece ao modelo. |
| `agente` | Utiliza recuperação, consulta exata por identificador de ocorrência e regras de abstenção e validação. |

A especialização foi implementada por ferramentas e regras; não houve fine-tuning, LoRA ou treinamento de pesos. O mecanismo de recuperação é lexical (TF-IDF de palavras e caracteres), não uma base vetorial de embeddings.

Esta versão não realiza detecção automática de obstáculos em fotos, cadastro de usuários, armazenamento de imagens, mapas ou vistorias reais. As ocorrências e os endereços de demonstração são fictícios. A API deve ser mantida localmente: não há autenticação para exposição pública.

## Tecnologias

Python 3.11, FastAPI, Pydantic, scikit-learn, Ollama e modelo `qwen2.5:3b-instruct-q4_K_M`, executado localmente com aceleração por GPU.

## Instalação e execução

Os comandos abaixo consideram Windows PowerShell, com o terminal aberto na raiz `GS-AI`.

### 1. Ambiente Python

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Modelo local

Instale e inicie o Ollama, depois obtenha o modelo usado nos experimentos:

```powershell
ollama pull qwen2.5:3b-instruct-q4_K_M
ollama list
```

Caso o serviço do Ollama não esteja iniciado, execute `ollama serve` em outro terminal. O serviço local padrão utiliza `http://127.0.0.1:11434`.

### 3. Testes automatizados

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Na execução documentada, 27 testes foram aprovados. Eles verificam funcionalidades do código e não substituem a auditoria factual das respostas geradas.

### 4. API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

A documentação interativa estará disponível em `http://127.0.0.1:8000/docs`.

Endpoint de perguntas: `POST /perguntar`. Exemplo de corpo JSON:

```json
{
  "pergunta": "A ocorrência OC002 já foi resolvida?",
  "modo": "agente"
}
```

Outros endpoints disponíveis: `GET /health`, `GET /fontes` e `GET /buscar`.

## Metodologia de avaliação

Foi realizada uma avaliação exploratória de 32 perguntas nos três modos, seguida de retestes dirigidos de cinco erros (Q04, Q07, Q13, Q20 e Q24) e de um conjunto distinto de 16 perguntas. As 48 respostas do conjunto distinto passaram por revisão humana, seguindo `avaliacao/rubrica_humana.md`.

A recuperação foi avaliada por Recall@1 e Recall@3. A correção factual e a presença de alucinações foram classificadas separadamente; uma citação com ID válido não garante que a afirmação esteja sustentada.

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

Os resultados se limitam aos conjuntos e ao corpus avaliados, sem demonstração de generalização para situações reais.

### Reproduzir as métricas

Avaliar recuperação no conjunto distinto sem realizar chamadas à LLM:

```powershell
.\.venv\Scripts\python.exe scripts\avaliar.py --perguntas avaliacao/perguntas_novas.json
```

Gerar novamente o placar a partir da auditoria já concluída (sem consultar a LLM):

```powershell
.\.venv\Scripts\python.exe scripts\placar.py --csv "avaliacao/rodadas/avaliacao_independente_e68b6315fca6/resultados_revisados_v2.csv" --perguntas avaliacao/perguntas_novas.json
```

Os arquivos de evidência encontram-se em `avaliacao/rodadas/`. A rodada `avaliacao_independente_e68b6315fca6` contém o placar final e as respostas auditadas; `reteste_cinco_erros_254bce103d96` contém os resultados dos cinco retestes.

## Estrutura do projeto

```text
GS-AI/
├── app/               # API, LLM, recuperação e agente
├── base/              # Trechos do corpus e descrição da base
├── avaliacao/         # Gabaritos, rubrica, métricas e rodadas
├── docs/              # Relatório técnico e análise de erros
├── notebooks/         # Análise da base, recuperação e comparação
├── scripts/           # Calibração, avaliação e placar
├── tests/             # Testes automatizados
├── requirements.txt
└── README.md
```

## Documentação

- [Relatório técnico (Word)](docs/relatorio_tecnico.docx)
- [Cinco erros e correções](docs/erros_e_correcoes.md)
- [Rubrica de auditoria](avaliacao/rubrica_humana.md)
- [Base de conhecimento](base/trechos.json)


## Privacidade, LGPD e limitações

A base utilizada nos experimentos contém ocorrências fictícias e não armazena fotografias, localizações reais ou cadastros de pessoas. O sistema aceita texto livre nas perguntas e, portanto, não deve ser utilizado com dados pessoais reais sem controles adicionais. A execução local e o uso de dados simulados reduzem a exposição, mas não constituem certificação de conformidade com a LGPD.

Para uma implantação com usuários reais seriam necessários, entre outros, definição de finalidade e base legal, minimização e retenção de dados, controle de acesso, segurança de registros e tratamento de solicitações dos titulares. As respostas do assistente não substituem vistorias, orientação técnica profissional nem a consulta à redação vigente das normas citadas.

## Referências

As referências dos trechos, suas naturezas e URLs estão documentadas em `base/trechos.json`. Incluem a Lei Brasileira de Inclusão (Lei nº 13.146/2015), orientações da Prefeitura de São Paulo sobre calçadas e o Decreto municipal nº 59.671/2020. Os trechos públicos são paráfrases e devem ser conferidos nas fontes oficiais para uso além do experimento.
