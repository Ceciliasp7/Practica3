# Practica3
Este es el repositorio creado para la práctica 3 de la asignatura Programación Paralela, la correspondiente a la parte de programación distribuida. El objetivo es crear un programa que tenga información distribuida y que se tenga que compartir entre los clientes. Nosotros hemos elegido hacer un juego multiusuario, en concreto hemos programado un futbolín.

Nuestro programa está diseñado para 4 personas, que controlan a cada uno de los 4 jugadores del futbolin. El juego consta de dos equipos, el equipo rojo y el equipo azul. Cada equipo está formado por un portero y un delantero. Se trata de que la pelota, que va rebotando en los jugadores y en las paredes, se introduzca en la portería. Hemos reducido el área en la que poder marcar gol al área grande dibujada en el campo.
Además hemos añadido un contador de tiempo a la partida. Hay una cuenta atrás que empieza en 30 segundos y la partida se finaliza cuando el contador llega a cero.

Hemos subido a este repositorio las imágenes correspondientes al campo de fútbol y a la pelota, y dos archivos con el código: uno llamado 'player_futbolin1.py' donde se implementan las funciones para enviar comandos y recibe actualizaciones del estado del juego en tiempo real; y otro llamado 'sala_futbolin1.py', que coordina y gestiona de forma centralizada todo lo que ocurre en el juego, incluyendo la comunicación entre los jugadores y las actualizaciones en el estado del juego.

Además hemos incluido un vídeo que muestra lo que realiza nuestro programa cuando se ejecuta.
