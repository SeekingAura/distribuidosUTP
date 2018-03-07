import socket


class UDPSocketServer:
	def __init__(self, ip, puerto):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.ip=ip
		self.puerto=puerto
		self.sock.bind((ip, puerto))
		self.sock.settimeout(1)#Establecer tiempo limite de espera en segundos por cada recvfrom
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
	servidor=UDPSocketServer(ipServer, puertoServer)
	print("Server iniciado")
	while True:
		data, addr = servidor.recieveMsg(1024) # buffer size is 1024 bytes
		if data is not None:
			print("Mesaje recibido '{}' de '{}':".format(data, addr))
			servidor.sendMsg(data, addr)
			servidor.sendMsg(data, addr)
			servidor.sendMsg("end", addr)
		#print("perdido")