from django.db import models
import uuid


class Video(models.Model):

    CATEGORY_CHOICES = [
        ('Sports', 'Sports'),
        ('Kids', 'Kids'),
        ('News', 'News'),
        ('Politics', 'Politics'),
        ('Music', 'Music'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()
    description = models.TextField()
    category = models.TextField(choices=CATEGORY_CHOICES)

class Objects(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()

