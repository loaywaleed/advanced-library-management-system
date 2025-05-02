from django.contrib import admin
from .models import (
    Book,
    Author,
    Category,
    Library,
)

admin.site.register(Library)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Category)
