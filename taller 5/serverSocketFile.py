import socket
import operator
import re

class UDPSocketServer:
	def __init__(self, ip, puerto, tipo="server", id="0"):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.ip=ip
		self.puerto=puerto
		self.sock.bind((ip, puerto))
		self.sock.settimeout(30)#Establecer tiempo limite de espera en segundos por cada recvfrom
		self.tipo=tipo
		self.id=id
		self.clients=[]
		
	
	def sendMsg(self, id, tipo, message, addres):
		
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
			return False
		tempId, tempTipo, tempMensaje, tempAddr=self.recieveMsg()
		if(tempId==id, tempTipo==tipo, tempMensaje=="recibido", tempAddr==addres):
				return True
		return False
			
	def recieveMsg(self, size=int(1024)):
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
			self.sock.sendto((self.id+":"+self.tipo+":"+"recibido:").encode('utf-8'), addr)
			return (id, tipo, mensaje, addr)
		except socket.timeout:
			print("Tiempo de espera superado")
			return (None, None, None, None)
			
		except:
			return (None, None, None, None)
	def recieveFile(self, size=1024):
		data, addr = self.sock.recvfrom(size)
		return data.decode("utf-8")

	def runServer(self):
		print("servidor iniciado")
		data=""
		while True:
			print("Esperando por archivos")
			idClient, tipoClient, mensajeClient, addrClient=self.recieveMsg()
			if(mensajeClient=="enviar"):
				data=""
				print("recibiendo archivo...")
				self.sendMsg(idClient, tipoClient, "recibiendo", addrClient)
				while True:
					mensaje=self.recieveFile()
					print("recibí", mensaje)
					if(mensaje=="-.-"):
						break
					else:
						data+=mensaje

			if(data!=""):
				file = open("recibido.txt","w") 
				file.write(data)
				file.close()
				#print("recibido archivo -> ", data)
			
			
			
if __name__ == '__main__':
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = int(input("ingrese el puerto del server -> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	servidor=UDPSocketServer(ipServer, puertoServer)
	servidor.runServer()