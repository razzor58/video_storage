from django.db import models
from django.contrib.auth.models import User
from django.db.models import PROTECT


class Record(models.Model):
    objects = models.Manager()

    NEW_FILE = 0
    NEW_LINK = 1
    MAKING_PREVIEW = 3
    CONVERTING_MP4 = 4
    CONVERTING_WEBM = 5
    READY = 6
    ERROR = 999

    MP4 = 'mp4'
    WEBM = 'webm'

    STATUS_CHOICES = [
        (NEW_FILE, 'New video file'),
        (NEW_LINK, 'New video link'),
        (MAKING_PREVIEW, 'Making preview'),
        (CONVERTING_MP4, 'Converting to mp4'),
        (CONVERTING_WEBM, 'Converting to webm'),
        (READY, 'Ready'),
        (ERROR, 'Error'),
    ]
    RESULT_FORMATS = {
        CONVERTING_MP4: MP4,
        CONVERTING_WEBM: WEBM,
    }

    NEXT_STEPS = {
        NEW_LINK: MAKING_PREVIEW,
        NEW_FILE: MAKING_PREVIEW,
        MAKING_PREVIEW: CONVERTING_MP4,
        CONVERTING_MP4: CONVERTING_WEBM,
        CONVERTING_WEBM: READY
    }

    class Meta:
        verbose_name_plural = 'Загруженные видео'

    name = models.CharField(max_length=2000, verbose_name='имя файла', null=True, blank=True)
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')
    upload_by = models.ForeignKey(User, verbose_name='Кем добавлен', null=True, blank=True, on_delete=PROTECT)
    process_status = models.IntegerField(choices=STATUS_CHOICES, verbose_name='Статус обработки')

    def __str__(self):
        return self.name


class RecordFiles(models.Model):
    objects = models.Manager()

    PREVIEW = 0
    CONVERTED_VIDEO = 1

    FILE_TYPE_CHOICES = [
        (PREVIEW, 'Preview image file'),
        (CONVERTED_VIDEO, 'Converted video file'),
    ]

    record = models.ForeignKey(Record, verbose_name='Запись пользователя', null=True, blank=True, on_delete=PROTECT)
    file_type = models.IntegerField(choices=FILE_TYPE_CHOICES, default=PREVIEW, verbose_name='Тип файла')
    file_format = models.FileField(blank=True, null=True, verbose_name='Расширение')
    file = models.FileField(blank=True, null=True, verbose_name='Файл')
