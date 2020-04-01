# Openventi WebClient

## Servidor
Servidor que simula el websocket a utilizarse en el yubox para propósitos de prueba. Requiere Python 3.

Instalar prerequisitos:
```
pip install websockets
```

Correr el servidor:
```
python server-simulador.py <puerto de escucha> <frecuencia_sensores> <frecuencia_alertas>
```

## Cliente
Colgar en cualquier servidor web, ya que sólo usa HTML5 y js!
