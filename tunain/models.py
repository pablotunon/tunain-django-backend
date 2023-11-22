from django.contrib.auth.models import AbstractUser
from django.contrib import admin
from django.db import models


class AppUser(AbstractUser):
    # Custom user model so it's easy to extend if needed
    pass

admin.site.register(AppUser)

class Book(models.Model):
    system_prompt = models.CharField(max_length=1024)
    initial_input = models.CharField(max_length=256)
    genre = models.CharField(blank=True, null=True, max_length=256)
    art_extra_prompt = models.CharField(blank=True, null=True, max_length=512)
    owner = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.DO_NOTHING)
    views = models.IntegerField()

admin.site.register(Book)

class Page(models.Model):
    book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.DO_NOTHING)
    number = models.IntegerField()
    content = models.JSONField()
    image_url = models.CharField(null=True, blank=True, max_length=256)
    user_input = models.CharField(null=True, blank=True, max_length=256)
    next_page = models.ForeignKey('Page', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='previous_page')
    alternative_to = models.ForeignKey('Page', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='original')
    owner = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.DO_NOTHING)
    views = models.IntegerField()

admin.site.register(Page)
