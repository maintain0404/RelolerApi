from django.urls import path

from .views import PostView, CommentListView, VideoView

urlpatterns = [
    path('post/<str:pk>', PostView.as_view(), name="post_detail"),
    # path('posts/<str:pk_starts>', PostListView.as_view()),
    # path('posts/latestes',),
    path('comment/<str:pk>/<str:sk>', CommentListView.as_view()),
    path('video/<str:pk>/<str:sk>', VideoView.as_view())
]