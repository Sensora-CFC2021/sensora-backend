# Generated by Django 3.1.6 on 2021-10-06 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('references', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Farmer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=20, null=True, verbose_name='Өрхийн бүртгэлийн дугаар / ААН-н регистрийн дугаар')),
                ('owner_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Овог нэр/ ААНБ-н нэр')),
                ('image', models.ImageField(default='farmers/image/default.jpg', upload_to='farmers/image')),
                ('type', models.CharField(choices=[('IN', 'ӨРХ'), ('CM', 'ААНБ')], default='IN', max_length=2)),
                ('bag_khoroo', models.CharField(blank=True, max_length=30, null=True, verbose_name='Баг хороо ')),
                ('is_verified', models.BooleanField(default=False)),
                ('has_trial', models.BooleanField(default=False)),
                ('has_subscription', models.BooleanField(default=False)),
                ('trial_end_at', models.DateField(auto_now_add=True)),
                ('crops', models.ManyToManyField(blank=True, to='references.Crop')),
                ('ref_province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='references.refprovince')),
                ('ref_sum', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='references.refsum')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='farmer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Өрхийн бүртгэл',
                'verbose_name_plural': 'Өрхийн бүртгэлүүд',
            },
        ),
    ]
