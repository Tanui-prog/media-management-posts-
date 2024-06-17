from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    def __str__(self):
        return self.user.username

class Media(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    )
    file = models.FileField(upload_to='posts_files/')
    media_type = models.CharField(choices=MEDIA_TYPE_CHOICES, max_length=10)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.media_type} - {self.file.name}'

class Post(models.Model):
    POST_TYPE_CHOICES = (
        ('status', 'Status'),
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('location', 'Location'),
        ('gif', 'GIF'),
        ('live_event', 'Live Event'),
        ('feeling', 'Feeling'),
        ('tagged', 'Tagged'),
    )
    content = models.TextField(blank=True)
    post_type = models.CharField(choices=POST_TYPE_CHOICES, max_length=20, default='status')
    location = models.CharField(max_length=255, blank=True)
    feeling = models.CharField(max_length=50, blank=True)
    tagged_people = models.ManyToManyField(User, related_name='tagged_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.ManyToManyField(Media, related_name='posts', blank=True)

    def __str__(self):
        return f'Post by {self.created_by.username} at {self.created_at}'

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Like by {self.liked_by.username} on {self.post.id}'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.commented_by.username} on {self.post.id}'
