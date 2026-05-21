from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    bio = models.TextField(blank=True, default='', help_text='A short bio about yourself')

    def __str__(self):
        return f'{self.user.username} Profile'
