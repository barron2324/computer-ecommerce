from django.shortcuts import render, redirect
from carts.models import Cart, CartItem
from django.http import HttpResponse, JsonResponse
from .models import Payment, Order, OrderProduct
from store.models import Product
from .forms import OrderForm
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.
import datetime
import json

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    #เก็บรายละเอียดการทำธุรกรรมไว้ในวิธีการชำระเงิน
    payment = Payment (
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment 
    order.is_ordered = True
    order.save()

    # ย้ายรายการรถเข็นไปยังตารางรายการสั่งซื้อ
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.c_quantity
        orderproduct.product_price = item.product.pd_price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

    # ลดปริมาณสินค้าที่ขาย
        product = Product.objects.get(id=item.product_id)
        product.pd_stock -= item.c_quantity
        product.save()

    # ลบรถเข็นหลังจากสั่งซือสำเร็จ
    CartItem.objects.filter(user=request.user).delete()

    # ส่งคำสั่งซื้อที่ได้รับอีเมลไปยังลูกค้า
    mail_subject = 'ขอขอบคุณสำหรับการสั่งซื้อของคุณ'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # ส่งรหัสการโอนหมายเลขคำสั่งซื้อกลับไปที่เมธอด sendData ผ่าน JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

    return render(request, 'orders/payments.html')


def place_order(request, total=0, c_quantity=0):
    current_user = request.user

    # หากจำนวนรถเข็นน้อยกว่าหรือเท่ากับ 0 ให้เปลี่ยนเส้นทางกลับไปที่ร้านค้า
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.pd_price * cart_item.c_quantity)
        c_quantity += cart_item.c_quantity
    tax = (7 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # เก็บข้อมูลการเรียกเก็บเงินทั้งหมดภายในตารางการสั่งซื้อ
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.district = form.cleaned_data['district']
            data.province = form.cleaned_data['province']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            

            #สร้างหมายเลขคำสั่งซื้อ
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20221605
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'title':'ชำระเงิน',
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')
    

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')