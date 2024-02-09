# Generated by Django 3.2 on 2021-07-19 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0013_userprofile_言語'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='サイト',
            field=models.URLField(blank=True, max_length=900, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='言語',
            field=models.CharField(choices=[('日本語', '日本語'), ('English', 'English'), ('ਪੰਜਾਬੀ', 'ਪੰਜਾਬੀ')], default=('English', 'English'), max_length=900),
        ),
    ]
