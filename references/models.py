
from django.db import models

from django.contrib.auth.models import User
from sorl.thumbnail import ImageField


class RefReference(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Нэр")
    is_active = models.BooleanField(default=False, verbose_name="Идэвхтэй эсэх")
    sort_order = models.IntegerField(blank=True, null=True, verbose_name="Эрэмбэ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Шинэчилсэн огноо")

    class Meta:
        abstract = True

    def __str__(self):
        if self.name:
            return "{}".format(self.name)
        return ""


class RefListingType(RefReference):
    class Meta:
        verbose_name = 'Listing type'
        verbose_name_plural = 'Listing types'
        ordering = ['sort_order']


class RefCropType(RefReference):
    class Meta:
        verbose_name = 'Ургамлын төрөл'
        verbose_name_plural = 'Ургамлын төрлүүд'
        ordering = ['sort_order']


class RefProvince(RefReference):

    @property
    def sums(self):
        return RefSum.objects.filter(ref_province=self).exclude(is_active=False).all()

    class Meta:
        verbose_name = 'Аймаг'
        verbose_name_plural = 'Аймгууд'
        ordering = ['sort_order']


class RefSum(RefReference):
    ref_province = models.ForeignKey(RefProvince, on_delete=models.CASCADE, null=True,
                                     blank=True, )
    lat = models.FloatField(default=0.0)
    lon = models.FloatField(default=0.0)

    def __str__(self):
        return "{} аймаг {}".format(self.ref_province.name, self.name)

    class Meta:
        verbose_name = 'Сум'
        verbose_name_plural = 'Сумууд'
        ordering = ['sort_order']


class RefPlanting(RefReference):
    class Meta:
        verbose_name = 'Тарих арга'
        verbose_name_plural = 'Тарих аргууд'
        ordering = ['sort_order']


class RefNewsFeed(RefReference):
    topic = models.CharField(max_length=100, verbose_name="topic")

    class Meta:
        verbose_name = 'RefNewsFeed'
        verbose_name_plural = 'RefNewsFeeds'
        ordering = ['sort_order']



class Crop(models.Model):
    name = models.CharField(max_length=250, verbose_name="Таримал", blank=True, null=True)
    ref_crop_type = models.ForeignKey(RefCropType, verbose_name="Төрөл ", on_delete=models.SET_NULL,
                                      blank=True,
                                      null=True)
    icon = ImageField(upload_to='crop/icon', blank=True, null=True)
    image = ImageField(upload_to='crop/image', blank=True, null=True)
    is_mobile_home = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Таримал'
        verbose_name_plural = 'Тарималууд'