
from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static
from django.conf import settings
from core.views import permission_denied


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("events.urls")),
    path("users/", include('users.urls')),
    path('permission-denied/', permission_denied, name='permission_denied')
]+ debug_toolbar_urls()

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)