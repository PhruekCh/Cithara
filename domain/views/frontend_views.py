"""
Template-serving views for the Cithara frontend.

These views render HTML pages and ensure each authenticated user
has a Creator + Library record (auto-created on first visit).
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from domain.models import Creator, Library, Song


# ─── Helpers ──────────────────────────────────────────────────────

def _ensure_creator_and_library(user):
    """
    Given a Django auth user, ensure they have a matching
    Creator + Library.  Returns (creator, library).
    """
    try:
        creator = Creator.objects.get(email=user.email)
    except Creator.DoesNotExist:
        creator = Creator.objects.create(
            email=user.email,
            display_name=user.get_full_name() or user.username or user.email,
        )

    # Ensure the Creator has a Library
    library, _ = Library.objects.get_or_create(creator=creator)
    return creator, library


# ─── Pages ────────────────────────────────────────────────────────

def register_view(request):
    """Register a new account using username + email + password."""
    if request.user.is_authenticated:
        return redirect('/library/')

    error = None
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password1:
            error = 'All fields are required.'
        elif password1 != password2:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error = f'Username "{username}" is already taken.'
        elif User.objects.filter(email=email).exists():
            error = 'An account with that email already exists.'
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
            )
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/library/')

    return render(request, 'domain/register.html', {'error': error})


def login_view(request):
    """Render login page; handle fallback form POST."""
    if request.user.is_authenticated:
        return redirect('/library/')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/library/')
        else:
            error = 'Invalid username or password.'

    return render(request, 'domain/login.html', {'error': error})


def logout_view(request):
    """Log out and redirect to login."""
    logout(request)
    return redirect('/login/')


@login_required
def library_view(request):
    """My Library — lists the user's songs."""
    creator, library = _ensure_creator_and_library(request.user)
    song_count = Song.objects.filter(library=library, is_deleted=False).count()
    return render(request, 'domain/library.html', {
        'library_id': library.pk,
        'song_count': song_count,
    })


@login_required
def studio_view(request):
    """Creation Studio — generate a new song."""
    creator, library = _ensure_creator_and_library(request.user)
    return render(request, 'domain/studio.html', {
        'library_id': library.pk,
    })


def song_detail_view(request, song_id):
    """
    Song detail / shared song page.
    Accessible to all authenticated users (FR-15: login to listen).
    """
    if not request.user.is_authenticated:
        return redirect(f'/login/?next=/song/{song_id}/')

    song = get_object_or_404(Song, pk=song_id)
    return render(request, 'domain/player.html', {
        'song': song,
    })


@login_required
def download_song_view(request, song_id):
    """
    Download a song's audio file (FR-13).

    Proxies the audio from its URL and streams it to the browser
    as a file attachment, avoiding CORS issues with direct downloads.
    """
    import requests as http_requests
    from django.http import HttpResponse

    song = get_object_or_404(Song, pk=song_id)

    if not song.audio_url or 'example.com' in song.audio_url:
        return HttpResponse(
            'No audio file available (mock mode).',
            status=404,
            content_type='text/plain',
        )

    try:
        resp = http_requests.get(song.audio_url, timeout=30, stream=True)
        resp.raise_for_status()
    except Exception:
        return HttpResponse(
            'Could not fetch the audio file.',
            status=502,
            content_type='text/plain',
        )

    content_type = resp.headers.get('Content-Type', 'audio/mpeg')
    safe_title = ''.join(c for c in song.title if c.isalnum() or c in ' _-').strip() or 'song'
    ext = '.mp3' if 'mpeg' in content_type else '.m4a'

    response = HttpResponse(resp.content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{safe_title}{ext}"'
    return response


def home_redirect(request):
    """Redirect root to library (or login)."""
    if request.user.is_authenticated:
        return redirect('/library/')
    return redirect('/login/')
