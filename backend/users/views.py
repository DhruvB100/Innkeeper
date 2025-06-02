from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Author, Follow
from .serializers import AuthorSerializer, RegisterSerializer, FollowSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Creates a new author account. Account needs to be approved by admin before
    they can actually use the platform.
    """
    queryset = Author.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': 'Account created! Waiting for admin approval before you can log in.',
            'username': user.username,
        }, status=status.HTTP_201_CREATED)


class AuthorListView(generics.ListAPIView):
    """
    GET /api/authors/
    Returns list of all approved authors on this node
    """
    serializer_class = AuthorSerializer
    # Anyone can see the list of authors, even without logging in
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Only show local approved authors
        return Author.objects.filter(is_remote=False, is_approved=True)


class AuthorDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/authors/<id>/  - Get author profile
    PUT /api/authors/<id>/  - Update author profile (only own profile)
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        # Only allow updating your own profile
        author = self.get_object()
        if author != request.user:
            return Response(
                {'error': 'You can only edit your own profile'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class FollowView(APIView):
    """
    POST /api/authors/<id>/follow/
    Send a follow request to an author
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            target_author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)

        # Can't follow yourself
        if target_author == request.user:
            return Response({'error': "You can't follow yourself"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already following
        existing = Follow.objects.filter(follower=request.user, following=target_author).first()
        if existing:
            return Response({'error': 'Already following this author'}, status=status.HTTP_400_BAD_REQUEST)

        # Create follow request
        follow = Follow.objects.create(
            follower=request.user,
            following=target_author,
            is_accepted=False  # needs to be accepted
        )

        return Response({
            'message': f'Follow request sent to {target_author.username}',
            'follow_id': str(follow.id)
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """Unfollow an author"""
        try:
            target_author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)

        follow = Follow.objects.filter(follower=request.user, following=target_author).first()
        if not follow:
            return Response({'error': 'Not following this author'}, status=status.HTTP_400_BAD_REQUEST)

        follow.delete()
        return Response({'message': 'Unfollowed successfully'}, status=status.HTTP_200_OK)


class FollowersListView(generics.ListAPIView):
    """GET /api/authors/<id>/followers/ - Get all followers of an author"""
    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        author_id = self.kwargs['pk']
        return Follow.objects.filter(following_id=author_id, is_accepted=True)


class FollowingListView(generics.ListAPIView):
    """GET /api/authors/<id>/following/ - Get all authors that this author is following"""
    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        author_id = self.kwargs['pk']
        return Follow.objects.filter(follower_id=author_id, is_accepted=True)


@api_view(['GET'])
def current_user(request):
    """GET /api/auth/me/ - Get current logged in user info"""
    if not request.user.is_authenticated:
        return Response({'error': 'Not logged in'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = AuthorSerializer(request.user)
    return Response(serializer.data)


class AcceptFollowView(APIView):
    """
    POST /api/authors/<id>/followers/<follower_id>/accept/
    Accept a follow request (only author can accept their own follow requests)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, follower_id):
        # Make sure the current user is the one being followed
        if str(request.user.pk) != str(pk):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            follow = Follow.objects.get(follower_id=follower_id, following_id=pk)
        except Follow.DoesNotExist:
            return Response({'error': 'Follow request not found'}, status=status.HTTP_404_NOT_FOUND)

        follow.is_accepted = True
        follow.save()

        return Response({'message': 'Follow request accepted'})
