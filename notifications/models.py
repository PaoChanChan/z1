from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from users.models import User
from shortuuid.django_fields import ShortUUIDField


class FollowRequestStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Rejected")


class FollowRequest(models.Model):
    request_id = ShortUUIDField(
        length=6, max_length=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789"
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="follow_requests_sent",
        on_delete=models.CASCADE,
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="follow_requests_received",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20,
        choices=FollowRequestStatus.choices,
        default=FollowRequestStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("from_user", "to_user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Solicitud de {self.from_user} a {self.to_user} - {self.status}"
