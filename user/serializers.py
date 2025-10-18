from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Address

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('mobile_number', 'alternate_mobile_number', 'password', 'password_confirm', 'first_name', 'last_name', 'email')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=10)
    password = serializers.CharField(write_only=True)

class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer that conditionally includes admin fields
    based on the requesting user's permissions
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'mobile_number', 'alternate_mobile_number', 'email',
                 'first_name', 'last_name', 'full_name', 'profile_picture',
                 'is_active', 'date_joined')
        read_only_fields = ('id', 'mobile_number', 'date_joined', 'full_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the request from context
        request = self.context.get('request')

        # Only include admin fields if the requesting user is staff or superuser
        if request and request.user and request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                # Add admin fields to the serializer
                self.fields['is_staff'] = serializers.BooleanField(read_only=True)
                self.fields['is_superuser'] = serializers.BooleanField(read_only=True)

                # Update Meta fields to include admin fields
                self.Meta.fields = self.Meta.fields + ('is_staff', 'is_superuser')

    def to_representation(self, instance):
        """
        Override to ensure admin fields are only included for authorized users
        """
        data = super().to_representation(instance)

        request = self.context.get('request')

        # Double-check: remove admin fields if user doesn't have permission
        if not (request and request.user and request.user.is_authenticated and
                (request.user.is_staff or request.user.is_superuser)):
            data.pop('is_staff', None)
            data.pop('is_superuser', None)

        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information
    """
    class Meta:
        model = CustomUser
        fields = ('alternate_mobile_number', 'email', 'first_name', 'last_name', 'profile_picture')

    def validate_email(self, value):
        """
        Validate that email is unique if provided
        """
        if value:
            user = self.instance
            if CustomUser.objects.filter(email=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Admin-only serializer for managing users with full access to admin fields
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'mobile_number', 'alternate_mobile_number', 'email',
                 'first_name', 'last_name', 'full_name', 'profile_picture',
                 'is_active', 'is_staff', 'is_superuser', 'date_joined')
        read_only_fields = ('id', 'mobile_number', 'date_joined', 'full_name')

    def validate(self, data):
        """
        Validate admin field changes
        """
        # Prevent removing superuser status from the last superuser
        if 'is_superuser' in data and not data['is_superuser']:
            if self.instance and self.instance.is_superuser:
                superuser_count = CustomUser.objects.filter(is_superuser=True).count()
                if superuser_count <= 1:
                    raise serializers.ValidationError(
                        "Cannot remove superuser status from the last superuser in the system."
                    )

        # Ensure superusers are also staff
        if data.get('is_superuser', False) and not data.get('is_staff', self.instance.is_staff if self.instance else False):
            data['is_staff'] = True

        return data


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'name', 'address', 'pincode', 'city', 'state', 'country', 'is_default')
        read_only_fields = ('id',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
