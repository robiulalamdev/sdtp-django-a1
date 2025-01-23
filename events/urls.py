
from django.contrib import admin
from django.urls import path
from events.views import home, create_event,event_update,event_delete, Dashboard, EventDetails, Show_Categories, create_category, category_update, Show_Participants, create_participant, participant_update

urlpatterns = [
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('events/', home, name='events'),
    path('events/<int:id>', EventDetails, name='event-details'),
    path('events/create', create_event, name='create-event'),
    path('events/update/<int:id>', event_update, name='update-event'),
    path('events/delete/<int:id>', event_delete, name='delete-event'),

    path('dashboard/', Dashboard, name='dashboard'),

    # for category,
    path('categories/', Show_Categories, name='categories'),
    path('categories/create/', create_category, name='create-category'),
    path('categories/update/<int:id>/', category_update, name='update-category'),


    # for participant
    path('participants/', Show_Participants, name='participants'),
    path('participants/create', create_participant, name='create-participant'),
    path('participants/update/<int:id>', participant_update, name='update-participant'),
]
