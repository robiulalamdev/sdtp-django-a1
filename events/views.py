from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib import messages
from events.models import Event, Category
from events.forms import EventForm, CategoryForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from users.views import is_admin, is_organizer_or_admin
from django.views import View
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView, CreateView

# 📌 Dashboard View
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

    event_filters = {
        'today': Q(date=current_date),
        'upcoming': Q(date__gt=current_date),
        'past': Q(date__lt=current_date),
    }

    event_name_map = {
        'today': "Today’s Events",
        'upcoming': "Upcoming Events",
        'past': "Past Events",
        'all': "Total Events"
    }

    events = Event.objects.select_related('category').prefetch_related('participants').annotate(
        total_participants=Count('participants', distinct=True)
    )

    if event_type in event_filters:
        events = events.filter(event_filters[event_type])
    
    event_name = event_name_map.get(event_type, "Total Events")

    categories = Category.objects.annotate(total_events=Count('events')).order_by('-id')

    # Get the correct User model dynamically
    User = get_user_model()  # This fetches either `auth.User` or your custom user model
    
    # Get participants (custom user model or default User model)
    participants = User.objects.annotate(total_events=Count('events')).order_by('-id')  

    context = {
        'counts': counts,
        'events': events,
        'event_type': event_type,
        'event_name': event_name,  
        'categories': categories,
        'participants': participants,
    }
    return render(request, 'dashboard/dashboard.html', context)

# 📌 Home View
def home(request):
    search = request.GET.get('search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')

    events = Event.objects.select_related('category').prefetch_related('participants').annotate(
        total_participants=Count('participants', distinct=True)
    )

    if search:
        events = events.filter(Q(name__icontains=search) | Q(location__icontains=search))

    if start_date:
        events = events.filter(date__gte=start_date)

    if end_date:
        events = events.filter(date__lte=end_date)

    if category:
        events = events.filter(category_id=category)

    categories = Category.objects.annotate(total_events=Count('events')).order_by('-id')

    participants_dict = {
        event.id: event.participants.all() for event in events
    }

    context = {
        'events': events,
        'categories': categories,
        'participants_dict': participants_dict,
    }

    return render(request, 'events/events.html', context)


# 📌 Create Event
@login_required
@user_passes_test(is_organizer_or_admin, login_url='permission_denied')
def create_event(request):
    if request.method == 'POST':
        print("FILES: ",request.FILES)
        form = EventForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save() 
            return redirect('home')  
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event', 'button_text': 'Create'})


view_Event_decorators = [login_required, user_passes_test(is_organizer_or_admin, login_url='permission_denied')]

@method_decorator(view_Event_decorators, name='dispatch')
class CreateEventView(View):
    template_name = 'events/event_form.html'

    def get(self, request, *args, **kwargs):
        form = EventForm()
        return render(request, self.template_name, {
            'form': form,
            'title': 'Create Event',
            'button_text': 'Create'
        })

    def post(self, request, *args, **kwargs):
        print("FILES: ", request.FILES)
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('home')

        return render(request, self.template_name, {
            'form': form,
            'title': 'Create Event',
            'button_text': 'Create'
        })


# 📌 Update Event
@login_required
@user_passes_test(is_organizer_or_admin, login_url='permission_denied')
def event_update(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('events')  
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Update Event', 'button_text': 'Update'})


@method_decorator(view_Event_decorators, name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events')  
    extra_context = {
        'title': 'Update Event',
        'button_text': 'Update'
    }

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the event.')
        return super().form_invalid(form)

# 📌 Delete Event
@login_required
@user_passes_test(is_organizer_or_admin, login_url='permission_denied')
def event_delete(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    messages.success(request, 'Event deleted successfully!')
    return redirect('events')


# 📌 Event Details
def EventDetails(request, id):
    event = get_object_or_404(Event.objects.select_related('category').prefetch_related('participants'), id=id)

    context = {
        'event': event,
        'category': event.category,
        'participants': event.participants.all(),
    }
    return render(request, 'events/event-details.html', context)


# 📌 Show Categories
def Show_Categories(request):
    categories = Category.objects.annotate(total_events=Count('events')).order_by('-id')
    return render(request, 'category/categories.html', {'categories': categories})


class CategoryListView(ListView):
    model = Category
    template_name = 'category/categories.html'
    context_object_name = 'categories'
    ordering = ['-id']

    def get_queryset(self):
        return Category.objects.annotate(total_events=Count('events')).order_by('-id')


# 📌 Create Category
@login_required
@user_passes_test(is_organizer_or_admin, login_url='permission_denied')
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')  
    else:
        form = CategoryForm()
    return render(request, 'category/category_form.html', {'category_form': form, 'title': 'Create Category', 'button_text': 'Create'})


category_view_decorators = [
    login_required,
    user_passes_test(is_organizer_or_admin, login_url='permission_denied')
]

@method_decorator(category_view_decorators, name='dispatch')
class CreateCategoryView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category/category_form.html'
    success_url = reverse_lazy('categories')  
    extra_context = {
        'title': 'Create Category',
        'button_text': 'Create'
    }

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


# 📌 Update Category
@login_required
@user_passes_test(is_organizer_or_admin, login_url='permission_denied')
def category_update(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('categories')  
    else:
        form = CategoryForm(instance=category)

    return render(request, 'category/category_form.html', {'category_form': form, 'title': 'Update Category', 'button_text': 'Update'})


# 📌 Delete Category
@login_required
@user_passes_test(is_organizer_or_admin, login_url='permission_denied')
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('categories')


# 📌 Show Participants (Users now)
def Show_Participants(request):
    participants = User.objects.annotate(total_events=Count('events')).order_by('-id')  # ✅ Fix: Use User model
    return render(request, 'participant/participants.html', {'participants': participants})


# 📌 Create Participant (User)
@user_passes_test(is_admin, login_url='permission_denied')
def create_participant(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)  # ✅ Fix: Use Django's User form
        if form.is_valid():
            form.save()
            return redirect('participants')
    else:
        form = UserCreationForm()
    return render(request, 'participant/participant_form.html', {'form': form, 'title': 'Create User', 'button_text': 'Create'})


# 📌 Update Participant (User)
@user_passes_test(is_admin, login_url='permission_denied')
def participant_update(request, id):
    participant = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=participant)  # ✅ Fix: Use User form
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('participants')  
    else:
        form = UserChangeForm(instance=participant)

    return render(request, 'participant/participant_form.html', {'form': form, 'title': 'Update User', 'button_text': 'Update'})


# 📌 Delete Participant (User)
@user_passes_test(is_admin, login_url='permission_denied')
def participant_delete(request, id):
    participant = get_object_or_404(User, id=id)
    participant.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('participants')
