# Openventi WebClient

## Servidor

Servidor que simula el websocket a utilizarse en el yubox para propósitos de prueba. Requiere Python 3.

Antes de instalar los paquetes es importante actualizar el gestor de paquetes pip

### Linux-Ubuntu

~~~~
sudo pip3 install --upgrade pip
~~~~

### Windows

~~~~
python3 -m pip install --upgrade pip
~~~~

### MACOS

~~~~
sudo pip3 install -U pip --ignore-installed pip
~~~~

1. Instalar prerequisitos:

~~~~
pip3 install websockets
~~~~

2. Correr el servidor:

~~~~
python3 server-simulador.py <puerto de escucha> <frecuencia_sensores> <frecuencia_alertas>
~~~~

## Cliente

1. Abrimos una ventana de Terminal e instalamos lo siguiente con pip3

~~~~
pip3 install httpserver
~~~~

2. Abrimos una ventana de Terminal e iniciamos el servidor web

~~~~
python -m http.server 8000
~~~~

4. En el terminal observamos y esta en ejecución el servidor web

![alt text](https://www.poftut.com/wp-content/uploads/2018/07/img_5b4d5f569b669.png  "Logo Title Text 1")

5. En el navegador web de nuestra preferencia digitamos y podemos visualizar el website.

~~~~
localhost:8000
~~~~
