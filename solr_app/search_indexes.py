from haystack import indexes
from .models import JobApplication

class JobApplicationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True,
        use_template=True,
        # template_name="myapp/myapp.txt"
    )
    name = indexes.CharField(model_attr='name', default='')
    email = indexes.CharField(model_attr='email')
    why_us = indexes.CharField(model_attr='why_us', default='')
    why_you = indexes.CharField(model_attr='why_you', default='')
    social_profile_link = indexes.CharField(model_attr='social_profile_link', default='')
    resume_link = indexes.CharField(model_attr='resume_link', default='')
    mobile_number = indexes.CharField(model_attr='mobile_number', default='')
    role = indexes.CharField(model_attr='role')
    other_role = indexes.CharField(model_attr='other_role', default='')
    experience = indexes.IntegerField(model_attr='experience', default=0)
    preferred_location = indexes.CharField(model_attr='preferred_location', default='')
    preferred_time_for_call = indexes.CharField(model_attr='preferred_time_for_call', default='')
    current_ctc = indexes.IntegerField(model_attr='current_ctc', default=0)
    notice_period = indexes.IntegerField(model_attr='notice_period', default=0)
    timestamp = indexes.DateTimeField(model_attr='timestamp')
    def get_model(self):
        return JobApplication

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
