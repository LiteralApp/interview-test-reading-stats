import pytest

pytestmark = pytest.mark.django_db


def test_book_list_returns_every_seeded_book(client, seeded):
    """The books endpoint lists all books."""
    response = client.get("/api/books/")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_book_list_filters_by_id_in(client, seeded):
    """The id__in filter narrows the list to the given ids."""
    first, second = [book["id"] for book in client.get("/api/books/").json()[:2]]

    response = client.get(f"/api/books/?id__in={first},{second}")

    assert response.status_code == 200
    assert {book["id"] for book in response.json()} == {first, second}
