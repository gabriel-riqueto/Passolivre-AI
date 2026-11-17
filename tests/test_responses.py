import json
import pytest
from app.core import response


def fake_message(resposta='Registrado e pendente.', fontes=None, recusou=False):
    return lambda messages: json.dumps({'resposta': resposta, 'fontes': fontes or [], 'recusou': recusou})


def test_llm_pura_nao_retrieval_e_sem_fontes():
    observed = []
    def fake(messages):
        observed.append(messages)
        return json.dumps({'resposta': 'Não sei se a OC001 foi validada.', 'fontes': [], 'recusou': True})
    result = response('A OC001 foi validada?', 'puro', chat_client=fake)
    assert result['recusou'] is True and result['fontes'] == []
    assert 'TRECHOS' not in observed[0][1]['content']


def test_rag_com_citacao_valida():
    result = response('OC001 foi validada?', 'rag', chat_client=fake_message('Está pendente.', ['S001']))
    assert result['fontes'] == ['S001']
    assert result['evidencias'][0]['id'] == 'S001'
    assert result['validacao']['fundamentacao_estrutural'] is True


def test_agente_com_citacao_valida():
    result = response('OC002 foi resolvida?', 'agente', chat_client=fake_message('Continua em andamento.', ['S002']))
    assert result['fontes'] == ['S002']


def test_citacao_inventada_bloqueada():
    result = response('OC001 foi validada?', 'agente', chat_client=fake_message('Sim', ['FALSA']))
    assert result['recusou'] is True
    assert result['validacao']['citacoes_validas'] is False


def test_fato_sem_citacao_bloqueado_pelo_agente():
    result = response('OC001 foi validada?', 'agente', chat_client=fake_message('Sim', []))
    assert result['recusou'] is True
    assert result['validacao']['bloqueio_agente'] is True


def test_rag_factual_sem_fonte_retorna_metrica_falsa_para_comparar():
    result = response('OC001 foi validada?', 'rag', chat_client=fake_message('Sim', []))
    assert result['recusou'] is False
    assert result['validacao']['fundamentacao_estrutural'] is False


def test_json_quebrado_bloqueado():
    result = response('OC001 foi validada?', 'agente', chat_client=lambda _: 'não é JSON')
    assert result['validacao']['json_valido'] is False
    assert result['recusou'] is True


def test_tipos_incorretos_bloqueados():
    result = response('OC001 foi validada?', 'agente',
                      chat_client=lambda _: '{"resposta": "sim", "fontes": "S001", "recusou": false}')
    assert result['validacao']['json_valido'] is False


def test_identificador_desconhecido_bloqueia_sem_rodar_llm():
    def fail(_):
        raise AssertionError('não deveria chamar LLM')
    result = response('Qual o status OC999?', 'agente', chat_client=fail)
    assert result['recusou'] and result['validacao']['bloqueio_agente']


def test_certificacao_bloqueia_sem_rodar_llm():
    def fail(_):
        raise AssertionError('não deveria chamar LLM')
    result = response('A rota é 100% seguro?', 'agente', chat_client=fail)
    assert result['recusou'] and result['validacao']['bloqueio_agente']


def test_modo_invalido():
    with pytest.raises(ValueError):
        response('Como está OC001?', 'errado', chat_client=fake_message())


def test_pergunta_invalida():
    with pytest.raises(ValueError):
        response('a', 'agente', chat_client=fake_message())


def test_certificacao_no_feminino_tambem_bloqueada():
    def fail(_):
        raise AssertionError('não deveria chamar LLM')
    result = response('Esta rota é 100% segura?', 'agente', chat_client=fail)
    assert result['recusou'] and result['validacao']['bloqueio_agente']
