from django.db import models

# Create your models here.

class BotoCache(models.Model):
    key = models.TextField(primary_key=True)
    e_tag = models.TextField()
    data = models.TextField()
