from datetime import timezone

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import User, Notification, Event
from posts.models import Post, Like


def home(request):
    # posts = Post.objects.exclude(posted_by=User.objects.get(is_superuser=True)).order_by('-pub_date')
    posts = Post.objects.all().order_by('-pub_date')
    return render(request, "posts/home.html", {'posts': posts})

@login_required(login_url='/accounts/login')
def create(request):
    if request.method == 'POST':
        imageFile = request.FILES.get('image', None)
        if request.POST['title'] or imageFile:
            post = Post()
            post.title = request.POST['title']
            post.image = imageFile
            post.posted_by = request.user
            post.save()
            return redirect('/posts/' + str(post.id))
            # return render(request, 'posts/create.html')
        else:
            return render(request, 'posts/create.html', {'error': 'All fields are required.'})
    else:
        return render(request,'posts/create.html')

@login_required(login_url='/accounts/login')
def details(request, post_id):
    current_user = request.user.id
    postDetail = get_object_or_404(Post, pk=post_id)
    likes = Like.objects.filter(post=postDetail.id)
    try:
        likedbycurrentUser = Like.objects.get(user=current_user, post=post_id)
        likedbycurrentUser = True
    except Like.DoesNotExist:
        likedbycurrentUser = False
    return render(request, 'posts/detail.html', {'post' : postDetail,'likes':len(likes),'likedbycurrentUser':likedbycurrentUser})

@login_required(login_url='/accounts/login')
def like(request, post_id):
    current_user = request.user.id
    postExists = Post.objects.get(pk=post_id)
    user_to_notify = User.objects.get(pk=postExists.posted_by.id)

   # userExists = User.objects.get(pk=postExists.posted_by)
    try:
        like = Like.objects.get(user=current_user, post=post_id)
        like.delete()
    except Like.DoesNotExist:
        like = Like()
        like.user = get_object_or_404(User, pk=current_user)
        like.post = get_object_or_404(Post, pk=post_id)
        like.save()
        notification = Notification()
        notification.user_to_notify = user_to_notify.id
        notification.user_who_fired_event = current_user
        notification.event_id = Event.objects.get(pk=2)
        notification.save()
    return redirect('/posts/' + str(post_id))

@login_required(login_url='/accounts/login')
def myposts(request):
    posts = Post.objects.filter(posted_by=get_object_or_404(User, pk=request.user.id)).order_by('-pub_date')
    return render(request, 'posts/my_post.html', {'posts': posts})