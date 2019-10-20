import os
import re
import mimetypes
from wsgiref.util import FileWrapper

from django.http.response import StreamingHttpResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Video, FrameObjectData
from .util import RangeFileWrapper, get_objs_for_query, rank_videos
from .yolov3.detect import detect


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


def watch(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    path = video.video_file_path
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, _ = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length), status=206, content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp

def upload(request):
    post_data = request.POST
    file_object = request.FILES['video_file']
    print(post_data)
    try:
        file_name = os.path.join(settings.MEDIA_ROOT, file_object.name)
        with open(file_name, 'wb+') as destination:
            for chunk in file_object.chunks():
                destination.write(chunk)
        video = Video(
            title=post_data['title'],
            description=post_data['description'],
            category=post_data['category'],
            video_file_path=file_name
        )
        video.save()

        frame_data = detect(file_name)
        for frame in frame_data:
            data = None
            for object, quantity in frame['objects'].items():
                data = FrameObjectData(
                    video=video,
                    frame_no=frame['frame'],
                    object=object,
                    quantity=quantity
                )
            if data is not None:
                data.save()

        return HttpResponse(content="Successfully uploaded", status=200)
    except KeyError:
        return HttpResponse(content="Form incomplete", status=400)
    except Exception as err:
        print(err)
        return HttpResponse(content="Internal Server Error", status=500)

def search(request):
    post_data = request.POST
    print(post_data)
    try:
        return JsonResponse(rank_videos(get_objs_for_query(post_data)), status=200)
    except Exception as err:
        print(err)
        return HttpResponse(content="Internal Server Error", status=500)

def new_ad():
    pass
