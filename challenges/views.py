from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from .models import Challenge, Category, Submission, Report
from django.contrib.auth.models import User
from users.models import Profile

def home(request):
    challenges = Challenge.objects.filter(is_approved=True).order_by('-created_at')[:3]
    total_users = User.objects.count()
    total_challenges = Challenge.objects.filter(is_approved=True).count()
    total_solves = Submission.objects.filter(is_correct=True).count()
    return render(request, 'home.html', {
        'challenges': challenges,
        'total_users': total_users,
        'total_challenges': total_challenges,
        'total_solves': total_solves,
    })

@login_required
def challenge_list(request):
    categories = Category.objects.all()
    challenges = Challenge.objects.filter(is_approved=True)
    solved_challenges = Submission.objects.filter(user=request.user, is_correct=True).values_list('challenge_id', flat=True)
    
    return render(request, 'challenges/challenge_list.html', {
        'categories': categories,
        'challenges': challenges,
        'solved_challenges': solved_challenges
    })

@login_required
def challenge_detail(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk, is_approved=True)
    already_solved = Submission.objects.filter(user=request.user, challenge=challenge, is_correct=True).exists()
    solve_count = Submission.objects.filter(challenge=challenge, is_correct=True).values('user').distinct().count()
    already_reported = Report.objects.filter(user=request.user, challenge=challenge).exists()
    
    if request.method == 'POST':
        if already_solved:
            messages.warning(request, "You have already solved this challenge.")
            return redirect('challenge_detail', pk=pk)
            
        submitted_flag = request.POST.get('flag')
        is_correct = (submitted_flag == challenge.flag)
        
        Submission.objects.create(
            user=request.user,
            challenge=challenge,
            submitted_flag=submitted_flag,
            is_correct=is_correct
        )
        
        if is_correct:
            profile = request.user.profile
            profile.total_score += challenge.points
            profile.save()
            messages.success(request, f"Correct! You earned {challenge.points} points.")
            return redirect('challenge_list')
        else:
            messages.error(request, "Incorrect flag. Try again.")
            
    return render(request, 'challenges/challenge_detail.html', {
        'challenge': challenge,
        'already_solved': already_solved,
        'solve_count': solve_count,
        'already_reported': already_reported,
    })

def leaderboard(request):
    import json
    top_profiles = Profile.objects.select_related('user').order_by('-total_score')[:10]
    max_score = top_profiles[0].total_score if top_profiles and top_profiles[0].total_score > 0 else 1
    
    # Build time-series data for each top user
    chart_data = []
    for profile in top_profiles:
        solves = Submission.objects.filter(
            user=profile.user, is_correct=True
        ).select_related('challenge').order_by('submitted_at')
        
        cumulative = 0
        points = [{'x': profile.user.date_joined.isoformat(), 'y': 0}]
        for s in solves:
            cumulative += s.challenge.points
            points.append({'x': s.submitted_at.isoformat(), 'y': cumulative})
        
        chart_data.append({
            'label': profile.user.username,
            'data': points,
        })
    
    return render(request, 'challenges/leaderboard.html', {
        'profiles': top_profiles,
        'max_score': max_score,
        'chart_data_json': json.dumps(chart_data),
    })

@login_required
def submit_challenge_user(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        points = request.POST.get('points')
        flag = request.POST.get('flag')
        writeup = request.POST.get('writeup', '')
        category_id = request.POST.get('category')
        
        # Validate writeup is provided
        if not writeup or not writeup.strip():
            messages.error(request, "You must provide a writeup for your challenge.")
            categories = Category.objects.all()
            return render(request, 'challenges/submit_challenge.html', {
                'categories': categories,
                'form_data': request.POST,
            })
        
        # Check if flag already exists in any challenge
        if Challenge.objects.filter(flag=flag).exists():
            messages.error(request, "This flag is already used by another challenge. Please use a unique flag.")
            categories = Category.objects.all()
            return render(request, 'challenges/submit_challenge.html', {
                'categories': categories,
                'form_data': request.POST,
            })
        
        category = get_object_or_404(Category, id=category_id)
        
        Challenge.objects.create(
            title=title,
            description=description,
            writeup=writeup,
            points=points,
            flag=flag,
            author=request.user,
            category=category,
            status='PENDING',
            is_approved=False
        )
        messages.success(request, "Challenge submitted! It will appear on the platform once approved by an admin.")
        return redirect('dashboard')
        
    categories = Category.objects.all()
    return render(request, 'challenges/submit_challenge.html', {'categories': categories})

@login_required
def report_challenge(request, pk):
    """Handle reporting a challenge."""
    if request.method == 'POST':
        challenge = get_object_or_404(Challenge, pk=pk, is_approved=True)
        
        # Check if user already reported this challenge
        if Report.objects.filter(user=request.user, challenge=challenge).exists():
            messages.warning(request, 'You have already reported this challenge.')
            return redirect('challenge_detail', pk=pk)
        
        reason = request.POST.get('reason', 'OTHER')
        details = request.POST.get('details', '')
        
        Report.objects.create(
            user=request.user,
            challenge=challenge,
            reason=reason,
            details=details,
        )
        
        messages.success(request, 'Report submitted successfully. An admin will review it.')
        return redirect('challenge_detail', pk=pk)
    
    return redirect('challenge_detail', pk=pk)

@user_passes_test(lambda u: u.is_superuser)
def admin_review_list(request):
    pending_challenges = Challenge.objects.filter(status='PENDING').order_by('-created_at')
    reports = Report.objects.filter(is_resolved=False).select_related('user', 'challenge').order_by('-created_at')
    return render(request, 'challenges/admin_review.html', {
        'pending_challenges': pending_challenges,
        'reports': reports,
    })

@user_passes_test(lambda u: u.is_superuser)
def admin_challenge_detail(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    reports = Report.objects.filter(challenge=challenge).select_related('user').order_by('-created_at')
    return render(request, 'challenges/admin_challenge_detail.html', {
        'challenge': challenge,
        'reports': reports,
    })

@user_passes_test(lambda u: u.is_superuser)
def approve_challenge(request, pk):
    if request.method == 'POST':
        challenge = get_object_or_404(Challenge, pk=pk)
        challenge.is_approved = True
        challenge.status = 'APPROVED'
        challenge.save()
        messages.success(request, f"Challenge '{challenge.title}' has been approved.")
    return redirect('admin_review')

@user_passes_test(lambda u: u.is_superuser)
def reject_challenge(request, pk):
    if request.method == 'POST':
        challenge = get_object_or_404(Challenge, pk=pk)
        rejection_reason = request.POST.get('rejection_reason')
        challenge.status = 'REJECTED'
        challenge.is_approved = False
        challenge.rejection_reason = rejection_reason
        challenge.save()
        messages.warning(request, f"Challenge '{challenge.title}' has been rejected.")
    return redirect('admin_review')

@user_passes_test(lambda u: u.is_superuser)
def resolve_report(request, pk):
    if request.method == 'POST':
        report = get_object_or_404(Report, pk=pk)
        report.is_resolved = True
        report.save()
        messages.success(request, "Report has been resolved.")
    return redirect('admin_review')
