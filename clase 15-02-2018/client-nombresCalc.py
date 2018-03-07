import socket


class UDPSocketClient:
	def __init__(self, ip, puerto):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.serverMainAddr=(ip, puerto)
		self.id="-1"
		self.tipo="cliente"
		self.sock.settimeout(60)
		
	def sendMsg(self, message, addres):
		
		if isinstance(message, str):
			message=self.id+":"+self.tipo+":"+message+":"
			self.sock.sendto(message.encode('utf-8'), addres)
			print("mensaje enviado - {}".format(message))
		elif isinstance(message, bytes):
			message=self.id+":"+self.tipo+":"+message.decode('utf-8')+":"
			self.sock.sendto(message, addres)
			print("mensaje enviado - {}".format(message.decode('utf-8')))
		else:
			print("ERROR - Data type to send can't work")
			return None
		
	def recieveMsg(self, size):
		try:
			data, addr = self.sock.recvfrom(size)
			print("Mensaje recibido - {}".format(data.decode('utf-8')))
			id=None
			tipo=None
			mensaje=None
			temp=""
			for i in data.decode('utf-8'):
				if(i!=":"):
					temp+=i
				elif (id is None and i==":"):
					id=temp
					temp=""
				elif(tipo is None and i==":"):
					tipo=temp
					temp=""
				elif(mensaje is None and i==":"):
					mensaje=temp
					temp=""
				
			return (id, tipo, mensaje, addr)
		except socket.timeout:
			print("Tiempo de espera superado")
			return (None, None, None, None)
			
		except:
			return (None, None, None, None)

	def comServerMain(self):
		print("Comunicandose con server main")
		while True:
			MESSAGE=input("> ")
			self.sendMsg(MESSAGE, (ipServer, puertoServer))
			data=""
			while data!="end" and data is not None:
				id, tipo, data, addr=self.recieveMsg(1024)
				if (data is not None):
					print("Recibido dato '{}' de '{}'".format(data, addr))
					if(data!="end"):
						if("~" in data):
							tag=None
							temp=""
							for i in data:
								if(i!="~"):
									temp+=i
								else:
									tag=temp
									temp=""
							if(tag=="dirección"):
								ip, addr=temp[1:-1].split(", ")
								ip=ip[1:-1]
								addr=int(addr)
								return (ip, addr)
						
	def comServerService(self, addr):
		print("Conectando a un servicio")
		self.sendMsg("operar", addr)
		id, tipo, data, addr=self.recieveMsg(1024)
		data=None
		while data != "end":
			id, tipo, data, addr=self.recieveMsg(1024)
		print("conectado! pasa salir escriba 'exit'")
		while True:
			MESSAGE=input("> ")
			self.sendMsg(MESSAGE, addr)
			data=""
			if MESSAGE=="exit":
				return None
			while data!="end" and data is not None:
				id, tipo, data, addr=self.recieveMsg(1024)
				if (data is not None):
					print("Recibido dato '{}' de '{}'".format(data, addr))
			
		
	def runClient(self):
		print("Cliente iniciado")
		while True:
			addr=self.comServerMain()
			if(addr is not None):
				print("dir", addr)
				self.comServerService(addr)
if __name__ == '__main__':
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = int(input("ingrese el puerto del server -> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	cliente=UDPSocketClient(ipServer, puertoServer)
	
	cliente.runClient()