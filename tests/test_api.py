from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_nao_finge_ollama():
    r = client.get('/health')
    assert r.status_code == 200
    assert 'Não testa' in r.json()['observacao']


def test_fontes_endpoint():
    r = client.get('/fontes')
    assert r.status_code == 200
    assert len(r.json()) == 17
    assert all('referencia' in x for x in r.json())


def test_invalida_modo_retorna_422():
    r = client.post('/perguntar', json={'pergunta': 'A OC001 foi resolvida?', 'modo': 'inventado'})
    assert r.status_code == 422


def test_buscar_limite_k():
    r = client.get('/buscar', params={'q': 'buraco na calçada', 'k': 11})
    assert r.status_code == 422


def test_erro_ollama_retorna_503(monkeypatch):
    from app.core import OllamaError
    monkeypatch.setattr('app.main.response', lambda *args: (_ for _ in ()).throw(OllamaError('fora')))
    r = client.post('/perguntar', json={'pergunta': 'ocorrência OC001', 'modo': 'puro'})
    assert r.status_code == 503
