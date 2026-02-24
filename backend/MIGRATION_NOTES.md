# Notas de Migración: Go → Django

> **Fecha:** 2026-02-11
> **Autor:** Lead Backend Engineer
> **Propósito:** Documentar decisiones técnicas de la migración del backend de Go (Gin) a Python (Django + DRF).

---

## 1. Resumen de la migración

| Aspecto          | Antes (Go)                       | Después (Django)                          |
|------------------|----------------------------------|-------------------------------------------|
| Framework        | Gin                              | Django 4.2 LTS + Django REST Framework    |
| Base de datos    | MongoDB (mongo-driver)           | PostgreSQL (prod) / SQLite (local/CI)     |
| Testing          | go test + testify                | pytest + pytest-django + pytest-cov       |
| Coverage         | go test -coverprofile            | pytest-cov → coverage.xml                 |
| Docker runtime   | Binary compilado (Alpine)        | gunicorn + python:3.11-slim               |
| CI/CD            | GitHub Actions (go test)         | GitHub Actions (pytest)                   |

---

## 2. Decisión: PostgreSQL en lugar de MongoDB

### Contexto
El backend Go usaba MongoDB con las colecciones `users` y `todos`. El modelo de datos es simple (no anidado, sin relaciones complejas pero tampoco sin relaciones que justifiquen NoSQL).

### Decisión
Migrar a **PostgreSQL** para el entorno de producción (Render) y **SQLite** para desarrollo local y CI.

### Justificación
1. **Django + PostgreSQL** es la combinación más estable y soportada del ecosistema Django.
2. PostgreSQL está disponible gratuitamente en Render (tier free).
3. El modelo de datos es relacional (users con email unique, todos con FK implícito por email).
4. SQLite en CI acelera los tests (in-memory) sin necesidad de servicios externos.
5. La abstracción por repositories hace que el cambio de DB no afecte la lógica de negocio.

### Impacto en el contrato API
**Ninguno.** Los IDs de MongoDB (ObjectID hex 24 chars) se reemplazan por UUIDs (36 chars con guiones). El frontend ya trataba los IDs como strings opacos, por lo que este cambio es transparente.

---

## 3. Decisión: Arquitectura "Modular Monolith"

### Estructura adoptada

```
backend/
├── config/              # Configuración Django (settings por ambiente, urls, wsgi)
│   └── settings/
│       ├── base.py      # Settings compartidos
│       ├── local.py     # Desarrollo local (SQLite, DEBUG=True)
│       ├── ci.py        # CI/tests (SQLite in-memory)
│       └── prod.py      # Producción (PostgreSQL, seguridad)
├── apps/                # Apps de dominio
│   ├── health/          # Health check
│   │   ├── api/         # Views + URLs
│   │   └── tests/
│   ├── users/           # Gestión de usuarios
│   │   ├── domain/      # Excepciones de dominio
│   │   ├── services/    # Lógica de negocio
│   │   ├── repositories/# Abstracción de acceso a datos
│   │   ├── api/         # Views + URLs + Serializers
│   │   └── tests/       # Tests por capa
│   └── todos/           # Gestión de tareas
│       ├── domain/
│       ├── services/
│       ├── repositories/
│       ├── api/
│       └── tests/
```

### Principios

- **Views delgadas:** Solo parsean requests y formatean responses. La lógica vive en `services/`.
- **Repositories:** Encapsulan el ORM de Django. Si se cambiara la DB mañana, solo se tocan los repositories.
- **Domain exceptions:** Errores de negocio tipados que las views traducen a HTTP status codes.
- **Settings por ambiente:** Cada environment tiene su propio archivo; las variables sensibles vienen del entorno.

---

## 4. Decisión: Sin JWT (preservar contrato)

El backend Go original NO usaba JWT. El login simplemente valida credenciales y retorna `{"message": "login exitoso"}`. No hay tokens, headers de autenticación, ni middleware de auth.

Para preservar el contrato exacto, Django tampoco implementa JWT. Las vistas usan `AllowAny` y no requieren autenticación.

**Nota para el futuro:** Si se quiere agregar JWT, se puede usar `djangorestframework-simplejwt` sin romper la arquitectura actual.

---

## 5. Decisión: Passwords en texto plano

El backend Go almacenaba passwords sin hashear. Esto se preserva en Django para mantener compatibilidad exacta con el comportamiento original.

**Riesgo conocido:** Esto NO es seguro para producción real. Se recomienda migrar a `bcrypt` o el hasher de Django en un futuro PR.

---

## 6. Mapping Go → Django

| Go (handler)           | Django (view)                          | Ruta              |
|------------------------|----------------------------------------|-------------------|
| `healthz` (inline)     | `apps.health.api.views.healthz`        | `GET /healthz`    |
| `auth.Register`        | `apps.users.api.views.register`        | `POST /register`  |
| `auth.Login`           | `apps.users.api.views.login`           | `POST /login`     |
| `auth.ListUsers`       | `apps.users.api.views.users_view`      | `GET /users`      |
| `auth.ClearUsers`      | `apps.users.api.views.users_view`      | `DELETE /users`    |
| `todo.ListTodos`       | `apps.todos.api.views.todos_collection`| `GET /todos`      |
| `todo.CreateTodo`      | `apps.todos.api.views.todos_collection`| `POST /todos`     |
| `todo.ClearTodos`      | `apps.todos.api.views.todos_collection`| `DELETE /todos`    |
| `todo.UpdateTodo`      | `apps.todos.api.views.todos_detail`    | `PUT /todos/:id`  |
| `todo.DeleteTodo`      | `apps.todos.api.views.todos_detail`    | `DELETE /todos/:id`|

---

## 7. Ejecución local

```bash
cd backend

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env

# Ejecutar migraciones
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate

# Levantar servidor
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver 8080

# Ejecutar tests
DJANGO_SETTINGS_MODULE=config.settings.ci python -m pytest -v

# Tests con coverage
DJANGO_SETTINGS_MODULE=config.settings.ci python -m pytest --cov --cov-report=xml --cov-report=term-missing
```

---

## 8. Variables de entorno (producción)

| Variable                 | Requerido | Descripción                              |
|--------------------------|-----------|------------------------------------------|
| `SECRET_KEY`             | Sí        | Clave secreta Django                     |
| `DATABASE_URL`           | Sí        | URL PostgreSQL (provista por Render)     |
| `ALLOWED_HOSTS`          | Sí        | Hosts permitidos (comma-separated)       |
| `FRONT_ORIGINS`          | Sí        | URLs del frontend para CORS              |
| `PORT`                   | No        | Puerto (default: 8080)                   |
| `DJANGO_SETTINGS_MODULE` | Sí        | `config.settings.prod`                   |
| `DEBUG`                  | No        | `False` en producción (default)          |
| `LOG_LEVEL`              | No        | Nivel de log (default: INFO)             |

---

## 9. Legacy

El código Go original se preserva en `/backend_legacy_go/` como referencia. No se ejecuta ni se incluye en el pipeline.
