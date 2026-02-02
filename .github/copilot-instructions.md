# Copilot instructions — SI-GOUVERNANCE

Short, practical guidance for AI coding agents working in this repository.

- Project type: Django web app (app name `core`, project `si_gouvernance`). Uses `mysqlclient`, `django-tailwind` and `django-browser-reload` (see `requirements.txt`).
  - Python: 3.13 (documented in `DOCUMENTATION_COMPLETE_SI_GOUVERNANCE.md`) — utilisez cette version ou une compatible proche.
- Entrypoints: `manage.py` for CLI; settings live in `si_gouvernance/settings.py` (DB configured via environment variables with `python-decouple`).

- Big picture:
  - Central domain: project governance with entities `Projet`, `EtapeProjet`, `ModuleProjet`, `TacheModule`, `TacheEtape` in `core/models.py`.
  - Auth: custom user model `core.Utilisateur` (UUID PK) — see `AUTH_USER_MODEL` in settings.
  - Audit: `core/utils.py` provides `enregistrer_audit()` and `ActionAudit` usage across views.
  - URLs use UUIDs for most resources (see `core/urls.py`) — keep PK types (UUID) consistent when adding routes or serializers.

- Key conventions / patterns to follow (discoverable in code):
  - Models frequently use `UUIDField(primary_key=True)` — do not migrate PK types lightly.
  - Permissions helpers live in `core/utils.py`: `peut_creer_taches(user, projet)`, `require_super_admin`, `require_project_access`. Use these rather than reinventing permission checks.
  - Audit every sensitive action with `enregistrer_audit()` (views do this repeatedly). Include `projet` and `request` where possible.
  - Module creation is restricted to development phase: check `EtapeProjet.peut_creer_modules_librement()` before creating modules.
  - Templates under `templates/core/` and front-end styles managed by the `theme` tailwind app (`TAILWIND_APP_NAME = 'theme'`).

- Developer workflows / commands (what to run):
  - Install deps: `python -m pip install -r requirements.txt` in a venv.
  - Set env vars for DB: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (settings use `decouple`).
  - DB migrations: `python manage.py migrate` then `python manage.py loaddata` if fixtures exist.
  - Run dev server: `python manage.py runserver` (or use `django-browser-reload` during UI work).
  - Tailwind: front-end assets are managed by `django-tailwind` (`TAILWIND_APP_NAME='theme'`) — run tailwind dev commands when editing CSS.
  - Tests: there are many tests at repo root (`test_*.py`) and in `core/tests.py` — run `python -m pytest` or `python manage.py test`.
  - Quick verification: `python verify_v2_implementation.py` (present in repo docs) validates V2 features.

- Integration points & external deps:
  - MySQL (primary DB) configured in `si_gouvernance/settings.py` — CI/dev may use local MySQL or override with sqlite for quick runs.
  - `django-tailwind` + `theme` app for CSS pipeline.
  - `django-browser-reload` used for live front-end reload while developing.

- Testing and safety notes for code edits:
  - Respect migrations 0001–0014 (v2 features). Many migrations change primary keys to UUID — avoid schema-breaking refactors.
  - When adding views or APIs, follow existing permission decorators and call `enregistrer_audit()` for create/update/delete operations.
  - URLs follow the UUID pattern; add `<uuid:...>` segments consistently.

- Files to reference when working on features:
  - `core/models.py` — domain model definitions and UUID PKs.
  - `core/utils.py` — permission helpers, audit helper, validation utilities.
  - `core/views.py` — canonical view implementations and examples of permission checks and audits.
  - `core/urls.py` — canonical URL patterns (UUID usage).
  - `si_gouvernance/settings.py` — env-based DB and installed apps (`theme`, `core`).
  - `DOCUMENTATION_COMPLETE_SI_GOUVERNANCE.md` (guide complet, v2.3), `ARCHITECTURE_ETAPES_MODULES_TACHES.md`, `IMPLEMENTATION_COMPLETE_V2.md`, `GESTION_TACHES_AVANCEE_V2.3_IMPLEMENTATION.md` — design & constraints documents (authoritative for v2 behavior).

- If anything here is unclear or you want more detail (example code snippets, how to run Tailwind, or test commands), tell me which area to expand. I can iterate the doc.
