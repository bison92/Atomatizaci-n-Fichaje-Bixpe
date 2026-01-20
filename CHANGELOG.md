# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-01-21

### Added
- **Simulation Mode** (`--simulate` flag): Allows testing the complete flow without actually clocking in/out. The script clicks "Cancel" on confirmation dialogs instead of "Confirm".
- **Pre-click Diagnostic Checklist**: Logs detailed information about button state before clicking (tag type, visibility, dimensions, overlay detection).
- **DOM Probe on Failure**: When a button is not found, the script lists all visible buttons to help diagnose selector issues.

### Changed
- **Login Selectors**: Updated to use precise IDs (`#emailLogin`, `#passwordLogin`) based on Bixpe documentation.
- **Action Button Selectors**: Updated to use precise IDs:
  - START: `#btn-start-workday`
  - PAUSE: `#btn-lunch-pause`
  - RESUME: `#btn-resume-workday`
  - END: `#btn-stop-workday`
- **Confirmation Dialog Handling**: Now uses SweetAlert2-specific selectors (`button.swal2-confirm`, `button.swal2-cancel`).
- **Click Strategy**: Implemented robust 3-layer approach:
  1. Wait for `#processing-text` overlay to disappear
  2. JavaScript click injection (bypasses overlay/tooltip issues)
  3. Fallback Playwright force-click

### Fixed
- **Event Loop Closed Error**: Resolved by switching from context manager to manual Playwright lifecycle management.
- **JavaScript Syntax Errors**: Fixed Python-style comments (`#`) in embedded JS and wrapped code in IIFE for valid `return` statements.
- **Indentation Errors**: Corrected `try/finally` block structure.

### GitHub Actions
- Updated all workflows to use Python 3.11 (more stable with Playwright)
- Added `playwright install-deps chromium` for proper browser dependencies
- Enhanced logging with timestamps
- Added debug artifact upload on failure (HTML dumps + screenshots)
- Unique artifact names per run to avoid overwriting

## [1.0.0] - 2026-01-18

### Added
- Initial implementation of Bixpe automation script
- GitHub Actions workflows for clock-in, break-start, break-end, clock-out
- Holiday checking functionality
- Schedule configuration via `schedule.json`
- Geolocation mocking for Bixpe requirements
