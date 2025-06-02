from rest_framework import serializers
from .models import Author, Follow


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model"""

    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id', 'username', 'display_name', 'email',
            'bio', 'github', 'profile_image', 'url', 'host',
            'is_remote', 'role', 'is_approved',
            'followers_count', 'following_count',
            'created_at'
        ]
        # Don't expose these fields in the API response
        read_only_fields = ['id', 'url', 'host', 'is_remote', 'created_at']

    def get_followers_count(self, obj):
        return obj.followers_set.filter(is_accepted=True).count()

    def get_following_count(self, obj):
        return obj.following_set.filter(is_accepted=True).count()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Author
        fields = ['username', 'email', 'password', 'password2', 'display_name']

    def validate(self, data):
        # Make sure passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        # Remove password2 before creating user
        validated_data.pop('password2')
        password = validated_data.pop('password')

        # Create user but don't approve them yet
        # Admin needs to approve new accounts
        user = Author(**validated_data)
        user.set_password(password)
        user.is_approved = False  # needs admin approval
        user.save()
        return user


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for follow relationships"""

    follower_info = AuthorSerializer(source='follower', read_only=True)
    following_info = AuthorSerializer(source='following', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'follower_info', 'following_info', 'is_accepted', 'created_at']
        read_only_fields = ['id', 'created_at']
