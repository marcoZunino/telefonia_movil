----- SCRIPTS ------

ejecutar como > python .\[script].py

-> proxy_listener
    iniciar socket para proxy
    (puerto 8000 por defecto)

-> client_interface
    interfaz para envio de requests (register/invite)
    permite configurar datos de usuario y proxy asociado

    se inicia automaticamente socket para cliente
    (puerto 5060 por defecto)


-> functions
    '-> codec: codificar y decodificar mensajes, chequeo de campos
    '-> methods: funciones para callbacks de requests (register/invite/responses...)
    '-> read_write: manejo de archivos de logs, LS, DNS
    '-> send: envio de mensajes
    '-> state: manejo de 'maquina' de estados
    '-> dynamic_prints: mostrar estado de 'ringing', 'talking', etc



----- ESTRUCTURA DE MENSAJES -----

Request:

{
    Request :
        {
            Method : REGISTER/INVITE/ACK/CANCEL/BYE
            uri : sip:<user>@<proxy> (no aplica para REGISTER)
        }
    Fields : {} *
}


Response:

{
    Request :
        {
            Method : "response"
            Response Code : 100/180/200
            Response Description : Trying/Ringing/OK
        }
    
    Fields : {} *
}


* Fields:

{
    Via : [
        {protocol, uri, [received], [branch], ...},
        {protocol, uri, [received], [branch], ...},
        ...
        ]
    Max-Forwards : (no aplica para responses)
    To :
    From :
    Call-ID :
    CSeq :
    [Contact : ]
    [Content-Type : ]
    [Content-Length : ]
}

