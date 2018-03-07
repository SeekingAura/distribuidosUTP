import socket
import operator
import re
import time

class UDPSocketClient:
	def __init__(self, ip, puerto, tipo="client", rol="query"):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.addrServer=(ip, puerto)
		#self.sock.sendto("".encode('utf-8'), ("localhost", 5549))
		#self.addrClient=self.sock.getsockname()
		self.sock.settimeout(5)#Establecer tiempo limite de espera en segundos por cada recvfrom
		self.tipo=tipo
		self.rol=rol
		
	
	def sendMsg(self, rol="", tipo="", message="", addres="", trys=int(5), sock=""):
		time.sleep(1)
		if isinstance(message, str):
			message=self.rol+":"+self.tipo+":"+message+":"
		elif isinstance(message, bytes):
			message=self.rol+":"+self.tipo+":"+message.decode('utf-8')+":"
		else:
			print("ERROR - Data type to send can't work")
			return False
		for i in range(trys):
			print("mensaje enviado - {} - a {}".format(message, addres))
			sock.sendto(message.encode('utf-8'), addres)
			try:
				tempMensaje, tempAddr=sock.recvfrom(1024)
				# print("tempm", tempMensaje)
				if(tempMensaje.decode('utf-8')=="recibido"):
					return True
			except socket.timeout:
				print("hubo un error")
				time.sleep(1)
				continue
		print("Intentos superados, no fue posible enviar")
		return False
			
	def recieveMsg(self, size=int(1024), trys=int(5), sock=""):
		for i in range(trys):
			try:
				data, addr = sock.recvfrom(size)
				print("Mensaje recibido - {} - de {}".format(data.decode('utf-8'), addr))
				rol=None
				tipo=None
				mensaje=None
				temp=""
				for i in data.decode('utf-8'):
					if(i!=":"):
						temp+=i
					elif (rol is None and i==":"):
						rol=temp
						temp=""
					elif(tipo is None and i==":"):
						tipo=temp
						temp=""
					elif(mensaje is None and i==":"):
						mensaje=temp
						temp=""
				sock.sendto("recibido".encode('utf-8'), addr)
				return (rol, tipo, mensaje, addr)
			except socket.timeout:
				print("Tiempo de espera superado")
				continue
		return ("", "", "", "")
	
	def getAddres(self, message):
		addres, port=message.split(", ")
		addres=str(addres)
		port=int(port)
		return (addres, port)

	
	def runClient(self):
		print("cliente iniciado")
		while True:
			mensaje=input("Indique el servicio a solicitar")
			self.sendMsg(message=mensaje, addres=self.addrServer, sock=self.sock)
			rolServer, tipoServer, mensajeServer, addrServer=self.recieveMsg(sock=self.sock)
			if(mensajeServer=="Almacene"):
				tempSend=[]
				while True:
					rolServer, tipoServer, mensajeServer, addrServer=self.recieveMsg(sock=self.sock)
					if(mensajeServer=="fin"):
						break
					addres=self.getAddres(mensajeServer)
					tempSend.append(addres)

				for i in tempSend:
					self.sendMsg(message="operar", addres=i, sock=self.sock)
				self.sendMsg(message="operar", addres=self.addrServer, sock=self.sock)
				values=input("indique los operadores a enviar de la forma #.#, #.#")
				for i in tempSend:
					self.sendMsg(message=values, addres=i, sock=self.sock)
				rolServer, tipoServer, mensajeServer, addrServer=self.recieveMsg(sock=self.sock)
				print("respuesta = ", mensajeServer)
			else:
				while True:
					rolServer, tipoServer, mensajeServer, addrServer=self.recieveMsg(sock=self.sock)
					if(mensaje=="fin"):
						break

		while True:
			print("Indique operación")
	

			
if __name__ == '__main__':
	ipServer = input("Ingrese la ip del server Main-> ")
	puertoServer = int(input("ingrese el puerto del server Main-> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	client=UDPSocketClient(ipServer, puertoServer)
	client.runClient()