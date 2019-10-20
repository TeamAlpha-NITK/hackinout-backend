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
    video_file_path = models.TextField()


# class Object(models.Model):
#     # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.TextField(primary_key=True)


class FrameObjectData(models.Model):
    video = models.ForeignKey(to=Video, on_delete=models.CASCADE)
    object = models.TextField()
    frame_no = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return "[{} - {}] {}: {}\n".format(self.video.title, self.frame_no, self.object, self.quantity)
