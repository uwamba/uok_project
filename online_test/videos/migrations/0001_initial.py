# Generated by Django 4.2.17 on 2025-01-08 19:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import videos.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('exams', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=videos.models.video_upload_path)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MonitoringLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('activity_type', models.CharField(choices=[('webcam', 'Webcam'), ('screen', 'Screen'), ('audio', 'Audio')], max_length=50)),
                ('data', models.TextField()),
                ('screenshot', models.ImageField(blank=True, null=True, upload_to='monitoring_screenshots/')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.test')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
