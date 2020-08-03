from os import system
from pathlib import Path
from requests import get
from celery import shared_task
from logging import getLogger

from django.core.files import File
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .models import Record, RecordFiles


fs = FileSystemStorage()
logger = getLogger(__name__)


class FileHandler:
    def __init__(self, record_id, file_path, file_name):
        self.record_id = record_id
        self.file_path = file_path
        self.file_name = file_name
        self.record = Record.objects.get(pk=record_id)
        self.os_cmd = f'{settings.CODEC_PATH}ffmpeg'

        self.result_file_name = None
        self.result_file_path = None

    def update_status(self):
        self.record.process_status = Record.NEXT_STEPS[self.record.process_status]
        self.record.save()

    def save_result_file(self, file_type, file_format):
        with open(self.result_file_path, 'rb') as f:
            _ = RecordFiles.objects.create(record=self.record,
                                           file_type=file_type,
                                           file_format=file_format,
                                           file=File(f, name=self.file_name))

    def process(self):
        pass


class SourceLinkSaver(FileHandler):
    def __init__(self, record_id, file_path, file_name):
        super().__init__(record_id, file_path, file_name)
        self.result_file_name = self.file_name

    def process(self):
        remote_content = get(self.file_path).content
        file_path = Path(settings.MEDIA_ROOT, 'google_err.html')
        with open(file_path, 'wb') as f:
            f.write(remote_content)

        with open(file_path, 'rb') as f:
            filename = fs.save(self.file_name, File(f))
            self.result_file_path = fs.path(filename)
            self.update_status()

        return self.result_file_path


class SourceFileSaver(FileHandler):
    def __init__(self, record_id, file_path, file_name):
        super().__init__(record_id, file_path, file_name)
        self.result_file_name = self.file_name

    def process(self):
        with open(self.file_path, 'rb') as f:
            filename = fs.save(self.file_name, File(f))
            self.result_file_path = fs.path(filename)
            self.update_status()

        return self.result_file_path


class PreviewMaker(FileHandler):
    def __init__(self, record_id, file_path, file_name):
        super().__init__(record_id, file_path, file_name)
        self.result_file_name = f'preview_{Path(self.file_path).stem}.{settings.PREVIEW_FORMAT}'
        self.result_file_path = str(Path(settings.MEDIA_ROOT, self.result_file_name))

    def process(self):
        cmd = f'{self.os_cmd} -i {self.file_path} -vf "select=eq(n\,0)" -q:v 3 {self.result_file_path}'  # noqa: W605
        system(cmd)

        self.save_result_file(RecordFiles.PREVIEW, settings.PREVIEW_FORMAT)
        self.update_status()

        return self.file_path


class Converter(FileHandler):
    def __init__(self, record_id, file_path, file_name):
        super().__init__(record_id, file_path, file_name)

        self.result_format = Record.RESULT_FORMATS.get(self.record.process_status)
        self.result_file_name = f'{Path(self.file_path).stem}.{self.result_format}'
        self.file_name = self.result_file_name
        self.result_file_path = str(Path(settings.MEDIA_ROOT, self.result_file_name))

    def process(self):
        if not self.result_format:
            return

        command = f'{self.os_cmd} -i {self.file_path} -s {settings.CONVERTING_SIZE} {self.result_file_path}'
        system(command)

        self.save_result_file(RecordFiles.CONVERTED_VIDEO, self.result_format)
        self.update_status()

        return self.file_path


class FileHandlerFactory:
    def __init__(self):
        self._creators = {}

    def register_handler(self, record_status, handler_class):
        self._creators[record_status] = handler_class

    def process_file(self, record_id, record_status, file_name, file_path):
        creator = self._creators.get(record_status)
        if creator:
            return creator(record_id, file_path, file_name).process()
        else:
            return


factory = FileHandlerFactory()
factory.register_handler(Record.NEW_LINK, SourceLinkSaver)
factory.register_handler(Record.NEW_FILE, SourceFileSaver)
factory.register_handler(Record.MAKING_PREVIEW, PreviewMaker)
factory.register_handler(Record.CONVERTING_MP4, Converter)
factory.register_handler(Record.CONVERTING_WEBM, Converter)


@shared_task
def handle_video(record_id, file_name, file_path):
    record_status = Record.objects.get(pk=record_id).process_status

    while record_status not in (Record.ERROR, Record.READY):

        try:
            file_path = factory.process_file(record_id, record_status, file_name, file_path)
            record_status = Record.objects.get(pk=record_id).process_status
        except Exception as e:
            logger.error(e, exc_info=True)
            break
