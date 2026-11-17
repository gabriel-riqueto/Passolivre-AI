# Rubrica para auditoria humana das respostas

Todas as respostas do conjunto selecionado devem ser avaliadas. 

O conjunto original possui 32 perguntas (96 respostas).
O conjunto independente possui 16 perguntas (48 respostas).

Cada pergunta deve ser avaliada nos modos puro, RAG e agente.

Preencher no `resultados.csv`: `correcao_humana` (1/0), `alucinacao_humana` (1/0), `justificativa_humana`, `revisor`, `data_revisao`.

**Correção:** 1 somente se responder corretamente à pergunta, lidar com status/limitações e não contradizer o gabarito; em perguntas sem resposta, somente se recusar adequadamente. Caso contrário, 0.

**Alucinação:** 1 quando houver afirmação objetiva falsa ou não sustentada pelas informações disponíveis para aquele modo; 0 quando não ocorrer. A auditoria deve examinar o texto, não apenas o ID de fonte. Uma citação existente pode acompanhar uma afirmação falsa.

**Recusa:** comparar `recusou` ao gabarito. A taxa total de recusa **não** indica qualidade isoladamente; monitorar recusa correta, recusa indevida e falha de recusa.

**JSON:** é medido estruturalmente. Não confundir cumprimento do JSON com correção factual.

**Recall:** avaliado somente para perguntas com `trechos_relevantes` não vazio; no caso de duas fontes relevantes, mede-se a fração recuperada. Os testes de ausência de informação não entram nessa média, mas contam nas recusas.

**Limiar de recuperação:** o padrão 0,15 foi selecionado em um conjunto separado de 10 consultas em `avaliacao/calibracao.json`; a amostra pequena não prova generalização. Não ajustar repetidamente o limiar olhando este gabarito final.

## Avaliação das citações

Uma citação com identificador válido não garante que a
resposta esteja corretamente fundamentada.

A revisão deve verificar se a fonte citada realmente
sustenta a afirmação apresentada.

Respostas parcialmente corretas, incompletas ou com
fundamentação inadequada recebem correção_humana = 0.

Alucinação deve ser avaliada separadamente:
1 indica afirmação factual falsa ou sem suporte;
0 indica ausência de afirmações desse tipo.

Uma recusa inadequada não constitui automaticamente
uma alucinação.

Toda classificação deve possuir justificativa.
