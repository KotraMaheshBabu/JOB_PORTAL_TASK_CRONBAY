from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from .models import JobPosting, Bid, UserProfile
from .forms import JobPostingForm, BidForm, UserRegistrationForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect

def home(request):
    # Get 10 most recent job postings
    recent_jobs = JobPosting.objects.filter(
        is_active=True,
        expiration_date__gt=timezone.now()
    ).order_by('-posted_date')[:10]
    
    # Get top 10 most active jobs (by number of bids)
    active_jobs = JobPosting.objects.filter(
        is_active=True,
        expiration_date__gt=timezone.now()
    ).annotate(
        bid_count=Count('bids')
    ).order_by('-bid_count')[:10]
    
    return render(request, 'job_portal/home.html', {
        'recent_jobs': recent_jobs,
        'active_jobs': active_jobs
    })

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.poster = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobPostingForm()
    
    return render(request, 'job_portal/post_job.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Job Marketplace!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'job_portal/register.html', {'form': form})

def custom_logout(request):
    # Store the referring URL in the session before logout
    next_page = request.GET.get('next')
    if not next_page:
        next_page = request.META.get('HTTP_REFERER')
    
    if next_page:
        # Clean the URL to prevent open redirect vulnerability
        from urllib.parse import urlparse
        url_parts = urlparse(next_page)
        if not url_parts.netloc:  # Only accept relative URLs
            request.session['logout_redirect'] = next_page
    
    # Perform logout
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    
    # Get the stored redirect URL from session
    redirect_url = request.session.pop('logout_redirect', None)
    
    if redirect_url:
        return HttpResponseRedirect(redirect_url)
    return redirect('home')

def job_detail(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)
    
    # Check if auction is expired
    if job.is_expired() and job.is_active:
        job.is_active = False
        winning_bid = job.get_lowest_bid()
        if winning_bid:
            job.winner = winning_bid.bidder
        job.save()
    
    if request.method == 'POST' and request.user.is_authenticated:
        bid_form = BidForm(request.POST)
        if bid_form.is_valid() and not job.is_expired():
            bid = bid_form.save(commit=False)
            bid.job = job
            bid.bidder = request.user
            bid.save()
            messages.success(request, 'Bid placed successfully!')
            return redirect('job_detail', pk=pk)
    else:
        bid_form = BidForm()
    
    context = {
        'job': job,
        'bid_form': bid_form,
        'lowest_bid': job.get_lowest_bid(),
        'bid_count': job.get_bid_count()
    }
    
    return render(request, 'job_portal/job_detail.html', context)
