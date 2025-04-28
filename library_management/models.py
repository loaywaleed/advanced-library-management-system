from django.db import models


class Library(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name
