# core/urls.py

from django.urls import path, re_path
from . import views

from django.shortcuts import redirect

def redirect_to_feed(request):
    return redirect('feed')

urlpatterns = [
    # Redirecting to Home Page to Feed Page
    path('', views.login_view, name='login'),
    # Signup Page
    path('signup/', views.signup, name='signup'),
    # Login
    path('login/', views.login_view, name='login'),
    # Logout
    path('logout/', views.logout_view, name='logout'),
    # Feed Page
    path('feed/', views.feed, name='feed'),
    # Post Create
    path('post/create/', views.post_create, name='post_create'),
    # Post Delete
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    # Comment on Posts
    path('post/<int:pk>/comment/', views.comment_create, name='comment_create'),
    # Delete Comment
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    # Like Post
    path('post/<int:pk>/like/', views.like, name='like'),
    # Redirecting to Latest Username
    re_path(r'^profile/(?!change-username/)(?P<username>\w+)/$', views.user_profile, name='user_profile'),
    # For fetching user the username on posts
    path('guest/profile/<str:username>/', views.guest_profile, name='guest_profile'),
    # Change Username
    path('profile/change-username/', views.change_username, name='change_username'),
    # Search Users
    path('search/', views.search_users, name='search_users'),

    path('profile/<str:username>/follow/', views.follow, name='follow'),

    path('profile/<str:username>/unfollow/', views.unfollow, name='unfollow'),

    path('followed_users/', views.followed_users, name='followed_users'),

    path('post/<int:pk>/', views.post_detail, name='post_detail'),
 
    path('recommend/', views.recommend_view, name='recommend'),
]
