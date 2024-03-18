from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.urls import get_resolver
from django.conf import settings


schema_view = get_schema_view(
   openapi.Info(
      title="Swagger with django API",
      default_version='v1',
    ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

# class ApiRoot(GenericAPIView): # TODO: Revisit later to check why it was causing issue while swagger reload
class ApiRoot(APIView): 
    name = 'api-root'

    def get_urls(self, request, url_patterns, current_app=None):
        urls = []
        for pattern in url_patterns:
            url_name = f"{pattern.name}"
            urls.append(request.build_absolute_uri(reverse(url_name, current_app=current_app)))
        return urls

    def get(self, request):
        app_names = [i.split('.')[0] for i in settings.LOCAL_APPS]
        app_names = ['content_management']
        endpoints = {}
        for app in app_names:
            resolver = get_resolver(app)
            endpoints[app] = {}
            resolver = get_resolver(f"{app}.urls")
            url_patterns = resolver.url_patterns
            print(url_patterns)
            endpoints[app] = self.get_urls(
                request, url_patterns, current_app=app
            )
        return Response(endpoints)