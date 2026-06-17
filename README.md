# Prokar Ekspert Audit — Website

Corporate website for **Prokar Ekspert Audit** (ООО «Прокар Эксперт Аудит») — an auditing, accounting, tax, and legal consulting firm in Tashkent, Uzbekistan.

Built with Django 4.2, Tailwind CSS 3, CKEditor, django-modeltranslation (RU/UZ), and django-unfold for the admin panel.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2 (Python 3.10+) |
| Styling | Tailwind CSS 3 via `django-tailwind` |
| Rich Text | CKEditor 4 via `django-ckeditor` |
| Translations | `django-modeltranslation` (RU + UZ) |
| Admin | `django-unfold` |
| Static Files | WhiteNoise (+ nginx in production) |
| Dev DB | SQLite |
| Prod DB | PostgreSQL |

---

## Project Structure

```
prokar-agency-website/
├── prokar_site/          # Django project config (settings, urls, wsgi, middleware)
├── apps/
│   ├── blog/             # Post + Tag models, views, admin, translations
│   └── core/             # Feedback model, home view, context processor
├── theme/                # django-tailwind app (Tailwind source + compiled CSS)
├── templates/            # HTML templates (base, home, blog/list, blog/detail)
├── static/               # Project-level static files (images, etc.)
├── locale/               # i18n .po/.mo files (ru, uz)
├── media/                # Uploaded files (git-ignored)
├── .env.example          # Environment variable template
└── requirements.txt
```

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm** (for Tailwind CSS compilation)
- **gettext** (for compiling translation files) — on macOS: `brew install gettext`

---

## Local Development Setup

### 1. Clone and enter the directory

```bash
git clone <repo-url>
cd prokar-agency-website
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env — the defaults work for local SQLite development.
# SECRET_KEY is already pre-filled for dev; change it for production.
```

Key variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (pre-filled) | Django secret key |
| `DEBUG` | `True` | Enable debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts |
| `USE_SQLITE` | `True` | `True` = SQLite, `False` = PostgreSQL |
| `DB_NAME` / `DB_USER` / … | — | PostgreSQL credentials (used when `USE_SQLITE=False`) |

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (for admin access)

```bash
python manage.py createsuperuser
```

### 7. Compile translation files

```bash
python manage.py compilemessages --locale=ru --locale=uz
```

### 8. Install Tailwind CSS dependencies

```bash
python manage.py tailwind install
```

This runs `npm install` inside `theme/static_src/`.

### 9. Run in two terminals

**Terminal 1 — Django dev server:**
```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 — Tailwind watcher (live CSS rebuild):**
```bash
source venv/bin/activate
python manage.py tailwind start
```

> **Note:** During development the site uses the Tailwind Play CDN automatically (via the `{% if debug %}` block in `base.html`), so Tailwind watching is optional for quick prototyping. The compiled CSS is needed for production.

Open **http://127.0.0.1:8000/** in your browser.  
Admin panel: **http://127.0.0.1:8000/admin/** (always in Russian).

---

## Adding Content

### Creating a Blog Post

1. Go to **Admin → Публикации → + Добавить**
2. Fill in **Заголовок (рус)** — slug is auto-generated from this title
3. Fill in **Заголовок (узб)** — its slug is auto-generated too
4. Write the body in **Содержание (рус)** and **Mazmun (uzb)** using CKEditor
5. Add tags in the **Теги** field as comma-separated names  
   Example: `Налоговое право, IT Park, Аудит` → creates `#налоговое_право`, `#it_park`, `#аудит`
6. Set **Активна** to ✓ to make it visible on the site
7. Save — a preview link appears at the top of the form

### Tag rules

- Tags are normalised on save: lowercased, spaces → underscores
- Tags are get-or-created (entering an existing name reuses it)
- Displayed with `#` prefix: `law` → `#law`

### Post URLs

Both slugs resolve to the same post:
```
/posts/kak-pravilno-vybrat-sistemu-nalogooblozheniya/   ← Russian slug
/posts/soliq-tizimini-qanday-tanlash-kerak/             ← Uzbek slug
```

### Viewing Feedback

Admin → **Обращения клиентов**. All submissions from the footer form appear here. Mark as read with the checkbox in the list view.

---

## Language Switching

The public site supports **Russian** (default) and **Uzbek** via the RU/UZ switcher in the nav bar. Language is stored in the session cookie.

The admin panel is **always in Russian** (enforced by `AdminLocaleMiddleware`).

---

## Production Deployment

### 1. PostgreSQL database

Set `USE_SQLITE=False` in `.env` and fill in the `DB_*` variables.

### 2. Build Tailwind CSS

```bash
python manage.py tailwind build
```

### 3. Collect static files

```bash
python manage.py collectstatic --no-input
```

### 4. Gunicorn

```bash
pip install gunicorn
gunicorn prokar_site.wsgi:application --bind 0.0.0.0:8000
```

### 5. nginx config (example)

```nginx
server {
    listen 80;
    server_name prokar.uz www.prokar.uz;

    location /static/ {
        alias /path/to/prokar-agency-website/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/prokar-agency-website/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

> Static and media files are served by nginx directly. WhiteNoise acts as a fallback in case nginx is not in front.

---

## Useful Management Commands

| Command | Purpose |
|---|---|
| `python manage.py makemigrations` | Create new migrations after model changes |
| `python manage.py migrate` | Apply migrations |
| `python manage.py createsuperuser` | Create admin user |
| `python manage.py compilemessages --locale=ru --locale=uz` | Recompile translations after editing .po files |
| `python manage.py tailwind install` | Install npm packages for Tailwind |
| `python manage.py tailwind start` | Watch & rebuild CSS in development |
| `python manage.py tailwind build` | Build minified CSS for production |
| `python manage.py collectstatic` | Collect all static files for production |

---

## Environment Variables Reference

```dotenv
SECRET_KEY=your-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,prokar.uz

USE_SQLITE=True          # False for production PostgreSQL

DB_NAME=prokar_db
DB_USER=prokar_user
DB_PASSWORD=strong_password
DB_HOST=localhost
DB_PORT=5432
```

---

## License

MIT — see [LICENSE](LICENSE).
