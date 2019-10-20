import os
import spacy
import operator
from spacy.lang.en.stop_words import STOP_WORDS
from .models import Video, FrameObjectData
from django.db.models import Sum


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def get_objs_for_query(search_query):

    nlp = spacy.load('en_core_web_md')

    with open('api/classes.txt') as f:
        object_set = f.readlines()
    object_set = [x.strip() for x in object_set] 

    threshold = 0.5

    # tokenize
    doc = nlp(search_query)

    filtered_tokens = []
    # remove stop words
    for token in doc:
        print(nlp.vocab[0])
        lexeme = nlp.vocab[str(token)]
        if lexeme.is_stop == False:
            filtered_tokens.append(token)
    
    # create map of token to set of objects
    #	1. if similarity is 1 only consider that
    #	2. else consider top 3 based on which qualify threshold reverse sorted
    query_tokens_objects = {}
    found_match = False
    for token in filtered_tokens:
        for object in object_set:
            similarity = token.similarity(nlp(object)) # check if similarity function works on lemma_ of a token
            if object in query_tokens_objects:
                continue
            if similarity >= threshold:
                query_tokens_objects[object] = 1
            if similarity == 1.0:
                found_match = True
                break
        # if not found_match:
            # sort based on similarity
            # query_tokens_objects[token].sort(key=operator.itemgetter(1), reverse=True)
            # get top three
            # query_tokens_objects[token] = query_tokens_objects[token][:3]
    print(query_tokens_objects)
    return query_tokens_objects


def rank_videos(query_tokens_objects):
    query_token_videos = {}
    # for query_token, objects in query_tokens_objects.items():
    #     # print("yo", query_token)
    #     for object, _ in objects:
    #         if query_token.text not in query_token_videos: 
    #             query_token_videos[query_token.text] = []
    #         query_token_videos[query_token.text] += get_videos(object)

    # print(query_token_videos)
    return query_token_videos

def get_videos(objects_dict):
    objects = [k for k in objects_dict.keys()]
    video_list = []
    frames = FrameObjectData.objects.filter(object__in=objects)
    d = {}
    for frame in frames:
        # video_obj = Video.objects.get(id=video['video'])
        video = frame.video
        if video.id in d:
            continue
        d[video.id] = 1
        video_list.append({
            "id": video.id,
            "title": video.title,
            "description": video.description,
            "category": video.category
        })
    return video_list
