from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_real():
    response = client.post("/api/chat", json={"query": "Apa rekomendasi cafe yang enak untuk WFA"})
    assert response.status_code == 200

    data = response.json()
    print("Jawaban AI:", data["answer"])

    assert "tidak tahu" in data["answer"].lower() or len(data["answer"]) > 10