from django.shortcuts import render
from django.http import JsonResponse
from django.utils.text import slugify
from django.utils.timesince import timesince
from django.contrib.auth.decorators import login_required
import shortuuid
from .models import Idea

# Create your views here.


def index(request):
    ideas = Idea.objects.filter(active=True, visibility="Public")
    context = {"ideas": ideas}
    return render(request, "ideas/index.html", context)


@login_required
def post_idea(request):
    if request.method == "POST":
        title = request.POST.get("title")
        body = request.POST.get("body")
        visibility = request.POST.get("visibility")

        if not title or not body:
            return JsonResponse({"error": "Título y cuerpo del post requeridos"})

        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]

        idea = Idea(
            title=title,
            body=body,
            visibility=visibility,
            author=request.user,
            slug=slugify(f"{title}-{uniqueid.lower()}"),
        )
        idea.save()
        return JsonResponse(
            {
                "idea": {
                    "title": idea.title,
                    "body": idea.body,
                    "full_name": idea.author.profile.full_name,
                    "visibility": idea.visibility,
                    "created_at": timesince(idea.created_at),
                    "id": idea.id,
                }
            }
        )

    return JsonResponse({"data": "sent"})


@login_required
def like_idea(request):
    id = request.GET.get("id")
    if not id:
        return JsonResponse({"error": "ID de la idea es requerido"})

    try:
        idea = Idea.objects.get(id=id)
    except Idea.DoesNotExist:
        return JsonResponse({"error": "La idea no existe"})

    user = request.user
    liked = False

    if user in idea.likes.all():
        idea.likes.remove(user)
    else:
        idea.likes.add(user)
        liked = True

    data = {
        "liked": liked,
        "likes_count": idea.likes.count(),
    }
    return JsonResponse({"data": data})
