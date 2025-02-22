from django.core.exceptions import ObjectDoesNotExist
from .models import FollowRequest, FollowRequestStatus


def send_follow_request(from_user, to_user):
    """
    Envía una solicitud de seguimiento de 'from_user' a 'to_user'.

    Retorna la instancia de FollowRequest creada o None si ya existe alguna solicitud entre estos usuarios.
    """
    # Verificar si ya existe una solicitud (pendiente o procesada)
    existing_request = FollowRequest.objects.filter(
        from_user=from_user, to_user=to_user
    ).first()
    if existing_request:
        return None  # O bien, podrías actualizarla o lanzar una excepción

    follow_request = FollowRequest.objects.create(from_user=from_user, to_user=to_user)
    return follow_request


def accept_follow_request(follow_request):
    """
    Acepta la solicitud de seguimiento si está pendiente.

    Actualiza el estado a 'accepted' y establece la relación de seguidores entre ambos usuarios.
    En este ejemplo, se establecen seguidores mutuos: cada perfil se añade a la lista 'followers'
    del otro.

    Retorna True si la solicitud se acepta correctamente o False si no estaba pendiente.
    """
    if follow_request.status != FollowRequestStatus.PENDING:
        return False

    follow_request.status = FollowRequestStatus.ACCEPTED
    follow_request.save()

    # Obtener los perfiles asociados a los usuarios
    from_profile = follow_request.from_user.profile
    to_profile = follow_request.to_user.profile

    # Establecer seguidores mutuos
    from_profile.followers.add(to_profile)
    to_profile.followers.add(from_profile)

    return True


def reject_follow_request(follow_request):
    """
    Rechaza la solicitud de seguimiento si está pendiente.

    Actualiza el estado a 'rejected' y no modifica las relaciones de seguidores.

    Retorna True si la solicitud se rechaza correctamente o False si no estaba pendiente.
    """
    if follow_request.status != FollowRequestStatus.PENDING:
        return False

    follow_request.status = FollowRequestStatus.REJECTED
    follow_request.save()

    return True
