# Generated by Django 2.2.5 on 2019-12-11 06:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20191210_0713'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=255, unique=True)),
                ('comment', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seen_by_user', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Event')),
                ('user_to_notify', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_to_notify', to=settings.AUTH_USER_MODEL)),
                ('user_who_fired_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_who_fired_event', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]