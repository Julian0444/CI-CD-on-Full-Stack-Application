# OWNERSHIP AUDIT — TP8INGSOFT3

> **Fecha de auditoría:** 2026-02-09
> **Repositorio:** `tp8ingsoft3`
> **Objetivo:** Detectar TODA referencia a cuentas, organizaciones o credenciales de terceros y definir qué cambiar para que el proyecto quede 100 % bajo control propio.

---

## 1. Resumen ejecutivo

El repositorio contiene **5 integraciones externas** vinculadas a la cuenta de **`ignaciomagoia`** (GitHub/SonarCloud/GHCR) y a servicios de **Render** desplegados bajo esa cuenta. Además, el módulo Go y el archivo `coverage.out` referencian repositorios de dicha cuenta (incluyendo un repo anterior `tp6ingdesoft`).

**No se detectaron credenciales, tokens ni passwords commiteados en texto plano** (los secrets se leen correctamente desde `${{ secrets.* }}`). Sin embargo, hay **URLs de Render hardcodeadas** y un **username GHCR hardcodeado** en el pipeline.

---

## 2. Tabla de integraciones externas detectadas

| # | Integración | Dónde aparece | Qué está hardcodeado | Qué debe cambiar | Qué NO debe commitearse |
|---|-------------|---------------|----------------------|-------------------|-------------------------|
| 1 | **SonarCloud** | `sonar-project.properties` líneas 2-4 | `sonar.projectKey=ignaciomagoia_tp8ingsoft3`, `sonar.organization=ignaciomagoia` | Reemplazar por `TU_ORG_tp8ingsoft3` y `TU_ORG` (tu usuario/org de SonarCloud) | `SONAR_TOKEN` (secret de GitHub) |
| 2 | **GHCR (GitHub Container Registry)** | `.github/workflows/full-ci.yml` líneas 11-12 y 113 | `ghcr.io/ignaciomagoia/tp8-backend`, `ghcr.io/ignaciomagoia/tp8-frontend`, `username: ignaciomagoia` | Reemplazar `ignaciomagoia` por tu usuario de GitHub en las 3 ocurrencias | `GHCR_PAT` (Personal Access Token, secret de GitHub) |
| 3 | **Render (QA)** | `.github/workflows/full-ci.yml` líneas 160, 163, 170, 195 | URLs `https://frontend-qa-qymo.onrender.com` (hardcodeadas en echo y en `CYPRESS_BASE_URL`) | Reemplazar por la URL de tu servicio frontend QA en Render | `RENDER_BACKEND_QA_HOOK`, `RENDER_FRONTEND_QA_HOOK` (secrets) |
| 4 | **Render (PROD)** | `.github/workflows/full-ci.yml` líneas 221, 224, 231 | URL `https://frontend-prod-z6yw.onrender.com` (hardcodeada en echo) | Reemplazar por la URL de tu servicio frontend PROD en Render | `RENDER_BACKEND_PROD_HOOK`, `RENDER_FRONTEND_PROD_HOOK` (secrets) |
| 5 | **Go Module Path** | `backend/go.mod` línea 1, `backend/main.go` líneas 12-13, `backend/internal/handlers/auth_handler.go` línea 9, `backend/internal/handlers/todo_handler.go` línea 9, `backend/internal/handlers/test_helpers_test.go` línea 12 | `github.com/ignaciomagoia/tp8ingsoft3/backend` | Reemplazar `ignaciomagoia` por tu usuario de GitHub (`github.com/TU_USUARIO/tp8ingsoft3/backend`) | N/A |
| 6 | **Azure (posible/legacy)** | `frontend/dockerfile` línea 12 | Comentario: `https://tp8-back-prod.azurewebsites.net` | Eliminar o actualizar el comentario — parece un vestigio de otra config | N/A |
| 7 | **Coverage legacy (tp6)** | `backend/coverage.out` (todo el archivo), `backend/coverage.html` | Rutas `github.com/ignaciomagoia/tp6ingdesoft/backend/...` | Este archivo es generado; se regenera con `go test`. Eliminar o regenerar. No requiere edición manual. | N/A |

---

## 3. Detalle de hallazgos por archivo

### 3.1 `.github/workflows/full-ci.yml`

**Líneas 11-12 — Imágenes Docker GHCR (hardcoded)**:
```yaml
env:
  BACKEND_IMAGE: ghcr.io/ignaciomagoia/tp8-backend
  FRONTEND_IMAGE: ghcr.io/ignaciomagoia/tp8-frontend
```
→ Cambiar `ignaciomagoia` por tu usuario de GitHub.

**Línea 113 — Username GHCR (hardcoded)**:
```yaml
          username: ignaciomagoia
```
→ Cambiar por tu usuario de GitHub. **Mejor práctica:** usar `${{ github.actor }}` o un secret `${{ secrets.GHCR_USERNAME }}`.

**Línea 114 — Password GHCR (OK, usa secret)**:
```yaml
          password: ${{ secrets.GHCR_PAT }}
```
→ Correcto, lee de secret. Solo asegurarse de que el secret `GHCR_PAT` esté configurado en tu repo con tu PAT personal.

**Líneas 98-99 — SonarCloud (OK, usa secrets)**:
```yaml
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
→ Correcto. `GITHUB_TOKEN` es automático. Solo configurar `SONAR_TOKEN` de tu cuenta.

**Líneas 160, 163 — Deploy hooks Render QA (OK, usa secrets)**:
```yaml
        run: curl -X POST "${{ secrets.RENDER_BACKEND_QA_HOOK }}"
        run: curl -X POST "${{ secrets.RENDER_FRONTEND_QA_HOOK }}"
```
→ Correcto, lee de secrets.

**Línea 170 — URL Frontend QA (hardcoded)**:
```yaml
          echo "   https://frontend-qa-qymo.onrender.com"
```
→ Cambiar por la URL de tu servicio QA en Render.

**Línea 195 — CYPRESS_BASE_URL (hardcoded)**:
```yaml
          CYPRESS_BASE_URL: https://frontend-qa-qymo.onrender.com
```
→ **CRÍTICO**: Cambiar por tu URL de QA. Mejor práctica: mover a un secret o variable de entorno del environment `qa` (e.g., `${{ vars.FRONTEND_QA_URL }}`).

**Líneas 221, 224 — Deploy hooks Render PROD (OK, usa secrets)**:
```yaml
        run: curl -X POST "${{ secrets.RENDER_BACKEND_PROD_HOOK }}"
        run: curl -X POST "${{ secrets.RENDER_FRONTEND_PROD_HOOK }}"
```

**Línea 231 — URL Frontend PROD (hardcoded)**:
```yaml
          echo "   https://frontend-prod-z6yw.onrender.com"
```
→ Cambiar por la URL de tu servicio PROD en Render.

---

### 3.2 `sonar-project.properties`

**Líneas 2-4 (hardcoded)**:
```properties
sonar.projectKey=ignaciomagoia_tp8ingsoft3
sonar.organization=ignaciomagoia
sonar.host.url=https://sonarcloud.io
```
→ Cambiar `projectKey` y `organization` por los de tu cuenta SonarCloud.
→ `sonar.host.url` queda igual (es el SaaS público de SonarCloud).

---

### 3.3 `backend/go.mod`

**Línea 1 (hardcoded)**:
```go
module github.com/ignaciomagoia/tp8ingsoft3/backend
```
→ Cambiar `ignaciomagoia` por tu usuario de GitHub.

---

### 3.4 `backend/main.go`

**Líneas 12-13 (hardcoded — imports)**:
```go
	"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/handlers"
	"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/services"
```
→ Cambiar `ignaciomagoia` por tu usuario de GitHub.

---

### 3.5 `backend/internal/handlers/auth_handler.go`

**Línea 9 (hardcoded — import)**:
```go
	"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/services"
```
→ Cambiar `ignaciomagoia` por tu usuario de GitHub.

---

### 3.6 `backend/internal/handlers/todo_handler.go`

**Línea 9 (hardcoded — import)**:
```go
	"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/services"
```
→ Cambiar `ignaciomagoia` por tu usuario de GitHub.

---

### 3.7 `backend/internal/handlers/test_helpers_test.go`

**Línea 12 (hardcoded — import)**:
```go
	"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/services"
```
→ Cambiar `ignaciomagoia` por tu usuario de GitHub.

---

### 3.8 `frontend/dockerfile`

**Línea 12 (comentario legacy)**:
```dockerfile
# docker build -t front-prod --build-arg VITE_API_URL=https://tp8-back-prod.azurewebsites.net .
```
→ Eliminar o actualizar este comentario. Hace referencia a un dominio Azure de terceros.

---

### 3.9 `backend/coverage.out` y `backend/coverage.html`

Estos archivos **no deberían estar en el repositorio** (son artefactos generados). Contienen rutas con `github.com/ignaciomagoia/tp6ingdesoft/` (repo anterior). Se recomienda:
- Agregarlos al `.gitignore`
- Eliminarlos del tracking

---

### 3.10 `Decisiones.md`

**Línea 3** — Referencia textual a `tp7ingsoft3` (repo anterior):
```markdown
El TP7 consolida todo el trabajo previo en un solo repo (`tp7ingsoft3`) ...
```
→ Actualizar o dejarlo como documentación histórica (no es un riesgo de seguridad).

---

## 4. Secrets y variables requeridos por los workflows

| Secret/Variable | Usado en | Tipo | Estado actual | Acción requerida |
|-----------------|----------|------|---------------|------------------|
| `SONAR_TOKEN` | `full-ci.yml:98` | Secret (repo) | Lee de `secrets.SONAR_TOKEN` ✅ | Crear token en tu cuenta SonarCloud y configurarlo |
| `GITHUB_TOKEN` | `full-ci.yml:99` | Secret (auto) | Provisto automáticamente por GitHub ✅ | Nada |
| `GHCR_PAT` | `full-ci.yml:114` | Secret (repo) | Lee de `secrets.GHCR_PAT` ✅ | Crear PAT (Classic) con scope `write:packages` y configurarlo |
| `RENDER_BACKEND_QA_HOOK` | `full-ci.yml:160` | Secret (env: qa) | Lee de `secrets.RENDER_BACKEND_QA_HOOK` ✅ | Obtener deploy hook de tu servicio backend QA en Render |
| `RENDER_FRONTEND_QA_HOOK` | `full-ci.yml:163` | Secret (env: qa) | Lee de `secrets.RENDER_FRONTEND_QA_HOOK` ✅ | Obtener deploy hook de tu servicio frontend QA en Render |
| `RENDER_BACKEND_PROD_HOOK` | `full-ci.yml:221` | Secret (env: prod) | Lee de `secrets.RENDER_BACKEND_PROD_HOOK` ✅ | Obtener deploy hook de tu servicio backend PROD en Render |
| `RENDER_FRONTEND_PROD_HOOK` | `full-ci.yml:224` | Secret (env: prod) | Lee de `secrets.RENDER_FRONTEND_PROD_HOOK` ✅ | Obtener deploy hook de tu servicio frontend PROD en Render |

### Variables recomendadas (mejora propuesta):

| Variable propuesta | Para reemplazar | Scope |
|--------------------|-----------------|-------|
| `vars.GHCR_USERNAME` | Username hardcoded `ignaciomagoia` en `full-ci.yml:113` | Repo |
| `vars.FRONTEND_QA_URL` | URL hardcodeada `https://frontend-qa-qymo.onrender.com` | Environment `qa` |
| `vars.FRONTEND_PROD_URL` | URL hardcodeada `https://frontend-prod-z6yw.onrender.com` | Environment `prod` |

---

## 5. Archivos a modificar — Cambios exactos

### 5.1 `.github/workflows/full-ci.yml`

| Línea | Valor actual | Nuevo valor |
|-------|-------------|-------------|
| 11 | `ghcr.io/ignaciomagoia/tp8-backend` | `ghcr.io/TU_USUARIO_GITHUB/tp8-backend` |
| 12 | `ghcr.io/ignaciomagoia/tp8-frontend` | `ghcr.io/TU_USUARIO_GITHUB/tp8-frontend` |
| 113 | `username: ignaciomagoia` | `username: TU_USUARIO_GITHUB` (o mejor: `username: ${{ github.actor }}`) |
| 170 | `https://frontend-qa-qymo.onrender.com` | `https://TU-FRONTEND-QA.onrender.com` |
| 195 | `CYPRESS_BASE_URL: https://frontend-qa-qymo.onrender.com` | `CYPRESS_BASE_URL: https://TU-FRONTEND-QA.onrender.com` |
| 231 | `https://frontend-prod-z6yw.onrender.com` | `https://TU-FRONTEND-PROD.onrender.com` |

### 5.2 `sonar-project.properties`

| Línea | Valor actual | Nuevo valor |
|-------|-------------|-------------|
| 2 | `sonar.projectKey=ignaciomagoia_tp8ingsoft3` | `sonar.projectKey=TU_USUARIO_tp8ingsoft3` |
| 3 | `sonar.organization=ignaciomagoia` | `sonar.organization=TU_USUARIO` |

### 5.3 `backend/go.mod`

| Línea | Valor actual | Nuevo valor |
|-------|-------------|-------------|
| 1 | `module github.com/ignaciomagoia/tp8ingsoft3/backend` | `module github.com/TU_USUARIO/tp8ingsoft3/backend` |

### 5.4 `backend/main.go`

| Línea | Valor actual | Nuevo valor |
|-------|-------------|-------------|
| 12 | `"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/handlers"` | `"github.com/TU_USUARIO/tp8ingsoft3/backend/internal/handlers"` |
| 13 | `"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/services"` | `"github.com/TU_USUARIO/tp8ingsoft3/backend/internal/services"` |

### 5.5 `backend/internal/handlers/auth_handler.go`

| Línea | Valor actual | Nuevo valor |
|-------|-------------|-------------|
| 9 | `"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/services"` | `"github.com/TU_USUARIO/tp8ingsoft3/backend/internal/services"` |

### 5.6 `backend/internal/handlers/todo_handler.go`

| Línea | Valor actual | Nuevo valor |
|-------|-------------|-------------|
| 9 | `"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/services"` | `"github.com/TU_USUARIO/tp8ingsoft3/backend/internal/services"` |

### 5.7 `backend/internal/handlers/test_helpers_test.go`

| Línea | Valor actual | Nuevo valor |
|-------|-------------|-------------|
| 12 | `"github.com/ignaciomagoia/tp8ingsoft3/backend/internal/services"` | `"github.com/TU_USUARIO/tp8ingsoft3/backend/internal/services"` |

### 5.8 `frontend/dockerfile`

| Línea | Valor actual | Nuevo valor |
|-------|-------------|-------------|
| 12 | `# docker build -t front-prod --build-arg VITE_API_URL=https://tp8-back-prod.azurewebsites.net .` | Eliminar línea o reemplazar URL por la de tu backend PROD |

### 5.9 `.gitignore` (agregar)

Agregar las siguientes líneas para evitar commitear artefactos generados:
```
backend/coverage.out
backend/coverage.html
frontend/coverage/
```

### 5.10 Archivos a eliminar del tracking (pero no del disco)

```bash
git rm --cached backend/coverage.out
git rm --cached backend/coverage.html
git rm -r --cached frontend/coverage/
```

---

## 6. Plan de migración

### Paso 1 — SonarCloud
1. Ir a [https://sonarcloud.io](https://sonarcloud.io) y loguearte con **tu** cuenta de GitHub.
2. Importar el repositorio `tp8ingsoft3` como nuevo proyecto.
3. Anotar tu `organization` (usualmente tu usuario de GitHub) y el `projectKey` generado (formato: `tu_usuario_tp8ingsoft3`).
4. Generar un token de análisis en SonarCloud → **Security → Generate Token**.

### Paso 2 — Actualizar SonarCloud en el repo
1. Editar `sonar-project.properties` con tu `organization` y `projectKey`.
2. En GitHub → Settings → Secrets → Actions → crear/actualizar el secret `SONAR_TOKEN` con tu token de SonarCloud.

### Paso 3 — GHCR (GitHub Container Registry)
1. Ir a GitHub → Settings → Developer settings → Personal Access Tokens → Tokens (classic).
2. Crear un PAT con scope: `write:packages`, `read:packages`, `delete:packages`.
3. En el repo → Settings → Secrets → Actions → crear/actualizar el secret `GHCR_PAT` con tu PAT.
4. Editar `.github/workflows/full-ci.yml`:
   - Cambiar las env `BACKEND_IMAGE` y `FRONTEND_IMAGE` con tu usuario.
   - Cambiar el `username` en el login de GHCR.

### Paso 4 — Render
1. Crear una cuenta en [https://render.com](https://render.com) (o usar la tuya existente).
2. Crear **4 servicios Web**:
   - `backend-qa` (Docker, imagen: `ghcr.io/TU_USUARIO/tp8-backend:qa-latest`)
   - `frontend-qa` (Docker, imagen: `ghcr.io/TU_USUARIO/tp8-frontend:qa-latest`)
   - `backend-prod` (Docker, imagen: `ghcr.io/TU_USUARIO/tp8-backend:prod-latest`)
   - `frontend-prod` (Docker, imagen: `ghcr.io/TU_USUARIO/tp8-frontend:prod-latest`)
3. En cada servicio, ir a **Settings → Deploy Hook** y copiar la URL.
4. Configurar las env vars en cada servicio de Render:
   - Backend QA/PROD: `MONGO_URI`, `MONGO_DB`, `FRONT_ORIGINS` (con la URL del frontend correspondiente)
   - Frontend QA/PROD: `VITE_API_URL` (con la URL del backend correspondiente)
5. En GitHub → Settings → Environments:
   - Environment **qa**: secrets `RENDER_BACKEND_QA_HOOK`, `RENDER_FRONTEND_QA_HOOK`
   - Environment **prod**: secrets `RENDER_BACKEND_PROD_HOOK`, `RENDER_FRONTEND_PROD_HOOK`
6. Actualizar las URLs hardcodeadas en `full-ci.yml` (líneas 170, 195, 231).

### Paso 5 — Módulo Go
1. Renombrar el módulo en `backend/go.mod` de `github.com/ignaciomagoia/...` a `github.com/TU_USUARIO/...`.
2. Actualizar todos los imports en los archivos `.go` que importan paquetes internos (ver sección 5).
3. Ejecutar `cd backend && go mod tidy` para validar.

### Paso 6 — Validación
1. Hacer un push a `develop` o abrir un PR contra `main`.
2. Verificar que cada job del pipeline pase:
   - ✅ `backend-tests`
   - ✅ `frontend-tests`
   - ✅ `sonarcloud-analysis`
   - ✅ `build_images` (push a GHCR)
   - ✅ `deploy_qa` (deploy a Render QA)
   - ✅ `e2e-tests` (Cypress contra QA)
   - ✅ `approve_prod` (gate manual)
   - ✅ `deploy_prod` (deploy a Render PROD)

### Paso 7 — Limpieza
1. Eliminar artefactos de coverage del repositorio (ver sección 5.10).
2. Actualizar `.gitignore` para evitar futuros commits de artefactos.
3. Si el PAT anterior de `ignaciomagoia` fue compartido, rotarlo/revocarlo.

---

## 7. ALERTAS

### ⚠️ ALERTA BAJA — Artefactos de coverage commiteados

**Archivos afectados:**
- `backend/coverage.out`
- `backend/coverage.html`
- `frontend/coverage/` (directorio completo con reportes)

**Riesgo:** Estos son artefactos generados que no deberían estar en el repo. El `coverage.out` contiene rutas con el módulo de un repo anterior (`tp6ingdesoft`). No contienen credenciales, pero ensucian el historial y revelan estructura interna.

**Acción:**
```bash
# Agregar al .gitignore
echo "backend/coverage.out" >> .gitignore
echo "backend/coverage.html" >> .gitignore
echo "frontend/coverage/" >> .gitignore

# Eliminar del tracking (sin borrar del disco)
git rm --cached backend/coverage.out
git rm --cached backend/coverage.html
git rm -r --cached frontend/coverage/

git commit -m "chore: remove generated coverage artifacts from tracking"
```

### ✅ NO se detectaron credenciales commiteadas

No se encontraron tokens, API keys, contraseñas reales ni deploy hooks en el código fuente. Todos los secrets se leen correctamente desde `${{ secrets.* }}` en GitHub Actions.

Las "passwords" encontradas en archivos de test (`"secret"`, `"superSecret123"`) son **datos de prueba ficticios** y no representan un riesgo.

---

## 8. Checklist accionable

- [ ] Crear cuenta/proyecto en SonarCloud bajo tu usuario
- [ ] Actualizar `sonar-project.properties` (projectKey + organization)
- [ ] Configurar secret `SONAR_TOKEN` en GitHub con tu token de SonarCloud
- [ ] Crear PAT de GitHub con scope `write:packages`
- [ ] Configurar secret `GHCR_PAT` en GitHub con tu PAT
- [ ] Actualizar `BACKEND_IMAGE` en `full-ci.yml` (línea 11) con tu usuario
- [ ] Actualizar `FRONTEND_IMAGE` en `full-ci.yml` (línea 12) con tu usuario
- [ ] Actualizar `username` de GHCR login en `full-ci.yml` (línea 113) con tu usuario
- [ ] Crear 4 servicios en Render (backend-qa, frontend-qa, backend-prod, frontend-prod)
- [ ] Obtener deploy hooks de cada servicio Render
- [ ] Configurar secrets de Render en GitHub (environment `qa` y `prod`)
- [ ] Actualizar URL de QA hardcodeada en `full-ci.yml` línea 170
- [ ] Actualizar `CYPRESS_BASE_URL` en `full-ci.yml` línea 195
- [ ] Actualizar URL de PROD hardcodeada en `full-ci.yml` línea 231
- [ ] Actualizar module path en `backend/go.mod` (línea 1)
- [ ] Actualizar imports en `backend/main.go` (líneas 12-13)
- [ ] Actualizar import en `backend/internal/handlers/auth_handler.go` (línea 9)
- [ ] Actualizar import en `backend/internal/handlers/todo_handler.go` (línea 9)
- [ ] Actualizar import en `backend/internal/handlers/test_helpers_test.go` (línea 12)
- [ ] Ejecutar `cd backend && go mod tidy` para validar módulo
- [ ] Actualizar o eliminar comentario Azure en `frontend/dockerfile` (línea 12)
- [ ] Agregar artefactos de coverage al `.gitignore`
- [ ] Eliminar artefactos de coverage del tracking con `git rm --cached`
- [ ] Hacer push de prueba y validar pipeline completo
- [ ] Revocar cualquier PAT viejo de `ignaciomagoia` si fue compartido

---

## 9. Comandos de re-verificación local

Ejecutar después de aplicar todos los cambios para confirmar que no quedan referencias a cuentas antiguas:

```bash
# Buscar cualquier referencia residual al usuario anterior
rg "ignaciomagoia" --type-not lockfile -g '!package-lock.json' -g '!go.sum' -g '!coverage.*' -g '!*.html'

# Buscar URLs de Render del owner anterior
rg "frontend-qa-qymo\.onrender\.com"
rg "frontend-prod-z6yw\.onrender\.com"

# Buscar referencias a Azure legacy
rg "azurewebsites\.net"

# Buscar referencias al repo anterior (tp6)
rg "tp6ingdesoft" -g '!coverage.*' -g '!*.html'

# Verificar que no hay tokens/secrets en texto plano
rg "ghp_[A-Za-z0-9]+" # GitHub PAT pattern
rg "sqp_[A-Za-z0-9]+" # SonarCloud token pattern
rg "rnd_[A-Za-z0-9]+" # Render API key pattern
rg "Bearer [A-Za-z0-9]+"

# Listar todos los secrets referenciados en workflows
rg "secrets\." .github/workflows/

# Verificar que no hay .env con contenido real
find . -name ".env" -o -name ".env.local" -o -name ".env.production" | head -20
```

---

## 10. Resumen de archivos tocados

| Archivo | Tipo de cambio |
|---------|---------------|
| `.github/workflows/full-ci.yml` | Editar (6 cambios: 3 GHCR + 3 URLs Render) |
| `sonar-project.properties` | Editar (2 cambios: projectKey + organization) |
| `backend/go.mod` | Editar (1 cambio: module path) |
| `backend/main.go` | Editar (2 cambios: imports) |
| `backend/internal/handlers/auth_handler.go` | Editar (1 cambio: import) |
| `backend/internal/handlers/todo_handler.go` | Editar (1 cambio: import) |
| `backend/internal/handlers/test_helpers_test.go` | Editar (1 cambio: import) |
| `frontend/dockerfile` | Editar (1 cambio: eliminar/actualizar comentario Azure) |
| `.gitignore` | Editar (agregar 3 líneas para excluir coverage) |
| `backend/coverage.out` | Eliminar del tracking |
| `backend/coverage.html` | Eliminar del tracking |
| `frontend/coverage/` | Eliminar del tracking |

**Total: 9 archivos a editar + 3 artefactos a destrackear**
