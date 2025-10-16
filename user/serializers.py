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

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'name', 'address', 'pincode', 'city', 'state', 'country', 'is_default')
        read_only_fields = ('id',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
