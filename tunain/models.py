from django.db import models

class Book(models.Model):
    pass

class Page(models.Model):
    book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.DO_NOTHING)
    number = models.IntegerField()
    content = models.JSONField()
    user_input = models.CharField(max_length=256)
    next_page = models.ForeignKey('Page', null=True, blank=True, on_delete=models.DO_NOTHING)
    alternative_to = models.ForeignKey('Page', null=True, blank=True, on_delete=models.DO_NOTHING)
