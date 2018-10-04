import datetime

import alipay
from alipay import AliPay
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.

# 确认订单
from django.views.decorators.csrf import csrf_exempt

from apps.home.models import ShopCar, Order
from tmall.settings import APP_ID, APP_PRIVATE_STRING, ALI_PAY_PUBLIC_KEY_STRING, ALI_PAY_URL


def confirm_order(request):
    checks = request.POST.getlist('ck')
    if checks:
        check_dic = {}
        # 获得商品的数量
        numbers = request.POST.getlist('number')
        # 获得car_id
        ids = request.POST.getlist('car_id')
        # 组合成 id: number字典
        for i in checks:
            check_dic[ids[int(i)]] = numbers[int(i)]
        try:
            with transaction.atomic():
                # 保存确认购买的商品的数量
                for key, value in check_dic.items():
                    ShopCar.objects.filter(car_id=int(key)).update(number=int(value), status=2)
        except Exception as e:
            print(e)
            # 回滚
            transaction.rollback()
    # 获得那些被将要被购买的商品
    cars = ShopCar.objects.filter(user_id=request.session['user'].uid, status=2)
    if cars:
        for car in cars:
            # 获取商品的图片信息
            car.img = car.shop.shopimage_set.all().first()
    return render(request, 'confirm.html', {'cars': cars})


# 生成订单
@transaction.atomic
def create_order(request):
    if request.method == 'POST':
        # 获得表单数据
        address = request.POST.get('address')
        receiver = request.POST.get('receiver')
        post = request.POST.get('post')
        mobile = request.POST.get('mobile')
        user_message = request.POST.get('user_message')
        pay_code = request.POST.get('rd')
        # 获得user的id
        uid = request.session.get('user').uid
        # 生成订单号(时间加上用户id)
        order_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        order_code = order_time + '_' + str(request.session.get('user').uid)
        # 生成订单
        order = Order(
            order_code=order_code,
            address=address,
            receiver=receiver,
            post=post,
            mobile=mobile,
            user_message=user_message,
            user_id=uid
        )
        order.save()
        # 用户下面购物车的数据会被清空
        ShopCar.objects.filter(user_id=uid, status=2).update(status=-1, order=order)
        if int(pay_code) == 1:
            # 微信支付
            pass
        else:
            pay('订单号', '金额', '订单名称')
        return render(request, 'success.html')


# 支付
def pay(out_trade_no, total_amount, subject):
    # 创建用进行支付宝支付的工具对象
    alipay = AliPay(
        appid=APP_ID,
        app_notify_url=None,  # 默认回调url
        app_private_key_string=APP_PRIVATE_STRING,
        alipay_public_key_string=ALI_PAY_PUBLIC_KEY_STRING,
        debug=False
    )
    # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        # 订单号
        out_trade_no='123456',
        # 商品总价
        total_amount=str(0.01),  # 将Decimal类型转换为字符串交给支付宝
        # 订单名称
        subject="天猫商城-{}".format(123456),
        # 支付成功之后 前端跳转的界面或者移动端
        return_url='https://baidu.com/',
        # 支付成功后台跳转接口
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    # 让用户进行支付的支付宝页面网址
    url = ALI_PAY_URL + "?" + order_string
    return redirect(url)


@csrf_exempt
def aliapy_back_url(request):
    # 验证alipay的异步通知，data来自支付宝回调POST 给你的data，字典格式.
    data = {
        "subject": "测试订单",
        "gmt_payment": "2016-11-16 11:42:19",
        "charset": "utf-8",
        "seller_id": "xxxx",
        "trade_status": "TRADE_SUCCESS",
        "buyer_id": "xxxx",
        "auth_app_id": "xxxx",
        "buyer_pay_amount": "0.01",
        "version": "1.0",
        "gmt_create": "2016-11-16 11:42:18",
        "trade_no": "xxxx",
        "fund_bill_list": "[{\"amount\":\"0.01\",\"fundChannel\":\"ALIPAYACCOUNT\"}]",
        "app_id": "xxxx",
        "notify_time": "2016-11-16 11:42:19",
        "point_amount": "0.00",
        "total_amount": "0.01",
        "notify_type": "trade_status_sync",
        "out_trade_no": "xxxx",
        "buyer_logon_id": "xxxx",
        "notify_id": "xxxx",
        "seller_email": "xxxx",
        "receipt_amount": "0.01",
        "invoice_amount": "0.01",
        "sign": "xxx"
    }
    signature = data.pop("sign")
    success = alipay.AliPay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        print("trade succeed")
