"""Contract tests for the endpoint you are asked to build.

These fail until the endpoint exists. Do not change the assertions in
`test_stats_response_shape` or `test_stats_stays_within_query_budget` --
they are the contract. Add as many tests of your own as you like.
"""

import pytest

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
