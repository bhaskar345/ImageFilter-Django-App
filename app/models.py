from django.db import models

class Image(models.Model):
    Original=models.ImageField(null=True, blank=True)
    Img = models.ImageField(null=True,blank=True)