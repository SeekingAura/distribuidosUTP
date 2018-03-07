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

class UDPSocketServer:
	def __init__(self, ip, puerto):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.ip=ip
		self.puerto=puerto
		self.sock.bind((ip, puerto))
		self.sock.settimeout(1)#Establecer tiempo limite de espera en segundos por cada recvfrom
		self.clients=[]
		self.data=[]
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
	
	def operar(self, data):
		self.data=[]
		temp=""
		for i in data:
			if(re.match('[+\-\*\%\/]*', str(i)).group(0)!=""):
				self.data.append(float(temp))
				self.data.append(str(i))
				temp=""
			elif(re.match('[0-9]*', str(i)).group(0)!=""):
				temp+=i
			else:
				print("El mensaje recibido no es del formato compatible")
				return None
		if(temp==""):
			print("El mensaje recibido no es del formato compatible")
			return None
		else:
			self.data.append(float(temp))
		return self.MathOperator(self.data)
	
	def MathOperator(self, operaciones):
		resultado=None
		operator=None
		if(re.match('[\*\%\/]*', str(operaciones[0])).group(0)!="" or re.match('[+\-\*\%\/]*', str(operaciones[-1])).group(0)!=""):
			print("el primer operador no es funcional")
			return None
		elif(re.match('[+\-]*', str(operaciones[0])).group(0)!=""):
			operator=operaciones.pop(0)
			opTemp=0
			count=0
			resultado=0
			for i in operaciones:
				count+=1
				if(i[0]==re.match('[+\-\*\%\/]*', str(i)).group(0)!=""):
					opTemp+=i
				else:
					resultado+=get_operator_fn(operator)(0, float(opTemp))
					break
			for i in range(count):
				operaciones.pop(0)
		opTemp=None
		operator=None
		if(resultado is None):
			resultado=operaciones.pop(0)
		for i in operaciones:
			if(re.match('[0-9]*', str(i)).group(0)!=""):
				opTemp=i
				resultado=get_operator_fn(operator)(resultado, float(opTemp))
			else:
				operator=i
		return resultado
			
			
			
			
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
			servidor.sendMsg("Operando...", addr)
			operaciones=servidor.operar(data)
			if operaciones is not None:
				servidor.sendMsg("Operación {} = {}".format(data, operaciones), addr)
			else:
				servidor.sendMsg("No es operable", addr)
			print("Enviando respuestas':".format(data, addr))
			servidor.sendMsg("end", addr)