# Generated by Django 2.2.2 on 2019-06-21 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kip_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('course', 'name')},
        ),
    ]