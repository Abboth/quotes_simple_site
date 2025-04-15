from aiohttp import request
from django.db import models
from django.contrib.auth import get_user_model


class Author(models.Model):
    name = models.CharField(max_length=80)
    born_date = models.CharField(max_length=50)
    born_location = models.CharField(max_length=255)
    description = models.TextField()

    created_by_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='authors_created'
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    visit_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Quote(models.Model):
    quote = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    created_by_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='quotes_created'
    )

    def __str__(self):
        return self.quote[:50]


class CreateQuote(models.Model):
    quote = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_by_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )


class CreateAuthor(models.Model):
    name = models.CharField(max_length=80)
    born_date = models.CharField(max_length=50)
    born_location = models.CharField(max_length=255)
    description = models.TextField()
    created_by_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
