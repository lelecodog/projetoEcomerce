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
            console.log('Dados recebidos:', data)
            // Recarregar a página após a atualização
            location.reload();
           
        })
        // Adicione um bloco catch para lidar com erros
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
        cart[productId]['quantity'] -= 1

        if (cart[productId]['quantity'] <= 0) {
            console.log('Item deve ser deletado')
            delete cart[productId];
        }
    }
    console.log('CART:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    location.reload()
}
    