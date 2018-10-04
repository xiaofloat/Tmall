import json

from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from apps.home.models import ShopCar, Shop


def add_car(request):
    # 判断是否登录
    if request.session.get('user'):
        uid = request.session['user'].uid
        number = int(request.GET.get('num'))
        shop_id = request.GET.get('shop_id')
        # 两个操作
        # 创建操作 如果商品不存在购物车
        # 更新操作 商品已经存在  数量++
        car = ShopCar.objects.filter(user_id=uid, shop_id=shop_id, status=1).first()
        if car:
            car.number += number
            car.save()
        else:
            car = ShopCar(user_id=uid, shop_id=shop_id, number=number, status=1)
            car.save()
            request.session['count'] += 1
        return HttpResponse('success')
    else:
        # 没有登录
        # 跳转到登录界面
        return HttpResponse(json.dumps({'to_login': True}), content_type='application/json')
        

# 展示购物车中的商品
def show(request):
    if request.session.get('user'):
        cars = ShopCar.objects.filter(status=1).all()
        for car in cars:
            # 获取商品的图片信息
            car.img = car.shop.shopimage_set.all().first()

        return render(request, 'cars.html', {'cars': cars})
    else:
        return HttpResponse('错误！')


# 移除选中的商品
@csrf_exempt
def delete(request):
    # 获得car_id
    car_id = request.POST.get('car_id')
    # 更改该条的状态
    ShopCar.objects.filter(car_id=car_id).update(status=0)
    return HttpResponse(json.dumps({'result': 'success'}), content_type='application/json')
