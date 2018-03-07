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
		return "---Operaciones---\n- suma - aplica valor1+valor2\n- resta - aplica valor1-valor2\n- multi - aplica valor1*valor2\n- div - aplica valor1/valor2"
		
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
			
	def soliOP(self, server, op1, op2):
		print("Solicitando operación de los valores {}, {} al servidor {}".format(op1, op2, server))
		if(server in [*self.servers]):
			return self.servers[server].op(op1, op2)
		return "el servidor {} No existe".format(server)
			
class ServerRPCSuma(ServerRPCMain):
	def __init__(self, ip, puerto):
		ServerRPCMain.__init__(self, ip, puerto, "suma")
		
	def MathSuma(self, value1, value2):
		print("Efectuando operación {}+{}".format(value1, value2))
		return float(value1)+float(value2)
	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.MathSuma, 'op')
		self.server.serve_forever()
				
class ServerRPCResta(ServerRPCMain):
	def __init__(self, ip, puerto):
		ServerRPCMain.__init__(self, ip, puerto, "resta")
		
			
	def MathResta(self, value1, value2):
		print("Efectuando operación {}-{}".format(value1, value2))
		return float(value1)-float(value2)
		
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.MathResta, 'op')
		self.server.serve_forever()
		
class ServerRPCMulti(ServerRPCMain):
	def __init__(self, ip, puerto):
		ServerRPCMain.__init__(self, ip, puerto, "multiplicación")
	
	def MathMulti(self, value1, value2):
		print("Efectuando operación {}*{}".format(value1, value2))
		return float(value1)*float(value2)
		
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.MathMulti, 'op')
		self.server.serve_forever()
		
class ServerRPCDiv(ServerRPCMain):
	def __init__(self, ip, puerto):
		ServerRPCMain.__init__(self, ip, puerto, "división")
		
	def MathDiv(self, value1, value2):
		print("Efectuando operación {}/{}".format(value1, value2))
		return float(value1)/float(value2)
		
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.MathDiv, 'op')
		self.server.serve_forever()
	
if __name__ == '__main__':

	tipo=input("Ingrese el tipo de server -> ")
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = int(input("ingrese el puerto del server -> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	
	
	servidor=globals()["ServerRPC"+tipo.title()](ipServer, puertoServer)
	servidor.runServer()