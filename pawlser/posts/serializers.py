from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Media, Post, Like, Comment

class ProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)

    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'followers', 'followers_count', 'following_count']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    tagged_people = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    liked_by = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    commented_by = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
