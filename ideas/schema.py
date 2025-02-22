import graphene
from graphene_django import DjangoObjectType
from .models import Idea
from users.models import User


class IdeaType(DjangoObjectType):
    class Meta:
        model = Idea
        fields = (
            "id",
            "title",
            "body",
            "created_at",
            "updated_at",
            "author",
            "visibility",
            "idea_id",
            "likes",
            "dislikes",
            "active",
            "slug",
            "views",
        )


class CreateIdea(graphene.Mutation):
    idea = graphene.Field(IdeaType)
    success = graphene.Boolean()
    errors = graphene.String()

    class Arguments:
        title = graphene.String(required=True)
        body = graphene.String(required=True)
        visibility = graphene.String(required=True)

    def mutate(self, info, title, body, visibility):
        user = info.context.user
        if user.is_anonymous:
            return CreateIdea(
                success=False, errors="Debe estar autenticado para crear una idea"
            )

        idea = Idea(title=title, body=body, author=user, visibility=visibility)
        idea.save()
        return CreateIdea(idea=idea, success=True)


class UpdateIdea(graphene.Mutation):
    idea = graphene.Field(IdeaType)

    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        body = graphene.String()
        visibility = graphene.String()
        active = graphene.Boolean()

    def mutate(self, info, id, title=None, body=None, visibility=None, active=None):
        idea = Idea.objects.get(id=id)
        if title:
            idea.title = title
        if body:
            idea.body = body
        if visibility:
            idea.visibility = visibility
        if active is not None:
            idea.active = active
        idea.save()
        return UpdateIdea(idea=idea)


class DeleteIdea(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        idea = Idea.objects.get(id=id)
        idea.delete()
        return DeleteIdea(success=True)


class LikeIdea(graphene.Mutation):
    success = graphene.Boolean()
    likes_count = graphene.Int()
    liked = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        user = info.context.user
        if user.is_anonymous:
            return LikeIdea(success=False, likes_count=0, liked=False)

        idea = Idea.objects.get(id=id)
        if user in idea.likes.all():
            idea.likes.remove(user)
            liked = False
        else:
            idea.likes.add(user)
            liked = True

        return LikeIdea(success=True, likes_count=idea.likes.count(), liked=liked)


class Query(graphene.ObjectType):
    all_ideas = graphene.List(IdeaType)
    idea_by_slug = graphene.Field(IdeaType, slug=graphene.String(required=True))

    def resolve_all_ideas(root, info):
        return Idea.objects.all()

    def resolve_idea_by_slug(root, info, slug):
        return Idea.objects.get(slug=slug)

    def resolve_my_ideas(root, info):
        user = info.context.user
        if user.is_anonymous:
            return Idea.objects.none()
        return Idea.objects.filter(author=user).order_by("-created_at")


class Mutation(graphene.ObjectType):
    create_idea = CreateIdea.Field()
    update_idea = UpdateIdea.Field()
    delete_idea = DeleteIdea.Field()
    like_idea = LikeIdea.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
