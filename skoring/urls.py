from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"), #URL index. mengakses file views.py di function index
    path("analyze/", views.analyze, name="analyze"), #URL analyze mengakses file views.py di function analyze
    path("add/", views.add, name="add"), #URL add mengakses file views.py di function add
]
