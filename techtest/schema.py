import graphene
import users.schema
import ideas.schema


class Query(users.schema.Query, ideas.schema.Query, graphene.ObjectType):
    pass


class Mutation(users.schema.Mutation, ideas.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
