from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction
from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('این شماره قبلاً ثبت‌نام کرده است')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        # The existence check in validate_phone() is not atomic with this
        # create: two concurrent signups for the same phone number can both
        # pass validation and race to create_user(). Without this guard the
        # loser of the race hits an unhandled IntegrityError (username is
        # unique) and the client gets a raw 500 instead of a clean error.
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=validated_data['phone'],
                    first_name=validated_data['name'],
                    password=validated_data['password'],
                )
        except IntegrityError:
            raise serializers.ValidationError(
                {'phone': 'این شماره قبلاً ثبت‌نام کرده است'}
            )
        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True)
