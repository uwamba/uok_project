# Generated by Django 5.1.4 on 2024-12-19 12:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0010_question_duration_test_countertype_test_duration'),
        ('results', '0007_alter_resultdetail_question'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultdetail',
            name='selected_option',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='options', to='exams.questionoption'),
        ),
    ]
