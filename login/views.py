from django.shortcuts import render,redirect
from . import models
from .forms import RegisterForm
import hashlib
from login.utils.email_send import fasong
from django.views.generic.base import View
from login.models import EmailVerifyRecord, User

 
def index(request):
    pass
    return render(request,'login/index.html')
 
def login(request):
    if request.method == "GET":
        return render(request, 'login/login.html')
    if request.method == "POST":
        email = request.POST.get('email', None)
        password = request.POST.get('pwd', None)
        message = "所有字段都必须填写！"
        if email and password:  # 确保用户名和密码都不为空
            email = email.strip() #验证
            try:
                email = models.User.objects.get(email=email)
                if email.is_active != 1:
                    message = "用户未激活！"
                elif email.password == hash_code(password):
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
            return render(request, 'login/login.html', {"message": message})
        else:
            return render(request, 'login/login.html', {"message": message})
    return render(request, 'login/login.html')

def register(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            email = register_form.cleaned_data['email']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())
 
                # 当一切都OK的情况下，创建新用户

                new_user = models.User.objects.create()
                # 默认激活状态为False，也就是未激活
                new_user.is_active = False
                new_user.email = email
                new_user.password = hash_code(password1)  # 使用加密密码
                new_user.save()
                fasong(email, 'register')
                message = "邮件已发送，请在30分钟之内验证！"
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())
 
def logout(request):
    pass
    return redirect('/index/')

def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()

class ActiveUserView(View):
    def get(self, request, active_code):
        # 用于查询邮箱验证码是否存在
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
 
        if all_record:
            for record in all_record:
                # 获取到对应的邮箱
                email = record.email
                # 查找到邮箱对应的用户
                new_user = User.objects.filter(email=email)
                for i in range(len(new_user)):
                    new_user[i].is_active= True
                    new_user[i].save()
                # 激活成功跳转到登录页面
        else:
            return render(request, "login/active_fail.html")
        return render(request, "login/login.html")

