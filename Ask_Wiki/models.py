from django.db import models

# Create your models here.
class Wiki(models.Model):

  title = models.CharField(max_length=20)
  summary = models.TextField()