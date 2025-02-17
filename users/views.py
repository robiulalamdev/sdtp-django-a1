from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm, AddParticipantForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm, EditProfileForm
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch, Count, Sum, Q
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import  TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from events.models import Event, Category
from users.signals import rsvp_signal  



User = get_user_model()


def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def is_organizer_or_admin(user):
    # Check if the user belongs to either 'Organizer' or 'Admin' group
    return user.groups.filter(name__in=['Organizer', 'Admin']).exists()


class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')




def sign_up(request):
    form = CustomRegistrationForm()
    
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST) 

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.is_active = False
            user.save()
            
            messages.success(
                request, 'A Confirmation mail sent. Please check your email')
            return redirect('sign-in')
        else:
            print("Form is not valid", form.errors) 

    return render(request, 'auth/sign_up.html', {"form": form, "button_text": "Register", "title":"Create an account"})

def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.groups.filter(name='Admin').exists():
                return redirect('admin-dashboard') 
            elif user.groups.filter(name='Organizer').exists():
                return redirect('organizer-dashboard') 
            elif user.groups.filter(name='Participant').exists():
                return redirect('participant-dashboard') 
            else:
                return redirect('home') 
            
    return render(request, 'auth/login.html', {'form': form, "button_text": "Login", "title": "Login"})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()


class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm



@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('sign-in')


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(
                request, 'User account activated successfully')
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or token')

    except User.DoesNotExist:
        return HttpResponse('User not found')


@user_passes_test(is_admin, login_url='permission_denied')
def admin_dashboard(request):
    counts = Event.objects.aggregate(
        total_events=Count('id', distinct=True),
        total_participants=Count('participants', distinct=True),
        upcoming_events=Count('id', distinct=True),
        past_events=Count('id'),
    )

    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()
    events = Event.objects.select_related('category').prefetch_related('participants').annotate(total_participants=Count('participants', distinct=True))
    groups = Group.objects.prefetch_related('permissions').annotate(
    total_users=Count('user')
    ).all()
    participants = User.objects.filter(events__isnull=False).values(
    'events__id', 'events__name', 'id', 'username'
    )
    categories = Category.objects.annotate(total_events=Count('events')).order_by('-id')


    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No Assigned'

    context = {
        'counts': counts,
        "users": users, 
        'events':events, 
        'groups': groups, 
        'participants': participants,
        'categories': categories
    }
    return render(request, 'dashboard/admin_dashboard.html', context)



# ORGANIGER
@user_passes_test(is_organizer, login_url='permission_denied')
def organizer_dashboard(request):
    counts = Event.objects.aggregate(
        total_events=Count('id', distinct=True),
        total_participants=Count('participants', distinct=True),
        upcoming_events=Count('id', distinct=True),
        past_events=Count('id'),
    )
    events = Event.objects.select_related('category').prefetch_related('participants').annotate(total_participants=Count('participants', distinct=True))
    categories = Category.objects.annotate(total_events=Count('events')).order_by('-id')

    context = {
        'counts': counts,
        'events':events, 
        'categories': categories
    }
    return render(request, 'organizer/organizer_dashboard.html', context)


# Participant
@login_required
@user_passes_test(is_participant, login_url='permission_denied')
def participant_dashboard(request):
    # events = Event.objects.select_related('category').prefetch_related('participants').annotate(total_participants=Count('participants', distinct=True))
    user = request.user
    events = Event.objects.filter(participants=user)  
    
    context = {
        'events':events,
    }
    return render(request, 'participant/participant_dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='permission_denied')
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()  # Remove old roles
            user.groups.add(role)
            messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
            return redirect('admin-dashboard')

    return render(request, 'dashboard/assign_role.html', {"form": form})


@login_required
@user_passes_test(is_admin, login_url='permission_denied')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('create-group')

    return render(request, 'dashboard/create_group.html', {'form': form})


@login_required
@user_passes_test(is_admin, login_url='permission_denied')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups': groups})



@login_required
@user_passes_test(is_admin, login_url='permission_denied')
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)

    # Check if the logged-in user is in the 'Admin' group
    if request.user.groups.filter(name="Admin").exists():
        user_to_delete.delete()
        messages.success(request, "User deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete users.")

    return redirect('admin-dashboard')  


@login_required
@user_passes_test(is_organizer_or_admin, login_url='permission_denied')
def add_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = AddParticipantForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Participants added successfully!")
            return redirect('admin-dashboard')
    else:
        form = AddParticipantForm(instance=event)

    return render(request, 'dashboard/add_participants.html', {'form': form, 'event': event})


@login_required
@user_passes_test(is_admin, login_url='permission_denied')
def delete_group(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        group.delete()
        messages.success(request, f"Group '{group.name}' deleted successfully.")
    except Group.DoesNotExist:
        messages.error(request, "Group not found.")

    return redirect('admin-dashboard')  


@login_required
@user_passes_test(is_admin, login_url='permission_denied')
def remove_participant(request, event_id, user_id):
    event = get_object_or_404(Event, id=event_id)
    user = get_object_or_404(User, id=user_id)

    if user in event.participants.all():
        event.participants.remove(user)  # Remove user from event
        messages.success(request, f"{user.username} was removed from {event.name}.")
    else:
        messages.error(request, "This user is not a participant of this event.")

    return redirect('admin-dashboard')


@login_required()
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user
    
    if user in event.participants.all():
        messages.error(request, "Cannot RSVP more than once for the same event.")
        return redirect('events')
    else:
        event.participants.add(user)
        rsvp_signal.send(sender=Event, user=user, event=event)
        
        # Show success message
        messages.success(request, "You have successfully RSVP'd to the event.")
        return redirect('events')




class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['phone_number'] = user.phone_number
        context['profile_image'] = user.profile_image

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)

