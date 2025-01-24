from django.shortcuts import render, redirect, HttpResponse
from events.forms import CategoryForm, EventForm, ParticipantForm
from events.models import Event, Category, Participant
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils.timezone import now, timedelta

def Dashboard(request):
    current_date = now().date()

    counts = Event.objects.aggregate(
        total_events=Count('id', distinct=True),
        total_participants=Count('participants', distinct=True),
        upcoming_events=Count('id', filter=Q(date__gt=current_date), distinct=True),
        past_events=Count('id', filter=Q(date__lt=current_date)),
    )


    event_type = request.GET.get('type', 'today')  
    event_name = "Today’s Events"

    # Events filtered based on type
    if event_type == 'upcoming':
        event_name = "Upcoming Events"
        events = Event.objects.filter(date__gt=current_date).select_related('category').prefetch_related('participants').annotate(total_participants=Count('participants', distinct=True))
    elif event_type == 'past':
        event_name = "Past Events"
        events = Event.objects.filter(date__lt=current_date).select_related('category').prefetch_related('participants').annotate(total_participants=Count('participants', distinct=True))
    elif event_type == 'today':
        event_name = "Today’s Events"
        events = Event.objects.filter(date=current_date).select_related('category').prefetch_related('participants').annotate(total_participants=Count('participants', distinct=True))
    else:  # 'all' or any other value
        event_name = "Total Events"
        events = Event.objects.select_related('category').prefetch_related('participants').annotate(total_participants=Count('participants', distinct=True))

    categories = Category.objects.annotate(total_events=Count('events')).order_by('-id')
    participants = Participant.objects.annotate(total_events=Count('events')).order_by('-id')
    
    print(events)
    context = {
        'counts': counts,
        'events': events,
        'event_type': event_type,
        'event_name': event_name,  
        'categories': categories,
        'participants': participants,
    }
    return render(request, 'dashboard/dashboard.html', context)


# Home view
def home(request):
    search = request.GET.get('search')

    if search:
        events = Event.objects.filter(
            Q(name__icontains=search) | Q(location__icontains=search)
        ).select_related('category').prefetch_related('participants').annotate(total_participants=Count('participants', distinct=True))
    else:
        events = Event.objects.select_related('category').prefetch_related('participants').annotate(total_participants=Count('participants', distinct=True))

    # Prepare context
    context = {
        'events': events,
        'categories': [],
        'participants': [],
    }
    return render(request, 'events/events.html', context)  


# Create event view
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('events')  
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
            return redirect('events')  
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Update Event', 'button_text': 'Update'})


# Event delete view
def event_delete(request, id):
    event = Event.objects.get(id=id)
    event.delete()
    messages.success(request, 'Event deleted successfully!')
    return redirect('events')




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



# Category delete view
def category_delete(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('categories')




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



# Category delete view
def participant_delete(request, id):
    participant = Participant.objects.get(id=id)
    participant.delete()
    messages.success(request, 'Participant deleted successfully!')
    return redirect('participants')




