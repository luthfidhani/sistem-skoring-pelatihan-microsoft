from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("analyze/", views.analyze, name="analyze"),
    path("add/", views.add, name="add"),
]
