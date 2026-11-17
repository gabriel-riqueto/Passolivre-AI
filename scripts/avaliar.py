"""Avaliação offline de recall; --llm chama Ollama e salva dados BRUTOS.

Nunca declara acurácia/hallucination auditadas sem preenchimento humano.
"""
import argparse
import csv
import json
import sys
import unicodedata
import hashlib
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core import ROOT, MODEL, OllamaError, response, retrieve
questions = json.loads((ROOT / 'avaliacao/perguntas.json').read_text(encoding='utf-8'))
OUT = ROOT / 'avaliacao'
QUESTIONS = json.loads((OUT / "perguntas.json").read_text(encoding="utf-8"))

def recall_at(k, questions=questions):
    queries = [q for q in questions if q['trechos_relevantes']]
    if not queries:
        return None
    scores = []
    for q in queries:
        relevant = set(q['trechos_relevantes'])
        found = {d['id'] for d in retrieve(q['pergunta'], k=k)}
        scores.append(len(relevant & found) / len(relevant))
    return round(sum(scores) / len(scores), 4)


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s.casefold()) if not unicodedata.combining(c))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--llm', action='store_true', help='executa os 3 modos contra o Ollama local')
    parser.add_argument('--limit', type=int, default=0, help='somente primeiras N perguntas (smoke test, NÃO comparar notas)')
    parser.add_argument('--reset', action='store_true', help='exclui checkpoint anterior da geração')
    parser.add_argument('--rodada', type=str, default='v2_prompts', help='Identificação da rodada experimental')
    parser.add_argument('--perguntas', type=str, default='avaliacao/perguntas.json', help='Arquivo JSON contendo o conjunto de perguntas')
    args = parser.parse_args()
    questions_path = ROOT / args.perguntas

    if not questions_path.is_file():
        parser.error(
            f"Arquivo de perguntas não encontrado: {questions_path}"
        )
    questions = json.loads(
        questions_path.read_text(encoding="utf-8")
    )
    if not isinstance(questions, list) or not questions:
        parser.error("O conjunto de perguntas está vazio ou inválido.")
    print(f'Corpus: {len(__import__("app.core", fromlist=["load_chunks"]).load_chunks())} trechos')
    print(f'Questões: {len(questions)}; recuperação: {sum(bool(q["trechos_relevantes"]) for q in questions)}')
    recall = {'recall_at_1': recall_at(1, questions), 'recall_at_3': recall_at(3, questions)}
    print('Recall@1:', recall['recall_at_1'], 'Recall@3:', recall['recall_at_3'])
    with (OUT / 'recall_resultados.json').open('w', encoding='utf-8') as f:
        json.dump({'metrica': 'media da fração de fontes relevantes recuperadas por questão',
                   'limitacao': 'busca TF-IDF + n-gramas; não é busca semântica', **recall}, f, indent=2, ensure_ascii=False)
    if not args.llm:
        print('LLM NÃO executada: use --llm para gerar resultados brutos. Não existem métricas reais de alucinação.')
        return 0
    if args.limit < 0:
        parser.error('--limit deve ser 0 (todos) ou positivo')
    chosen = questions[:args.limit] if args.limit else questions
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", args.rodada):
        parser.error("Use apenas letras, números, _ ou - no nome da rodada.")
    assinatura = {
        "perguntas": questions,
        "modelo": MODEL,
        "core_sha256": hashlib.sha256(
            (ROOT / "app" / "core.py").read_bytes()
        ).hexdigest(),
        "base_sha256": hashlib.sha256(
            (ROOT / "base" / "trechos.json").read_bytes()
        ).hexdigest()
    }
    fingerprint = hashlib.sha256(
        json.dumps(
            assinatura,
            ensure_ascii=False,
            sort_keys=True
        ).encode("utf-8")
    ).hexdigest()[:12]
    run_dir = OUT / "rodadas" / f"{args.rodada}_{fingerprint}"
    run_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = run_dir / "checkpoint.jsonl"
    configuracao = {
        "rodada": args.rodada,
        "fingerprint": fingerprint,
        "modelo": MODEL,
        "quantidade_perguntas": len(questions),
        "core_sha256": assinatura["core_sha256"],
        "base_sha256": assinatura["base_sha256"]
    }
    (run_dir / "configuracao.json").write_text(
        json.dumps(configuracao, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    (run_dir / "recall_resultados.json").write_text(
        (OUT / "recall_resultados.json").read_text(encoding="utf-8"),
        encoding="utf-8"
    )
    if args.reset and checkpoint.exists():
        checkpoint.unlink()
    existing = {}
    if checkpoint.exists():
        for line in checkpoint.read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                existing[(row['id'], row['modo'])] = row
    results = []
    for q in chosen:
        for mode in ('puro', 'rag', 'agente'):
            key = (q['id'], mode)
            if key in existing:
                results.append(existing[key])
                print(f"{q['id']}/{mode}: reaproveitado checkpoint")
                continue
            try:
                result = response(q['pergunta'], mode)
                prediction = result['resposta']
                terms = q['termos_chave']
                term_hit = bool(terms) and any(fold(t) in fold(prediction) for t in terms)
                row = {
                    'id': q['id'], 'modo': mode, 'pergunta': q['pergunta'],
                    'resposta': prediction, 'fontes': ';'.join(result['fontes']),
                    'recusou': result['recusou'],
                    'deve_recusar': q['deve_recusar'],
                    'recusa_correta': result['recusou'] == q['deve_recusar'],
                    'termo_encontrado_nao_e_acuracia': term_hit,
                    'json_valido': result['validacao']['json_valido'],
                    'chamada_llm': result['validacao']['chamada_llm'],
                    'citacoes_validas': result['validacao']['citacoes_validas'],
                    'fundamentacao_estrutural': result['validacao']['fundamentacao_estrutural'],
                    'correcao_humana': '', 'alucinacao_humana': '',
                    'justificativa_humana': '', 'revisor': '', 'data_revisao': ''
                }
                results.append(row)
                with checkpoint.open('a', encoding='utf-8') as f:
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')
                print(f"{q['id']}/{mode}: salvo no checkpoint")
            except OllamaError as exc:
                print(f'FALHA {q["id"]}/{mode}: {exc}', file=sys.stderr)
                print('Resultados anteriores preservados no checkpoint. Reinicie após corrigir Ollama.', file=sys.stderr)
                return 2
    out = run_dir / ('resultados_amostra.csv' if args.limit else 'resultados.csv')
    with out.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        resumo = {
            "aviso": (
                "Métricas estruturais. Não representam "
                "acurácia factual nem taxa de alucinação."
            ),
            "recall": recall,
            "modos": {}
        }

        for mode in ("puro", "rag", "agente"):
            subset = [r for r in results if r["modo"] == mode]

            chamadas = [
                r for r in subset
                if r["chamada_llm"] is True
            ]

            total = len(subset)

            resumo["modos"][mode] = {
                "total_perguntas": total,

                "chamadas_llm": len(chamadas),

                "recusa_conforme_gabarito_pct": round(
                    100 * sum(r["recusa_correta"] is True for r in subset) / total,
                    2
                ) if total else None,

                "json_valido_nas_chamadas_pct": round(
                    100 * sum(r["json_valido"] is True for r in chamadas)
                    / len(chamadas),
                    2
                ) if chamadas else None,

                "fundamentacao_estrutural_pct": round(
                    100 * sum(
                        r["fundamentacao_estrutural"] is True
                        for r in subset
                    ) / total,
                    2
                ) if total else None
            }

        (run_dir / "resumo_automatico.json").write_text(
            json.dumps(resumo, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
    if args.limit:
        print('AVISO: amostra parcial para checagem técnica. Não use como placar final.')
    print('Respostas brutas gravadas em:', out)
    print('Acurácia/alucinação dependem de preenchimento e revisão HUMANA, não foram calculadas.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
