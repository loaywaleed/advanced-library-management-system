from django.contrib import admin

# Register your models here.
from .models import BorrowingRecord

admin.site.register(BorrowingRecord)
