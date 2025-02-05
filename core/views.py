from django.shortcuts import render

# Create your views here.


def permission_denied(request):
    return render(request, 'permission_denied.html')