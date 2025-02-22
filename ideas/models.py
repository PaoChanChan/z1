from django.db import models
from users.models import Profile, User
from django.utils.text import slugify
import shortuuid
from shortuuid.django_fields import ShortUUIDField


VISIBILITY = (
    ("Private", "Private"),
    ("Public", "Public"),
    ("Friends", "Friends"),
    ("Followers", "Followers"),
)


class Idea(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    visibility = models.CharField(max_length=10, choices=VISIBILITY, default="Public")
    idea_id = ShortUUIDField(
        length=6, max_length=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789"
    )
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    dislikes = models.ManyToManyField(User, related_name="dislikes", blank=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.user.username

    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(f"{self.title}-{uniqueid.lower()}")

        super(Idea, self).save(*args, **kwargs)

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def dislikes_count(self):
        return self.dislikes.count()
