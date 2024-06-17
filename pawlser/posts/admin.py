from django.contrib import admin
from .models import Media, Post, Like, Comment

# Register your models here.
admin.site.register(Media)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)

