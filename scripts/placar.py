"""Calcula métricas estruturais e métricas humanas após revisão completa."""

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = ("puro", "rag", "agente")


def as_bool(value):
    return str(value).strip().casefold() in ("true", "verdadeiro", "1")


def caminho(valor):
    path = Path(valor)
    return path if path.is_absolute() else ROOT / path


def avaliada(row):
    return (
        row.get("correcao_humana") in ("0", "1")
        and row.get("alucinacao_humana") in ("0", "1")
        and bool(row.get("justificativa_humana", "").strip())
        and bool(row.get("revisor", "").strip())
        and bool(row.get("data_revisao", "").strip())
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--csv",
        default="avaliacao/resultados.csv",
        help="Arquivo CSV com as respostas avaliadas"
    )

    parser.add_argument(
        "--perguntas",
        default="avaliacao/perguntas.json",
        help="Arquivo JSON com o gabarito correspondente"
    )

    args = parser.parse_args()

    csv_path = caminho(args.csv)
    question_path = caminho(args.perguntas)

    if not csv_path.is_file():
        parser.error(f"CSV não encontrado: {csv_path}")

    if not question_path.is_file():
        parser.error(f"Gabarito não encontrado: {question_path}")

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))

    expected = json.loads(
        question_path.read_text(encoding="utf-8")
    )

    if not rows or not expected:
        parser.error("CSV ou conjunto de perguntas vazio.")

    expected_ids = [q["id"] for q in expected]

    if len(set(expected_ids)) != len(expected_ids):
        parser.error("IDs duplicados no gabarito.")

    expected_pairs = {
        (qid, mode)
        for qid in expected_ids
        for mode in MODES
    }

    actual_pairs = [
        (row.get("id"), row.get("modo"))
        for row in rows
    ]

    if (
        len(actual_pairs) != len(expected_pairs)
        or set(actual_pairs) != expected_pairs
    ):
        parser.error(
            "O CSV deve conter exatamente uma linha "
            "por pergunta e por modo, sem duplicações."
        )

    output = {
        "metodologia": (
            "Acurácia e alucinação exigem revisão humana completa. "
            "Recusa conforme gabarito não equivale a acurácia."
        ),
        "modos": {}
    }

    for mode in MODES:
        sample = [
            row for row in rows
            if row["modo"] == mode
        ]

        generated = [
            row for row in sample
            if as_bool(row["chamada_llm"])
        ]

        total = len(sample)

        metrics = {
            "total_questoes": total,

            "fracao_chamadas_llm": round(
                len(generated) / total, 4
            ),

            "json_valido_nas_geracoes": (
                round(
                    sum(as_bool(r["json_valido"]) for r in generated)
                    / len(generated), 4
                )
                if generated else None
            ),

            "citacoes_ids_validos_nas_geracoes": (
                round(
                    sum(as_bool(r["citacoes_validas"]) for r in generated)
                    / len(generated), 4
                )
                if generated and mode != "puro" else None
            ),

            "recusas_conforme_gabarito": round(
                sum(as_bool(r["recusa_correta"]) for r in sample)
                / total, 4
            ),

            "respostas_fundamentadas_estruturalmente": round(
                sum(
                    as_bool(r["fundamentacao_estrutural"])
                    for r in sample
                ) / total, 4
            )
        }

        reviewed_count = sum(
            avaliada(row) for row in sample
        )

        metrics["revisadas"] = f"{reviewed_count}/{total}"

        if reviewed_count == total:
            metrics["acuracia_humana"] = round(
                sum(
                    int(row["correcao_humana"])
                    for row in sample
                ) / total, 4
            )

            metrics["taxa_alucinacao_humana"] = round(
                sum(
                    int(row["alucinacao_humana"])
                    for row in sample
                ) / total, 4
            )

        else:
            metrics["acuracia_humana"] = None
            metrics["taxa_alucinacao_humana"] = None
            metrics["situacao_revisao"] = "PENDENTE"

        output["modos"][mode] = metrics

    outpath = csv_path.with_name("placar.json")

    outpath.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print(json.dumps(output, ensure_ascii=False, indent=2))
    print("Placar:", outpath)


if __name__ == "__main__":
    main()