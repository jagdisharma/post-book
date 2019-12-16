import math
import random
from datetime import date, datetime
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from twilio.rest import Client

# Create your views here.
from accounts.models import User, MobileVerification, Follower, Notification, Event
from posts.models import Post


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
        user = auth.authenticate(username=request.POST['username'],password= request.POST['password'])
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

@login_required(login_url='/accounts/login')
def profile(request):
    current_user = request.user
    following = Follower.objects.filter(user_from=current_user)
    followers = Follower.objects.filter(user_to=current_user)
    return render(request, 'profile/profile.html',{
        'following': following,
        'followers': followers
    })

@login_required(login_url='/accounts/login')
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

@login_required(login_url='/accounts/login')
def sendOtp(request):
    # otpExist = get_object_or_404(MobileVerification, user=request.user)
    # if otpExist:
    #     otpExist.delete()
    otp = generateOTP()
    current_user_contact_number = request.user.contact_number
    current_user_contact_number = '+91' + current_user_contact_number

    sendOTP(otp, current_user_contact_number)

    mobileVerification = MobileVerification()
    mobileVerification.user = request.user
    mobileVerification.otp = otp
    mobileVerification.save()
    messages.success(request, 'Verification code has been sent.')
    return redirect('verify')

@login_required(login_url='/accounts/login')
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

@login_required(login_url='/accounts/login')
def following(request):
    current_user = request.user
    followings = Follower.objects.filter(user_from=current_user)
    return render(request, 'profile/following.html',{'followings': followings})

@login_required(login_url='/accounts/login')
def followers(request):
    current_user = request.user
    followers = Follower.objects.filter(user_to=current_user)
    return render(request, 'profile/followers.html',{'followers': followers})

@login_required(login_url='/accounts/login')
def viewUserProfile(request, username):
    userData = User.objects.get(username=username)# for getting single entry fron database
    if userData ==  request.user:
        return redirect('profile')
    #userData = User.objects.filter(username=username)# for getting multiple entry fron database
    followers = Follower.objects.filter(user_to=userData)
    followings = Follower.objects.filter(user_from=userData)
    posts = Post.objects.filter(posted_by=userData)

    loggedInUserFollow = Follower.objects.filter(user_to=userData, user_from = request.user)
    followedByLoggedInUser = True
    if not loggedInUserFollow:
        followedByLoggedInUser = False
    return render(request, 'profile/view-profile.html',{
        'viewUser': userData,
        'followers' : followers,
        'followings': followings,
        'posts': posts,
        'followedByLoggedInUser':followedByLoggedInUser
    })

@login_required(login_url='/accounts/login')
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

@login_required(login_url='/accounts/login')
def unfollow(request, user_id):
    current_user = request.user
    userExists = User.objects.get(pk=user_id)
    if userExists:
        follower = Follower.objects.filter(user_to=userExists, user_from= current_user)
        follower.delete()
    return redirect('viewUserProfile' , username =userExists.username)

@login_required(login_url='/accounts/login')
def notifications(request):
    current_user = request.user
    userNotifications = Notification.objects.filter(user_to_notify=current_user,seen_by_user=False).order_by('-created_at').values()
    for user in userNotifications:
        user['user_to_notify_name'] =  get_object_or_404(User, pk=user['user_to_notify_id']).username
        user['user_who_fired_event_name'] =  get_object_or_404(User, pk=user['user_who_fired_event_id']).username
    return JsonResponse({"userNotifications": list(userNotifications)})

@login_required(login_url='/accounts/login')
def allNotifications(request):
    current_user = request.user
    notifications = Notification.objects.filter(user_to_notify = current_user).order_by('-created_at')
    return render(request, 'profile/notifications.html',{'notifications': notifications})


def sendOTP(otp, current_user_contact_number):
    account_sid = "ACfbe1c1a1f6862727cdd0fdf99df03474"
    # Your Auth Token from twilio.com/console
    auth_token = "2b7d95100ee26edb22e815b04897f5e8"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+917508332062",
        from_="+13343578105",
        body="Your 6 digit verification code is " + otp)
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

