from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Profile, Media, Post, Like, Comment
from .serializers import (
    ProfileSerializer, UserSerializer, MediaSerializer,
    PostSerializer, LikeSerializer, CommentSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        profile = self.get_object()
        user_profile = request.user.profile
        if profile != user_profile:
            if profile.followers.filter(id=user_profile.id).exists():
                profile.followers.remove(user_profile)
            else:
                profile.followers.add(user_profile)
            profile.save()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        media_files = request.FILES.getlist('files')
        response_data = []
        for file in media_files:
            media_instance = Media.objects.create(file=file, uploaded_by=request.user)
            response_data.append(MediaSerializer(media_instance).data)
        return Response(response_data, status=status.HTTP_201_CREATED)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        media_ids = data.pop('media_ids', [])
        tagged_user_ids = data.pop('tagged_people_ids', [])
        post = Post.objects.create(created_by=request.user, **data)
        post.media.set(Media.objects.filter(id__in=media_ids))
        post.tagged_people.set(User.objects.filter(id__in=tagged_user_ids))
        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        like, created = Like.objects.get_or_create(post_id=data['post'], liked_by=request.user)
        if not created:
            return Response({'detail': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        comment = Comment.objects.create(commented_by=request.user, **data)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        Profile.objects.create(user=user)
        return Response({'success': 'User created successfully'}, status=status.HTTP_201_CREATED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
