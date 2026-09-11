import pytest
from django.core.management import call_command

from reading.models import Student


@pytest.fixture
def seeded(db):
    call_command("seed")


@pytest.fixture
def ana(seeded):
    return Student.objects.get(name="Ana")


@pytest.fixture
def eve(seeded):
    return Student.objects.get(name="Eve")
