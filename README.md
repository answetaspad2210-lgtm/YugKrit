# YugKrit — "From Problems to Solutions"

YugKrit is a societal innovation and collaboration platform that connects **Government**,
**Universities**, **ULBs/NGOs**, and **Students**. It takes a real-world societal problem,
gets it verified by government, matches it with a university and a student team, tracks the
full solution-development lifecycle (research → design → prototype → testing → community
validation), and — on verified completion — automatically updates every student's permanent
**Innovation Growth Profile** with achievements and certificates.

This is a complete, working Flask application with a real SQLite database, real
authentication, real file uploads, and a real (rule-based) AI recommendation engine. There are
no placeholder pages, no fake buttons, and no "Coming Soon" screens for core features.

---

## 1. Features

- **One shared platform**, four dashboards (Government, University, ULB/NGO, Student), all
  built on the same authentication system, database, and permission model.
- **Full challenge lifecycle**: submission (with map pin + evidence upload) → AI analysis →
  government verification → university assignment/application → project creation.
- **Team Builder** that links students by `institution_id + registration_number` — a student
  is **never** duplicated, no matter how many projects they join.
- **Milestone workflow**: Research → Design → Prototype → Testing → Community Validation →
  Pilot → Implementation → Final Submission, each trackable with status transitions.
- **Achievement engine**: on verified project completion, achievements, skills, impact, and
  certificate eligibility are derived automatically from database relationships — nothing is
  manually copied.
- **Certificate system** with a public, unauthenticated verification page
  (`/verify/certificate/<id>`).
- **Rule-based AI engine** (`services/ai_service.py`) for challenge categorization, priority
  scoring, skill recommendation, similar-challenge detection, and university matching — works
  out of the box with no external API key. A real LLM/API can be swapped in later.
- **RBAC** with roles and permissions stored in the database and enforced via
  `@role_required(...)` / `@permission_required(...)` decorators — no scattered role checks.
- **Audit log** of every significant action (verifications, assignments, milestone changes,
  project completion).
- **In-app notifications**, file uploads with validation, Leaflet + OpenStreetMap for
  location picking and challenge maps, and Chart.js analytics.
- **Fully responsive** — sidebar collapses to a hamburger menu, tables become cards, forms
  stack to a single column, tested at 375 / 390 / 768 / 1024 / 1440 / 1920px.
- **REST API** (`/api/...`) mirroring the server-rendered routes, ready for a future mobile
  app or JS frontend.
- **13 automated tests** covering auth, RBAC, challenge verification, team/duplicate
  prevention, and the milestone → achievement → certificate pipeline.

---

## 2. Technology Stack

| Layer      | Technology                              |
|------------|------------------------------------------|
| Frontend   | HTML5, CSS3 (custom, no default Bootstrap look), Vanilla JavaScript |
| Backend    | Python 3 + Flask                          |
| Database   | SQLite (dev) — structured so PostgreSQL can be swapped in via `DATABASE_URL` |
| ORM        | SQLAlchemy (via Flask-SQLAlchemy)         |
| Templates  | Jinja2                                    |
| Charts     | Chart.js                                  |
| Maps       | Leaflet.js + OpenStreetMap                |
| Icons      | Font Awesome                              |
| CSS Utility| Bootstrap 5 grid concepts only — all visual styling is custom |

---

## 3. Folder Structure

```
YUGKRIT/
├── app.py                     # Application factory + blueprint registration
├── config.py                  # Environment-driven configuration
├── requirements.txt
├── .env.example
│
├── database/
│   ├── database.py            # SQLAlchemy singleton + init_db()
│   ├── models.py               # All ~35 models (Users, Challenges, Projects, ...)
│   ├── seed.py                 # Roles/permissions + full demo workflow seeder
│   └── schema.sql              # Reference DDL (auto-generated from models)
│
├── routes/                     # One blueprint per area — thin, delegate to services/
│   ├── public_routes.py
│   ├── auth_routes.py
│   ├── government_routes.py
│   ├── university_routes.py
│   ├── ulb_routes.py
│   ├── student_routes.py
│   ├── certificate_routes.py   # public certificate verification
│   ├── notification_routes.py
│   └── api_routes.py           # JSON REST API
│
├── services/                   # All business logic lives here
│   ├── auth_service.py
│   ├── challenge_service.py
│   ├── project_service.py
│   ├── student_service.py      # the critical dedup logic
│   ├── verification_service.py
│   ├── achievement_service.py
│   ├── certificate_service.py
│   ├── notification_service.py
│   ├── ai_service.py           # rule-based mock AI engine
│   └── audit_service.py
│
├── utils/
│   ├── validators.py
│   ├── decorators.py           # @login_required, @role_required, @permission_required
│   ├── helpers.py              # file upload, code generation, API response helpers
│   └── permissions.py          # single source of truth: ROLE -> [permissions]
│
├── templates/
│   ├── base.html                # public site layout
│   ├── shared/                  # dashboard_base.html, sidebars, navbar, footer, errors
│   ├── public/, auth/
│   ├── government/, university/, ulb/, student/
│
├── static/
│   ├── css/  (main.css, dashboard.css, components.css, responsive.css)
│   ├── js/   (main.js, auth.js, dashboard.js, challenges.js, projects.js,
│   │          students.js, notifications.js, charts.js, maps.js)
│   ├── images/
│   └── uploads/                 # created at runtime for uploaded files
│
└── tests/
    ├── conftest.py               # isolated per-test SQLite DB fixture
    ├── test_auth.py
    ├── test_permissions.py
    ├── test_challenges.py
    ├── test_projects.py
    └── test_students.py
```

---

## 4. Installation & Setup

### 4.1 Prerequisites
- Python 3.10+
- pip

### 4.2 Steps

```bash
# 1. Clone / unzip the project, then enter the folder
cd yugkrit

# 2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables
cp .env.example .env
# Edit .env and set a real SECRET_KEY for anything beyond local dev

# 5. Seed the database (creates tables + demo accounts + demo workflow)
python database/seed.py

# 6. Run the application
python app.py
```

The app will be available at **http://127.0.0.1:5000**.

### 4.3 Resetting the database
Delete `yugkrit.db` and re-run `python database/seed.py`.

### 4.4 Moving to PostgreSQL later
Set `DATABASE_URL` in `.env` to a PostgreSQL connection string, e.g.:
```
DATABASE_URL=postgresql://user:password@localhost:5432/yugkrit
```
No model code changes are needed — SQLAlchemy handles the dialect difference.

---

## 5. Demo Accounts (development only)

Seeded by `database/seed.py`. Password for all accounts: **`Demo@123`**

| Role        | Email                       |
|-------------|------------------------------|
| Government  | gov@yugkrit.local             |
| University  | university@yugkrit.local      |
| Faculty     | faculty@yugkrit.local          |
| ULB         | ulb@yugkrit.local              |
| Student     | student@college.local          |

The seed script also creates the full demo workflow from the spec: **"Urban Park Renovation
and Smart Monitoring"** (Lucknow, HIGH priority, 2,400 affected) → verified by government →
assigned to ABC University → project **"Smart Park Monitoring"** created → 5-student team
("Team Parkwatch") added by registration number → Research/Design/Prototype milestones marked
complete, Testing in progress. Advance the remaining milestones from the University dashboard
to see achievements and certificates generate automatically.

---

## 6. Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

Each test gets its own isolated, temporary SQLite database (see `tests/conftest.py`), so tests
never interfere with each other or with your local `yugkrit.db`.

---

## 7. Key Database Relationships (plain language)

- **A student is unique per (institution, registration number).** `StudentProfile` has a
  database-level unique constraint on `(institution_id, registration_number)`. The *only*
  correct way to attach a student to a team is
  `services/student_service.find_or_invite_student(...)` — it looks the student up first and
  only creates a new (INVITED) profile if truly not found. This is exercised by
  `tests/test_students.py` and `tests/test_projects.py`.
- **Challenge → Project → Team → Student** is the core chain: a `Challenge` (submitted by a
  ULB/NGO, verified by Government) is assigned to a `University`, which creates a `Project`,
  which has one or more `ProjectTeam`s, each with `ProjectTeamMember`s pointing at a
  `StudentProfile`.
- **Project → Milestones → Achievements → Certificates → Growth Profile**: when every
  `Milestone` on a `Project` reaches `COMPLETED`, `project_service.complete_project()` fires
  `achievement_service.generate_achievements_for_project()`, which walks
  `Project → ProjectTeam → ProjectTeamMember → StudentProfile` and creates
  `StudentAchievement` + `Certificate` rows for every team member. The Growth Profile
  (`services/student_service.get_growth_profile`) is **always computed live** from these
  relationships — nothing is duplicated or cached.

---

## 8. API Endpoints (selected)

All responses follow `{"success": true, "data": ...}` or
`{"success": false, "error": {"code": ..., "message": ...}}`.

```
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/register

GET    /api/challenges
GET    /api/challenges/<id>
POST   /api/challenges                       (ULB/NGO)
POST   /api/challenges/<id>/verify           (Government)
POST   /api/challenges/<id>/assign           (Government)

GET    /api/universities
GET    /api/ulbs
GET    /api/students/<id>

GET    /api/projects
GET    /api/projects/<id>
POST   /api/milestones/<id>/submit           (Student)
POST   /api/milestones/<id>/approve          (Faculty / University Admin)

GET    /api/achievements/<student_id>
GET    /api/certificates/<certificate_id>
GET    /api/certificates/<certificate_id>/verify

GET    /api/notifications
POST   /api/notifications/<id>/read

GET    /api/analytics
GET    /api/audit
```

---

## 9. Adding a New Dashboard (e.g. Industry, Citizen, Mentor)

The platform was built specifically so this does **not** require touching existing dashboards:

1. **Add the role & permissions** in `utils/permissions.py`:
   ```python
   ROLE_PERMISSIONS["INDUSTRY_ADMIN"] = ["challenge.view", "project.view", ...]
   ROLE_DASHBOARD["INDUSTRY_ADMIN"] = "industry.overview"
   ```
   Re-run `python database/seed.py` to create the role in the database.

2. **Create the blueprint**: `routes/industry_routes.py`
   ```python
   industry_bp = Blueprint("industry", __name__, template_folder="../templates/industry")

   @industry_bp.route("/")
   @role_required("INDUSTRY_ADMIN")
   def overview():
       return render_template("industry/overview.html")
   ```
   Register it in `app.py`:
   ```python
   from routes.industry_routes import industry_bp
   app.register_blueprint(industry_bp, url_prefix="/dashboard/industry")
   ```

3. **Create the templates**: `templates/industry/_base.html` (extends
   `shared/dashboard_base.html`, overrides the `sidebar_menu` block) and
   `templates/industry/overview.html` (extends `industry/_base.html`).

4. **Add static assets** if needed: `static/js/industry.js`, extra CSS rules.

No existing model, route, or template needs to change — `User.role_id` and
`User.organization_id` already generalize to any future role/org type.

## 10. Adding a New Role to an Existing Dashboard
Add the role to `ROLE_PERMISSIONS` in `utils/permissions.py`, add it to the relevant
`@role_required(...)` calls, and re-seed. No schema change is required — `Role` and
`Permission` are already data-driven tables.

## 11. Adding a New Feature (e.g. Messaging thread UI)
The `Message` model already exists in `database/models.py`. To surface it: add a service
function in `services/`, a route in the relevant blueprint, and a template. Follow the
pattern used by Notifications (`services/notification_service.py` →
`routes/notification_routes.py` → `templates/shared/notifications.html`).

---

## 12. Configuration Reference

All configuration lives in `.env` (see `.env.example`):

| Variable       | Purpose                                              |
|----------------|-------------------------------------------------------|
| `SECRET_KEY`   | Flask session signing key — set a real random value in production |
| `DATABASE_URL` | SQLAlchemy connection string (SQLite by default, PostgreSQL-ready) |
| `FLASK_DEBUG`  | `1` for local development, `0` in production          |
| `AI_API_KEY`   | Optional — leave blank to use the built-in rule-based AI engine |

## 13. File Upload Setup
Uploaded files are stored under `static/uploads/<category>/` with randomized filenames
(`secure_filename` + UUID) to prevent path traversal and collisions. Allowed extensions are
configured in `config.py` (`ALLOWED_EXTENSIONS`) and enforced server-side in
`utils/helpers.save_uploaded_file()`. Max upload size is 10MB (`MAX_CONTENT_LENGTH`).

## 14. Troubleshooting

- **`sqlite3.OperationalError: no such table`** — run `python database/seed.py` to create and
  seed the database.
- **Login fails for demo accounts** — re-run the seed script; it's idempotent and safe to
  run multiple times.
- **File upload rejected** — check the extension is in `ALLOWED_EXTENSIONS` in `config.py`
  and the file is under 10MB.
- **Port already in use** — change the port in the `app.run(...)` call at the bottom of
  `app.py`, or stop the process using port 5000.
- **Want to inspect the schema** — see `database/schema.sql` (auto-generated reference DDL)
  or open `yugkrit.db` with any SQLite browser.

---

## 15. Security Notes

- Passwords are hashed with Werkzeug's `generate_password_hash` (never stored in plain text).
- Sessions are signed, HTTP-only, `SameSite=Lax` cookies.
- All role/permission checks go through `utils/decorators.py` — never scattered inline.
- File uploads are validated by extension, given randomized names, and size-limited.
- No secrets are hardcoded — everything sensitive is read from `.env` (which is gitignored;
  only `.env.example` is committed).
- User-facing errors never expose Python stack traces (`app.py` registers 404/403/500
  handlers that render a clean error page).

---

## 16. Demo Accounts Are Development-Only

The five seeded accounts (`gov@yugkrit.local`, `university@yugkrit.local`,
`faculty@yugkrit.local`, `ulb@yugkrit.local`, `student@college.local`) are clearly for local
demonstration and evaluation only. Do not seed these into a production database.
