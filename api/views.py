import os
import re
import mimetypes
import random
from wsgiref.util import FileWrapper

from django.http.response import StreamingHttpResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Video, FrameObjectData, Ad
from .util import RangeFileWrapper, get_objs_for_query, get_videos
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
        response = {"videos": get_videos(get_objs_for_query(post_data['query']))}
        print(response)
        return JsonResponse(response, status=200)
    except Exception as err:
        print(err)
        return HttpResponse(content="Internal Server Error", status=500)

def new_ad(request):
    post_data = request.POST
    print(post_data)
    try:
        ad = Ad(
            redirect_link=post_data['redirect_link'],
            category=post_data['category'],
            object=post_data['object'],
            image_link=post_data['image_link']
        )
        ad.save()
    except KeyError:
        return HttpResponse(content="Form incomplete", status=400)
    except Exception as err:
        print(err)
        return HttpResponse(content="Internal Server Error", status=500)

def get_video(request, video_id):
    try:
        video = get_object_or_404(Video, pk=video_id)
        print(video.title)
        possible_ads = Ad.objects.filter(category=video.category)
        frame_data = FrameObjectData.objects.filter(video=video)
        # print(frame_data)
        objects = {}
        for frame in frame_data:
            if frame.object not in objects:
                objects[frame.object] = 0
            objects[frame.object] += frame.quantity
        
        possible_ads_ = possible_ads
        for _ in objects:
            if len(possible_ads_) <= 3:
                break
            possible_ads = possible_ads_
            max_key = max(objects.keys(), key=(lambda k: objects[k]))
            objects.pop(max_key, None)
            possible_ads_ = possible_ads_.filter(object=max_key)
        
        if 3 >= len(possible_ads_) > 0:
            possible_ads = possible_ads_
        
        if len(possible_ads) == 0:
            result = {
                "video": {
                    "title": video.title,
                    "description": video.description,
                    "category": video.category
                },
                "ad_data": {}
            }

            return JsonResponse(result, status=200)
        
        ad = random.choice(possible_ads)

        max_occurences = -1
        best_frame = 0
        for frame in frame_data:
            # print(frame)
            if frame.object == ad.object and frame.quantity > max_occurences:
                # print(frame)
                max_occurences = frame.quantity
                best_frame = frame.frame_no
        
        result = {
            "video": {
                "title": video.title,
                "description": video.description,
                "category": video.category
            },
            "ad_data": {
                "redirect_link": ad.redirect_link,
                "image_link": ad.image_link,
                "category": ad.category,
                "object": ad.object,
                "best_frame": best_frame
            }
        }

        return JsonResponse(result, status=200)
    except Exception as err:
        print(err)
        return HttpResponse(content="Internal Server Error", status=500)

def all_videos(request):
    try:
        videos = Video.objects.all()
        videos_list = []
        for video in videos:
            videos_list.append({
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "category": video.category
            })
        return JsonResponse({"videos": videos_list}, status=200)
    except Exception as err:
        print(err)
        return HttpResponse(content="Internal Server Error", status=500)
