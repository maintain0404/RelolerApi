from django.urls import path

from .views import post, CommentListView, VideoView

urlpatterns = [
    path('post/<str:pk>/<str:sk>', post, name="post_detail"),
    path('comment/<str:pk>', CommentListView.as_view()),
    path('video/<str:pk>/<str:sk>', VideoView.as_view())
]