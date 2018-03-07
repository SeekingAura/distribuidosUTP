from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2',)

class ServerRPC:
	def __init__(self, ip, puerto, tipo="main"):
		self.server=SimpleXMLRPCServer((ip, puerto), requestHandler=RequestHandler, allow_none=True)
		self.server.register_introspection_functions()
		self.ip=ip
		self.puerto=puerto
		self.tipo=tipo
		self.servers={}
	def modTipo(self, tipo):
		print("tipo era", self.tipo)
		self.tipo=tipo
		print("tipo es", self.tipo)
		return "cambiado tipo de server a "+tipo
# Create server
server= ServerRPC("localhost", 8000)

# Register pow() function; this will use the value of
# pow.__name__ as the name, which is just 'pow'.
server.server.register_function(pow)
server.server.register_function(server.modTipo)

# Register a function under a different name
def adder_function(x,y):
	return x + y
server.server.register_function(adder_function, 'add')

# Register an instance; all the methods of the instance are
# published as XML-RPC methods (in this case, just 'mul').
class MyFuncs:
	def mul(self, x, y):
		return x * y

server.server.register_instance(MyFuncs())

# Run the server's main loop
server.server.serve_forever()