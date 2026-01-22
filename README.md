# Automatización Fichaje Bixpe

Script de automatización para fichar entrada/salida y pausas en la plataforma Bixpe Control Horario.

## Características

- ✅ Fichaje automático de entrada (START)
- ✅ Pausa para comida (PAUSE)
- ✅ Vuelta de pausa (RESUME)
- ✅ Fichaje de salida (END)
- ✅ Gestión de festivos y vacaciones
- ✅ Modo simulación para pruebas
- ✅ Integración con cron-job.org para máxima puntualidad

## Requisitos

- Python 3.11+
- Playwright
- Cuenta en Bixpe Control Horario

## Instalación

```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuración

### Variables de entorno
Configura las siguientes variables de entorno o crea un archivo `.env`:

```env
BIXPE_EMAIL=tu_email@ejemplo.com
BIXPE_PASSWORD=tu_contraseña
```

### Festivos y vacaciones
Edita `holidays.json` para añadir días festivos o de vacaciones:

```json
[
  "2026-01-01",
  "2026-12-25",
  "2026-08-15"
]
```

### Horarios
Configura los horarios en `schedule.json`:

```json
{
    "mon_thu": {
        "start": "08:30",
        "break_start": "14:00",
        "break_end": "15:00",
        "end": "18:00"
    },
    "friday": {
        "start": "08:00",
        "break_start": null,
        "break_end": null,
        "end": "14:00"
    },
    "timezone": "Europe/Madrid"
}
```

## Uso

### Ejecución manual
```bash
# Fichar entrada
python src/bixpe_bot.py --action START

# Iniciar pausa
python src/bixpe_bot.py --action PAUSE

# Fin de pausa
python src/bixpe_bot.py --action RESUME

# Fichar salida
python src/bixpe_bot.py --action END

# Modo simulación (no ficha realmente)
python src/bixpe_bot.py --action START --simulate
```

### Ejecución automática
Los workflows se activan automáticamente mediante [cron-job.org](https://cron-job.org) para máxima puntualidad.

## Historial de cambios

Consulta el [CHANGELOG.md](CHANGELOG.md) para ver todos los cambios y actualizaciones.

## Licencia

MIT
