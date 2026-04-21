"""
URL configuration for cithara project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from domain.views.frontend_views import (
    home_redirect,
    login_view,
    logout_view,
    library_view,
    studio_view,
    song_detail_view,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # REST API (unchanged)
    path('api/', include('domain.urls')),

    # Google OAuth (allauth)
    path('accounts/', include('allauth.urls')),

    # Frontend pages
    path('', home_redirect, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('library/', library_view, name='library'),
    path('studio/', studio_view, name='studio'),
    path('song/<int:song_id>/', song_detail_view, name='song-detail'),
]
