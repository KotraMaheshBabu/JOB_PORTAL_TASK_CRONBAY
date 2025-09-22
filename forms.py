from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import JobPosting, Bid, UserProfile

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'requirements', 'expiration_date']
        widgets = {
            'expiration_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 5}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'})
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Bid amount must be greater than zero.")
        return amount

class UserRegistrationForm(UserCreationForm):
    contact_info = forms.CharField(max_length=200, required=True)
    is_bidder = forms.BooleanField(required=False, initial=False, label='Register as a Bidder')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'contact_info', 'is_bidder')

    def save(self, commit=True):
        user = super().save(commit=True)
        profile = UserProfile.objects.create(
            user=user,
            contact_info=self.cleaned_data['contact_info'],
            is_bidder=self.cleaned_data['is_bidder']
        )
        return user
