from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("env", views.init_state, name="env"),
    path("action", views.perform_action, name="action")
]