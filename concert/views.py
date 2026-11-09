import os
import requests as req
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user = User.objects.create_user(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
        except IntegrityError:
            form.add_error("username", "This username is already in use.")
        else:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    return render(request, "signup.html", {"form": form})


def index(request):
    return render(request, "index.html")


def service_page(request, setting, default_url, template, context_key):
    try:
        response = req.get(os.environ.get(setting, default_url), timeout=10)
        response.raise_for_status()
        items = response.json()
        if not isinstance(items, list):
            raise ValueError("Expected a list from the catalogue service")
    except (req.RequestException, ValueError):
        return render(request, template, {context_key: [], "error": "Catalogue temporarily unavailable."}, status=503)
    return render(request, template, {context_key: items})


def songs(request):
    return service_page(request, "SONGS_SERVICE_URL", "http://127.0.0.1:5001/song", "songs.html", "songs")


def photos(request):
    return service_page(request, "PICTURES_SERVICE_URL", "http://127.0.0.1:5002/picture", "photos.html", "photos")


def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return HttpResponseRedirect(reverse("index"))
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url="login")
def concerts(request):
    attendance = {row.concert_id: row.attending for row in ConcertAttending.objects.filter(user=request.user)}
    items = [{"concert": concert, "status": attendance.get(concert.id, "-")} for concert in Concert.objects.order_by("date", "id")]
    return render(request, "concerts.html", {"concerts": items})


@login_required(login_url="login")
def concert_detail(request, id):
    concert = get_object_or_404(Concert, pk=id)
    attendance = ConcertAttending.objects.filter(concert=concert, user=request.user).first()
    return render(request, "concert_detail.html", {"concert_details": concert, "status": attendance.attending if attendance else "-", "attending_choices": ConcertAttending.AttendingChoices.choices})


@login_required(login_url="login")
@require_POST
def concert_attendee(request):
    try:
        concert_id = int(request.POST.get("concert_id", ""))
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid concert id")
    concert = get_object_or_404(Concert, pk=concert_id)
    choice = request.POST.get("attendee_choice")
    if choice not in ConcertAttending.AttendingChoices.values:
        return HttpResponseBadRequest("Invalid attendance choice")
    ConcertAttending.objects.update_or_create(concert=concert, user=request.user, defaults={"attending": choice})
    return HttpResponseRedirect(reverse("concerts"))
