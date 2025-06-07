from django.urls import path
from . import views
from users.views import (
    AuthorListView, AuthorDetailView, FollowView,
    FollowersListView, FollowingListView, AcceptFollowView
)

urlpatterns = [
    # Node info
    path('', views.node_info, name='node_info'),

    # Authors
    path('authors/', AuthorListView.as_view(), name='author_list'),
    path('authors/<uuid:pk>/', AuthorDetailView.as_view(), name='author_detail'),
    path('authors/<uuid:pk>/follow/', FollowView.as_view(), name='follow'),
    path('authors/<uuid:pk>/followers/', FollowersListView.as_view(), name='followers'),
    path('authors/<uuid:pk>/following/', FollowingListView.as_view(), name='following'),
    path('authors/<uuid:pk>/followers/<uuid:follower_id>/accept/', AcceptFollowView.as_view(), name='accept_follow'),

    # Inbox (federation)
    path('authors/<uuid:pk>/inbox/', views.InboxView.as_view(), name='inbox'),

    # Posts by author
    path('authors/<uuid:author_id>/posts/', views.AuthorPostListView.as_view(), name='author_posts'),

    # Posts
    path('posts/', views.PostListCreateView.as_view(), name='post_list_create'),
    path('posts/<uuid:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<uuid:pk>/like/', views.LikePostView.as_view(), name='post_like'),

    # Comments
    path('posts/<uuid:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment_list_create'),

    # Feed
    path('feed/', views.FeedView.as_view(), name='feed'),

    # Nodes (admin only)
    path('nodes/', views.NodeListView.as_view(), name='node_list'),
]
