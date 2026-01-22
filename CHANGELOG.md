# Historial de Cambios

Todos los cambios notables de este proyecto se documentarán en este archivo.

## [1.2.0] - 2026-01-22

### Añadido
- **Integración con cron-job.org**: Los workflows ahora se activan externamente mediante cron-job.org en lugar del scheduler interno de GitHub Actions. Esto proporciona mayor puntualidad (1-2 minutos vs 0-60 minutos de retraso).
- **Disparador `repository_dispatch`**: Los workflows aceptan eventos externos vía API de GitHub.
- **Disparador manual `workflow_dispatch`**: Permite ejecutar workflows manualmente desde la interfaz de GitHub.

### Cambiado
- **Eliminación de schedules internos**: Se eliminaron los cron schedules de GitHub Actions para evitar duplicación. Ahora solo cron-job.org dispara los workflows.
- **Selector PAUSE corregido**: Cambiado de `#btn-lunch-pause` a `#btn-pause-lunch` (selector correcto según el HTML de Bixpe).
- **Lógica de confirmación**: START y END requieren confirmación; PAUSE y RESUME no.

### Corregido
- **Comprobación de festivos siempre activa**: Los festivos definidos en `holidays.json` ahora se comprueban siempre, incluso con `--force`. El flag `--force` solo omite la comprobación de horario.

### Configuración de cron-job.org
Los siguientes jobs deben configurarse en [cron-job.org](https://cron-job.org):

| Job | Horario | event_type |
|-----|---------|------------|
| Clock In (L-J) | 08:30 | `clock_in` |
| Clock In (V) | 08:00 | `clock_in` |
| Break Start (L-J) | 14:00 | `break_start` |
| Break End (L-J) | 15:00 | `break_end` |
| Clock Out (L-J) | 18:00 | `clock_out` |
| Clock Out (V) | 14:00 | `clock_out` |

---

## [1.1.0] - 2026-01-21

### Añadido
- **Modo Simulación** (flag `--simulate`): Permite probar el flujo completo sin fichar realmente. El script hace clic en "Cancelar" en los diálogos de confirmación en lugar de "Confirmar".
- **Checklist de Diagnóstico Pre-Clic**: Registra información detallada sobre el estado del botón antes de hacer clic (tipo de etiqueta, visibilidad, dimensiones, detección de overlay).
- **Sondeo del DOM en Fallo**: Cuando no se encuentra un botón, el script lista todos los botones visibles para ayudar a diagnosticar problemas con selectores.

### Cambiado
- **Selectores de Login**: Actualizados para usar IDs precisos (`#emailLogin`, `#passwordLogin`) basados en la documentación de Bixpe.
- **Selectores de Botones de Acción**: Actualizados para usar IDs precisos:
  - INICIO: `#btn-start-workday`
  - PAUSA: `#btn-pause-lunch`
  - REANUDAR: `#btn-resume-workday`
  - FIN: `#btn-stop-workday`
- **Manejo de Diálogo de Confirmación**: Ahora usa selectores específicos de SweetAlert2 (`button.swal2-confirm`, `button.swal2-cancel`).
- **Estrategia de Clic**: Implementado enfoque robusto de 3 capas:
  1. Esperar a que desaparezca el overlay `#processing-text`
  2. Inyección de clic por JavaScript (evita problemas de overlay/tooltip)
  3. Clic forzado de Playwright como respaldo

### Corregido
- **Error "Event Loop Closed"**: Resuelto cambiando del gestor de contexto a gestión manual del ciclo de vida de Playwright.
- **Errores de Sintaxis JavaScript**: Corregidos comentarios estilo Python (`#`) en JS embebido y envuelto código en IIFE para sentencias `return` válidas.
- **Errores de Indentación**: Corregida estructura de bloques `try/finally`.

### GitHub Actions
- Actualizados todos los workflows para usar Python 3.11 (más estable con Playwright)
- Añadido `playwright install-deps chromium` para dependencias correctas del navegador
- Mejorado logging con marcas de tiempo
- Añadida subida de artefactos de depuración en fallo (volcados HTML + capturas)
- Nombres de artefactos únicos por ejecución para evitar sobrescritura

---

## [1.0.0] - 2026-01-18

### Añadido
- Implementación inicial del script de automatización de Bixpe
- Workflows de GitHub Actions para entrada, inicio-pausa, fin-pausa, salida
- Funcionalidad de comprobación de festivos
- Configuración de horarios vía `schedule.json`
- Simulación de geolocalización para requisitos de Bixpe
