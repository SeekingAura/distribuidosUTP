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

class UDPSocketServerMain:
	def __init__(self, ip, puerto, tipo="main"):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.ip=ip
		self.puerto=puerto
		self.sock.bind((ip, puerto))
		self.sock.settimeout(60)#Establecer tiempo limite de espera en segundos por cada recvfrom
		self.tipo=tipo
		self.servers={}
	def sendMsg(self, message, addres):
		
		if isinstance(message, str):
			self.sock.sendto(message.encode('utf-8'), addres)
			print("mensaje enviado - {}".format(message))
		elif isinstance(message, bytes):
			self.sock.sendto(message, addres)
			print("mensaje enviado - {}".format(message.decode('utf-8')))
		else:
			print("ERROR - Data type to send can't work")
			return None
		
	def recieveMsg(self, size):
		try:
			data, addr = self.sock.recvfrom(size)
			print("Mensaje recibido - {}".format(data.decode('utf-8')))
			return (data.decode('utf-8'), addr)
		except socket.timeout:
			print("Tiempo de espera superado")
			return (None, None)
			
		except:
			return (None, None)
	
	def menu(self, addr):
		self.sendMsg("---Operaciones---", addr)
		self.sendMsg("- suma - aplica valor1+valor2", addr)
		self.sendMsg("- resta - aplica valor1-valor2", addr)
		self.sendMsg("- multi - aplica valor1*valor2", addr)
		self.sendMsg("- div - aplica valor1/valor2", addr)
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		if self.tipo=="main":
			print("conectado a servidores externos")
			for i in ["suma", "resta", "multi", "div"]:
				ipServer = input("Ingrese la ip del server de {} -> ".format(i))
				puertoServer = int(input("ingrese el puerto del server de {} -> ".format(i)))
				print("server IP:", ipServer, i)
				print("server port:", puertoServer, i)
				self.servers[i]=(ipServer, puertoServer)
				
			print("Servidores conectados, iniciando servidor de comunicación media")
			print("Server iniciado")
			while True:
				data, addrClient = self.recieveMsg(1024) # buffer size is 1024 bytes
				if data is not None:
					if(data=="cerrar"):
						for i in ["suma", "resta", "multi", "div"]:
							self.sendMsg("cerrar", self.servers[i])
						break
					operando=False
					if(data=="suma" or data=="resta" or data=="multi" or data=="div"):
						self.sendMsg("operar", self.servers[data])
						operando=True
						self.sendMsg("indique 2 valores de la forma #.#, #.#", addrClient)
						self.sendMsg("end", addrClient)
					else:
						self.sendMsg("La operación indicada no existe", addrClient)
						self.menu(addrClient)
						self.sendMsg("end", addrClient)
						
					if(operando):
						dataOp, addrClient = self.recieveMsg(1024)
						if dataOp is None:
							self.sendMsg("tiempo de espera superado".format(data), addrClient)
							self.sendMsg("end", addr)
						else:
							if "," in dataOp:
								self.sendMsg(dataOp, self.servers[data])
								dataResult, addrRespond = self.recieveMsg(1024)
								self.sendMsg("resultado: {}".format(dataResult), addrClient)
								self.sendMsg("end", self.servers[data])
								self.sendMsg("end", addrClient)
								self.menu(addrClient)
								
							else:
								self.sendMsg("Tiempo de espera superado...", addrClient)
								self.menu(addrClient)
								self.sendMsg("end", addrClient)
				elif(addrClient is not None):
					self.menu(addrClient)
					self.sendMsg("end", addrClient)
			self.sendMsg("end", addrClient)	
class UDPSocketServerSuma(UDPSocketServerMain):
	def __init__(self, ip, puerto):
		UDPSocketServerMain.__init__(self, ip, puerto, "suma")
		
	def MathSuma(self, value1, value2):
		return float(value1)+float(value2)
	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		while True:
			data, addr = servidor.recieveMsg(1024) # buffer size is 1024 bytes
			if data=="operar":
				data, addr = self.recieveMsg(1024)
				if data is not None:
					if data=="cerrar":
						break
					value1, value2=data.split(", ")
					servidor.sendMsg(str(self.MathSuma(value1, value2)), addr)
					#servidor.sendMsg("end", addr)
				#else:
					#servidor.sendMsg("Tiempo de espera superado", addr)
					#servidor.sendMsg("end", addr)
			elif data=="cerrar":
				break
				
class UDPSocketServerResta(UDPSocketServerMain):
	def __init__(self, ip, puerto):
		UDPSocketServerMain.__init__(self, ip, puerto, "resta")
		
			
	def MathResta(self, value1, value2):
		return float(value1)-float(value2)
		
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		while True:
			data, addr = servidor.recieveMsg(1024) # buffer size is 1024 bytes
			if data=="operar":
				data, addr = self.recieveMsg(1024)
				if data is not None:
					if data=="cerrar":
						break
					value1, value2=data.split(", ")
					servidor.sendMsg(str(self.MathResta(value1, value2)), addr)
					#servidor.sendMsg("end", addr)
				#else:
				#	servidor.sendMsg("Tiempo de espera superado", addr)
				#	servidor.sendMsg("end", addr)
			elif data=="cerrar":
				break
class UDPSocketServerMulti(UDPSocketServerMain):
	def __init__(self, ip, puerto):
		UDPSocketServerMain.__init__(self, ip, puerto, "multiplicación")
	
	def MathMulti(self, value1, value2):
		return float(value1)*float(value2)
		
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		while True:
			data, addr = servidor.recieveMsg(1024) # buffer size is 1024 bytes
			if data=="operar":
				data, addr = self.recieveMsg(1024)
				if data is not None:
					if data=="cerrar":
						break
					value1, value2=data.split(", ")
					servidor.sendMsg(str(self.MathMulti(value1, value2)), addr)
					#servidor.sendMsg("end", addr)
				# else:
					# servidor.sendMsg("Tiempo de espera superado", addr)
					# servidor.sendMsg("end", addr)
			elif data=="cerrar":
				break
		
class UDPSocketServerDiv(UDPSocketServerMain):
	def __init__(self, ip, puerto):
		UDPSocketServerMain.__init__(self, ip, puerto, "división")
		
	def MathDiv(self, value1, value2):
		return float(value1)/float(value2)
		
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		while True:
			data, addr = servidor.recieveMsg(1024) # buffer size is 1024 bytes
			if data=="operar":
				data, addr = self.recieveMsg(1024)
				if data is not None:
					value1, value2=data.split(", ")
					servidor.sendMsg(str(self.MathDiv(value1, value2)), addr)
					#servidor.sendMsg("end", addr)
				# else:
					# servidor.sendMsg("Tiempo de espera superado", addr)
					# servidor.sendMsg("end", addr)
			elif data=="cerrar":
				break
	
if __name__ == '__main__':

	tipo=input("Ingrese el tipo de server -> ")
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = int(input("ingrese el puerto del server -> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	
	
	servidor=globals()["UDPSocketServer"+tipo.title()](ipServer, puertoServer)
	servidor.runServer()