from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class Challenge(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    writeup = models.TextField(blank=True, help_text='Writeup explaining the challenge solution approach')
    points = models.IntegerField(default=10)
    flag = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='authored_challenges')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='challenges')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    submitted_flag = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.challenge.title} - {"Correct" if self.is_correct else "Incorrect"}'

class Report(models.Model):
    REASON_CHOICES = [
        ('INCORRECT_FLAG', 'Incorrect Flag'),
        ('DUPLICATE', 'Duplicate Challenge'),
        ('INAPPROPRIATE', 'Inappropriate Content'),
        ('UNCLEAR', 'Unclear Description'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge')
        ordering = ['-created_at']

    def __str__(self):
        return f'Report by {self.user.username} on {self.challenge.title}'
