from abc import ABC

from cffi.backend_ctypes import xrange
from django.db import transaction
from django.http import Http404
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.views import APIView
import random
import string
from django.contrib.auth.models import User
from sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField

from users import models as user_model
from rest_framework import status
from references import models as ref_model
from farmers import models as farmer_model


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    gender = serializers.IntegerField()
    age = serializers.IntegerField()
    user_type = serializers.IntegerField()
    sum_id = serializers.IntegerField()
    province_id = serializers.IntegerField()
    fcm_id = serializers.CharField(required=False)

    def validate(self, data):
        try:
            user = User.objects.get(username=data.get('username'))
            if user:
                raise serializers.ValidationError(("Системд бүртгэлтэй байна"))
        except User.DoesNotExist:
            pass
        return data

    class Meta:
        model = User
        fields = ('username', 'password', 'is_active', 'user_type', 'name', 'gender', 'age', 'sum_id', 'province_id',
                  'fcm_id')
        extra_kwargs = {'user_type': {'read_only': True},
                        'name': {'read_only': True},
                        'gender': {'read_only': True},
                        'age': {'read_only': True},
                        'sum_id': {'read_only': True},
                        'province_id': {'read_only': True},
                        'fcm_id': {'read_only': True},
                        }


class PhoneConfirmCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ref_model.PhoneConfirmationCode
        fields = ('code', 'phone',)

    def update(self, instance, validated_data):
        if not instance.is_confirm and instance.is_active:
            instance.is_confirm = True
            instance.save()
            return instance
        else:
            raise serializers.ValidationError("code and phone does not much")


class ForgotConfirmCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ref_model.ForgotPassConfirmationCode
        fields = ('code', 'phone',)

    def update(self, instance, validated_data):
        if not instance.is_confirm and instance.is_active:
            instance.is_confirm = True
            instance.save()
            return instance
        else:
            raise serializers.ValidationError("code and phone does not much")


class ForgotNewPassSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_model.Role
        fields = ('user_type', 'username',)


class SumSerializer(serializers.ModelSerializer):
    class Meta:
        model = ref_model.RefSum
        fields = ('id', 'name', 'lat', 'lon')


class ProvinceListSerializer(serializers.ModelSerializer):
    sums = SumSerializer(many=True)

    class Meta:
        model = ref_model.RefProvince
        fields = ('id', 'name', 'sums')


class ProvinceNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ref_model.RefProvince
        fields = ('id', 'name')


class NewsFeedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ref_model.RefNewsFeed
        fields = ('id', 'name', 'topic')


class CropsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ref_model.Crop
        fields = ('id', 'name', 'icon',)


class CropsListAddSerializer(serializers.Serializer):
    crops = serializers.CharField()


class CropsUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ref_model.Crop
        fields = ('id',)


class ProfileFarmerStatsSerializer(serializers.Serializer):
    selling_count = serializers.IntegerField()
    crops_count = serializers.IntegerField()
    forums_count = serializers.IntegerField()
    fields_history_count = serializers.IntegerField()


class AppSubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = farmer_model.AppSubscriptions
        fields = ('id', 'end_at')


class FarmerProfileSerializer(serializers.ModelSerializer):
    active_subscription = AppSubscriptionsSerializer(many=False)
    image = HyperlinkedSorlImageField('52x52', options={"crop": "center"})

    class Meta:
        model = farmer_model.Farmer
        fields = ('user_id', 'username', 'type_name', 'role', 'role_name',
                  'name', 'ref_province', 'region_name', 'code', 'type', 'is_verified', 'image',
                  'has_subscription', 'active_subscription', 'has_trial', 'trial_end_at',)


class FarmerVerifyCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = farmer_model.Farmer
        fields = (
            'code', 'type', 'is_verified')


class UserNewsFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_model.NewsSubscriptions
        fields = ('feed', "fcm_id")


class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = farmer_model.Farmer
        fields = ('user', 'owner_name')


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(many=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'date_joined')


class MobileNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_model.Notifications
        fields = ('id', 'title', 'route', 'params', 'is_read', 'created_at')


def gen_random_string(char_set, length):
    if not hasattr(gen_random_string, "rng"):
        gen_random_string.rng = random.SystemRandom()  # Create a static variable
    return ''.join([gen_random_string.rng.choice(char_set) for _ in xrange(length)])


class NotificationsSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = user_model.Notifications
        fields = '__all__'
