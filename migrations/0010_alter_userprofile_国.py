# Generated by Django 3.2 on 2021-07-17 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0009_auto_20210717_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='国',
            field=models.CharField(choices=[('アメリカ', 'アメリカ'), ('インド', 'インド'), ('メキシコ', 'メキシコ'), ('ドイツ', 'ドイツ'), ('韓国', '韓国'), ('北朝鮮', '北朝鮮'), ('台湾', '台湾'), ('日本', '日本')], default='green', max_length=6),
        ),
    ]
