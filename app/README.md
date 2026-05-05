# App FastAPI - laboratoarele 3 + 4 + 5

Aplicatia implementeaza un task manager cu SQLite, JWT, CRUD protejat, endpoint PATCH de finalizare rapida, filtrare pentru sarcini nefinalizate, interfata web completa si configurare pregatita pentru deployment.

Proiectul este organizat pe layere, pregatit pentru extindere ulterioara cu Alembic, fara a adauga complexitate inutila.

## Interfata web (Lab 4)

Interfata este in directorul static si acopera flux complet:

- inregistrare si autentificare
- listare sarcini cu filtru server-side pentru nefinalizate
- cautare client-side dupa titlu
- creare, editare inline, finalizare, stergere cu confirmare
- statistici rapide (total, in progres, finalizate)
- notificari toast reutilizabile pentru succes/eroare/atentie
- refresh automat al paginii cand detecteaza schimbari in fisierele frontend

UI este responsive si servit direct de FastAPI la ruta /. Frontend-ul foloseste URL-uri relative pentru API.

## Structura pe layere

- api: transport HTTP, routere, dependinte FastAPI
- services: reguli de business si orchestrare cazuri de utilizare
- db: schema initiala, sesiune SQLite, repositories
- core: configurare, securitate, exceptii de domeniu
- schemas: contracte Pydantic pentru request/response

Structura actuala:

- main.py
- api/app.py
- api/dependencies.py
- api/routers/auth.py
- api/routers/tasks.py
- services/auth_service.py
- services/task_service.py
- db/schema.py
- db/session.py
- db/repositories.py
- core/config.py
- core/security.py
- core/exceptions.py
- schemas/auth.py
- schemas/task.py
- static/index.html
- static/assets/styles.css
- static/assets/app.js
- render.yaml
- Dockerfile
- docker-compose.yml
- .dockerignore

## Rulare (din app)

Important: repository-ul git este in app/, iar laboratorul markdown poate ramane in directorul parinte.

1. Intra in app:

cd /home/user/Desktop/Labs/app

2. Activeaza mediul virtual local:

source venv/bin/activate

3. Configureaza SECRET_KEY in fisierul .env din app:

SECRET_KEY=dev-only-change-this-secret

4. Instaleaza dependintele si ruleaza:

pip install -r requirements.txt
uvicorn main:app --reload

Optional, poti suprascrie valoarea din .env direct din shell:

export SECRET_KEY="alta-cheie"

Swagger UI:
- http://127.0.0.1:8000/docs

Interfata web:
- http://127.0.0.1:8000/

## Endpoint-uri

- POST /inregistrare
- POST /autentificare
- GET /sarcini
- GET /sarcini/{sarcina_id}
- POST /sarcini
- PUT /sarcini/{sarcina_id}
- PATCH /sarcini/{sarcina_id}/finalizeaza
- DELETE /sarcini/{sarcina_id}

## Note pentru frontend

- autentificarea foloseste OAuth2PasswordRequestForm, deci /autentificare primeste application/x-www-form-urlencoded
- token-ul JWT se salveaza in localStorage si este trimis prin header Authorization: Bearer
- endpoint-ul GET /sarcini suporta query param doar_nefinalizate=true
- API-ul este apelat prin URL relativ (const API_BASE = "")

## Observatii de design

- Dependency injection este centralizat in api/dependencies.py.
- Layerele superioare nu depind de detalii HTTP in business logic.
- Repositories izoleaza SQL-ul si permit migrare mai usoara spre ORM/Alembic.
- Configuratia sensibila este stricta: SECRET_KEY este obligatorie, fara fallback.

## Tratare erori si logging

- Middleware-ul adauga `X-Request-ID` pentru corelarea cereri-raspuns-logs.
- Exista exception handlers globale pentru:
	- erori de domeniu (autentificare, conflict, not found, politica parola),
	- erori de validare (`422`),
	- erori HTTP explicite,
	- erori SQLite (`503`),
	- erori neasteptate (`500`).
- Formatul raspunsului de eroare este consistent:

{
	"error": {
		"code": "...",
		"message": "...",
		"status": 400,
		"request_id": "...",
		"timestamp": "..."
	}
}

## Deployment (Lab 5)

- configuratia sensibila vine din .env (SECRET_KEY, ALGORITHM, EXPIRARE_TOKEN_MINUTE, DATABASE_PATH)
- Render foloseste render.yaml pentru build si start command
- endpoint de health check: /healthz
- Docker este disponibil prin Dockerfile si docker-compose.yml
