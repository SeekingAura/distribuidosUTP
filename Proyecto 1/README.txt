08-05-2018
Servidor de Archivos
1. El servidor recibe las peticiones de varios clientes de diferentes clientes y debe permitir acceder a archivos distribuidos en diferentes partes de la red (el servidor no comparte archivos solo es mediador)
2. Cada cliente debe compartir una carpeta que contiene archivos. La primera vez que se conecte debe enviar la lista o en su defecto tiene alguna forma de obtener la lista de sus archivos que comparte
3. El servidor debe asignar de manera aleatoria, permisos (lectura, escritura, borrar, ninguno) sobre todos los archivos del sistema, a cada cliente cuando se conecta; y eso a cada archivo, es decir a cada archivo darle permisos distintos. [[{"nombre archivo": "permisos"}], ]
4. El servidor debe permitir las siguientes operaciones sobre los archivos:
	4.1 Listar: Debe enviar los nombres y sus permisos al cliente
	4.2 Leer: Recibe el nombre del archivo y envía el contenido
	4.3 Escribir: recibe el nombre, envia el contenido y espera los datos modificados
	4.4 Borrar: Recibe el nombre y envía comando de borrar
	El servidor debe verificar si el cliente tiene el permiso respectivo antes de permitir el acceso|
5. El servidor debe de garantizar que solo 1 cliente (al tiempo) pueda escribir sobre un archivo 
6. Para evitar problemas con nombres repetidos, en los archivos consultar en la documentación nombres de dos niveles

