# Generated by Django 5.1.4 on 2024-12-19 12:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0010_question_duration_test_countertype_test_duration'),
        ('results', '0006_result_attempt_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultdetail',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='exams.question'),
        ),
    ]