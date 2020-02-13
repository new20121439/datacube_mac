from django.db import models

# Create your models here.
class DownloadTaskk(models.Model):
    uuid = models.CharField(max_length=100, default="", primary_key=True)
    title = models.CharField(max_length=100, default="")
    
