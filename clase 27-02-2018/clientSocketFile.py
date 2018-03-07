import socket
import operator
import re
import time

class UDPSocketClient:
	def __init__(self, ip, puerto, tipo="client", id="0"):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.ip=ip
		self.puerto=puerto
		self.sock.settimeout(30)#Establecer tiempo limite de espera en segundos por cada recvfrom
		self.tipo=tipo
		self.id=id
		self.clients=[]
		
	
	def sendMsg(self, id, tipo, message, addres):
		print("enviando {} -> tipo {}".format(message, type(message)))
		if isinstance(message, str):
			message=self.id+":"+self.tipo+":"+message+":"
			self.sock.sendto(message.encode('utf-8'), addres)
			print("mensaje enviado - {}".format(message))
		elif isinstance(message, bytes):
			message=self.id+":"+self.tipo+":"+message.decode('utf-8')+":"
			self.sock.sendto(message.encode('utf-8'), addres)
			print("mensaje enviado - {}".format(message.decode('utf-8')))
		else:
			print("ERROR - Data type to send can't work")
			return False
		tempId, tempTipo, tempMensaje, tempAddr=self.recieveMsg()
		if(tempId==id, tempTipo==tipo, tempMensaje=="recibido", tempAddr==addres):
				return True
		return False
			
	def sendFile(self, data, addr):
		print("enviando -> \n", data)
		try:
			self.sock.sendto(data, addr)
			return True
		except:
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
	
	def runClient(self):
		print("cliente iniciado")
		data=""
		while True:
			fileName=input("indique el nombre del archivo ->\n")
			
			
			if(self.sendMsg("0", "server", "enviar", (self.ip, self.puerto))):
				print("enviado archivo...")
				fileComplete=open(fileName, 'rb')
				filePart=fileComplete.read(1024)
				while(filePart):
					time.sleep(1)
					if(not self.sendFile(filePart, (self.ip, self.puerto))):
						print("hubo errores al enviar")
						break
					filePart=fileComplete.read(1024)
				time.sleep(1)
				self.sendFile("-.-".encode("utf-8"), (self.ip, self.puerto))
				
			if(data!=""):
				print("recibido archivo -> ", data)
	
			
			
if __name__ == '__main__':
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = int(input("ingrese el puerto del server -> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	client=UDPSocketClient(ipServer, puertoServer)
	client.runClient()