from django.urls import path

from .views import post, comment

urlpatterns = [
    path('post/<str:pk>/<str:sk>', post, name="post_detail"),
    path('comment/<str:pk>', comments, name="comments"),
    path('comment/<str:pk>/<str:sk>', comment, name="comment_detail"),
]