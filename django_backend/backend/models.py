from django.db import models

# Create your models here.
class IPCamera(models.Model):
    Source = models.CharField(max_length=150, default="", primary_key=True)
    Entrance_Code = models.CharField(max_length=5, default="")
    Entrance_Name = models.CharField(max_length=10, default="")

class history(models.Model):
    Timestamp = models.DateTimeField()
    Plate = models.CharField(max_length=7, default="")
    Entrance = models.CharField(max_length=5, default="")
    Color = models.CharField(max_length=2, default="")
    Image = models.CharField(max_length=10, default="")