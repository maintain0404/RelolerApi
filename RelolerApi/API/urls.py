from django.urls import path

from .views import *

urlpatterns = [
    path('post/<str:pk>/<str:sk>', PostView.as_view(), name="post_detail"),
    path('post', PostListView.as_view(), name = 'post_list'),
    # path('posts/<str:pk_starts>', PostListView.as_view()),
    path('oauth', OauthView.as_view()),
    path('oauth\google', ),
    path('comment/<str:pk>', CommentListView.as_view()),
    # path('login/'),
]