# Todo App — Full Stack con CI/CD

Aplicación full-stack de gestión de tareas con pipeline CI/CD completo.

## Stack

| Capa             | Tecnología                                       |
|------------------|--------------------------------------------------|
| **Backend**      | Django 4.2 LTS + Django REST Framework            |
| **Frontend**     | React 19 + react-scripts                          |
| **Base de datos**| PostgreSQL (prod) / SQLite (local/CI)             |
| **Tests**        | pytest + Jest + Cypress                            |
| **CI/CD**        | GitHub Actions + SonarCloud                        |
| **Deploy**       | Docker + Render (QA + Prod)                        |

## Arquitectura backend

Monolito modular (modular monolith) con separación por capas:

```
backend/
├── config/              # Settings por ambiente, URLs, WSGI
├── apps/
│   ├── health/          # GET /healthz
│   ├── users/           # POST /register, POST /login, GET|DELETE /users
│   └── todos/           # CRUD /todos, /todos/:id
│       ├── domain/      # Excepciones de dominio
│       ├── services/    # Lógica de negocio
│       ├── repositories/# Acceso a datos (ORM)
│       ├── api/         # Views, URLs, Serializers
│       └── tests/       # Tests por capa
```

## Ejecución local

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver 8080
```

### Frontend

```bash
cd frontend
npm ci
npm start
```

### Tests

```bash
# Backend
cd backend && source .venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.ci python -m pytest --cov --cov-report=term-missing -v

# Frontend
cd frontend && npm test -- --coverage --watchAll=false

# E2E
cd frontend && npm run e2e
```

## API

Documentación OpenAPI disponible en:
- Schema: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`

Contrato detallado: [`backend/API_CONTRACT.md`](backend/API_CONTRACT.md)

## CI/CD Pipeline

```
backend-tests → ─┐
                  ├── sonarcloud-analysis → ─┐
frontend-tests → ─┤                          ├── deploy_prod → summary
                  ├── build_images → deploy_qa → e2e-tests ──┘
                  └──────────────────────────────────────────┘
```

## Documentación

- [API Contract](backend/API_CONTRACT.md) — Endpoints, payloads, status codes
- [Migration Notes](backend/MIGRATION_NOTES.md) — Decisiones técnicas Go → Django
- [Decisiones](Decisiones.md) — Estrategia de calidad y stack original
