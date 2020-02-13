from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .tasks import sentinel_query_task

# Create your views here.
def QueryView(request):
    platformname = request.GET['platformname']
    min_lon = request.GET['min_lon']
    max_lon = request.GET['max_lon']
    min_lat = request.GET['min_lat']
    max_lat = request.GET['max_lat']
    start_time = request.GET['start_time']
    end_time = request.GET['end_time']
    product_df = sentinel_query_task().query(platformname, min_lon, max_lon, min_lat, max_lat, start_time, end_time)
    print(product_df)
    if product_df.empty:
        return JsonResponse({})
    return JsonResponse({
     'uuid': product_df['uuid'].to_dict(),
     'title': product_df['title'].to_dict(),
     'link_icon': product_df['link_icon'].to_dict(),
     'link': product_df['link'].to_list(),
     'size': product_df['size'].to_list(),
     'producttype': product_df['producttype'].to_list(),
     'ingestiondate': product_df['ingestiondate'].to_list()
    })

def dung(request):
    def validate(name):
        if not name:
            raise NotImplementedError(" You must set name")
        return name
    name = request.GET['name']
    name = validate(name)
    return JsonResponse({
        'name': name,
    })