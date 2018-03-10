import socket
import operator
import re
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client

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

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2',)
	


class ServerRPCMain:
	def __init__(self, ip, puerto, tipo="main"):
		self.server=SimpleXMLRPCServer((ip, puerto), requestHandler=RequestHandler)
		self.server.register_introspection_functions()
		self.ip=ip
		self.puerto=puerto
		self.tipo=tipo
		self.servers={}
		
		
	
	def menu(self):
		return "---Operaciones---\n- suma - aplica valor1+valor2\n- resta - aplica valor1-valor2\n- multi - aplica valor1*valor2\n- div - aplica valor1/valor2\nDebe indicarse servidor, version, valor1, valor2, valor3, valor4\n la versión 1 es operación binarin, la 2 es de 3 valores y la 3 es de 4 valores"
		
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		if self.tipo=="main":
			print("conectado a servidores externos")
			for i in ["suma", "resta", "multi", "div"]:
				ipServer = str(input("Ingrese la ip del server de {} -> ".format(i)))
				puertoServer = str(input("ingrese el puerto del server de {} -> ".format(i)))
				print("server IP:", ipServer, i)
				print("server port:", puertoServer, i)
				self.servers[i]=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer)
				
			print("Servidores conectados, iniciando servidor de comunicación media")
			print("Server iniciado")
			self.server.register_function(self.soliOP, 'op')
			self.server.register_function(self.menu, 'menu')
			self.server.serve_forever()
			
	def soliOP(self, server, version, values):
		print("Solicitando operación de los valores {} al servidor {}, versión {}".format(values, server, version))
		if(server in [*self.servers]):
			if(version+1==len(values) and len(values)>1):
				if(len(values)==2):
					value1, value2=values
					print("valores", value1, value2)
					return self.servers[server].op1(value1, value2)
				elif(len(values)==3):
					value1, value2, value3=values
					return self.servers[server].op2(value1, value2, value3)
				elif(len(values)==4):
					value1, value2, value3, value4=values
					return self.servers[server].op3(value1, value2, value3, value4)
				return "Formato incorrecto"
		else:
			return "el servidor {} No existe".format(server)
			
class ServerRPCSuma(ServerRPCMain):
	def __init__(self, ip, puerto):
		ServerRPCMain.__init__(self, ip, puerto, "suma")
		
	def MathSuma1(self, value1, value2):
		print("Efectuando operación {}+{}".format(value1, value2))
		return float(value1)+float(value2)
		
	def MathSuma2(self, value1, value2, value3):
		print("Efectuando operación {}+{}+{}".format(value1, value2, value3))
		return float(value1)+float(value2)+float(value3)
		
	def MathSuma3(self, value1, value2, value3, value4):
		print("Efectuando operación {}+{}+{}+{}".format(value1, value2, value3, value4))
		return float(value1)+float(value2)+float(value3)+float(value4)
	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.MathSuma1, 'op1')
		self.server.register_function(self.MathSuma2, 'op2')
		self.server.register_function(self.MathSuma3, 'op3')
		self.server.serve_forever()
				
class ServerRPCResta(ServerRPCMain):
	def __init__(self, ip, puerto):
		ServerRPCMain.__init__(self, ip, puerto, "resta")
		
			
	def MathResta1(self, value1, value2):
		print("Efectuando operación {}-{}".format(value1, value2))
		return float(value1)-float(value2)
		
	def MathResta2(self, value1, value2, value3):
		print("Efectuando operación {}-{}-{}".format(value1, value2, value3))
		return float(value1)-float(value2)-float(value3)
		
	def MathResta3(self, value1, value2, value3, value4):
		print("Efectuando operación {}-{}-{}-{}".format(value1, value2, value3, value4))
		return float(value1)-float(value2)-float(value3)-float(value4)
		
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.MathResta1, 'op1')
		self.server.register_function(self.MathResta2, 'op2')
		self.server.register_function(self.MathResta3, 'op3')
		self.server.serve_forever()
		
class ServerRPCMulti(ServerRPCMain):
	def __init__(self, ip, puerto):
		ServerRPCMain.__init__(self, ip, puerto, "multiplicación")
	
	def MathMulti1(self, value1, value2):
		print("Efectuando operación {}*{}".format(value1, value2))
		return float(value1)*float(value2)
		
	def MathMulti2(self, value1, value2, value3):
		print("Efectuando operación {}*{}*{}".format(value1, value2, value3))
		return float(value1)*float(value2)*float(value3)
		
	def MathMulti3(self, value1, value2, value3, value4):
		print("Efectuando operación {}*{}*{}*{}".format(value1, value2, value3, value4))
		return float(value1)*float(value2)*float(value3)*float(value4)
	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.MathMulti1, 'op1')
		self.server.register_function(self.MathMulti2, 'op2')
		self.server.register_function(self.MathMulti3, 'op3')
		self.server.serve_forever()
		
class ServerRPCDiv(ServerRPCMain):
	def __init__(self, ip, puerto):
		ServerRPCMain.__init__(self, ip, puerto, "división")
		
	def MathDiv1(self, value1, value2):
		print("Efectuando operación {}/{}".format(value1, value2))
		return float(value1)/float(value2)
		
	def MathDiv2(self, value1, value2, value3):
		print("Efectuando operación {}/{}/{}".format(value1, value2, value3))
		return float(value1)/float(value2)/float(value3)
		
	def MathDiv3(self, value1, value2, value3, value4):
		print("Efectuando operación {}/{}/{}/{}".format(value1, value2, value3, value4))
		return float(value1)/float(value2)/float(value3)/float(value4)
		
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.MathDiv1, 'op1')
		self.server.register_function(self.MathDiv2, 'op2')
		self.server.register_function(self.MathDiv3, 'op3')
		self.server.serve_forever()
	
if __name__ == '__main__':
	tipo=input("Ingrese el tipo de server -> ")
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = int(input("ingrese el puerto del server -> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	
	
	servidor=globals()["ServerRPC"+tipo.title()](ipServer, puertoServer)
	servidor.runServer()