from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'Administration Professor Market'
admin.site.site_title = 'Professor Market'
admin.site.index_title = 'Gestion du contenu et des commandes'

urlpatterns = [
    path('admin-pro/', admin.site.urls),
    path('', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
