import socket


class UDPSocketClient:
	def __init__(self, ip, puerto):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.ip=ip
		self.puerto=puerto
		self.sock.settimeout(60)
		self.clients=[]
	def sendMsg(self, message, addres):
		if isinstance(message, str):
			self.sock.sendto(message.encode('utf-8'), addres)
		elif isinstance(message, bytes):
			self.sock.sendto(message, addres)
		else:
			print("ERROR - Data type to send can't work")
			return None
	def recieveMsg(self, size):
		try:
			data, addr = self.sock.recvfrom(size)
			return (data.decode('utf-8'), addr)
		except socket.timeout:
			return (None, None)

if __name__ == '__main__':
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = int(input("ingrese el puerto del server -> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	cliente=UDPSocketClient(ipServer, puertoServer)
	print("Cliente iniciado")
	while True:
		MESSAGE=input("> ")
		cliente.sendMsg(MESSAGE, (ipServer, puertoServer))
		recibidoData=""
		while recibidoData!="end" and recibidoData is not None:
			recibidoData, recibidoAdress=cliente.recieveMsg(1024)
			if(recibidoData!="end"):
				print("Recibido dato '{}' de '{}'".format(recibidoData, recibidoAdress))