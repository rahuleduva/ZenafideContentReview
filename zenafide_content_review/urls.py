from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from zenafide_content_review.views import schema_view, ApiRoot

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('user_management.urls'), name='user_management'),
    path('api/content_management/', include('content_management.urls'), name='content_management'),
    # for swagger ui
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),    
    path ('api/api.json', schema_view.without_ui( cache_timeout=0), name='schema-swagger-ui'),
    path ('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', 
        ApiRoot.as_view(), 
        name=ApiRoot.name),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)


