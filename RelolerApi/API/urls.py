from django.urls import path

from .views import *

urlpatterns = [
    # path('post', PostListView.as_view(), name = 'post_list'),
    # path('post/<str:pk>/<str:sk>', PostView.as_view(), name="post_detail"),
    # path('post/<str:pk>/<str:sk>/comment', CommentListView.as_view()),
    path('signin/google', GoogleSignInView.as_view()),
    path('signout', SignOutView.as_view()),
    path('user/riotid', RiotIDAuthView.as_view()),
]