# Generated by Django 4.2.7 on 2023-11-27 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunain', '0004_book_finished_book_title_alter_book_views'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
