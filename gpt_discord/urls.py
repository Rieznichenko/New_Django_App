from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from llm_bot.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('llm_bot.urls')),
    path('', include('analytics.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
 + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)