# Generated by Django 5.1.4 on 2024-12-19 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0010_question_duration_test_countertype_test_duration'),
        ('results', '0008_alter_resultdetail_selected_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultdetail',
            name='selected_option',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='selected_options', to='exams.questionoption'),
        ),
    ]
