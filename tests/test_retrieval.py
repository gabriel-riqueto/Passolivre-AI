import json
from app.core import load_chunks, retrieve, agent_evidence


def test_base_com_proveniencia():
    data = load_chunks()
    assert len(data) == 17
    assert len({d['id'] for d in data}) == len(data)
    assert sum(d['tipo'] == 'publico' for d in data) == 7
    assert all(d['licenca'] and d['referencia'] and d['titulo'] for d in data)


def test_busca_ocorrencia():
    assert retrieve('buraco Rua Exemplo')[0]['id'] == 'S001'


def test_busca_fontes_publicas():
    assert retrieve('artigo 53 Lei Brasileira Inclusão')[0]['id'] == 'G002'


def test_busca_vazia_ou_abaixo_limiar():
    assert retrieve('') == []
    assert retrieve('OC001', min_score=1.1) == []


def test_agent_lookup_exato_prioritario():
    docs, reason = agent_evidence('OC004 foi validada?')
    assert reason is None and docs[0]['id'] == 'S009'


def test_agent_desconhecida_recusada():
    docs, reason = agent_evidence('E quanto à OC999?')
    assert docs == [] and 'Não consta' in reason


def test_agent_certificacao_bloqueada():
    docs, reason = agent_evidence('O trajeto é 100% seguro?')
    assert reason is not None


def test_gabarito_sem_ids_inexistentes():
    from scripts.avaliar import QUESTIONS
    ids = {c['id'] for c in load_chunks()}
    assert len(QUESTIONS) >= 30
    assert all(set(q['trechos_relevantes']) <= ids for q in QUESTIONS)


def test_recall_script_sem_llm():
    from scripts.avaliar import recall_at
    assert recall_at(3) >= recall_at(1)
    assert 0 <= recall_at(1) <= 1
