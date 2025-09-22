from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=16384)  # 16KB limit
    requirements = models.TextField(max_length=16384)  # 16KB limit
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    posted_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_jobs')
    
    def is_expired(self):
        return timezone.now() >= self.expiration_date
    
    def get_lowest_bid(self):
        return self.bids.order_by('amount').first()
    
    def get_bid_count(self):
        return self.bids.count()

    def __str__(self):
        return self.title

class Bid(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['amount']

    def __str__(self):
        return f"{self.bidder.username} - ${self.amount} on {self.job.title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_info = models.CharField(max_length=200)
    is_bidder = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
