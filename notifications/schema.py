import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from users.models import Profile, User
from .models import FollowRequest, FollowRequestStatus
from .views import send_follow_request, accept_follow_request, reject_follow_request

# Funciones auxiliares para eliminar la relación de seguimiento


def unfollow_user(from_user, to_user):
    """
    Permite que 'from_user' deje de seguir a 'to_user'.
    Se elimina la relación mutua en los perfiles.
    """
    from_profile = from_user.profile
    to_profile = to_user.profile
    # Se elimina de ambos lados
    from_profile.followers.remove(to_profile)
    to_profile.followers.remove(from_profile)
    return True


def remove_follower(user, follower):
    """
    Permite que 'user' elimine a 'follower' de sus seguidores.
    Se elimina la relación de seguimiento de forma mutua.
    """
    user_profile = user.profile
    follower_profile = follower.profile
    user_profile.followers.remove(follower_profile)
    follower_profile.followers.remove(user_profile)
    return True


# Tipo GraphQL para FollowRequest
class FollowRequestType(DjangoObjectType):
    class Meta:
        model = FollowRequest
        fields = (
            "request_id",
            "from_user",
            "to_user",
            "status",
            "created_at",
            "updated_at",
        )


# Mutación para enviar una solicitud de seguimiento
class SendFollowRequestMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    follow_request = graphene.Field(FollowRequestType)
    ok = graphene.Boolean()

    def mutate(self, info, username):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(
                "Se requiere autenticación para enviar solicitudes de seguimiento."
            )

        try:
            to_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Exception("El usuario destino no existe.")

        follow_request = send_follow_request(user, to_user)
        if not follow_request:
            raise Exception(
                "Ya existe una solicitud de seguimiento entre estos usuarios."
            )

        return SendFollowRequestMutation(follow_request=follow_request, ok=True)


# Mutación para aceptar una solicitud de seguimiento
class AcceptFollowRequestMutation(graphene.Mutation):
    class Arguments:
        request_id = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, request_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Se requiere autenticación para aceptar solicitudes.")

        try:
            follow_request = FollowRequest.objects.get(request_id=request_id)
        except FollowRequest.DoesNotExist:
            raise Exception("La solicitud de seguimiento no existe.")

        # Solo el usuario destino puede aceptar la solicitud
        if follow_request.to_user != user:
            raise Exception("No estás autorizado para aceptar esta solicitud.")

        success = accept_follow_request(follow_request)
        if not success:
            raise Exception("La solicitud ya no está pendiente o no puede aceptarse.")

        return AcceptFollowRequestMutation(ok=True)


# Mutación para rechazar una solicitud de seguimiento
class RejectFollowRequestMutation(graphene.Mutation):
    class Arguments:
        request_id = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, request_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Se requiere autenticación para rechazar solicitudes.")

        try:
            follow_request = FollowRequest.objects.get(request_id=request_id)
        except FollowRequest.DoesNotExist:
            raise Exception("La solicitud de seguimiento no existe.")

        # Solo el usuario destino puede rechazar la solicitud
        if follow_request.to_user != user:
            raise Exception("No estás autorizado para rechazar esta solicitud.")

        success = reject_follow_request(follow_request)
        if not success:
            raise Exception("La solicitud ya no está pendiente o no puede rechazarse.")

        return RejectFollowRequestMutation(ok=True)


# Mutación para dejar de seguir a un usuario (unfollow)
class UnfollowUserMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, username):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(
                "Se requiere autenticación para dejar de seguir a un usuario."
            )

        try:
            to_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Exception("El usuario objetivo no existe.")

        # Verificar que el usuario autenticado realmente sigue al usuario destino.
        if to_user.profile not in user.profile.followers.all():
            raise Exception("No sigues a este usuario.")

        unfollow_user(user, to_user)
        return UnfollowUserMutation(ok=True)


# Mutación para eliminar un seguidor
class RemoveFollowerMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, username):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Se requiere autenticación para eliminar un seguidor.")

        try:
            follower = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Exception("El usuario seguidor no existe.")

        # Verificar que efectivamente el usuario es seguido por 'follower'
        if user.profile not in follower.profile.followers.all():
            raise Exception("Este usuario no es tu seguidor.")

        remove_follower(user, follower)
        return RemoveFollowerMutation(ok=True)


# Definición de Query para obtener solicitudes de seguimiento
class Query(graphene.ObjectType):
    follow_requests_received = graphene.List(FollowRequestType)
    follow_requests_sent = graphene.List(FollowRequestType)

    def resolve_follow_requests_received(self, info):
        user = info.context.user
        if user.is_anonymous:
            return FollowRequest.objects.none()
        return FollowRequest.objects.filter(to_user=user)

    def resolve_follow_requests_sent(self, info):
        user = info.context.user
        if user.is_anonymous:
            return FollowRequest.objects.none()
        return FollowRequest.objects.filter(from_user=user)


# Definición de todas las mutaciones en el schema
class Mutation(graphene.ObjectType):
    send_follow_request = SendFollowRequestMutation.Field()
    accept_follow_request = AcceptFollowRequestMutation.Field()
    reject_follow_request = RejectFollowRequestMutation.Field()
    unfollow_user = UnfollowUserMutation.Field()
    remove_follower = RemoveFollowerMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
