import math
import random
import uuid
from datetime import date, datetime
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from twilio.rest import Client
from django.conf import settings

# Create your views here.
from accounts.models import User, MobileVerification, Follower, Notification, Event
from posts.models import Post, Like


def signup(request):
    if request.method == 'POST':
        if request.POST['password'] == request.POST['confirm_password']:
            try:
                user = User.objects.get(email=request.POST['email'])
                # user = User.objects.get(email=request.POST['email'])
                # user = User.objects.get(contact_number=request.POST['contact_number'])
                return render(request, 'register/signup.html',{'error': 'Email has been already been taken'})
            except User.DoesNotExist:
                user= User.objects.create_user(request.POST['email'],request.POST['username'],request.POST['contact_number'], password= request.POST['password'])
                auth.login(request,user)
                return redirect('home')
        else:
            return render(request, 'register/signup.html', {'error': 'Passwords must match'})
    else:
        return render(request, 'register/signup.html')

def login(request):
    if request.method == 'POST':
        user = auth.authenticate(email=request.POST['email'],password= request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            return render(request, 'login/login.html', {'error': 'Username or Password is incorrect.'})
    else:
        return render(request, 'login/login.html')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')

@login_required(login_url='/account/login')
def findUsers(request):
    users = User.objects.filter(username__startswith=request.GET['startwith']).exclude(id=request.user.id).exclude(is_superuser=True).order_by('username').values()
    return JsonResponse({"users": list(users)})

@login_required(login_url='/account/login')
def profile(request):
    current_user = request.user
    following = Follower.objects.filter(user_from=current_user)
    followers = Follower.objects.filter(user_to=current_user)
    return render(request, 'profile/profile.html',{
        'following': following,
        'followers': followers
    })

@login_required(login_url='/account/login')
def uploadProfilePic(request):
    user = request.user
    profile_pic = request.FILES.get('profile_pic', None)
    if profile_pic:
        user.profile_pic = profile_pic
        user.save()
    return redirect('profile')

@login_required(login_url='/account/login')
def verify(request):
    user = get_object_or_404(User, id=request.user.id)
    if user.verified == True:
        messages.success(request, 'Already Verified')
        return redirect('profile')
    # created_at = otpExist.created_at
    # created_at = created_at.replace(tzinfo=None)
    # today = datetime.today()
    # minDiff = today - created_at
    #
    # minDiff = math.floor(minDiff.total_seconds() / 60)
    # if minDiff > 45:
    if request.method == 'POST':
        print(request.POST['opt_number'])
        if request.POST['opt_number']:
            otpExist = get_object_or_404(MobileVerification, user=request.user)
            if int(otpExist.otp) == int(request.POST['opt_number']):
                user = get_object_or_404(User, id = request.user.id)
                user.verified = True
                user.save()
                messages.success(request, 'Verified')
                return redirect('verify')
            else:
                return render(request, 'register/verify.html', {'error': 'Not a valid OTP'})
        else:
            return render(request, 'register/verify.html', {'error': 'Not a valid OTP'})
    return render(request, 'register/verify.html')

@login_required(login_url='/account/login')
def sendOtp(request):
    try:
        otpExist = MobileVerification.objects.get(user=request.user)
        if otpExist:
            otpExist.delete()
    except MobileVerification.DoesNotExist:
        pass
    otp = generateOTP()
    current_user_contact_number = request.user.contact_number
    # print(current_user_contact_number)
    current_user_contact_number = '+91' + current_user_contact_number

    sendOTP(otp, current_user_contact_number)

    mobileVerification = MobileVerification()
    mobileVerification.user = request.user
    mobileVerification.otp = otp
    mobileVerification.save()
    messages.success(request, 'Verification code has been sent.')
    return redirect('verify')

@login_required(login_url='/account/login')
def changePassword(request):
    if request.method == 'POST':
        if request.POST['password'] == request.POST['confirm-password']:
            u = User.objects.get(username=request.user.username)
            u.set_password(request.POST['password'])
            u.save()
            update_session_auth_hash(request, u)
            messages.success(request, 'Password successfully changed.')
            # messages.debug(request, '%s SQL statements were executed.' % count)
            # messages.info(request, 'Three credits remain in your account.')
            # messages.success(request, 'Profile details updated.')
            # messages.warning(request, 'Your account expires in three days.')
            # messages.error(request, 'Document deleted.')
            return render(request, 'profile/change-password.html')
        else:
            return render(request, 'profile/change-password.html', {'error': 'It looks like that your entered Password does not match with Confirm Password!'})
    else:
        return render(request, 'profile/change-password.html')

@login_required(login_url='/account/login')
def following(request):
    current_user = request.user
    followings = Follower.objects.filter(user_from=current_user)
    return render(request, 'profile/following.html',{'followings': followings})

@login_required(login_url='/account/login')
def followers(request):
    current_user = request.user
    followers = Follower.objects.filter(user_to=current_user)
    return render(request, 'profile/followers.html',{'followers': followers})

@login_required(login_url='/account/login')
def viewUserProfile(request, username):
    userData = User.objects.get(username=username)# for getting single entry fron database
    if userData ==  request.user:
        return redirect('profile')
    #userData = User.objects.filter(username=username)# for getting multiple entry fron database
    followers = Follower.objects.filter(user_to=userData)
    followings = Follower.objects.filter(user_from=userData)
    posts = Post.objects.filter(posted_by=userData).values()
    for post in posts:
        post['total_likes'] = Like.objects.filter(post=post['id'])
        post['total_likes'] = len(post['total_likes'])
        liked_by_loggedin_user = Like.objects.filter(post=post['id'], user = request.user.id)
        post['liked_by_loggedin_user'] = False
        if liked_by_loggedin_user:
            post['liked_by_loggedin_user'] = True
        posted_by = User.objects.get(id=post['posted_by_id'])
        post['posted_by'] = posted_by.username
        post['posted_by_profile_pic'] = posted_by.profile_pic

    loggedInUserFollow = Follower.objects.filter(user_to=userData, user_from = request.user)
    followedByLoggedInUser = True
    if not loggedInUserFollow:
        followedByLoggedInUser = False
    return render(request, 'profile/view-profile.html',{
        'viewUser': userData,
        'followers' : followers,
        'followings': followings,
        'posts': list(posts),
        'followedByLoggedInUser':followedByLoggedInUser
    })

@login_required(login_url='/account/login')
def follow(request, user_id):
    current_user = request.user
    userExists = User.objects.get(pk=user_id)
    if userExists:
        follower = Follower()
        follower.user_from = current_user
        follower.user_to = userExists
        follower.save()
        notification = Notification()
        notification.user_to_notify = userExists
        notification.user_who_fired_event = current_user
        notification.event_id = Event.objects.get(pk=1)
        notification.save()
    return redirect('viewUserProfile' , username =userExists.username)

@login_required(login_url='/account/login')
def unfollow(request, user_id):
    current_user = request.user
    userExists = User.objects.get(pk=user_id)
    if userExists:
        follower = Follower.objects.filter(user_to=userExists, user_from= current_user)
        follower.delete()
    return redirect('viewUserProfile' , username =userExists.username)

# def notifications(request):
#     current_user = request.user
#     userNotifications = Notification.objects.filter(user_to_notify=current_user,seen_by_user=False).order_by('-created_at').values()
#     for user in userNotifications:
#         user['user_to_notify_name'] =  get_object_or_404(User, pk=user['user_to_notify_id']).username
#         user['user_who_fired_event_name'] =  get_object_or_404(User, pk=user['user_who_fired_event_id']).username
#         user_profile = User.objects.filter(id=user['user_who_fired_event_id']).values()
#         for user_profile_pic in user_profile:
#             user['profile_pic'] = user_profile_pic['profile_pic']
#         user['event_comment'] = get_object_or_404(Event, pk=user['event_id_id']).comment
#     return JsonResponse({"userNotifications": list(userNotifications)})

@login_required(login_url='/account/login')
def allNotifications(request):
    current_user = request.user
    notifications = Notification.objects.filter(user_to_notify = current_user).order_by('-created_at')
    return render(request, 'profile/notifications.html',{'notifications': notifications})


def sendOTP(otp, current_user_contact_number):
    account_sid = "AC7aa621f3e57483b996466b9d163fc48d"
    # Your Auth Token from twilio.com/console
    auth_token = settings.AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+917508332062",
        from_="+18036755617",
        body="Your 6 digit verification code is " + otp)
    print(message)
    return True

def generateOTP():
    # Declare a digits variable
    # which stores all digits
    digits = "0123456789"
    OTP = ""

    # length of password can be chaged
    # by changing value in range
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]

    return OTP

def myNotifications(request):
    current_user = request.user
    if not request.user.is_authenticated:
        return {}
    userNotifications = Notification.objects.filter(user_to_notify=current_user,seen_by_user=False).order_by('-created_at').values()
    for user in userNotifications:
        user['user_to_notify_name'] =  get_object_or_404(User, pk=user['user_to_notify_id']).username
        user['user_who_fired_event_name'] =  get_object_or_404(User, pk=user['user_who_fired_event_id']).username
        user_profile = User.objects.filter(id=user['user_who_fired_event_id']).values()
        for user_profile_pic in user_profile:
            user['profile_pic'] = user_profile_pic['profile_pic']
        user['event_comment'] = get_object_or_404(Event, pk=user['event_id_id']).comment
    return {
            "userNotifications": list(userNotifications)
    }
