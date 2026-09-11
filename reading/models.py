from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=120)
    timezone = models.CharField(max_length=64, default="UTC")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    page_count = models.PositiveIntegerField()

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class ReadingSession(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="sessions"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="sessions")
    started_at = models.DateTimeField()
    minutes = models.PositiveIntegerField()

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.student} / {self.book} @ {self.started_at:%Y-%m-%d %H:%M}"
