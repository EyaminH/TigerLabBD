from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from challenges.models import Submission, Challenge

from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}! You can now login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def dashboard(request):
    submissions = Submission.objects.filter(user=request.user).order_by('-submitted_at')
    solved_count = submissions.filter(is_correct=True).count()
    authored_challenges = request.user.authored_challenges.all().order_by('-created_at')
    
    return render(request, 'users/dashboard.html', {
        'submissions': submissions,
        'solved_count': solved_count,
        'authored_challenges': authored_challenges
    })

def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    
    solved_submissions = Submission.objects.filter(
        user=profile_user, is_correct=True
    ).select_related('challenge', 'challenge__category').order_by('-submitted_at')
    
    authored_challenges = Challenge.objects.filter(
        author=profile_user, is_approved=True
    ).select_related('category').order_by('-created_at')
    
    solved_count = solved_submissions.values('challenge').distinct().count()
    authored_count = authored_challenges.count()
    
    return render(request, 'users/public_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'solved_submissions': solved_submissions[:10],
        'authored_challenges': authored_challenges[:10],
        'solved_count': solved_count,
        'authored_count': authored_count,
    })
