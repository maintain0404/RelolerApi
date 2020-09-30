from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from rest_framework import permissions, routers

from .views import *

urlpatterns = [
    # path('post', PostListView.as_view(), name = 'post_list'),
    # path('post/<str:pk>/<str:sk>', PostView.as_view(), name="post_detail"),
    # path('post/<str:pk>/<str:sk>/comment', CommentListView.as_view()),
    path('signin/google/uri', GoogleSignInUriView.as_view()),
    path('signin/google', GoogleSignInView.as_view()),
    path('signout', SignOutView.as_view()),
    path('user/riotid', RiotIDAuthView.as_view()),
    path('user/gdrive', GoogleDriveView.as_view())
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="Reloler API",
            default_version='v1',
            description="Test description",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="maintain0404@gmail.com"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    urlpatterns += [
        # path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path(r'redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
    ]