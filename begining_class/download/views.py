from django.shortcuts import render
from django.http import JsonResponse
from .tasks import sentinel2_google_cloud
from query.tasks import sentinel_query_task

download_dir = ''
destination_dir = '.'

def DownloadView(request):
    platformname = request.GET['platformname']
    uuid = request.GET['uuid']
    title = sentinel_query_task().get_title_by_uuid(uuid)
    if platformname == 'SENTINEL-2' or platformname == 'Sentinel-2':
        path_tif = sentinel2_google_cloud(title).download(destination_dir)
    if platformname == 'SENTINEL-1' or platformname == 'Sentinel-1':
        print('need to be complete')
    return JsonResponse({
        'Status': 'Success',
        'path': path_tif
    })