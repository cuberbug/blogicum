# Generated by Django 3.2.16 on 2023-09-06 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_fix_comment'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='post',
            name='Unique person constraint',
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='post_images/', verbose_name='Фото'),
        ),
    ]
