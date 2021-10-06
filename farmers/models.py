from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property

from references import models as ref_models


class Farmer(models.Model):
    INDIVIDUAL = 'IN'
    COMPANY = 'CM'

    TYPES = (
        (INDIVIDUAL, 'ӨРХ'),
        (COMPANY, 'ААНБ'),
    )
    user = models.OneToOneField(User, related_name="farmer", on_delete=models.CASCADE)
    code = models.CharField(max_length=20, verbose_name="Өрхийн бүртгэлийн дугаар / ААН-н регистрийн дугаар",
                            blank=True, null=True)
    owner_name = models.CharField(max_length=250, verbose_name="Овог нэр/ ААНБ-н нэр", blank=True, null=True)
    image = models.ImageField(
        upload_to='farmers/image', default='farmers/image/default.jpg')

    type = models.CharField(max_length=2, choices=TYPES, null=False, default=INDIVIDUAL)
    ref_province = models.ForeignKey(ref_models.RefProvince, on_delete=models.SET_NULL, null=True, blank=True, )
    ref_sum = models.ForeignKey(ref_models.RefSum, on_delete=models.SET_NULL, null=True, blank=True, )

    bag_khoroo = models.CharField(max_length=30, verbose_name="Баг хороо ", blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    has_trial = models.BooleanField(default=False)
    has_subscription = models.BooleanField(default=False)
    trial_end_at = models.DateField(auto_now_add=True)
    crops = models.ManyToManyField(ref_models.Crop, blank=True)

    def __str__(self):
        return str(self.owner_name)

    @cached_property
    def role(self):
        return self.user.role.user_type

    @cached_property
    def role_name(self):
        return self.user.role.role_name

    @cached_property
    def username(self):
        return self.user.username

    @cached_property
    def name(self):
        return self.owner_name

    @cached_property
    def type_name(self):
        return dict(self.TYPES)[str(self.type)]

    @cached_property
    def region_name(self):
        return "{}, {}".format(self.ref_province.name, self.ref_sum.name)

    @cached_property
    def contact_phone(self):
        return self.user.username

    class Meta:
        verbose_name = 'Өрхийн бүртгэл'
        verbose_name_plural = 'Өрхийн бүртгэлүүд'
