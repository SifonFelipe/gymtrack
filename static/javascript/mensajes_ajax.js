// get the url path
const path = window.location.pathname;

// split the path into segments
const segments = path.split('/');

// get the part you want
const groupNameQuery = segments[segments.length - 1];

function on_boton_traer_mensajes_click() {
    $.ajax({url: "/ajax/mensajes/" + groupNameQuery}).done(on_mensajes_ajax);
}

function on_mensajes_ajax(data) {
    var div_mensajes = $("#mensajes_de_grupo");
    var message_to_send = '';

    for (var chat_id in data.messages) {
        if (data.messages.hasOwnProperty(chat_id)) {
            var message = data.messages[chat_id];
            var user_id = chat_id;
            var user = data.users[user_id];
            message_to_send += `<p class="message">${user}: ${message}</p>`;
        }
    }
    
    console.log(div_mensajes)
    console.log(message_to_send);
    div_mensajes.html(message_to_send);
}

function on_pagina_cargada() {
    var boton_traer_mensajes = $("#boton-traer-mensajes");
    boton_traer_mensajes.bind("click", on_boton_traer_mensajes_click);
}

$(on_pagina_cargada);

setInterval(on_boton_traer_mensajes_click, 1000);