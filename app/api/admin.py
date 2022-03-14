from django.contrib import admin
from api.models import Note, Tag


# Register your models here.

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("title", "created_date")

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "private", "modified_date")
