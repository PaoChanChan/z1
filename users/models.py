from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
import shortuuid


# Modelo de usuario personalizado que extiende de AbstractUser
class User(AbstractUser):

    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)

    # Configuración de autenticación
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


# Modelo de perfil asociado a un usuario
class Profile(models.Model):

    profile_id = ShortUUIDField(
        length=6, max_length=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789"
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, null=True, blank=True)

    # Relaciones ManyToMany para seguidores y seguidos
    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:2]
            self.slug = slugify(f"{self.full_name}-{uniqueid.lower()}")
        super(Profile, self).save(*args, **kwargs)


"""Funciones para crear y guardar un perfil asociado a un usuario
de forma automática al detectar creación de usuario"""


def create_user_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):

    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
