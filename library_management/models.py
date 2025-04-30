from django.db import models
from django.contrib.gis.db import models as gis_models


class Library(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    location = gis_models.PointField(geography=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Libraries"


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey("Author", on_delete=models.CASCADE, related_name="books")
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name="books")
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, related_name="books"
    )
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()

    @classmethod
    def get_filtered_authors(cls, filters=None):
        filter_conditions = {}
        if filters:
            if "library" in filters:
                filter_conditions["books__library__name__icontains"] = filters[
                    "library"
                ]
            if "category" in filters:
                filter_conditions["books__category__name__icontains"] = filters[
                    "category"
                ]

        return cls.objects.annotate(
            book_count=models.Count(
                "books", filter=models.Q(**filter_conditions), distinct=True
            )
        )

    @classmethod
    def get_authors_with_books(cls, filters=None):
        """
        Get authors with prefetched books and categories, optionally filtered
        """
        queryset = cls.objects.prefetch_related(
            models.Prefetch(
                "books", queryset=Book.objects.select_related("category", "library")
            )
        )

        if filters:
            if "library" in filters:
                queryset = queryset.filter(
                    books__library__name__icontains=filters["library"]
                )
            if "category" in filters:
                queryset = queryset.filter(
                    books__category__name__icontains=filters["category"]
                )

        return queryset.distinct().annotate(
            book_count=models.Count("books", distinct=True)
        )

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
