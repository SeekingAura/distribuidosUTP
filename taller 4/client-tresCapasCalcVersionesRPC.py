
import xmlrpc.client
if __name__ == '__main__':
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = input("ingrese el puerto del server -> ")
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	server=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer)
	print("Cliente iniciado")
	
	while True:
		print(server.menu())
		MESSAGE=input("\nIndique su operación de la manera server, version, value1, value2, value3, value4 (la cantidad de values dependen de la versión a usar > \n").split(", ")
		if(len(MESSAGE)>=3):
			print("resultado")
			servidor=MESSAGE.pop(0)
			version=MESSAGE.pop(0)
			values=MESSAGE
			values=[float(x) for x in values]
			print(server.op(servidor, int(version), values))
		else:
			print("Formato incorrecto")