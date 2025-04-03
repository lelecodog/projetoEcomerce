var updateBtns = document.getElementsByClassName('update-cart')

for ( i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'Action:', action)

        console.log('USER:', user)
        if (user == 'AnonymousUser'){
            addCookieItem(productId, action)
        }else{
            updateUserOrder(productId, action)
        }
    })
}

function updateUserOrder(productId, action){
    console.log('Usuario está autenticado, enviando dados...')

        var url = '/update_item/'

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ 'productId': productId, 'action': action })
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            console.log('Dados recebidos:', data);
    
            // Atualizar a quantidade para o item específico
            const quantityElement = document.querySelector(
                `.chg-quantity[data-product="${productId}"]`
            ).closest('.cart-row').querySelector('.quantity');
            
            if (quantityElement) {
                quantityElement.textContent = data.productQuantity; // Atualiza a quantidade do produto
            }
    
            // Atualizar o total do produto específico
            const productTotalElement = document.querySelector(
                `.product-total[data-product="${productId}"]`
            );
            if (productTotalElement) {
                productTotalElement.textContent = `$${data.productTotal.toFixed(2)}`;
            }

            // Atualizar o total do carrinho
            const cartTotalElement = document.querySelector('.cart-total');
            if (cartTotalElement) {
                cartTotalElement.textContent = `$${data.cartTotal.toFixed(2)}`;
            }

            // Atualizar o número total de itens no carrinho
            const cartItemsElement = document.querySelector('.cart-items');
            if (cartItemsElement) {
                cartItemsElement.textContent = `${data.cartItems}`;
            }
            
        })
        .catch((error) => {
            console.error('Erro ao atualizar:', error);
            alert('Erro ao atualizar o carrinho. Tente novamente.');
        });
}

function addCookieItem(productId, action) {
    console.log('Usuario não autenticado')

    if (action == 'add') {
        if (cart[productId] == undefined) {
        cart[productId] = {'quantity': 1}

        }else {
            cart[productId]['quantity'] += 1
        }
    }

    if (action == 'remove') {
        cart[productId]['quatity'] -= 1

        if (cart[productId]['quatity'] <= 0) {
            console.log('Item deve ser deletado')
            delete cart[productId];
        }
    }
    console.log('CART:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    location.reload()
}
    