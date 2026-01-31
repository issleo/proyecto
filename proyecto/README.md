Estimados este es mi proyecto, lo trate de hacer con los conocimiento que tengo y consultado, no es lo perfecto pero espero que se pueda ver mi esfuerzo y que si tengo ganas de aprender
#Comentario
En el setting se deja toda la configuración para la base de PostgresSQL
Los testing los hice lo mejor posible espero que puedan validar con un ejemplo colocado por ustedes en el apartado de TEST
Para ejecutar los test por favor ejecutar el comando: python manage.py test aplicacion
Todas las configuraciones y variables de entorno se encuentran en settings.py
Para ocupar las url en postman por favor ocupar http://localhost:8000/customers/
#decisiones tecnicas
Decisión:
Usar Django REST Framework (DRF).
Motivo:
Facilita exponer endpoints REST para chat, login y usuarios.
Compatible con Postman para pruebas.
Soporta autenticación Token o JWT fácilmente.
Decisión:
Usar TestCase de Django con base de datos temporal en Docker.
Motivo:
Permite pruebas unitarias y de integración sin afectar la base real.
