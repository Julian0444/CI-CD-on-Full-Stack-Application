# Django REST API — From Zero Guide

> **Basado en:** el código real de `/backend` en este repositorio.
> **Audiencia:** Desarrolladores que quieren aprender a construir APIs REST con Django + DRF siguiendo buenas prácticas.
> **Nivel:** Intermedio (se asume conocimiento básico de Python y HTTP).

---

## 0) Mapa del proyecto

Antes de construir nada, veamos qué existe y para qué sirve cada carpeta.

```
backend/
├── manage.py                    # CLI de Django (runserver, migrate, test, etc.)
├── requirements.txt             # Dependencias Python del proyecto
├── pyproject.toml               # Configuración de pytest y coverage
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore                   # Archivos excluidos de Git
├── dockerfile                   # Imagen Docker para producción
│
├── config/                      # === CONFIGURACIÓN GLOBAL ===
│   ├── __init__.py
│   ├── urls.py                  # Rutas raíz (incluye las URLs de cada app)
│   ├── wsgi.py                  # Entry point para gunicorn en producción
│   ├── asgi.py                  # Entry point async (no usado actualmente)
│   └── settings/                # Settings divididos por ambiente
│       ├── __init__.py
│       ├── base.py              # Config compartida (DRF, CORS, logging, apps)
│       ├── local.py             # Desarrollo local (SQLite, DEBUG=True)
│       ├── ci.py                # CI/Tests (SQLite in-memory, rápido)
│       └── prod.py              # Producción (PostgreSQL, seguridad)
│
└── apps/                        # === APPS DE DOMINIO ===
    ├── __init__.py
    │
    ├── health/                  # App: Health check (GET /healthz)
    │   ├── apps.py              # Registro de la app en Django
    │   ├── api/
    │   │   ├── views.py         # La view del endpoint
    │   │   └── urls.py          # Ruta /healthz
    │   └── tests/
    │       └── test_api.py      # Test del endpoint
    │
    ├── users/                   # App: Gestión de usuarios
    │   ├── apps.py
    │   ├── models.py            # Modelo User (tabla app_users)
    │   ├── admin.py             # Registro en Django Admin
    │   ├── domain/
    │   │   └── exceptions.py    # Excepciones de negocio (InvalidUserInput, etc.)
    │   ├── repositories/
    │   │   └── user_repository.py  # Acceso a datos (ORM encapsulado)
    │   ├── services/
    │   │   └── user_service.py  # Lógica de negocio (register, login, list, clear)
    │   ├── api/
    │   │   ├── serializers.py   # Definición de campos de entrada
    │   │   ├── views.py         # Views HTTP (thin: delegan al service)
    │   │   └── urls.py          # Rutas: /register, /login, /users
    │   ├── tests/
    │   │   ├── test_services.py # Tests de lógica de negocio
    │   │   └── test_api.py      # Tests de contrato HTTP
    │   └── migrations/          # Migraciones de base de datos
    │
    └── todos/                   # App: Gestión de tareas (misma estructura)
        ├── apps.py
        ├── models.py            # Modelo Todo (UUID, email, title, completed, created_at)
        ├── admin.py
        ├── domain/
        │   └── exceptions.py    # InvalidTodoInput, InvalidTodoID, TodoNotFound
        ├── repositories/
        │   └── todo_repository.py
        ├── services/
        │   └── todo_service.py
        ├── api/
        │   ├── serializers.py
        │   ├── views.py
        │   └── urls.py
        ├── tests/
        │   ├── test_services.py
        │   └── test_api.py
        └── migrations/
```

### ¿Por qué esta estructura?

| Carpeta               | Responsabilidad                                          |
|-----------------------|----------------------------------------------------------|
| `config/`             | Todo lo que NO es lógica de negocio: settings, URL raíz, WSGI |
| `apps/<dominio>/`     | Un bounded context por dominio de negocio                |
| `domain/`             | Errores y reglas puras (sin dependencias de Django)      |
| `services/`           | Lógica de negocio — la "inteligencia" de la aplicación   |
| `repositories/`       | Acceso a datos — encapsula el ORM                        |
| `api/`                | HTTP puro: views, serializers, urls                      |
| `tests/`              | Tests organizados por capa                               |

---

## 1) Construcción desde cero — pasos exactos

Esta es la sección principal. Vas a reconstruir mentalmente este backend paso a paso, entendiendo **por qué** se crea cada archivo y **qué** hace.

---

### 1.1 Crear entorno y dependencias

**Concepto:** Antes de escribir una línea de Django, necesitás un entorno Python aislado y las librerías instaladas.

**Comandos:**

```bash
# 1. Crear carpeta del proyecto
mkdir backend && cd backend

# 2. Crear entorno virtual
python3 -m venv .venv

# 3. Activarlo
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# 4. Instalar dependencias
pip install -r requirements.txt
```

**Archivo real:** `backend/requirements.txt`

```
# Django core
Django>=4.2,<4.3
djangorestframework>=3.14,<3.16
django-cors-headers>=4.3,<5.0

# API documentation
drf-spectacular>=0.27,<0.29

# Environment variables
django-environ>=0.11,<0.13

# Production server
gunicorn>=21.2,<24.0

# Database
psycopg2-binary>=2.9,<2.10

# Testing
pytest>=7.4,<9.0
pytest-django>=4.7,<5.0
pytest-cov>=4.1,<7.0
```

**¿Qué es cada librería?**

| Paquete               | Para qué sirve                                     |
|-----------------------|----------------------------------------------------|
| `Django`              | El framework web (ORM, routing, settings, etc.)    |
| `djangorestframework` | Extensión para construir APIs REST (serializers, views, responses) |
| `django-cors-headers` | Middleware que agrega headers CORS automáticamente  |
| `drf-spectacular`     | Genera documentación OpenAPI/Swagger desde tu código |
| `django-environ`      | Lee variables de entorno y archivos `.env`          |
| `gunicorn`            | Servidor WSGI de producción (reemplaza `runserver`) |
| `psycopg2-binary`     | Driver PostgreSQL para producción                   |
| `pytest`              | Framework de testing (mejor que `unittest`)         |
| `pytest-django`       | Plugin que conecta pytest con Django (DB, client)   |
| `pytest-cov`          | Plugin para generar reportes de code coverage       |

**Punto clave:** Usamos `>=X,<Y` en versiones para permitir parches de seguridad pero evitar breaking changes.

---

### 1.2 Crear proyecto Django (estructura base)

**Concepto:** En Django, un "project" es la configuración global. Las "apps" son módulos de funcionalidad. El proyecto se compone de:

- `manage.py` — CLI para todos los comandos Django
- `config/` — configuración (en vez del nombre `myproject/` por defecto)

**¿Cómo se creó?**

Normalmente harías `django-admin startproject config .` pero en este repo la estructura se creó manualmente para tener más control. Lo importante es que estos archivos existan:

**Archivo real:** `backend/manage.py`

```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
```

**¿Qué hace?** Es el punto de entrada de todos los comandos:
- `python manage.py runserver` — levantar servidor local
- `python manage.py migrate` — aplicar migraciones de DB
- `python manage.py makemigrations` — crear migraciones
- `python manage.py createsuperuser` — crear admin

**El `DJANGO_SETTINGS_MODULE`** le dice a Django qué archivo de settings usar. Por defecto apunta a `config.settings.local` (desarrollo).

**Archivo real:** `backend/config/urls.py`

```python
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # App routes — mounted at root to match Go paths
    path("", include("apps.health.api.urls")),
    path("", include("apps.users.api.urls")),
    path("", include("apps.todos.api.urls")),
]
```

**¿Qué hace?** Es el "router principal". Cada `include(...)` delega a las URLs de cada app. Las rutas se montan en `""` (raíz) para que los paths sean `/healthz`, `/register`, `/todos`, etc. — sin prefijo `/api/`.

**Archivo real:** `backend/config/wsgi.py`

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
application = get_wsgi_application()
```

**¿Qué hace?** Es el punto de entrada para servidores de producción como gunicorn. Cuando hacés `gunicorn config.wsgi:application`, Python ejecuta este archivo.

---

### 1.3 Settings por ambiente (local / ci / prod)

**Concepto:** Nunca uses un solo archivo de settings. En este repo hay 4 archivos que forman una cadena de herencia:

```
base.py   ← config compartida (apps, middleware, DRF, CORS, logging)
  │
  ├── local.py   ← hereda de base, agrega: DEBUG=True, SQLite en archivo
  ├── ci.py      ← hereda de base, agrega: SQLite in-memory, SECRET_KEY fija
  └── prod.py    ← hereda de base, agrega: PostgreSQL, headers de seguridad
```

**Archivo real:** `backend/config/settings/base.py` (fragmentos clave)

```python
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "change-me-in-production"),
    ALLOWED_HOSTS=(list, ["*"]),
    FRONT_ORIGINS=(str, ""),
    DATABASE_URL=(str, "sqlite:///db.sqlite3"),
)

# Read .env file if it exists
env_file = BASE_DIR / ".env"
if env_file.is_file():
    env.read_env(str(env_file))
```

**¿Qué hace `django-environ`?** Lee variables de entorno o de un archivo `.env` y las convierte al tipo correcto. Ejemplo: `DEBUG=(bool, False)` significa "leé `DEBUG` del entorno; si no existe, usá `False`; conviértelo a boolean".

**Configuración de DRF en base.py:**

```python
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "UNAUTHENTICATED_USER": None,
}
```

**¿Qué dice esto?** "Solo acepto y devuelvo JSON. No hay autenticación. Cualquiera puede acceder." Esto coincide con el backend Go original.

**Configuración de CORS en base.py:**

```python
_default_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
_extra = env("FRONT_ORIGINS")
_extra_origins = [o.strip() for o in _extra.split(",") if o.strip()] if _extra else []

CORS_ALLOWED_ORIGINS = list(dict.fromkeys(_default_origins + _extra_origins))
CORS_ALLOW_CREDENTIALS = True
```

**¿Qué dice esto?** "Permite requests desde estos orígenes del frontend. En producción, agrega más vía la variable `FRONT_ORIGINS`."

**Archivo real:** `backend/config/settings/ci.py`

```python
from .base import *  # noqa

DEBUG = False
SECRET_KEY = "ci-test-secret-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",   # ← DB en RAM, super rápido para tests
    }
}
```

**¿Por qué SQLite in-memory para CI?** Porque cada test crea y destruye la DB en milisegundos. No necesitás PostgreSQL ni persistencia para correr tests unitarios.

**Archivo real:** `backend/config/settings/prod.py`

```python
from .base import *  # noqa

DEBUG = False
SECRET_KEY = env("SECRET_KEY")       # OBLIGATORIO desde env var
ALLOWED_HOSTS = env("ALLOWED_HOSTS") # OBLIGATORIO desde env var

DATABASES = {
    "default": env.db("DATABASE_URL"),  # PostgreSQL en Render
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
```

**Archivo real:** `backend/.env.example`

```
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
FRONT_ORIGINS=http://localhost:3000,http://localhost:5173
PORT=8080
DJANGO_SETTINGS_MODULE=config.settings.local
LOG_LEVEL=INFO
```

**Regla de oro:** Nunca comitees un `.env` real. Solo commiteá `.env.example` con valores placeholder.

---

### 1.4 Crear apps (dominio) como modular monolith

**Concepto:** En vez de meter todo en una sola app gigante, separamos por dominio de negocio:

| App       | Responsabilidad              | Endpoints                         |
|-----------|------------------------------|-----------------------------------|
| `health`  | Health check del servidor    | `GET /healthz`                    |
| `users`   | Registro, login, gestión     | `POST /register`, `POST /login`, `GET\|DELETE /users` |
| `todos`   | CRUD de tareas               | `GET\|POST\|DELETE /todos`, `PUT\|DELETE /todos/:id` |

**¿Cómo se crea una app?**

```bash
# Crear la carpeta con estructura completa
mkdir -p apps/health/{api,tests}
mkdir -p apps/users/{domain,services,repositories,api,tests}
mkdir -p apps/todos/{domain,services,repositories,api,tests}

# Crear todos los __init__.py necesarios
touch apps/__init__.py
touch apps/health/__init__.py apps/health/api/__init__.py apps/health/tests/__init__.py
# ... etc para cada subcarpeta
```

**Registrar la app en Django:** Cada app necesita un `apps.py`:

```python
# backend/apps/health/apps.py
from django.apps import AppConfig

class HealthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.health"        # ← path completo con el prefijo "apps."
    verbose_name = "Health"
```

Y debe estar en `INSTALLED_APPS` de `base.py`:

```python
INSTALLED_APPS = [
    # ...django apps...
    # Third-party
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    # Project apps
    "apps.health",
    "apps.users",
    "apps.todos",
]
```

**Capas dentro de cada app:**

```
users/
├── domain/         # Excepciones de negocio: InvalidUserInput, UserAlreadyExists...
│                   # Esta capa NO importa Django. Es Python puro.
│
├── services/       # Lógica de negocio: register(), login(), list_users()
│                   # Importa domain/ y repositories/. NO conoce HTTP.
│
├── repositories/   # Acceso a datos: find_by_email(), insert(), clear()
│                   # Encapsula el ORM de Django. Si cambias la DB, solo tocas acá.
│
├── api/            # HTTP puro: views parsean requests, llaman al service,
│                   # formatean responses con status codes correctos.
│
└── tests/          # Tests separados: test_services.py (lógica) + test_api.py (HTTP)
```

**¿Por qué esta separación?** Porque si tu view hace `User.objects.filter(...)` y `if email == "": return 400`, estás mezclando HTTP con lógica con acceso a datos. Eso se llama "fat view" y es difícil de testear y mantener.

---

### 1.5 Implementar un endpoint simple (Health) desde 0

**El endpoint más simple posible.** Perfecto para entender el flujo URL → View → Response.

**Paso 1 — Crear la view:**

```python
# backend/apps/health/api/views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def healthz(request):
    """Health-check endpoint. Returns {"status": "ok"}."""
    return Response({"status": "ok"}, status=status.HTTP_200_OK)
```

**¿Qué es `@api_view`?** Es un decorador de DRF que convierte una función normal en una API view. Le dice "esta función solo acepta GET". Si alguien manda POST, DRF responde `405 Method Not Allowed` automáticamente.

**¿Qué es `Response`?** El equivalente DRF de `JsonResponse` de Django. Serializa diccionarios a JSON y setea `Content-Type: application/json`.

**Paso 2 — Crear la URL de la app:**

```python
# backend/apps/health/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("healthz", views.healthz, name="healthz"),
]
```

**¿Qué hace `path()`?** Mapea un string de URL a una función view. `"healthz"` (sin barra inicial) se concatena con lo que diga `config/urls.py`.

**Paso 3 — Incluir en las URLs globales:**

```python
# backend/config/urls.py (ya visto antes)
path("", include("apps.health.api.urls")),
```

`path("")` + `path("healthz")` = la URL final es `/healthz`.

**Paso 4 — Testear:**

```python
# backend/apps/health/tests/test_api.py
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestHealthEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_healthz_returns_ok(self):
        response = self.client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
```

**¿Qué es `APIClient`?** Es un cliente HTTP de testing de DRF. Simula requests sin levantar un servidor real. `self.client.get("/healthz")` hace un GET interno y devuelve el response.

**¿Qué es `@pytest.mark.django_db`?** Le dice a pytest: "este test necesita acceso a la base de datos". Sin este marker, Django bloquea cualquier operación de DB.

**Flujo completo:**

```
GET /healthz
  └── config/urls.py: path("", include("apps.health.api.urls"))
      └── apps/health/api/urls.py: path("healthz", views.healthz)
          └── apps/health/api/views.py: return Response({"status": "ok"})
```

---

### 1.6 Implementar auth básico (register / login) desde 0

Ahora vamos a algo real. El flujo completo de register tiene **4 capas** que colaboran.

#### Capa 1: Domain — Excepciones de negocio

```python
# backend/apps/users/domain/exceptions.py
class InvalidUserInput(Exception):
    """Email o password vacíos después de normalización."""
    pass

class UserAlreadyExists(Exception):
    """Se intenta registrar un email que ya existe."""
    pass

class InvalidCredentials(Exception):
    """Email/password no coinciden o no existen."""
    pass
```

**¿Por qué excepciones custom?** Porque la lógica de negocio no sabe nada de HTTP. No puede devolver `400` ni `409`. En cambio, lanza una excepción tipada, y la view la traduce al status code correcto.

#### Capa 2: Model — Definir la tabla

```python
# backend/apps/users/models.py
from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = "app_users"
        ordering = ["email"]

    def __str__(self):
        return self.email
```

**Después de crear el modelo, generás la migración:**

```bash
python manage.py makemigrations
# → Crea apps/users/migrations/0001_initial.py

python manage.py migrate
# → Ejecuta el SQL: CREATE TABLE app_users (...)
```

#### Capa 3: Repository — Acceso a datos

```python
# backend/apps/users/repositories/user_repository.py
from apps.users.models import User

class UserRepository:
    def find_by_email(self, email: str) -> Optional[User]:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def insert(self, email: str, password: str) -> User:
        return User.objects.create(email=email, password=password)

    def list_all(self) -> List[User]:
        return list(User.objects.all().order_by("email"))

    def clear(self) -> None:
        User.objects.all().delete()
```

**¿Por qué un repository si Django ya tiene ORM?** Porque encapsula el acceso a datos. Si mañana cambias de PostgreSQL a otro sistema, solo tocás este archivo. El service no cambia.

#### Capa 4: Service — Lógica de negocio

```python
# backend/apps/users/services/user_service.py
class UserService:
    def __init__(self, repo: Optional[UserRepository] = None):
        self.repo = repo or UserRepository()

    def register(self, email: str, password: str) -> None:
        email = _normalize_email(email)    # strip + lower
        password = _normalize_text(password) # strip

        if not email or not password:
            raise InvalidUserInput()

        existing = self.repo.find_by_email(email)
        if existing is not None:
            raise UserAlreadyExists()

        self.repo.insert(email=email, password=password)
```

**Flujo de register:**
1. Normalizar email (lower + trim) y password (trim)
2. Si alguno queda vacío → `InvalidUserInput`
3. Buscar si ya existe → `UserAlreadyExists`
4. Insertar en DB

**Flujo de login:**

```python
    def login(self, email: str, password: str) -> None:
        email = _normalize_email(email)
        password = _normalize_text(password)

        if not email or not password:
            raise InvalidCredentials()

        user = self.repo.find_by_email(email)
        if user is None or user.password != password:
            raise InvalidCredentials()
```

Notar: no devuelve nada. Si no lanza excepción, el login fue exitoso.

#### Capa 5: View — HTTP thin layer

```python
# backend/apps/users/api/views.py
@api_view(["POST"])
def register(request):
    service = _get_service()
    email = request.data.get("email", "")
    password = request.data.get("password", "")

    try:
        service.register(email, password)
        return Response(
            {"message": "usuario registrado con exito"},
            status=status.HTTP_201_CREATED,
        )
    except InvalidUserInput:
        return Response(
            {"error": "email y clave son requeridos"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except UserAlreadyExists:
        return Response(
            {"error": "usuario ya existe"},
            status=status.HTTP_409_CONFLICT,
        )
    except Exception:
        return Response(
            {"error": "error al registrar usuario"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
```

**Patrón clave:** La view es un "traductor" entre HTTP y excepciones de dominio:

| Excepción de dominio  | HTTP Status | Mensaje JSON                         |
|-----------------------|-------------|--------------------------------------|
| (ninguna)             | 201         | `{"message": "usuario registrado..."}` |
| `InvalidUserInput`    | 400         | `{"error": "email y clave son requeridos"}` |
| `UserAlreadyExists`   | 409         | `{"error": "usuario ya existe"}`     |
| `Exception` genérica  | 500         | `{"error": "error al registrar..."}` |

**Truco para GET + DELETE en la misma ruta (`/users`):**

```python
@api_view(["GET", "DELETE"])
def users_view(request):
    if request.method == "GET":
        # listar usuarios
    # DELETE:
        # borrar todos los usuarios
```

DRF permite declarar múltiples métodos en `@api_view`. Dentro de la función, chequeás `request.method`.

#### URLs de la app:

```python
# backend/apps/users/api/urls.py
urlpatterns = [
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("users", views.users_view, name="users"),
]
```

---

### 1.7 Implementar CRUD de todos desde 0

El todo es más complejo: tiene CRUD completo, IDs dinámicos en URLs, y filtrado por query params.

#### Modelo:

```python
# backend/apps/todos/models.py
import uuid
from django.db import models

class Todo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    title = models.CharField(max_length=500)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "app_todos"
        ordering = ["created_at"]
```

**¿Por qué UUID?** El backend Go original usaba MongoDB ObjectIDs (strings hexadecimales de 24 chars). Con UUID, los IDs siguen siendo strings únicos que el frontend trata como opacos. `auto_now_add=True` setea `created_at` automáticamente al crear.

#### Conversión a response dict:

```python
# backend/apps/todos/services/todo_service.py
def _todo_to_response(todo) -> Dict:
    return {
        "id": str(todo.id),
        "email": todo.email,
        "title": todo.title,
        "completed": todo.completed,
        "createdAt": (
            todo.created_at.isoformat().replace("+00:00", "Z")
            if todo.created_at else None
        ),
    }
```

**Detalle sutil:** El campo de la DB se llama `created_at` (snake_case, convención Django), pero en el JSON de respuesta se llama `createdAt` (camelCase, para preservar el contrato con el frontend). La conversión se hace aquí en el service, no en la view.

#### Repository del todo:

```python
# backend/apps/todos/repositories/todo_repository.py
class TodoRepository:
    def list(self, email: str = "") -> List[Todo]:
        qs = Todo.objects.all()
        if email:
            qs = qs.filter(email=email)
        return list(qs.order_by("created_at"))

    def create(self, email: str, title: str, completed: bool = False) -> Todo:
        return Todo.objects.create(email=email, title=title, completed=completed)

    def get_by_id(self, todo_id: uuid.UUID) -> Optional[Todo]:
        try:
            return Todo.objects.get(pk=todo_id)
        except Todo.DoesNotExist:
            return None
```

**QuerySet encadenado:** `Todo.objects.all().filter(email=email).order_by("created_at")` — Django construye el SQL con `WHERE email = ? ORDER BY created_at ASC`.

#### Validación de UUID en el service:

```python
def _parse_uuid(value: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError):
        raise InvalidTodoID()
```

Si el frontend envía `"invalid-id"`, esto lanza `InvalidTodoID()`, que la view traduce a `{"error": "id invalido"}` con status `400`.

#### Views: collection + detail

En las URLs del Go original, `/todos` maneja GET, POST y DELETE (collection), mientras que `/todos/:id` maneja PUT y DELETE (detail). En Django:

```python
# backend/apps/todos/api/urls.py
urlpatterns = [
    path("todos", views.todos_collection, name="todos-collection"),
    path("todos/<str:todo_id>", views.todos_detail, name="todos-detail"),
]
```

`<str:todo_id>` captura lo que venga después de `/todos/` y lo pasa como argumento `todo_id` a la view.

```python
# backend/apps/todos/api/views.py
@api_view(["GET", "POST", "DELETE"])
def todos_collection(request):
    if request.method == "GET":
        return _list_todos(request, service)
    elif request.method == "POST":
        return _create_todo(request, service)
    else:  # DELETE
        return _clear_todos(request, service)

@api_view(["PUT", "DELETE"])
def todos_detail(request, todo_id):
    if request.method == "PUT":
        return _update_todo(request, service, todo_id)
    else:  # DELETE
        return _delete_todo(request, service, todo_id)
```

**¿Cómo se lee el query param `email` en GET y DELETE?**

```python
email = request.query_params.get("email", "")
```

`request.query_params` es un diccionario con los parámetros de la URL (e.g., `/todos?email=alice`).

**¿Cómo se lee el body JSON en POST/PUT?**

```python
email = request.data.get("email", "")
title = request.data.get("title", "")
```

`request.data` es el body parseado por DRF (ya es un dict de Python).

---

### 1.8 Tests desde cero (pytest + pytest-django)

#### Configuración de pytest

**Archivo real:** `backend/pyproject.toml`

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.ci"
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
testpaths = ["apps"]
markers = [
    "unit: Pure logic tests without DB",
    "integration: Tests that require database",
]
addopts = ["--strict-markers", "-v"]
```

**¿Qué dice esto?**
- Usá los settings de CI (SQLite in-memory)
- Buscá tests en `apps/`
- Los archivos de test empiezan con `test_`
- Las clases de test empiezan con `Test`
- Las funciones de test empiezan con `test_`

#### Tipos de tests en este repo

**1. Service tests** — Testean lógica de negocio pura:

```python
# backend/apps/users/tests/test_services.py
@pytest.mark.django_db
class TestUserServiceRegister:
    def setup_method(self):
        self.service = UserService()

    def test_register_stores_normalized_user(self):
        self.service.register(" User@Example.com ", " secret ")
        users = self.service.list_users()
        assert len(users) == 1
        assert users[0]["email"] == "user@example.com"

    def test_register_rejects_duplicates(self):
        self.service.register("user@example.com", "secret")
        with pytest.raises(UserAlreadyExists):
            self.service.register("user@example.com", "secret")
```

**¿Qué testea?** Que el service normaliza emails, rechaza duplicados, y lanza la excepción correcta. No le importan status codes ni JSON — eso es responsabilidad de la view.

**2. API tests** — Testean el contrato HTTP completo:

```python
# backend/apps/users/tests/test_api.py
@pytest.mark.django_db
class TestRegisterEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_register_success(self):
        response = self.client.post(
            "/register",
            {"email": "User@example.com", "password": "secret"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json() == {"message": "usuario registrado con exito"}

    def test_register_rejects_duplicate(self):
        self.client.post("/register", {"email": "dup@ex.com", "password": "s"}, format="json")
        response = self.client.post("/register", {"email": "dup@ex.com", "password": "s"}, format="json")
        assert response.status_code == 409
        assert response.json() == {"error": "usuario ya existe"}
```

**¿Qué testea?** El contrato exacto: URL + método + body + status code + response body. Si cambiás un mensaje de error, este test falla. Eso es intencional: protege el contrato API.

**¿Por qué dos tipos de tests?** Porque si solo tenés API tests, no sabés si el bug está en la view, el service, o el repository. Con service tests aislados, podés pinpointear dónde está el problema.

#### Cómo correr los tests:

```bash
# Todos los tests
DJANGO_SETTINGS_MODULE=config.settings.ci python -m pytest -v

# Solo una app
DJANGO_SETTINGS_MODULE=config.settings.ci python -m pytest apps/users/ -v

# Solo un archivo
DJANGO_SETTINGS_MODULE=config.settings.ci python -m pytest apps/users/tests/test_api.py -v

# Solo un test
DJANGO_SETTINGS_MODULE=config.settings.ci python -m pytest -k "test_register_success" -v
```

---

### 1.9 Coverage y SonarCloud

#### Generar coverage:

```bash
DJANGO_SETTINGS_MODULE=config.settings.ci python -m pytest \
  --cov \
  --cov-report=xml \
  --cov-report=term-missing \
  -v
```

Esto produce:
- **Terminal:** reporte con porcentaje por archivo y líneas sin cubrir
- **`coverage.xml`** — archivo XML que SonarCloud consume

#### Configuración de coverage en pyproject.toml:

```toml
[tool.coverage.run]
source = ["apps", "config"]
omit = [
    "*/tests/*",       # No medir cobertura de los tests mismos
    "*/migrations/*",  # Código autogenerado
    "*/admin.py",      # Registro en Django Admin
    "manage.py",
    "config/settings/*",
    "config/asgi.py",
    "config/wsgi.py",
]

[tool.coverage.report]
show_missing = true
fail_under = 70        # El build falla si la cobertura baja del 70%

[tool.coverage.xml]
output = "coverage.xml"
```

#### ¿Cómo lo consume SonarCloud?

En `sonar-project.properties` (raíz del repo):

```properties
sonar.python.coverage.reportPaths=backend/coverage.xml
```

SonarCloud lee ese XML y muestra la cobertura en su dashboard.

#### Gitignore: no commitear artefactos

```gitignore
# backend/.gitignore
coverage.xml
.coverage
.coverage.*
htmlcov/
```

Estos archivos se generan en CI y se suben como artifacts de GitHub Actions — nunca al repositorio.

---

### 1.10 Dockerización (Render-ready)

**Archivo real:** `backend/dockerfile`

```dockerfile
# --- build stage: install dependencies ---
FROM python:3.11-slim AS build
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- runtime stage ---
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*
RUN adduser --disabled-password --no-create-home app
WORKDIR /app
COPY --from=build /install /usr/local
COPY . .
RUN DJANGO_SETTINGS_MODULE=config.settings.prod \
    SECRET_KEY=build-placeholder \
    DATABASE_URL=sqlite:///tmp.db \
    python manage.py collectstatic --noinput 2>/dev/null || true
USER app
ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=config.settings.prod
EXPOSE 8080
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 3 --timeout 120"]
```

**Anatomía del Dockerfile:**

| Etapa | Qué hace | Por qué |
|-------|----------|---------|
| **Build stage** | Instala `gcc` + `libpq-dev` + deps Python | Se necesitan para compilar `psycopg2`. No queremos gcc en prod. |
| **Runtime stage** | Copia solo las librerías compiladas | Imagen final más liviana y segura |
| `adduser app` | Crea usuario no-root | Buena práctica de seguridad |
| `collectstatic` | Recolecta archivos estáticos | Django Admin necesita CSS/JS |
| `migrate --noinput` | Aplica migraciones al iniciar | La DB de prod se actualiza automáticamente |
| `gunicorn` | Servidor WSGI de producción | `runserver` de Django NO es apto para producción |
| `--workers 3` | 3 procesos paralelos | Maneja múltiples requests concurrentes |

**Para correr local con Docker:**

```bash
cd backend
docker build -t backend-local .
docker run -p 8080:8080 \
  -e SECRET_KEY=dev-secret \
  -e DATABASE_URL=sqlite:///app/db.sqlite3 \
  -e ALLOWED_HOSTS=* \
  -e DEBUG=True \
  backend-local
```

---

### 1.11 Cómo encaja con Cypress y el frontend

#### El contrato API es sagrado

El frontend (`frontend/src/services/api.js`) hace requests como:

```javascript
const response = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
});
```

Si cambias la ruta de `/register` a `/api/register`, el frontend se rompe.
Si cambias el status code de `201` a `200`, los tests E2E se rompen.
Si cambias `"message"` por `"msg"` en el JSON, el frontend no sabe interpretarlo.

#### Cosas que rompen E2E (y cómo se evitaron en este repo)

| Causa de rotura | Cómo se evitó |
|-----------------|---------------|
| Rutas diferentes (`/api/register` vs `/register`) | URLs montadas en raíz `path("")` en `config/urls.py` |
| Status codes diferentes (200 vs 201 en register) | Tests API verifican status codes exactos |
| Campos JSON cambiados (`message` vs `msg`) | Mensajes idénticos al Go: `"usuario registrado con exito"` |
| IDs en formato diferente | UUID como string, frontend lo trata como opaco |
| `createdAt` vs `created_at` | Conversión explícita en `_todo_to_response()` |
| CORS bloqueado | `django-cors-headers` configurado con los mismos origins |

#### Cypress usa intercepts (no pega al backend real)

```javascript
// frontend/cypress/e2e/todos.cy.js
cy.intercept('POST', '**/todos', (req) => {
    expect(req.body.title).to.contain('Comprar pan');
    req.reply({
        statusCode: 201,
        body: { todo: { id: '1', title: req.body.title, completed: false } },
    });
}).as('createTodo');
```

Cypress mockea las respuestas del backend. Pero el contrato que mockea (status codes, formato JSON) DEBE coincidir con lo que el backend real devuelve. Si tu backend cambia `201` por `200`, Cypress sigue pasando con su mock... pero la app real se rompe.

---

## 2) Cómo funciona hoy el backend (visión rápida)

### Request flow general

```
HTTP Request
  → Django URL resolver (config/urls.py)
    → App URL resolver (apps/*/api/urls.py)
      → View function (apps/*/api/views.py)
        → Parse request.data / request.query_params
        → Call service method
          → Service validates + normalizes
            → Repository executes ORM query
              → Database
            ← Repository returns model instance
          ← Service converts to response dict
        ← View wraps in Response with status code
      ← DRF serializes to JSON
    ← Django middleware (CORS headers, etc.)
  ← HTTP Response
```

### Ejemplo 1: POST /register

```
POST /register {"email": " User@Ex.com ", "password": " secret "}
  └── config/urls.py → include("apps.users.api.urls")
      └── apps/users/api/urls.py → path("register", views.register)
          └── apps/users/api/views.py → register(request)
              ├── request.data.get("email") → " User@Ex.com "
              ├── service.register(" User@Ex.com ", " secret ")
              │   ├── _normalize_email → "user@ex.com"
              │   ├── _normalize_text → "secret"
              │   ├── repo.find_by_email("user@ex.com") → None
              │   └── repo.insert("user@ex.com", "secret") → User created
              └── return Response({"message": "usuario registrado con exito"}, 201)
```

### Ejemplo 2: PUT /todos/{id}

```
PUT /todos/abc-123 {"title": "Actualizada", "completed": true}
  └── config/urls.py → include("apps.todos.api.urls")
      └── apps/todos/api/urls.py → path("todos/<str:todo_id>", views.todos_detail)
          └── apps/todos/api/views.py → todos_detail(request, todo_id="abc-123")
              ├── request.method == "PUT" → _update_todo(...)
              ├── service.update("abc-123", title="Actualizada", completed=True)
              │   ├── _parse_uuid("abc-123") → uuid.UUID(...)
              │   ├── _normalize_text("Actualizada") → "Actualizada"
              │   ├── repo.get_by_id(uuid) → Todo instance
              │   ├── repo.update(todo, title="Actualizada", completed=True) → Updated Todo
              │   └── _todo_to_response(todo) → {"id": "abc-123", "title": "Actualizada", ...}
              └── return Response({"todo": {...}}, 200)
```

---

## 3) Checklist: Crear tu propia API Django desde cero

Lista reutilizable para tu próximo proyecto:

```
□  1. Crear venv + requirements.txt con Django, DRF, cors-headers, environ, pytest
□  2. Crear manage.py con DJANGO_SETTINGS_MODULE apuntando a local
□  3. Crear config/ con settings/base.py, local.py, ci.py, prod.py
□  4. Configurar en base.py: INSTALLED_APPS, MIDDLEWARE (CORS primero), REST_FRAMEWORK, CORS
□  5. Crear config/urls.py con includes a tus apps + docs opcionales
□  6. Crear config/wsgi.py + config/asgi.py
□  7. Crear .env.example con todas las variables necesarias
□  8. Crear apps/__init__.py
□  9. Para cada app de dominio:
      □ a. Crear carpetas: domain/, services/, repositories/, api/, tests/
      □ b. Crear apps.py y registrar en INSTALLED_APPS
      □ c. Crear models.py con los modelos de datos
      □ d. Crear domain/exceptions.py con errores de negocio
      □ e. Crear repositories/ con acceso a datos encapsulado
      □ f. Crear services/ con lógica de negocio (validación, normalización)
      □ g. Crear api/views.py con views thin que delegan al service
      □ h. Crear api/urls.py con las rutas de la app
      □ i. Incluir las urls en config/urls.py
      □ j. Crear tests/test_services.py (lógica) y tests/test_api.py (HTTP)
□ 10. Crear migraciones: python manage.py makemigrations
□ 11. Aplicar migraciones: python manage.py migrate
□ 12. Correr tests: python -m pytest -v
□ 13. Correr con coverage: python -m pytest --cov --cov-report=xml
□ 14. Crear pyproject.toml con config de pytest y coverage
□ 15. Crear .gitignore (excluir .venv, .env, *.sqlite3, coverage.xml, __pycache__)
□ 16. Crear Dockerfile multi-stage con gunicorn
□ 17. Probar con Docker: docker build + docker run
□ 18. Verificar todos los endpoints con curl o Postman
```

---

## 4) Glosario Django rápido

| Término       | Qué es                                                                                          |
|---------------|-------------------------------------------------------------------------------------------------|
| **Project**   | La configuración global de Django (`config/` en este repo). Contiene settings, URLs raíz, WSGI. |
| **App**       | Un módulo de funcionalidad (`apps/users/`, `apps/todos/`). Tiene models, views, tests propios.  |
| **Model**     | Una clase Python que mapea a una tabla de base de datos. Django genera el SQL por vos.           |
| **Migration** | Un archivo que describe cambios en la DB (crear tabla, agregar columna). Se genera con `makemigrations`. |
| **ORM**       | Object-Relational Mapping. Escribís `User.objects.get(email=x)` en vez de SQL.                  |
| **View**      | Una función (o clase) que recibe un HTTP request y devuelve un HTTP response.                   |
| **URLconf**   | Archivos `urls.py` que mapean URLs a views. Django los resuelve en cadena (root → app).         |
| **Serializer**| Clase DRF que valida datos de entrada y/o formatea datos de salida. Similar a un "form" de Django. |
| **Middleware** | Código que se ejecuta en CADA request/response (ej: CORS, seguridad, logging).                  |
| **Settings**  | Archivo de configuración (DB, apps instaladas, middleware, etc.). Cada ambiente tiene el suyo.   |
| **`@api_view`**| Decorador DRF que convierte una función en una API view (parseo JSON, content negotiation).     |
| **`Response`**| Clase DRF que serializa dicts/listas a JSON y setea status codes y headers.                     |
| **`APIClient`**| Cliente de testing DRF para simular HTTP requests sin levantar un servidor.                     |
| **`pytest.mark.django_db`** | Marker que autoriza al test a acceder a la base de datos.                           |
| **gunicorn**  | Servidor WSGI de producción. Maneja múltiples workers/requests concurrentes.                    |
| **WSGI**      | Web Server Gateway Interface. Protocolo estándar entre Python y servidores web.                  |
| **`django-environ`** | Librería que lee variables de entorno y `.env` con type casting automático.                |

---

> **Resultado final de este repo:** 54 tests pasando, 86% de cobertura, contrato API preservado, Docker-ready para Render.
