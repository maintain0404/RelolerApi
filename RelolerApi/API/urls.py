from django.urls import path

from .views import PostView, CommentListView

urlpatterns = [
    path('post/<str:pk>/<str:sk>', PostView.as_view(), name="post_detail"),
    # path('posts/<str:pk_starts>', PostListView.as_view()),
    # path('posts/latestes',),
    path('comment/<str:pk>', CommentListView.as_view()),
    # path('oauth/'),
    # path('login/'),
]