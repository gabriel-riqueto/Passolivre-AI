"""Calibração de score do retriever em conjunto SEPARADO do gabarito principal."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core import ROOT, retrieve

questions = json.loads((ROOT/'avaliacao/calibracao.json').read_text(encoding='utf-8'))
thresholds = (0.08, 0.12, 0.15, 0.16, 0.18, 0.20)
rows = []
for q in questions:
    found = retrieve(q['pergunta'], k=1, min_score=0.0)
    rows.append({**q, 'top1_score': found[0]['score'] if found else 0.0,
                 'top1_id': found[0]['id'] if found else None})

for threshold in thresholds:
    tp = sum(r['tem_fonte'] and r['top1_id'] == r['id_esperado'] and r['top1_score'] >= threshold for r in rows)
    fn = sum(r['tem_fonte'] and not (r['top1_id'] == r['id_esperado'] and r['top1_score'] >= threshold) for r in rows)
    tn = sum(not r['tem_fonte'] and r['top1_score'] < threshold for r in rows)
    fp = sum(not r['tem_fonte'] and r['top1_score'] >= threshold for r in rows)
    print(f'Limiar {threshold:.2f} | TP={tp} FN={fn} TN={tn} FP={fp}')

out=ROOT/'avaliacao'/'calibracao_resultados.json'
out.write_text(json.dumps({'nota': 'Calibração exploratória de 10 consultas; não é teste de generalização.',
                           'candidatos': rows, 'limiar_selecionado': 0.15},
                          indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Resultado salvo em:',out)
