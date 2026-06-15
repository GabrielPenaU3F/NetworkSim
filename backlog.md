# NETWORK SIM BACKLOG

## In progress
- Separar routing de envío de mensajes.
- Separar control de errores y retransmisiones (mover a capa de transporte)
- Implementar direcciones MAC en las interfaces.
- Implementar capa de enlace Ethernet-like
- Implementar hubs y switches.

## Completados
- Revisar si hay más clases triviales que puedan modelarse como dataclasses para simplificar el diseño.
- Revisar si hay validaciones que falten.
- Implementar un método que dibuje el grafo de la red.
- Completar la capa de red.
- Agregar tests de integración de capa de red y test de integración del sistema completo (hasta red).

## Permanente 
- Revisar si hay otros aspectos del diseño que puedan mejorarse o simplificarse.

## To do:
- Construir distintos tipos de nodos tales como switches y routers.
- Implementar puertas de enlace y redes privadas.
- Construir una red de prueba de tamaño decente y persistirla.
- Implementar capa de transporte con UDP.
- Implementar capa de transporte con TCP.
- Implementar concurrencia.