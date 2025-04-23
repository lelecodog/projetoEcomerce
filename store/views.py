from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import *
from django.http import JsonResponse
import json
import datetime
from.models import *
from .utils import cookieCart, cartData, guestOrder
from .forms import CustomUserCreationForm


def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    if request.user.is_authenticated:
        Customer.objects.get_or_create(
            user=request.user, 
            defaults={
                'name': request.user.username, 
                'email': request.user.email
            }
        )


    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    try:
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']

        customer = request.user.customer
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        cartItems = order.get_cart_items
        cartTotal = round(order.get_cart_total, 2)
        productQuantity = orderItem.quantity if orderItem.quantity > 0 else 0
        productTotal = round(orderItem.get_total, 2)

        return JsonResponse({'cartItems': cartItems, 'cartTotal': cartTotal, 'productQuantity': productQuantity, 'productTotal': productTotal}, safe=False)
    except Exception as e:
        print('Erro:', e)
        return JsonResponse({'error': str(e)}, status=500)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    # Substituir vírgula por ponto no total enviado
    total = float(data['form']['total'].replace(',', '.'))
    order.transaction_id = transaction_id

    # Logs para depuração
    print(f"Total enviado pelo cliente: {total}")
    print(f"Total calculado no servidor: {order.get_cart_total}")

    # Verificar se os totais correspondem
    if abs(round(total, 2) == round(order.get_cart_total, 2))< 0.01:
        order.complete = True
        order.save()
        print(f"Pedido {order.id} marcado como completo.")
    else:
        print('Erro: os totais não correspondem.')
        return JsonResponse({'error': 'Total não corresponde ao valor calculado'}, status=400)

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('store')
            else:
                messages.error(request, 'Username or password is incorrect')

        return render(request, 'store/login.html')

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        form = CustomUserCreationForm()
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                # Criar o objeto Customer associado ao usuário
                Customer.objects.create(
                    user=user,
                    name=form.cleaned_data.get('name'),
                    email=form.cleaned_data.get('email')
                )
                messages.success(request, 'Account created successfully')
                return redirect('login')

        context = {'form': form}
        return render(request, 'store/register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

def productDetail(request, pk):
    data = cartData(request)
    cartItems = data['cartItems']

    product = Product.objects.get(id=pk)
    context = {'product': product, 'cartItems': cartItems}
    return render(request, 'store/product_detail.html', context)
    
