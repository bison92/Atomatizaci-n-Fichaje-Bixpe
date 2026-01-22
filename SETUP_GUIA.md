# Guía de Configuración - Automatización Fichaje Bixpe

Esta guía te permitirá configurar tu propia automatización de fichaje en Bixpe.

---

## Requisitos previos

- Cuenta en Bixpe Control Horario (con email y contraseña)
- Cuenta de email para registros

---

## Paso 1: Crear cuenta en GitHub

1. Ve a https://github.com/signup
2. Completa el registro con tu email
3. Verifica tu email

---

## Paso 2: Hacer Fork del repositorio

1. Ve a: https://github.com/eaguadov/Atomatizaci-n-Fichaje-Bixpe
2. Click en el botón **"Fork"** (arriba a la derecha)
3. En la pantalla de fork, mantén el nombre por defecto
4. Click **"Create fork"**

Ahora tienes tu propia copia en: `https://github.com/TU_USUARIO/Atomatizaci-n-Fichaje-Bixpe`

> ✅ **BUENA NOTICIA**: El código es genérico, NO necesitas modificar ningún archivo. 
> 
> ⚠️ **ÚNICO CAMBIO NECESARIO**: En el **Paso 6** (cron-job.org), deberás poner TU usuario de GitHub en la URL de los cron jobs.


---

## Paso 3: Configurar Secrets en GitHub

Los secrets almacenan tus credenciales de forma segura.

1. Ve a tu fork: `https://github.com/TU_USUARIO/Atomatizaci-n-Fichaje-Bixpe`
2. Click en **Settings** (pestaña superior)
3. Menú izquierdo: **Secrets and variables** → **Actions**
4. Click **"New repository secret"**

### Secrets a crear:

| Name | Value |
|------|-------|
| `BIXPE_EMAIL` | Tu email de Bixpe |
| `BIXPE_PASSWORD` | Tu contraseña de Bixpe |

---

## Paso 4: Crear Personal Access Token (PAT)

El token permite a cron-job.org disparar tus workflows.

1. Ve a: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Configura:
   - **Note**: `cron-job-bixpe`
   - **Expiration**: `No expiration` o `1 year`
   - **Select scopes**: Marca solo ✅ **repo**
4. Click **"Generate token"**
5. **COPIA EL TOKEN** (empieza con `ghp_...`)

> ⚠️ El token solo se muestra UNA vez. Guárdalo en un lugar seguro.

---

## Paso 5: Crear cuenta en cron-job.org

1. Ve a: https://cron-job.org/en/signup/
2. Regístrate con tu email
3. Confirma tu cuenta

---

## Paso 6: Configurar los Cron Jobs

Crea **6 jobs** en cron-job.org con la siguiente configuración.

### Configuración común para TODOS los jobs:

**En la pestaña ADVANCED:**

| Campo | Valor |
|-------|-------|
| **Request Method** | `POST` |
| **Timeout** | `30` segundos |

**Headers (añadir los 3):**

| Key | Value |
|-----|-------|
| `Authorization` | `Bearer TU_TOKEN_AQUI` |
| `Accept` | `application/vnd.github.v3+json` |
| `Content-Type` | `application/json` |

> ⚠️ Sustituye `TU_TOKEN_AQUI` por el token que copiaste en el Paso 4.

---

### Los 6 Jobs a crear:

**URL para todos** (sustituye `TU_USUARIO`):
```
https://api.github.com/repos/TU_USUARIO/Atomatizaci-n-Fichaje-Bixpe/dispatches
```

| Job | Días | Hora | Request Body |
|-----|------|------|--------------|
| Clock In (L-J) | Mon, Tue, Wed, Thu | 08:30 | `{"event_type": "clock_in"}` |
| Clock In (V) | Fri | 08:00 | `{"event_type": "clock_in"}` |
| Break Start | Mon, Tue, Wed, Thu | 14:00 | `{"event_type": "break_start"}` |
| Break End | Mon, Tue, Wed, Thu | 15:00 | `{"event_type": "break_end"}` |
| Clock Out (L-J) | Mon, Tue, Wed, Thu | 18:00 | `{"event_type": "clock_out"}` |
| Clock Out (V) | Fri | 14:00 | `{"event_type": "clock_out"}` |

### Cómo crear cada job:

1. Click **"CREATE CRONJOB"**
2. **Title**: Nombre del job (ej: "Clock In L-J")
3. **URL**: Pega la URL de arriba (con TU_USUARIO)
4. **Schedule**: Selecciona "Custom" y configura días/hora
5. Ve a pestaña **ADVANCED**
6. Configura Request Method, Headers y Request Body
7. Click **"CREATE"**
8. **Asegúrate de que el job esté ENABLED** (habilitado)

---

## Paso 7: Gestionar vacaciones y festivos

Edita el archivo `holidays.json` en tu fork:

1. Ve a: `https://github.com/TU_USUARIO/Atomatizaci-n-Fichaje-Bixpe/blob/main/holidays.json`
2. Click en el icono de lápiz ✏️ (Edit)
3. Añade tus fechas de vacaciones:

```json
[
  "2026-01-01",
  "2026-08-15",
  "2026-12-25",
  "2026-07-15",
  "2026-07-16"
]
```

4. Click **"Commit changes"**

> Los días en esta lista NO se fichará automáticamente.

---

## Paso 8: Verificar que funciona

### Test manual:
1. En cron-job.org, entra en uno de tus jobs
2. Click **"TEST RUN"**
3. Debería mostrar **"204 No Content"** = ✅ Éxito

### Verificar en GitHub:
1. Ve a: `https://github.com/TU_USUARIO/Atomatizaci-n-Fichaje-Bixpe/actions`
2. Deberías ver el workflow ejecutándose

---

## Resumen de datos importantes

### URLs a personalizar:

| Uso | URL (sustituye TU_USUARIO) |
|-----|----------------------------|
| Tu fork | `https://github.com/TU_USUARIO/Atomatizaci-n-Fichaje-Bixpe` |
| Secrets | `https://github.com/TU_USUARIO/Atomatizaci-n-Fichaje-Bixpe/settings/secrets/actions` |
| Actions | `https://github.com/TU_USUARIO/Atomatizaci-n-Fichaje-Bixpe/actions` |
| API Dispatch | `https://api.github.com/repos/TU_USUARIO/Atomatizaci-n-Fichaje-Bixpe/dispatches` |

### Secrets de GitHub:

| Secret | Valor |
|--------|-------|
| `BIXPE_EMAIL` | Tu email de Bixpe |
| `BIXPE_PASSWORD` | Tu contraseña de Bixpe |

### Headers para cron-job.org:

| Header | Valor |
|--------|-------|
| `Authorization` | `Bearer ghp_xxxxxxxxxxxx` (tu token) |
| `Accept` | `application/vnd.github.v3+json` |
| `Content-Type` | `application/json` |

### Horarios de fichaje:

| Acción | Lunes-Jueves | Viernes |
|--------|--------------|---------|
| Entrada | 08:30 | 08:00 |
| Inicio pausa | 14:00 | - |
| Fin pausa | 15:00 | - |
| Salida | 18:00 | 14:00 |

---

## Solución de problemas

| Problema | Solución |
|----------|----------|
| Error 401 Unauthorized | Revisa que el token esté correcto en Authorization |
| Error 404 Not Found | Revisa que la URL tenga TU_USUARIO correcto |
| Job no se ejecuta | Verifica que el job esté ENABLED en cron-job.org |
| Workflow falla | Revisa los secrets en GitHub (BIXPE_EMAIL, BIXPE_PASSWORD) |

---

## Contacto

Si tienes problemas, contacta con el administrador del proyecto original.
