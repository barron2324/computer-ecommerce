from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, Userprofile, ContactList, ActionContact
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests
from orders.models import Order, OrderProduct

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = Userprofile.objects.get(user_id=request.user.id)

    context = {
        'title':'แดชบอร์ด',
        'orders_count':orders_count,
        'userprofile':userprofile,
    }

    return render(request, 'accounts/dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # สร้างโปรไฟล์ผู้ใช้
            profile = Userprofile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            #การเปิดใช้งานผู้ใช้
            current_site = get_current_site(request)
            mail_subject = 'เปิดใช้งานบัญชีของคุณ'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'ขอบคุณสำหรับการลงทะเบียน เราได้ส่งอีเมลยืนยันไปที่อีเมลของคุณแล้ว โปรดตรวจสอบอีเมลของคุณ')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    
    context = {
        'title':'สมัครสมาชิก',
        'form':form,
    }
    return render(request, 'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    # รับการเปลี่ยนแปลงสินค้าในรถเข็น(ID)
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # รับรายการรถเข็นจากผู้ใช้เพื่อเข้าถึงรูปแบบสินค้า
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)


                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.c_quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'ขณะนี้คุณเข้าสู่ระบบ')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
                
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'อีเมลล์หรือรหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง')
            return redirect('login')
            
    context = {
        'title':'เข้าสู่ระบบ',        
    }

    return render(request, 'accounts/login.html', context)

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'ขณะนี้คุณออกจากระบบ')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'ยินดีด้วย! บัญชีของคุณถูกเปิดใช้งาน')
        return redirect('login')
    else:
        messages.error(request, 'ลิงค์เปิดใช้งานไม่ถูกต้อง')
        return redirect('register')

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)

            mail_subject = 'เปลี่ยนรหัสผ่าน'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'คำขอเปลี่ยนรหัสผ่านถูกส่งไปยังอีเมลของคุณแล้ว')
            return redirect('login')
        else:
            messages.error(request, 'อีเมลล์นี้ไม่ในระบบ')
            return redirect('forgotpassword')
    context = {
        'title':'ลืมรหัสผ่าน',
    }
    return render(request, 'accounts/forgotpassword.html',context)

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request,'รีเซ็ตรหัสผ่านของคุณ')
        return redirect('resetpassword')
    else:
        messages.error(request, 'ลิงค์นี้หมดอายุแล้ว')
        return redirect('login')

def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'เปลี่ยนรหัสผ่านสำเร็จ')
            return redirect('login')
        else:
            messages.error(request, 'รหัสผ่านไม่ตรงกัน')
            return redirect('resetpassword')
    else:

        
        return render(request, 'accounts/resetpassword.html')

@login_required(login_url='login')  
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at') 

    context = {
        'title':'รายการสั่งซื้อ',
        'orders':orders,
    }
    return render(request,'accounts/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(Userprofile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'title':'ตั้งค่าโปรไฟล์',
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def charge_password(request):
        
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                
                messages.success(request, 'เปลี่ยนรหัสผ่านสำเร็จ')
                return redirect('dashboard')
            else:
                messages.error(request, 'กรุณาป้อนรหัสผ่านปัจจุบันที่ถูกต้อง')
                return redirect('charge_password')
        else:
            messages.error(request, 'รหัสผ่านไม่ตรงกัน')
            return redirect('charge_password')
    
    context = {
        'title':'เปลี่ยนรหัสผ่าน',
    }

    return render(request, 'accounts/charge_password.html',context)


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'title':'รายละเอียดการสั่งซื้อ',
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)


def contact(request):
    
    if request.method == 'POST':
        data = request.POST.copy()
        title = data.get('title')
        email = data.get('email')
        detail = data.get('detail')

        newrecode = ContactList()
        newrecode.title = title
        newrecode.email = email
        newrecode.detail = detail
        newrecode.save()
        

        mail_subject = 'ฝ่ายช่วยเหลือ'
        message = render_to_string('accounts/send_contact.html', {
            'newrecode':newrecode.email,
        })
        to_email = email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        messages.success(request, 'คำขอของคุณถูกส่งแล้ว แล้วจะตอบกลับโดยเร็ว')

    

        return redirect('contact')

    context = {
        'title':'ติดต่อ',
    }
    return render(request, 'accounts/contact.html',context)

def aboutus(request):
    context = {
        'title':'เกี่ยวกับเรา',
    }
    return render(request,'accounts/aboutus.html',context)