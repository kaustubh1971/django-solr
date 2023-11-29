from django.db import models

# Create your models here.

class JobApplication(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    why_us = models.TextField(blank=True, null=True)
    why_you = models.TextField(blank=True, null=True)
    social_profile_link = models.CharField(max_length=255, blank=True, null=True)
    resume_link = models.CharField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    # other_role = models.CharField(max_length=255, blank=True, null=True)
    other_role = models.CharField(max_length=255, blank=True)
    experience = models.IntegerField(blank=True, null=True)
    preferred_location = models.CharField(max_length=100, blank=True, null=True)
    preferred_time_for_call = models.CharField(max_length=255, blank=True, null=True)
    # current_ctc = models.CharField(max_length=255, blank=True, null=True)
    current_ctc = models.IntegerField(blank=True, null=True)
    # notice_period = models.CharField(max_length=255, blank=True, null=True)
    notice_period = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.email
