# Generated by Django 3.1.6 on 2021-10-06 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.CharField(choices=[('AGRONOMER', 'Агрономич'), ('FARMER', 'Тариаланч'), ('NORMAL', 'Энгийн хэрэглэгч'), ('SPECIALIST', 'Мэргэжилтэн'), ('ADMIN', 'БОСС')], default='NORMAL', max_length=10)),
                ('is_register_finish', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255)),
                ('not_styled_title', models.CharField(blank=True, max_length=255)),
                ('type', models.CharField(choices=[('MOBILE', 'MOBILE'), ('WEB', 'WEB')], default='MOBILE', max_length=10)),
                ('route', models.CharField(blank=True, max_length=255)),
                ('params', models.CharField(blank=True, max_length=1000)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Үүсгэсэн огноо')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MobileUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('0', 'FEMALE'), ('1', 'MALE')], default='0', max_length=1)),
                ('age', models.IntegerField(default=0)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('fcm_id', models.CharField(blank=True, max_length=255)),
                ('role', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.role')),
            ],
        ),
    ]
