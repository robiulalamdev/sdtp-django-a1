from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm, AddParticipantForm
from django.contrib import messages
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch, Count, Sum, Q
from django.contrib.auth.views import LoginView
from django.views.generic import  UpdateView
from django.contrib.auth import get_user_model
from events.models import Event



User = get_user_model()


def is_admin(user):
    return user.groups.filter(name='Admin').exists()


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
            return redirect('home')
    return render(request, 'auth/login.html', {'form': form, "button_text": "Login", "title": "Login"})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()


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

    print("participants: ",participants[0])



    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No Assigned'

    return render(request, 'dashboard/admin_dashboard.html', {"users": users, 'events':events, 'groups': groups, 'participants': participants})


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
            messages.success(request, f"User {
                             user.username} has been assigned to the {role.name} role")
            return redirect('admin-dashboard')

    return render(request, 'dashboard/assign_role.html', {"form": form})


@user_passes_test(is_admin, login_url='permission_denied')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {
                             group.name} has been created successfully")
            return redirect('create-group')

    return render(request, 'dashboard/create_group.html', {'form': form})


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



def add_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = AddParticipantForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Participants added successfully!")
            return redirect('event_details', id=event_id)
    else:
        form = AddParticipantForm(instance=event)

    return render(request, 'dashboard/add_participants.html', {'form': form, 'event': event})



def delete_group(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        group.delete()
        messages.success(request, f"Group '{group.name}' deleted successfully.")
    except Group.DoesNotExist:
        messages.error(request, "Group not found.")

    return redirect('admin-dashboard')  



def remove_participant(request, event_id, user_id):
    event = get_object_or_404(Event, id=event_id)
    user = get_object_or_404(User, id=user_id)

    if user in event.participants.all():
        event.participants.remove(user)  # Remove user from event
        messages.success(request, f"{user.username} was removed from {event.name}.")
    else:
        messages.error(request, "This user is not a participant of this event.")

    return redirect('admin-dashboard')
