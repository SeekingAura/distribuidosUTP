import socket
import operator
import re
def get_operator_fn(op):
    return {
        '+' : operator.add,
        '-' : operator.sub,
        '*' : operator.mul,
        '/' : operator.truediv,
        '%' : operator.mod,
        '^' : operator.xor,
        }[op]
		
def eval_binary_expr(op1, operator, op2):
    op1,op2 = int(op1), int(op2)
    return get_operator_fn(operator)(op1, op2)
	
def getKeyByValue(dict, value):
	x=[k for k,v in dict.items() if v == value]
	if(len(x)>=1):
		return [k for k,v in dict.items() if v == value][0]
	else:
		return None

class UDPSocketServerMain:
	def __init__(self, ip, puerto, tipo="main"):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.ip=ip
		self.puerto=puerto
		self.sock.bind((ip, puerto))
		self.sock.settimeout(60)#Establecer tiempo limite de espera en segundos por cada recvfrom
		self.id="-1"
		self.tipo=tipo
		self.servers={}
		self.clients={}
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
	
	def menu(self, addr):
		self.sendMsg("### Operaciones ###", addr)
		self.sendMsg("* suma -> aplica valor1+valor2", addr)
		self.sendMsg("* resta -> aplica valor1-valor2", addr)
		self.sendMsg("* multi -> aplica valor1*valor2", addr)
		self.sendMsg("* div -> aplica valor1/valor2", addr)
	def runServer(self):
		
		while True:
			id, tipo, data, addr = self.recieveMsg(1024) # buffer size is 1024 bytes 
			if data is not None:#getKeyByValue
				if(data=="registrar"):
					if tipo=="cliente":
						if(id=="-1"):
							changed=False
							for i in range(10):
								if(not(str(i) in [*self.clients])):
									self.clients[str(i)]=addr
									self.sendMsg("registrando id~"+str(i), addr)
									self.sendMsg("end", addr)
									changed=True
									break
							if(not changed):
								print("Limite alcanzado de clientes")
						else:
							print("ya está registrado")
					elif(tipo is not None):
						if(id=="-1"):
							changed=False
							if(not(tipo in [*self.servers])):
								self.servers[tipo]=addr
								self.sendMsg("registrando id~"+tipo, addr)
								self.sendMsg("end", addr)
								changed=True
							else:
								print("ya existe el servidor")
							if(not changed):
								print("Hubo problema al registrar el server")
				
				if((data=="suma" or data=="resta" or data=="multi" or data=="div") and tipo=="cliente"):
					self.sendMsg("dirección~"+str(self.servers[data]), addr)
					self.sendMsg("end", addr)
					
				elif(tipo=="cliente"):
					self.menu(addr)
					self.sendMsg("end", addr)
					
					
				
			else:
				if(tipo=="cliente"):
					self.menu(addrClient)
					self.sendMsg("end", addr)
		self.sendMsg("end", addr)
		

class UDPSocketServerSuma(UDPSocketServerMain):
	def __init__(self, ip, puerto):
		UDPSocketServerMain.__init__(self, ip, puerto, "suma")
		
	def MathSuma(self, value1, value2):
		return float(value1)+float(value2)
	
	
	def runServer(self):
		print("registrando servidor")
		ipServerMain=input("Indique la ip del servidor main -> ")
		puertoServerMain=int(input("Indique el puerto del servidor main -> "))
		while True:
			self.sendMsg("registrar", (ipServerMain, puertoServerMain))
			id, tipo, data, addr = self.recieveMsg(1024) # buffer size is 1024 bytes
			if("~" in data and tipo=="main"):
				tag=""
				temp=""
				for i in data:
					if(i!="~"):
						temp+=i
					if(i=="~"):
						tag=temp
						temp=""
						break
				if(tag=="registrando id"):
					self.id=temp
					break
		
		print("corriendo server de tipo {}".format(self.tipo))
		
		while True:
			id, tipo, data, addr = self.recieveMsg(1024) # buffer size is 1024 bytes
			if data=="operar" and tipo=="cliente":
				self.sendMsg("indique los datos a operar con {} de la forma #.#, #.#".format(self.tipo), addr)
				self.sendMsg("end", addr)
				while(data!="exit"):
					id, tipo, data, addr = self.recieveMsg(1024)
					if("," in data):
						value1, value2=data.split(", ")
						self.sendMsg(str(self.MathSuma(value1, value2)), addr)
					elif(data!="exit"):
						self.sendMsg("Operación mal ingresada" ,addr)
						self.sendMsg("indique los datos a operar con {} de la forma #.#, #.#".format(self.tipo), addr)
					self.sendMsg("end", addr)
			elif(data=="cerrar" and tipo=="main"):
				break
				
class UDPSocketServerResta(UDPSocketServerMain):
	def __init__(self, ip, puerto):
		UDPSocketServerMain.__init__(self, ip, puerto, "resta")
		
			
	def MathResta(self, value1, value2):
		return float(value1)-float(value2)
		
	def runServer(self):
		print("registrando servidor")
		ipServerMain=input("Indique la ip del servidor main -> ")
		puertoServerMain=int(input("Indique el puerto del servidor main -> "))
		while True:
			self.sendMsg("registrar", (ipServerMain, puertoServerMain))
			id, tipo, data, addr = self.recieveMsg(1024) # buffer size is 1024 bytes
			if("~" in data and tipo=="main"):
				tag=""
				temp=""
				for i in data:
					if(i!="~"):
						temp+=i
					if(i=="~"):
						tag=temp
						temp=""
						break
				if(tag=="registrando id"):
					self.id=temp
					break
		
		print("corriendo server de tipo {}".format(self.tipo))
		
		while True:
			id, tipo, data, addr = self.recieveMsg(1024) # buffer size is 1024 bytes
			if data=="operar" and tipo=="cliente":
				self.sendMsg("indique los datos a operar con {} de la forma #.#, #.#".format(self.tipo), addr)
				self.sendMsg("end", addr)
				while(data!="exit"):
					id, tipo, data, addr = self.recieveMsg(1024)
					if("," in data):
						value1, value2=data.split(", ")
						self.sendMsg(str(self.MathResta(value1, value2)), addr)
					elif(data!="exit"):
						self.sendMsg("Operación mal ingresada" ,addr)
						self.sendMsg("indique los datos a operar con {} de la forma #.#, #.#".format(self.tipo), addr)
				self.sendMsg("end", addr)
			elif(data=="cerrar" and tipo=="main"):
				break
class UDPSocketServerMulti(UDPSocketServerMain):
	def __init__(self, ip, puerto):
		UDPSocketServerMain.__init__(self, ip, puerto, "multiplicación")
	
	def MathMulti(self, value1, value2):
		return float(value1)*float(value2)
		
	def runServer(self):
		print("registrando servidor")
		ipServerMain=input("Indique la ip del servidor main -> ")
		puertoServerMain=int(input("Indique el puerto del servidor main -> "))
		while True:
			self.sendMsg("registrar", (ipServerMain, puertoServerMain))
			id, tipo, data, addr = self.recieveMsg(1024) # buffer size is 1024 bytes
			if("~" in data and tipo=="main"):
				tag=""
				temp=""
				for i in data:
					if(i!="~"):
						temp+=i
					if(i=="~"):
						tag=temp
						temp=""
				if(tag=="registrando id"):
					self.id=temp
					break
		
		print("corriendo server de tipo {}".format(self.tipo))
		
		while True:
			id, tipo, data, addr = self.recieveMsg(1024) # buffer size is 1024 bytes
			if data=="operar" and tipo=="cliente":
				self.sendMsg("indique los datos a operar con {} de la forma #.#, #.#".format(self.tipo), addr)
				self.sendMsg("end", addr)
				while(data!="exit"):
					id, tipo, data, addr = self.recieveMsg(1024)
					if("," in data):
						value1, value2=data.split(", ")
						self.sendMsg(str(self.MathMulti(value1, value2)), addr)
					elif(data!="exit"):
						self.sendMsg("Operación mal ingresada" ,addr)
						self.sendMsg("indique los datos a operar con {} de la forma #.#, #.#".format(self.tipo), addr)
				self.sendMsg("end", addr)
			elif(data=="cerrar" and tipo=="main"):
				break
		
class UDPSocketServerDiv(UDPSocketServerMain):
	def __init__(self, ip, puerto):
		UDPSocketServerMain.__init__(self, ip, puerto, "división")
		
	def MathDiv(self, value1, value2):
		return float(value1)/float(value2)
		
	def runServer(self):
		print("registrando servidor")
		ipServerMain=input("Indique la ip del servidor main -> ")
		puertoServerMain=int(input("Indique el puerto del servidor main -> "))
		while True:
			self.sendMsg("registrar", (ipServerMain, puertoServerMain))
			id, tipo, data, addr = self.recieveMsg(1024) # buffer size is 1024 bytes
			if("~" in data and tipo=="main"):
				tag=""
				temp=""
				for i in data:
					if(i!="~"):
						temp+=i
					if(i=="~"):
						tag=temp
						temp=""
				if(tag=="registrando id"):
					self.id=temp
					break
		
		print("corriendo server de tipo {}".format(self.tipo))
		
		while True:
			id, tipo, data, addr = self.recieveMsg(1024) # buffer size is 1024 bytes
			if data=="operar" and tipo=="cliente":
				self.sendMsg("indique los datos a operar con {} de la forma #.#, #.#".format(self.tipo), addr)
				self.sendMsg("end", addr)
				while(data!="exit"):
					id, tipo, data, addr = self.recieveMsg(1024)
					if("," in data):
						value1, value2=data.split(", ")
						self.sendMsg(str(self.MathDiv(value1, value2)), addr)
					elif(data!="exit"):
						self.sendMsg("Operación mal ingresada" ,addr)
						self.sendMsg("indique los datos a operar con {} de la forma #.#, #.#".format(self.tipo), addr)
				self.sendMsg("end", addr)
			elif(data=="cerrar" and tipo=="main"):
				break
	
	
	
if __name__ == '__main__':

	tipo=input("Ingrese el tipo de server -> ")
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = int(input("ingrese el puerto del server -> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	
	
	servidor=globals()["UDPSocketServer"+tipo.title()](ipServer, puertoServer)
	servidor.runServer()