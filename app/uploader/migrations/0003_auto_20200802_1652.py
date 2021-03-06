# Generated by Django 3.0.8 on 2020-08-02 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0002_auto_20200802_0903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='process_status',
            field=models.IntegerField(choices=[(0, 'New video file'), (1, 'New video link'), (3, 'Making preview'), (4, 'Converting to mp4'), (5, 'Converting to webm'), (6, 'Ready'), (999, 'Error')], verbose_name='Статус обработки'),
        ),
        migrations.AlterField(
            model_name='recordfiles',
            name='file_type',
            field=models.IntegerField(choices=[(0, 'Preview image file'), (1, 'Converted video file')], default=0, verbose_name='Тип файла'),
        ),
    ]
