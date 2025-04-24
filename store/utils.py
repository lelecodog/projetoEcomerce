import json
from .models import *

# Função para lidar com o carrinho de compras baseado em cookies (usuários não autenticados)
def cookieCart(request):
    # Tenta carregar o carrinho dos cookies; se não existir, cria um carrinho vazio
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {} 
    
    # Inicializa os itens, o pedido e o total de itens no carrinho
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    # Itera sobre os itens no carrinho
    for i in cart:
        # Bloco try para evitar erros caso um produto tenha sido removido do banco de dados
        try:
            cartItems += cart[i]['quantity']

            # Obtém o produto do banco de dados
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            # Atualiza o total do pedido e o número de itens no carrinho
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            # Cria um dicionário representando o item no carrinho
            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                    },
                'quantity': cart[i]['quantity'],
                'get_total': total,
                }
            items.append(item)

            # Verifica se o produto não é digital para definir a necessidade de envio
            if product.digital == False:
                order ['shipping'] = True
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}

# Função para obter os dados do carrinho, seja para usuários autenticados ou visitantes
def cartData(request):
    if request.user.is_authenticated:
        # Para usuários autenticados, obtém o cliente e o pedido associado
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Para visitantes, utiliza os dados do carrinho baseado em cookies
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}

# Função para criar um pedido para usuários não autenticados
def guestOrder(request, data):
    # Obtém os dados do formulário enviado pelo cliente
    name = data['form']['name']
    email = data['form']['email']

    # Obtém os dados do carrinho baseado em cookies
    cookieData = cookieCart(request)
    items = cookieData['items']

    # Cria ou obtém um cliente com base no e-mail
    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    # Cria um pedido associado ao cliente
    order = Order.objects.create(
        customer = customer,
        complete = False,
    )

    # Adiciona os itens do carrinho ao pedido
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity'],
        )
    return customer, order
