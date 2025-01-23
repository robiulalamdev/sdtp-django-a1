from django.shortcuts import render, redirect, HttpResponse
from events.forms import CategoryForm, EventForm, ParticipantForm
from events.models import Event, Category, Participant
from django.contrib import messages
from django.db.models import Count



# Home view
def home(request):
    search = request.GET.get('search')

    if search:
        events = Event.objects.filter(name__icontains=search).select_related('category').prefetch_related('participants')
    else:
        events = Event.objects.select_related('category').prefetch_related('participants')

    categories = Category.objects.all()
    participants = Participant.objects.all()

    # Prepare context
    context = {
        'events': events,
        'categories': categories,
        'participants': participants,
    }
    return render(request, 'events/events.html', context)  


# Create event view
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event', 'button_text': 'Create'})



# event update view
def event_update(request, id):
    
    event = Event.objects.get(id=id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('home')  
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Update Event', 'button_text': 'Update'})





# Event details view
def EventDetails(request, id):
    event =  Event.objects.select_related('category').prefetch_related('participants').get(id=id)
    print(event.participants.all())

    if not event:
        return HttpResponse('Event not found')
    else:
        context = {
            'event': event,
            'category': event.category,
            'participants': event.participants.all(),
        }
        return render(request, 'events/event-details.html', context)


# Dashboard view
def Dashboard(request):
    return render(request, 'dashboard/dashboard.html')


# Category views
def Show_Categories(request):
    categories = Category.objects.annotate(total_events=Count('events')).order_by('-id')

    return render(request, 'category/categories.html', {'categories': categories})


# Category views
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')  
    else:
        form = CategoryForm()
    return render(request, 'category/category_form.html', {'category_form': form, 'title': 'Create Category', 'button_text': 'Create'})


# Category update view
def category_update(request, id):
    
    category = Category.objects.get(id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('categories')  # Assuming you have a detail view
    else:
        form = CategoryForm(instance=category)

    return render(request, 'category/category_form.html', {'category_form': form, 'title': 'Update Category', 'button_text': 'Update'})



def Show_Participants(request):
    participants = Participant.objects.annotate(total_events=Count('events')).order_by('-id')
    return render(request, 'participant/participants.html', {'participants': participants})



# Participant views
def create_participant(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('participants')
    else:
        form = ParticipantForm()
    return render(request, 'participant/participant_form.html', {'form': form, 'title': 'Create Participant', 'button_text': 'Create'})


# Participant update view
def participant_update(request, id):
    
    participant = Participant.objects.get(id=id)
    if request.method == 'POST':
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Participant updated successfully!')
            return redirect('participants')  
    else:
        form = ParticipantForm(instance=participant)

    return render(request, 'participant/participant_form.html', {'form': form, 'title': 'Update Participant', 'button_text': 'Update'})







# def event_create(request):
#     if request.method == 'POST':
#         form = EventForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Event created successfully!')
#             return redirect('event_list')  # Assuming you have a list view
#     else:
#         form = EventForm()
#     return render(request, 'event_create.html', {'form': form})


# def event_update(request, pk):
#     event = get_object_or_404(Event, pk=pk)
#     if request.method == 'POST':
#         form = EventForm(request.POST, instance=event)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Event updated successfully!')
#             return redirect('event_detail')  # Assuming you have a detail view
#     else:
#         form = EventForm(instance=event)
#     return render(request, 'event_update.html', {'form': form, 'event': event})


# def participant_create(request):
#     if request.method == 'POST':
#         form = ParticipantForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Participant created successfully!')
#             return redirect('participant_list')  # Assuming you have a list view
#     else:
#         form = ParticipantForm()
#     return render(request, 'participant_create.html', {'form': form})


# def participant_update(request, pk):
#     participant = get_object_or_404(Participant, pk=pk)
#     if request.method == 'POST':
#         form = ParticipantForm(request.POST, instance=participant)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Participant updated successfully!')
#             return redirect('participant_detail')  # Assuming you have a detail view
#     else:
#         form = ParticipantForm(instance=participant)
#     return render(request, 'participant_update.html', {'form': form, 'participant': participant})