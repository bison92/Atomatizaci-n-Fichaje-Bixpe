# Automatización Fichaje Bixpe

Script de automatización para fichar entrada/salida y pausas en la plataforma Bixpe Control Horario.

## Cómo funciona

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   cron-job.org  │ ──▶  │  GitHub Actions │ ──▶  │     Bixpe       │
│  (Disparador)   │      │    (Script)     │      │   (Fichaje)     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

1. **cron-job.org** dispara el workflow a la hora programada
2. **GitHub Actions** ejecuta el script de Python
3. **El script** abre Bixpe, hace login y ficha automáticamente

## Características

- ✅ Fichaje automático de entrada (START)
- ✅ Pausa para comida (PAUSE)
- ✅ Vuelta de pausa (RESUME)
- ✅ Fichaje de salida (END)
- ✅ Gestión de festivos y vacaciones
- ✅ Modo simulación para pruebas
- ✅ Integración con cron-job.org para máxima puntualidad (~1-2 min)

## Horarios programados

Los horarios se configuran en **cron-job.org**, no en este repositorio.

| Acción | Lunes-Jueves | Viernes |
|--------|--------------|---------|
| Entrada (START) | 08:30 | 08:00 |
| Inicio pausa (PAUSE) | 14:00 | - |
| Fin pausa (RESUME) | 15:00 | - |
| Salida (END) | 18:00 | 14:00 |

## Configuración

### 1. Credenciales (GitHub Secrets)

Las credenciales de Bixpe se almacenan de forma segura en GitHub:
- `Settings` → `Secrets and variables` → `Actions`

| Secret | Descripción |
|--------|-------------|
| `BIXPE_EMAIL` | Tu email de Bixpe |
| `BIXPE_PASSWORD` | Tu contraseña de Bixpe |

### 2. Festivos y vacaciones

Edita `holidays.json` para añadir días en los que NO se debe fichar:

```json
[
  "2026-01-01",
  "2026-12-25",
  "2026-08-15"
]
```

Los fines de semana se detectan automáticamente.

### 3. Disparador externo (cron-job.org)

Los workflows se activan mediante [cron-job.org](https://cron-job.org):
- Crea una cuenta gratuita
- Configura los 6 jobs con los horarios deseados
- Cada job envía una petición POST a la API de GitHub

## Uso manual

```bash
# Fichar entrada
python src/bixpe_bot.py --action START --force

# Iniciar pausa
python src/bixpe_bot.py --action PAUSE --force

# Fin de pausa
python src/bixpe_bot.py --action RESUME --force

# Fichar salida
python src/bixpe_bot.py --action END --force

# Modo simulación (no ficha realmente)
python src/bixpe_bot.py --action START --simulate
```

## Archivos del proyecto

| Archivo | Descripción |
|---------|-------------|
| `src/bixpe_bot.py` | Script principal de automatización |
| `holidays.json` | Lista de festivos y vacaciones |
| `.github/workflows/` | Workflows de GitHub Actions |
| `SETUP_GUIA.md` | Guía para configurar tu propia copia |
| `CHANGELOG.md` | Historial de cambios |

## Para nuevos usuarios

Si quieres configurar tu propia automatización, sigue la guía completa:
👉 [SETUP_GUIA.md](SETUP_GUIA.md)

## Historial de cambios

Consulta el [CHANGELOG.md](CHANGELOG.md) para ver todas las actualizaciones.

## Licencia

MIT
