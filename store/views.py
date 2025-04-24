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

# View para exibir a página principal da loja
def store(request):
    #'Obtém os dados do carrinho   
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # Verifica se o usuário está autenticado e cria um objeto Customer se não existir
    if request.user.is_authenticated:
        Customer.objects.get_or_create(
            user=request.user, 
            defaults={
                'name': request.user.username, 
                'email': request.user.email
            }
        )

    #'Obtém todos os produtos da loja
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

# View para exibir a página do carrinho
def cart(request):
    #'Obtém os dados do carrinho
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # Passa os dados do carrinho para o template
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

# View para exibir a página de checkout
def checkout(request):
    #'Obtém os dados do carrinho
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # passa os dados do carrinho para o template
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

# View para atualizar o item no carrinho
def updateItem(request):
    try: # obtem os dados enviados pelo cliente
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']

        # Obtém o cliente e o pedido associado
        customer = request.user.customer
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Obtém ou cria o item do pedido
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        # Atualiza a quantidade do item com base na ação
        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1

        orderItem.save()

        # Remove o item se a quantidade for zero
        if orderItem.quantity <= 0:
            orderItem.delete()

        # Retorna os dados atualizados do carrinho
        cartItems = order.get_cart_items
        cartTotal = round(order.get_cart_total, 2)
        productQuantity = orderItem.quantity if orderItem.quantity > 0 else 0
        productTotal = round(orderItem.get_total, 2)

        return JsonResponse({'cartItems': cartItems, 'cartTotal': cartTotal, 'productQuantity': productQuantity, 'productTotal': productTotal}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# View para processar o pedido
def processOrder(request):
    # Gera um id único com base no timestamp atual
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        # Obtém o cliente autenticado e o pedido associado
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        # Para usuários não autenticados, cria um pedido temporário
        customer, order = guestOrder(request, data)

    # Substituir vírgula por ponto no total enviado
    total = float(data['form']['total'].replace(',', '.'))
    order.transaction_id = transaction_id

    # Verifica se o total enviado pelo cliente corresponde ao total calculado no servidor
    if abs(round(total, 2) == round(order.get_cart_total, 2))< 0.01:
        order.complete = True
        order.save()
    else:
        return JsonResponse({'error': 'Total não corresponde ao valor calculado'}, status=400)

    # Se o pedido requer envio, cria um endereço de envio associado
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

# View para exibir os detalhes de um produto específico
def productDetail(request, pk):
     # Obtém os dados do carrinho para o usuário atual ou visitante
    data = cartData(request)
    cartItems = data['cartItems']
    # Passa o produto e os itens do carrinho para o template
    product = Product.objects.get(id=pk)
    context = {'product': product, 'cartItems': cartItems}
    return render(request, 'store/product_detail.html', context)

# View para exibir a página de login
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

# View para exibir a página de registro
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

# View para fazer logout do usuário
def logoutUser(request):
    logout(request)
    return redirect('login')
