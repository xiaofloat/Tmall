from django.shortcuts import render, redirect

# Create your views here.
from apps.home.models import User


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        if username and password:
            user = User.objects.filter(name=username, status=1).first()
            if user:
                if password == user.password:
                    # 验证成功
                    user.is_login = True
                    request.session['user'] = user
                    return redirect('/')
                else:
                    # 密码错误
                    pass
            else:
                # 账号不存在
                pass
    return render(request, 'login.html')


def register_view(request):
    pass


def logout_view(request):
    # 退出登录
    if request.session.get('user'):
        del request.session['user']
    return redirect('/')
