from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from apps.home.models import Navigation, Category, Banner, Shop, Review, Property, PropertyValue, ShopCar


def index(request):
    # 导航
    navigations = Navigation.objects.all()
    # 一级分类
    categorys = Category.objects.all()
    for category in categorys:
        # 二级分类
        category.subs = category.submenu_set.all()
        for sub in category.subs:
            # 获取二级菜单分类的数据
            sub.subs2 = sub.submenu2_set.all()
        category.shops = category.shop_set.all()[0:5]
        # 获取商品的图片
        for shop in category.shops:
            shop.img = shop.shopimage_set.filter(type='type_single').order_by('shop_img_id').first()

    banners = Banner.objects.all().order_by('banner_id')
    count = 0
    if request.session.get('user'):
        count = ShopCar.objects.filter(user_id=request.session.get('user').uid, status=1).all().count()
    request.session['count'] = count
    return render(request, 'index.html', {
        'navigations': navigations,
        'banners': banners,
        'categorys': categorys,
    })


def shop_detail(request, id):
    try:
        shop = Shop.objects.get(shop_id=id)
        # 商品的图片信息
        shop.imgs = shop.shopimage_set.all()
        # 评论数
        review_count = Review.objects.filter(shop_id=id).count()
        # 属性
        properties = Property.objects.filter(cate__cate_id=shop.cate.cate_id)
        for property in properties:
            # 属性值
            property.pro_value = property.propertyvalue_set.get(shop_id=id, property_id=property.property_id)

        return render(request, 'shop_detail.html', {
            'shop': shop,
            'review_count': review_count,
            'properties': properties,
        })
    except Shop.DoesNotExist as e:
        pass
    except Shop.MultipleObjectsReturned as e:
        pass



