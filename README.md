# Reading Stats — take-home exercise

Small Django/DRF exercise. **Hard cap: 3 hours.** If you run out of time, stop and
write down what you would have done next — an honest, unfinished submission scores
better than a rushed complete one.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed
.venv/bin/python -m pytest
```

SQLite is used by default. If you would rather run Postgres (same engine we use in
production), `docker compose up -d db` and set `POSTGRES_HOST=localhost` before
running the commands above.

Right now 3 tests pass and 2 fail. The failing ones describe the endpoint you are
about to build.

## What is here

- `reading/models.py` — `Student`, `Book`, `ReadingSession`
- `reading/views.py`, `filters.py`, `serializers.py`, `urls.py` — a working
  `GET /api/books/` endpoint. It is the reference for how we write things; follow
  the same shape.
- `reading/management/commands/seed.py` — the sample data
- `reading/tests/` — the existing tests

## The task

Build `GET /api/students/<student_id>/stats/`, returning:

```json
{
  "student_id": 1,
  "total_minutes": 125,
  "current_streak": 5,
  "longest_streak": 5,
  "books": [
    {"book_id": 2, "title": "Holes", "minutes": 75, "session_count": 3}
  ]
}
```

- `total_minutes` — every minute the student has read
- `current_streak` — how many days in a row, up to now, the student has read
- `longest_streak` — the longest such run ever
- `books` — one entry per book the student has read, biggest `minutes` first

Requirements:

1. Use DRF and `django-filter`, matching the patterns already in the app.
2. Support `?book_id__in=1,2,3` to restrict the whole response to those books.
3. **Query budget: at most 4 database queries per request**, no matter how many
   sessions or books a student has. There is a test for this.
4. Write tests for the behaviour you build.
5. Unknown student id returns 404.

## Deliverable

A branch (or a zip) with your commits, plus a short note in `NOTES.md` covering:

- anything about the spec you had to decide for yourself, and what you decided
- what you would do next with more time
- anything you are unhappy with

We will read `NOTES.md` before we read the code.

## How we score it

Correctness, query count, test quality, and how you handled whatever was unclear.
We care much more about your reasoning than about polish.
