from django.shortcuts import render


# Create your views here.
from apps.home.models import Shop


def search(request):
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        # print(keyword)
        # print(type(keyword))
        shops = Shop.objects.filter(name__contains=keyword)
        for shop in shops:
            shop.image = shop.shopimage_set.filter(type='type_single').first()
        return render(request, 'search.html', {'shops': shops})
    else:
        return render(request, 'error/400.html')
