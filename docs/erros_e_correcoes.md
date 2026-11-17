# PassoLivre AI — cinco erros reais e retestes após correção

## Evidências, escopo e cautelas

- **Antes:** `avaliacao/resultados.csv`, com 32 perguntas × 3 modos = 96 linhas.
- **Depois:** `avaliacao/rodadas/reteste_cinco_erros_254bce103d96/resultados.csv`, com Q04, Q07, Q13, Q20 e Q24 em cada modo = 15 linhas.
- **Código inspecionado:** `app/core.py`, contendo `RAG_PROMPT`, `AGENT_PROMPT` e validações estruturais.
- As perguntas comparadas têm o mesmo enunciado nas duas rodadas. Nos cinco pares de interesse, `json_valido=True` e `chamada_llm=True` na rodada posterior.
- **Importante:** `recusou=False` significa que o modelo não marcou a saída como recusa, mas não comprova automaticamente a precisão factual do texto.

## Resumo

| Pergunta | Modo-alvo | Problema original | Resultado do reteste | Fonte |
|---|---|---|---|---|
| Q04 | `agente` | Rejeição da OC003 confundida com recusa | **Falha principal corrigida** | S003, S004 |
| Q07 | `agente` | Insuficiência de evidência alegada indevidamente para visão computacional | **Falha principal corrigida** | S008 |
| Q13 | `agente` | Ocorrência resolvida interpretada como informação insuficiente | **Falha principal corrigida** | S010 |
| Q20 | `rag` | Exceção de 80 cm negada apesar da fonte normativa | **Falha principal corrigida** | G006, G004 |
| Q24 | `agente` | Resposta negativa correta rotulada como recusa | **Falha principal corrigida** | G006 |

## Evidências por caso

### Q04 — Rejeição da OC003 confundida com recusa

**Modo observado:** `agente`  
**Pergunta:** Por que o relato OC003 foi rejeitado?  
**Fontes de referência:** S003; S004

**Antes — resposta literal:**

> O relato OC003 foi rejeitado porque a verificação não confirmou a ocorrência de desnível. A razão para a rejeição foi que a foto enviada era insuficiente para validar a ocorrência. Não há ocorrência confirmada de desnível na Praça Protótipo, conforme consta no registro simulado OC003.

**Antes — metadados:** `fontes=S003`, `recusou=True`, `deve_recusar=False`.

**Diagnóstico:** A fonte S003 informa que a fotografia era insuficiente. Na versão original, o agente explicou o motivo corretamente, mas marcou `recusou=True`. Assim, a falha principal foi a classificação estrutural da resposta, e não a invenção de um fato.

**Alteração no código:** O `RAG_PROMPT` passou a estabelecer `recusou=false` para fatos documentados, inclusive quando o relato foi rejeitado; o `AGENT_PROMPT` diferencia relato rejeitado de barreira confirmada.

**Depois — resposta literal:**

> O relato OC003 foi rejeitado porque a foto enviada era insuficiente para confirmar o desnível no local. A verificação rejeitou o relato, conforme estabelecido na política do PassoLivre.

**Depois — metadados:** `fontes=S003;S004`, `recusou=False`, `deve_recusar=False`, `json_valido=True`, `chamada_llm=True`.

**Conclusão:** Corrigido no reteste: o agente explicou a rejeição e marcou `recusou=False`.

### Q07 — Insuficiência de evidência alegada indevidamente para visão computacional

**Modo observado:** `agente`  
**Pergunta:** Visão computacional sozinha confirma um obstáculo?  
**Fontes de referência:** S008

**Antes — resposta literal:**

> Não consta informação suficiente para afirmar que visão computacional sozinha confirma um obstáculo.

**Antes — metadados:** `fontes=S008`, `recusou=True`, `deve_recusar=False`.

**Diagnóstico:** S008 esclarece que a visão computacional pode sugerir possíveis obstáculos, mas não comprova sua existência sem revisão humana. A resposta inicial alegou falta de informação e assinalou recusa.

**Alteração no código:** Regras do `RAG_PROMPT` passaram a diferenciar resposta negativa de recusa; o `AGENT_PROMPT` ganhou instrução para explicar capacidade, limitação e necessidade de etapa adicional quando a pergunta trata de ferramenta ou processo.

**Depois — resposta literal:**

> Visão computacional sozinha não confirma um obstáculo. Ela apenas sugere possíveis problemas, que precisam ser revisados por humanos.

**Depois — metadados:** `fontes=S008`, `recusou=False`, `deve_recusar=False`, `json_valido=True`, `chamada_llm=True`.

**Conclusão:** Corrigido no reteste: o agente disse que a visão computacional isolada não confirma o obstáculo, explicou a necessidade de revisão humana e marcou `recusou=False`.

### Q13 — Ocorrência resolvida interpretada como informação insuficiente

**Modo observado:** `agente`  
**Pergunta:** O piso irregular no Caminho Demonstrativo 42 continua aberto?  
**Fontes de referência:** S010

**Antes — resposta literal:**

> Não consta informação suficiente para afirmar que o piso irregular no Caminho Demonstrativo 42 continua aberto.

**Antes — metadados:** `fontes=S010`, `recusou=True`, `deve_recusar=False`.

**Diagnóstico:** S010 registra a ocorrência OC005 como resolvida, com evidência anexada. A resposta inicial não usou esse estado para responder se a ocorrência continuava aberta.

**Alteração no código:** O `AGENT_PROMPT` esclarece `resolvido` versus `em aberto`; o `RAG_PROMPT` determina resposta direta e `recusou=false` para estados explicitamente informados.

**Depois — resposta literal:**

> O piso irregular no Caminho Demonstrativo 42 foi resolvido, conforme o registro simulado OC005. No entanto, não há informações sobre a situação atual do piso irregular após a resolução.

**Depois — metadados:** `fontes=S010`, `recusou=False`, `deve_recusar=False`, `json_valido=True`, `chamada_llm=True`.

**Conclusão:** Falha principal corrigida: o agente informa que a ocorrência foi resolvida e marca `recusou=False`. Ressalva: acrescenta que não há informação sobre o estado posterior à resolução, o que é desnecessário e pode gerar confusão. Não se deve apresentar esse caso como qualidade textual perfeita.

### Q20 — Exceção de 80 cm negada apesar da fonte normativa

**Modo observado:** `rag`  
**Pergunta:** Há exceção para passagem com 80 cm em São Paulo?  
**Fontes de referência:** G006; G004

**Antes — resposta literal:**

> Não há exceção para passagem com 80 cm em São Paulo conforme os trechos fornecidos.

**Antes — metadados:** `fontes=G006;G004`, `recusou=False`, `deve_recusar=False`.

**Diagnóstico:** G006 contempla hipóteses excepcionais de passagem com 80 cm, condicionadas à situação e à norma aplicável. O RAG original afirmou que não havia exceção, contrariando o documento recuperado.

**Alteração no código:** A regra 4 do `RAG_PROMPT` passou a exigir que o sistema explique regra geral e exceções condicionadas com ressalvas, sem aprovar automaticamente um local.

**Depois — resposta literal:**

> Há exceção para passagem com 80 cm em São Paulo, mas deve ser avaliado caso a caso e a norma aplicável deve ser considerada.

**Depois — metadados:** `fontes=G006`, `recusou=False`, `deve_recusar=False`, `json_valido=True`, `chamada_llm=True`.

**Conclusão:** Corrigido no reteste do RAG: reconheceu a existência de exceção condicionada e a necessidade de avaliação caso a caso. O modo puro continuou negando a exceção; ele não consulta o corpus e não faz parte desta correção.

### Q24 — Resposta negativa correta rotulada como recusa

**Modo observado:** `agente`  
**Pergunta:** Uma calçada de 90 cm pode ser automaticamente aprovada?  
**Fontes de referência:** G006

**Antes — resposta literal:**

> Não pode ser automaticamente aprovada sem avaliação do caso e da norma aplicável.

**Antes — metadados:** `fontes=G006`, `recusou=True`, `deve_recusar=False`.

**Diagnóstico:** A resposta original explicava que uma calçada de 90 cm não pode ser aprovada automaticamente, mas o campo `recusou` foi marcado como verdadeiro. É erro de classificação, não necessariamente de conteúdo.

**Alteração no código:** O `RAG_PROMPT` passou a dizer expressamente que “não pode ser aprovado automaticamente” constitui resposta negativa documentada, não recusa.

**Depois — resposta literal:**

> Não, uma calçada de 90 cm não pode ser automaticamente aprovada sem avaliação específica

**Depois — metadados:** `fontes=G006`, `recusou=False`, `deve_recusar=False`, `json_valido=True`, `chamada_llm=True`.

**Conclusão:** Corrigido no reteste: o agente manteve a resposta negativa adequada e marcou `recusou=False`.

## Observações adicionais da rodada

- Q07 também melhorou no modo `rag`: de uma resposta que alegava evidência insuficiente para a explicação direta de que a visão computacional isolada não confirma um obstáculo.
- Q13 também melhorou no `rag`: de `recusou=True` por falta de informação para resposta correta de que a ocorrência estava resolvida.
- Q24 também corrigiu a classificação de `recusou` no modo `rag`: `True` → `False`.
- O reteste confirma esses cinco comportamentos nas perguntas examinadas, mas não prova que a mudança generaliza para novas perguntas ou elimina alucinações em qualquer situação.
