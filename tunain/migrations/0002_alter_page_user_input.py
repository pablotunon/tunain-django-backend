# Generated by Django 4.2.7 on 2023-11-22 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunain', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='user_input',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]