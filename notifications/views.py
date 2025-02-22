from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from users.models import User, Profile
from .models import FollowRequest, FollowRequestStatus, Notification, NotificationType


# Create your views here.
# Función para enviar una solicitud de seguimiento
def send_follow_request(from_user, to_user):
    # Verifica si ya existe una solicitud entre estos usuarios
    if FollowRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        return None  # Ya existe una solicitud
    follow_request = FollowRequest.objects.create(from_user=from_user, to_user=to_user)

    # Opcional: Crear una notificación informando de la solicitud
    Notification.objects.create(
        sender=from_user,
        recipient=to_user,
        notification_type=NotificationType.NEW_FOLLOW,
        # Puedes usar extra_data para almacenar el estado inicial de la solicitud
        extra_data={"status": FollowRequestStatus.PENDING},
    )
    return follow_request


# Función para aceptar una solicitud de seguimiento
def accept_follow_request(follow_request):
    if follow_request.status == FollowRequestStatus.PENDING:
        follow_request.status = FollowRequestStatus.ACCEPTED
        follow_request.save()

        # Agregar ambos usuarios como seguidores mutuamente
        from_user_profile = follow_request.from_user.profile
        to_user_profile = follow_request.to_user.profile
        from_user_profile.followers.add(to_user_profile)
        to_user_profile.followers.add(from_user_profile)
        return True
    return False


# Función para rechazar una solicitud de seguimiento
def reject_follow_request(follow_request):
    if follow_request.status == FollowRequestStatus.PENDING:
        follow_request.status = FollowRequestStatus.REJECTED
        follow_request.save()
        return True
    return False
