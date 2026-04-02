# Job Hunt Dashboard

A secure, visually interactive job search and application-tracking dashboard.  
Aggregates live listings from **RemoteOK · The Muse · Arbeitnow · Adzuna · HackerNews**,
with a built-in curated fallback dataset so results always appear even without API keys.

---

## Features

| Feature | Detail |
|---|---|
| Multi-source search | 5 platforms queried in parallel per search |
| Server-side cache | Identical queries served instantly (5-min TTL, no re-fetch) |
| Single bootstrap call | UI seeds sources + stats in **one** HTTP request on load |
| Kanban pipeline | Track saved → applied → interviewing → offer → rejected |
| Resume manager | Upload PDF/DOCX/DOC/TXT, set active, download |
| Secure by default | CSRF, input sanitisation, parameterised SQL, UUID filenames |

---

## Quick Start (local, no Docker)

### 1. Prerequisites
- Python 3.11+
- pip

### 2. Clone and enter the project

```bash
git clone https://github.com/Vamshi213/MyProjects.git
cd MyProjects/job_dashboard
```

### 3. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment (optional)

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY plus optional API keys (see below)
```

### 6. Run the development server

```bash
python run.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Deploy with Docker (recommended for production)

### 1. Prerequisites
- Docker 24+
- Docker Compose v2

### 2. Clone and enter

```bash
git clone https://github.com/Vamshi213/MyProjects.git
cd MyProjects/job_dashboard
```

### 3. Set your secret key

```bash
cp .env.example .env
# Set SECRET_KEY to a long random string, e.g.:
#   SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### 4. Build and start

```bash
docker compose up --build -d
```

Open **http://localhost:5000**.

### 5. Stop

```bash
docker compose down
```

Data (SQLite DB + uploaded resumes) is persisted in `./instance/` and `./static/uploads/`
via Docker volumes — survives container restarts.

---

## Optional: Live API Keys

The dashboard works out of the box with the curated demo dataset.  
To get **live** job postings, add keys to your `.env`:

| Variable | Where to get it |
|---|---|
| `ADZUNA_APP_ID` + `ADZUNA_API_KEY` | https://developer.adzuna.com (free) |

RemoteOK, The Muse, Arbeitnow, and HackerNews need **no keys**.

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/bootstrap` | **One-shot**: sources + stats + active resume |
| `GET` | `/api/jobs/search?q=<role>&location=<loc>` | Search all sources (cached 5 min) |
| `POST` | `/api/jobs/save` | Save a job |
| `GET` | `/api/jobs/saved` | List saved jobs |
| `PATCH` | `/api/jobs/saved/<id>` | Update status / notes |
| `DELETE` | `/api/jobs/saved/<id>` | Remove saved job |
| `POST` | `/api/resumes/upload` | Upload resume (multipart) |
| `GET` | `/api/resumes` | List resumes |
| `PATCH` | `/api/resumes/<id>/activate` | Set active resume |
| `GET` | `/api/resumes/<id>/download` | Download resume file |
| `DELETE` | `/api/resumes/<id>` | Delete resume |

---

## Project Structure

```
job_dashboard/
├── app.py                  # Flask app, all routes, search cache
├── config.py               # Config (reads .env)
├── models.py               # SQLAlchemy models (Resume, SavedJob, SearchHistory)
├── run.py                  # Dev server entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── job_sources/
│   ├── base.py             # BaseJobSource + normalize()
│   ├── remoteok.py
│   ├── themuse.py
│   ├── arbeitnow.py
│   ├── adzuna.py
│   ├── hackernews.py
│   └── demo_data.py        # 40-job curated fallback dataset
├── static/
│   ├── css/dashboard.css
│   └── js/dashboard.js     # Single-page app logic
└── templates/
    └── index.html
```
