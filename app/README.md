# App FastAPI - laborator 2

## Rulare

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Deschide in browser:
- http://127.0.0.1:8000/docs

Endpoint-uri implementate:
- GET /produse
- GET /produse/{produs_id}
- POST /produse
- DELETE /produse/{produs_id}
