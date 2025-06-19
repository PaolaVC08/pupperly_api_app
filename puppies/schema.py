import graphene
from graphene_django import DjangoObjectType
from users.schema import UserType
from .models import Puppy, Vote
from graphql import GraphQLError
from django.db.models import Q
from graphene_django.filter import DjangoFilterConnectionField


class PuppyType(DjangoObjectType):
    class Meta:
        model = Puppy
     #   fields = ('id', 'name', 'breed', 'description', 'created_at', 'posted_by')

class CountableConnectionBase(graphene.relay.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        return self.iterable.count()

class VoteType(DjangoObjectType):
    class Meta:
        model = Vote
        fields = ('user', 'puppy')
        filter_fields = ('user', 'puppy')
        interfaces = (graphene.relay.Node,)
        connection_class = CountableConnectionBase

class Query(graphene.ObjectType):
    puppies = graphene.List(
       PuppyType, 
       search=graphene.String(),
       first=graphene.Int(),
       skip=graphene.Int(),
    )
    #votes = graphene.List(VoteType)
    votes = DjangoFilterConnectionField(VoteType)


    def resolve_puppies(self, info, search=None, first=None, skip=None, **kwargs):
        qs = Puppy.objects.all()

        if search:
            filter = (
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(breed__icontains=search)
            )
            qs = qs.filter(filter)

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]
    
        return qs

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()


# ...code
#1
class CreatePuppy(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    breed = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    #2
    class Arguments:
        name = graphene.String()
        breed = graphene.String()
        description = graphene.String()

    #3
    def mutate(self, info, name, breed, description):
        user = info.context.user #or None

        # Verifica si el usuario está autenticado
        if user.is_anonymous:
            raise GraphQLError('You must be logged in to create a puppy!')

        puppy = Puppy(
            name=name, 
            breed=breed,
            description=description,
            posted_by=user,
        )
        puppy.save()

        return CreatePuppy(
            id=puppy.id,
            name=puppy.name,
            breed=puppy.breed,
            description=puppy.description,
            posted_by=puppy.posted_by,
        )


class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    puppy = graphene.Field(PuppyType)

    class Arguments:
        puppy_id = graphene.Int()

    def mutate(self, info, puppy_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged to vote!')

        puppy = Puppy.objects.filter(id=puppy_id).first()
        if not puppy:
            raise Exception('Invalid Puppy!')

        Vote.objects.create(
            user=user,
            puppy=puppy,
        )

        return CreateVote(user=user, puppy=puppy)

#4
class Mutation(graphene.ObjectType):
    create_puppy = CreatePuppy.Field()
    create_vote = CreateVote.Field()