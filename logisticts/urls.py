"""logisticts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic.base import RedirectView


schema_view = get_schema_view(
   openapi.Info(
      title="Shyper API",
      default_version='v1',
      description=("Shyper is a platform that facilitates the transportation "
      "of cargo. We connect cargo owners with appropriate transport companies "
      "and ensure that all orders are handled in a timely and professional "
      "manner."),
      terms_of_service="https://www.syper.com/policies/terms/",
      contact=openapi.Contact(email="contact@shyper.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/company/', include('companies.urls')),
    path('api/v1/docs/', schema_view.with_ui('swagger', cache_timeout = 0), name = 'api-documentation'),
    path('api/v1/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', RedirectView.as_view(url='api/v1/docs/',
                                  permanent=False),
         name='api_documentation'),
    path('api/v1/transporter/', include('transporter.urls')),
    path('api/v1/cargo_types/', include('cargo_types.urls')),
    path('api/v1/depots/', include('depots.urls')), 
    path('api/v1/assets/', include('assets.urls')),
    path('api/v1/rates/', include('rates.urls')),
]


if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
