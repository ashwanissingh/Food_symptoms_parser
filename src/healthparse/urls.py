from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.urls import include

urlpatterns = [
    path("", lambda request: redirect("dashboard", permanent=False)),
    path("admin/", admin.site.urls),
    path("", include("ui.urls")),
]
