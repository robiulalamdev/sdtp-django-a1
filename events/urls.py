
from django.contrib import admin
from django.urls import path
from events.views import home, create_event, CreateEventView, event_update, EventUpdateView, event_delete, Dashboard, EventDetails, Show_Categories, CategoryListView, create_category, CreateCategoryView, category_delete, category_update, Show_Participants, create_participant, participant_update, participant_delete

urlpatterns = [
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('events/', home, name='events'),
    path('events/<int:id>', EventDetails, name='event-details'),
    path('events/create', CreateEventView.as_view(), name='create-event'),
    path('events/update/<int:id>', EventUpdateView.as_view(), name='update-event'),
    path('events/delete/<int:id>', event_delete, name='delete-event'),

    path('dashboard/', Dashboard, name='dashboard'),

    # for category,
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('categories/create/', CreateCategoryView.as_view(), name='create-category'),
    path('categories/update/<int:id>/', category_update, name='update-category'),
    path('categories/delete/<int:id>/', category_delete, name='delete-category'),


    # for participant
    path('participants/', Show_Participants, name='participants'),
    path('participants/create', create_participant, name='create-participant'),
    path('participants/update/<int:id>', participant_update, name='update-participant'),
    path('participants/delete/<int:id>', participant_delete, name='delete-participant'),
]
