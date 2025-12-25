from django.urls import path

from ui import views

urlpatterns = [
    path("upload/", views.upload_view, name="upload"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("entry/<str:entry_id>/", views.entry_detail_view, name="entry_detail"),
]
