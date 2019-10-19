from django.urls import path

from . import views

urlpatterns = [
    path('video/upload/', views.upload, name='upload'),
    path('video/watch/', views.watch, name='watch'),
    path('video/search/', views.search, name='search'),
    path('ads/new/', views.new_ad, name='new_add')
]
