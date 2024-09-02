# Generated by Django 5.1 on 2024-09-02 16:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_jobcategory_category_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('form_fields', models.JSONField()),
                ('associated_job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.jobposting')),
            ],
        ),
    ]
