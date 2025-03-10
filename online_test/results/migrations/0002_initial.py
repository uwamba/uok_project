# Generated by Django 4.2.17 on 2025-01-08 19:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('results', '0001_initial'),
        ('users', '0001_initial'),
        ('exams', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.candidate'),
        ),
        migrations.AddField(
            model_name='result',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.test'),
        ),
    ]
