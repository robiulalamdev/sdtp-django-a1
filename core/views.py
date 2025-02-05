from django.shortcuts import render

# Create your views here.


def permission_denied(request):
    return render(request, 'permission_denied.html')


# def some_view(request):
#     dashboard_url = "#" 

#     if request.user.groups.filter(name="Admin").exists():
#         dashboard_url = "/users/admin/dashboard"
#     elif request.user.groups.filter(name="Organizer").exists():
#         dashboard_url = "/users/organizer/dashboard"
#     elif request.user.groups.filter(name="Participant").exists():
#         dashboard_url = "/users/participant/dashboard"

#     context = {"dashboard_url": dashboard_url}
#     return render(request, "your_template.html", context)
