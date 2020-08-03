from django.shortcuts import render
from django.views.generic import DetailView

from .models import Record, RecordFiles
from .tasks import handle_video


class IndexView(DetailView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        all_records = Record.objects.all().order_by('-upload_time')
        video_list = []
        for video in all_records:
            record_files = RecordFiles.objects.filter(record=video).all()
            video_list.append({
                'video': video,
                'preview': record_files.filter(file_type=RecordFiles.PREVIEW).first(),
                'video_file_mp4': record_files.filter(file_format=Record.MP4).first(),
                'video_file_webm': record_files.filter(file_format=Record.WEBM).first()
            })

        return {'video_list': video_list}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        video_file = request.FILES.get('video')
        video_link = request.POST.get('link')
        req_user = None if self.request.user.is_anonymous else request.user

        if video_file:
            obj = Record.objects.create(name=video_file.name, process_status=Record.NEW_FILE, upload_by=req_user)
            _ = handle_video.delay(obj.id, video_file.name, video_file.temporary_file_path())

        elif video_link:
            obj = Record.objects.create(process_status=Record.NEW_LINK, upload_by=req_user)
            _ = handle_video.delay(obj.id, video_link, video_link)

        return render(request, self.template_name, self.get_context_data())
