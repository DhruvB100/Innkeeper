"""
Custom JWT authentication that checks if the user is approved before
allowing them to log in.

The default DRF JWT doesn't check for our is_approved field so we need
to override the token generation to add that check.
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import PermissionDenied


class InkeeperTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer that checks if the user account is approved
    before issuing tokens.
    """

    def validate(self, attrs):
        # Call parent validation first (checks username/password)
        data = super().validate(attrs)

        # Check if the user is approved
        if not self.user.is_approved:
            raise PermissionDenied(
                'Your account is pending approval. Please wait for an admin to approve your account.'
            )

        # Add some extra user info to the token response
        data['username'] = self.user.username
        data['user_id'] = str(self.user.id)
        data['role'] = self.user.role
        data['is_approved'] = self.user.is_approved

        return data


class InkeeperTokenObtainPairView(TokenObtainPairView):
    """Use our custom serializer"""
    serializer_class = InkeeperTokenObtainPairSerializer
