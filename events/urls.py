
from django.contrib import admin
from django.urls import path
from events.views import home

urlpatterns = [
    path('', home),
    path('home/', home),
]
