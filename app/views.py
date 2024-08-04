from genericpath import exists
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Comment, Like, Follow
from .forms import PostForm, CommentForm, UsernameChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import Q, Exists, OuterRef  

# Signup View
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Login View 
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Logout View 
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# View for Logged In User Feed
def feed(request):
    follows = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=follows).order_by('-created_at')
    
    # User suggestions: users not followed by the current user, limited to 3
    user_suggestions = User.objects.exclude(id__in=follows).exclude(id=request.user.id).order_by('?')[:3]

    return render(request, 'feed.html', {'posts': posts, 'user_suggestions': user_suggestions})


# View for Creating a Post
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'post_create.html', {'form': form})

# View for Deleting a Post
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)
    post.delete()
    return redirect('feed')

# View for Commenting on a Post
@login_required
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('feed')
    else:
        form = CommentForm()
    return render(request, 'comment_create.html', {'form': form, 'post': post})

# View for Deleting a Comment
@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    comment.delete()
    return redirect('feed')

# View for Liking a Post
@login_required
def like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like_obj, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like_obj.delete()
    return redirect('feed')

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user)
    likes = Like.objects.filter(user=user)
    
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = user.followers.filter(id=request.user.id).exists()
    
    context = {
        'profile_user': user,
        'posts': posts,
        'likes': likes,
        'is_following': is_following,
    }
    return render(request, 'user_profile.html', context)


# View for showing a other user's profile for logged out users
def guest_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user)
    return render(request, 'guest_profile.html', {'profile_user': user, 'posts': posts})

# View for changing a user's username
@login_required
def change_username(request):
    if request.method == 'POST':
        form = UsernameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update session to keep user logged in
            messages.success(request, 'Your username has been updated.')
            return redirect('user_profile', user.username)
    else:
        form = UsernameChangeForm(instance=request.user)
    return render(request, 'change_username.html', {'form': form})

# View for searching users
def search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )

    if request.user.is_authenticated:
        follows = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        users = users.annotate(is_following=Exists(Follow.objects.filter(follower=request.user, following=OuterRef('pk'))))
    else:
        follows = []

    return render(request, 'search_users.html', {'users': users, 'query': query, 'follows': follows})


@login_required
def follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    
    # After following, get new suggestions
    follows = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    new_suggestions = User.objects.exclude(id__in=follows).exclude(id=request.user.id).order_by('?')[:3]
    
    return render(request, 'user_profile.html', {
        'profile_user': user_to_follow,
        'is_following': True,
        'user_suggestions': new_suggestions
    })

@login_required
def unfollow(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect('user_profile', username=username)

@login_required
def followed_users(request):
    follows = Follow.objects.filter(follower=request.user).select_related('following')
    followed_users = [follow.following for follow in follows]
    return render(request, 'followed_users.html', {'followed_users': followed_users})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post).order_by('created_at')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'post_detail.html', {'post': post, 'comments': comments, 'form': form})

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import render

def get_recommendations(prompt, num_recommendations=5):
    data = pd.read_csv('C:/Users/roicy/Downloads/Project3/social/social_media_dataset.csv')  # Adjust path as needed
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['PostContent'])
    prompt_tfidf = tfidf.transform([prompt])
    cosine_similarities = cosine_similarity(prompt_tfidf, tfidf_matrix).flatten()
    similar_indices = cosine_similarities.argsort()[-num_recommendations:][::-1]
    recommendations = data.iloc[similar_indices].sort_values(by='Likes', ascending=False).head(num_recommendations)
    return recommendations[['PostContent', 'Likes']]

def recommend_view(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        recommendations = get_recommendations(prompt)
        if recommendations.empty:
            return render(request, 'no_recommendations.html', {'prompt': prompt})
        else:
            recommendations_list = recommendations.to_dict(orient='records')
            return render(request, 'recommendations.html', {'prompt': prompt, 'recommendations': recommendations_list})
    return render(request, 'recommend_prompt.html')



