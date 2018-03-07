
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
		MESSAGE=input("\nIndique su operación de la manera server, value1, value2 > ").split(", ")
		if(len(MESSAGE)==3):
			print("resultado")
			print(server.op(MESSAGE[0], float(MESSAGE[1]), float(MESSAGE[2])))
		else:
			print("Formato incorrecto")
		