from django.db import models
from django.contrib.auth import get_user_model

_USER = get_user_model()


class BaseModel(models.Model):
    """Our base model that includes timestamp

    Attributes:
        created_date    The date this row was first created
        modified_date   The date this row was last modified

    """

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Tag(BaseModel):
    title = models.CharField(max_length=150)

class Note(BaseModel):
    """### The notes are plain text and should contain:

        * Title
        * Body
        * Tags

    """
    title = models.CharField(max_length=150)
    body = models.CharField(max_length=500)
    private = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="notes")
    created_by = models.ForeignKey(
        _USER,
        on_delete=models.CASCADE,
        related_name="notes_created_by",
    )
