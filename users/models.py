import django
from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property

from references import models as ref_models


class Role(models.Model):
    AGRONOMER = 'AGRONOMER'
    SPECIALIST = 'SPECIALIST'
    FARMER = 'FARMER'
    NORMAL = 'NORMAL'
    ADMIN = 'ADMIN'
    TYPES = (
        (AGRONOMER, 'Агрономич'),
        (FARMER, 'Тариаланч'),
        (NORMAL, 'Энгийн хэрэглэгч'),
        (SPECIALIST, 'Мэргэжилтэн'),
        (ADMIN, 'БОСС'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=TYPES, default=NORMAL)
    is_register_finish = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Role'

    @cached_property
    def role_name(self):
        return dict(self.TYPES)[str(self.user_type)]

    @cached_property
    def is_admin(self):
        return self.user_type == self.ADMIN

    @cached_property
    def is_specialist(self):
        return self.user_type == self.SPECIALIST

    @cached_property
    def is_normal(self):
        return self.user_type == self.NORMAL

    @cached_property
    def is_farmer(self):
        return self.user_type == self.FARMER

    @cached_property
    def is_agronomer(self):
        return self.user_type == self.AGRONOMER

    @cached_property
    def name(self):
        if self.user.role.is_farmer:
            return '{}'.format(self.user.farmer.name)
        if self.user.role.is_specialist:
            return '{}'.format(self.user.specialist.name)
        if self.user.role.is_normal:
            return '{}'.format(self.user.normal.name)



    @staticmethod
    def get_user_profile(user):
        profile = {
            'id': user.id,
            'name': '',
            'image': '',
            'location': '',
            'is_verified': False,
            'role': user.role.user_type,
            'role_name': user.role.role_name
        }
        try:
            if user.role.is_normal:
                normal = user.normal

                profile['name'] = normal.name
                profile['image'] = normal.image
                profile['location'] = normal.region_name
            if user.role.is_farmer:
                farmer = user.farmer
                profile['name'] = farmer.owner_name
                profile['image'] = farmer.image
                profile['location'] = farmer.region_name
                profile['is_verified'] = farmer.is_verified
            if user.role.is_specialist:
                specialist = user.specialist
                profile['name'] = specialist.fullname
                profile['image'] = specialist.image
                profile['location'] = specialist.province.name
                profile['is_verified'] = specialist.is_verified
        except Exception as ex:
            print(ex)
        return profile


# on login check mobileuser and create
class MobileUser(models.Model):
    FEMALE = '0'
    MALE = '1'
    TYPES = (
        (FEMALE, 'FEMALE'),
        (MALE, 'MALE'),
    )

    role = models.OneToOneField(Role, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=TYPES, default=FEMALE)
    age = models.IntegerField(default=0)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    fcm_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.role.user.username} Role'



class Notifications(models.Model):
    MOBILE = 'MOBILE'
    WEB = 'WEB'
    TYPES = (
        (MOBILE, 'MOBILE'),
        (WEB, 'WEB'),
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    not_styled_title = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=10, choices=TYPES, default=MOBILE)
    # /professional/detail
    route = models.CharField(max_length=255, blank=True)
    params = models.CharField(max_length=1000, blank=True)  # {"id":123}
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Үүсгэсэн огноо")

    class Meta:
        verbose_name = 'Notifications'
        ordering = ['-created_at']
