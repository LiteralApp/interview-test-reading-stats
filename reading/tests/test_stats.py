"""Contract tests for the endpoint you are asked to build.

These fail until the endpoint exists. Do not change the assertions in
`test_stats_response_shape` or `test_stats_stays_within_query_budget` --
they are the contract. Add as many tests of your own as you like.
"""

import pytest

from reading.models import Student

pytestmark = pytest.mark.django_db


def test_stats_response_shape(client, ana):
    """The stats endpoint returns the agreed keys for a student who has read."""
    response = client.get(f"/api/students/{ana.pk}/stats/")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "student_id",
        "total_minutes",
        "current_streak",
        "longest_streak",
        "books",
    }
    assert payload["student_id"] == ana.pk
    assert isinstance(payload["books"], list)
    assert set(payload["books"][0]) == {"book_id", "title", "minutes", "session_count"}


def test_stats_handles_a_student_who_has_never_read(client, eve):
    """A student with no sessions gets zeroes and an empty book list."""
    response = client.get(f"/api/students/{eve.pk}/stats/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_minutes"] == 0
    assert payload["current_streak"] == 0
    assert payload["longest_streak"] == 0
    assert payload["books"] == []


def test_stats_stays_within_query_budget(client, ana, django_assert_max_num_queries):
    """The endpoint answers in at most four queries, whatever the data size."""
    with django_assert_max_num_queries(4):
        client.get(f"/api/students/{ana.pk}/stats/")


def test_stats_can_filter_by_book_id(client, ana):
    holes_session = ana.sessions.filter(book__title="Holes").first()
    holes = holes_session.book

    response = client.get(
        f"/api/students/{ana.pk}/stats/?book_id__in={holes.pk}"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total_minutes"] == 75
    assert len(payload["books"]) == 1
    assert payload["books"][0]["book_id"] == holes.pk
    assert payload["books"][0]["title"] == "Holes"
    assert payload["books"][0]["minutes"] == 75
    assert payload["books"][0]["session_count"] == 3


def test_stats_calculates_current_and_longest_streak(client, ana):
    response = client.get(f"/api/students/{ana.pk}/stats/")

    assert response.status_code == 200

    payload = response.json()

    assert payload["current_streak"] == 5
    assert payload["longest_streak"] == 5


def test_stats_tracks_longest_streak_separately_from_current(client, seeded):
    ben = Student.objects.get(name="Ben")

    response = client.get(f"/api/students/{ben.pk}/stats/")

    assert response.status_code == 200

    payload = response.json()

    assert payload["current_streak"] == 2
    assert payload["longest_streak"] == 4


def test_stats_counts_multiple_sessions_on_same_day_once(client, seeded):
    dai = Student.objects.get(name="Dai")

    response = client.get(f"/api/students/{dai.pk}/stats/")

    assert response.status_code == 200

    payload = response.json()

    assert payload["current_streak"] == 2
    assert payload["longest_streak"] == 2


def test_stats_returns_404_for_unknown_student(client):
    response = client.get("/api/students/999999/stats/")

    assert response.status_code == 404


def test_stats_filter_applies_to_streaks(client, ana):
    holes_session = ana.sessions.filter(book__title="Holes").first()
    holes = holes_session.book

    response = client.get(
        f"/api/students/{ana.pk}/stats/?book_id__in={holes.pk}"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["current_streak"] == 1
    assert payload["longest_streak"] == 1
