
from django.contrib import admin
from django.urls import path
from events.views import home, Dashboard, EventDetails, Show_Categories, create_category, category_update, Show_Participants, create_participant

urlpatterns = [
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('events/<int:id>', EventDetails, name='event-details'),
    path('dashboard/', Dashboard, name='dashboard'),

    # for category,
    path('categories/', Show_Categories, name='categories'),
    path('categories/create/', create_category, name='create-category'),
    path('categories/update/<int:id>/', category_update, name='update-category'),


    # for participant
    path('participants/', Show_Participants, name='participants'),
    path('participants/create', create_participant, name='create-participant'),
]
