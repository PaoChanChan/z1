import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.models import User
from users.models import Profile

User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "full_name", "username", "email")


class ProfileType(DjangoObjectType):

    followers_count = graphene.Int()
    following_count = graphene.Int()

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "full_name",
            "bio",
            "country",
            "city",
            "created_at",
            "verified",
            "slug",
        )

    def resolve_followers_count(self, info):
        return self.followers.count()

    def resolve_following_count(self, info):
        return self.following.count()


class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    errors = graphene.String()

    class Arguments:
        full_name = graphene.String(required=True)
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, full_name, username, email, password):
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return RegisterUser(success=False, errors="Email ya registrado")

        user = User(full_name=full_name, username=username, email=email)
        user.set_password(password)
        user.save()

        profile = Profile.objects.create(user=user, full_name=full_name)
        profile.save()

        return RegisterUser(user=user, success=True)


class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    errors = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = authenticate(email=email, password=password)
        if user is not None:
            login(info.context, user)
            return LoginUser(user=user, success=True)
        else:
            return LoginUser(success=False, errors="Contraseña o usuario incorrectos")


class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()

    def mutate(self, info):
        logout(info.context)
        return LogoutUser(success=True)


class ChangePassword(graphene.Mutation):
    success = graphene.Boolean()
    errors = graphene.String()

    class Arguments:
        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    def mutate(self, info, old_password, new_password):
        user = info.context.user
        if user.is_anonymous:
            return ChangePassword(
                success=False,
                errors="Debe estar autenticado para cambiar la contraseña",
            )

        if not user.check_password(old_password):
            return ChangePassword(success=False, errors="Contraseña actual incorrecta")

        user.set_password(new_password)
        user.save()
        return ChangePassword(success=True)


class FollowUser(graphene.Mutation):
    success = graphene.Boolean()
    errors = graphene.String()
    target_profile = graphene.Field(ProfileType)

    class Arguments:
        username = graphene.String(required=True)

    def mutate(self, info, username):
        user = info.context.user
        if user.is_anonymous:
            return FollowUser(
                success=False,
                errors="Debe estar autenticado para seguir a otros usuarios",
            )

        # Se asume que cada usuario tiene un perfil asociado accesible desde user.profile
        try:
            follower_profile = user.profile
        except Profile.DoesNotExist:
            return FollowUser(success=False, errors="No se encontró tu perfil")

        try:
            target_profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return FollowUser(success=False, errors="El usuario a seguir no existe")

        if follower_profile == target_profile:
            return FollowUser(success=False, errors="No puedes seguirte a ti mismo")

        if follower_profile in target_profile.followers.all():
            return FollowUser(success=False, errors="Ya sigues a este usuario")

        target_profile.followers.add(follower_profile)
        return FollowUser(success=True, target_profile=target_profile)


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()
    logout_user = LogoutUser.Field()
    change_password = ChangePassword.Field()
    follow_user = FollowUser.Field()


class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    all_profiles = graphene.List(ProfileType)
    verified_profiles = graphene.List(ProfileType)
    my_followers = graphene.List(ProfileType)
    my_following = graphene.List(ProfileType)

    def resolve_all_users(root, info):
        return get_user_model().objects.all()

    def resolve_all_profiles(root, info):
        return Profile.objects.all()

    def resolve_verified_profiles(root, info):
        return Profile.objects.filter(verified=True)

    def resolve_my_followers(root, info):
        user = info.context.user
        if user.is_anonymous:
            return Profile.objects.none()
        return user.profile.followers.all()

    def resolve_my_following(root, info):
        user = info.context.user
        if user.is_anonymous:
            return Profile.objects.none()
        return user.profile.following.all()


schema = graphene.Schema(query=Query, mutation=Mutation)
