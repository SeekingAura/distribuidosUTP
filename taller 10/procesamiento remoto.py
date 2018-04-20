import psutil
#for i in range(1000):
#    print("YOLO")
print(psutil.cpu_percent())# muestra porcentaje de la cpu

print(psutil.virtual_memory())#Ram

import tkinter as tkinter
import threading
import time
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
	

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2',)


class serverRPC:
	def __init__(self, ip="localhost", puerto=5500, tipo="main"):
		#Server Control
		self.server=SimpleXMLRPCServer((ip, puerto), requestHandler=RequestHandler, allow_none=True)
		self.server.register_introspection_functions()
		self.ip=ip
		self.puerto=puerto
		self.tipo=tipo
		self.conecction=None
		self.busyWith=None
		self.servers=["http://"+ip+":"+str(puerto)]
		
		#Control Tkinter
		self.executing=False
		self.executingHelp=False
		self.startExecuteTime=0.0
		self.numberOfExecutes=0

		#Tkinter
		self.root = tkinter.Tk()
		self.root.wm_title("machine-"+tipo)#da el titulo a la ventana
		
		scrollbar = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
		scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

		self.TextoBox = tkinter.Text(self.root, height=8, width=80, yscrollcommand=scrollbar.set)
		self.TextoBox.pack(side=tkinter.LEFT, fill=tkinter.Y)
		
		frame = tkinter.Frame(self.root)
		frame.pack()
		

		tkinter.Label(frame, text='Estado:').grid(row=0, column=0)
		self.answer = tkinter.StringVar()
		self.answer.set("Ready")
		tkinter.Label(frame, textvariable=self.answer).grid(row=0, column=1)
		self.buttonExec=None
		if(tipo[:6]!="server" and tipo!="main"):
			self.buttonExec = tkinter.Button(frame, text='Execute', command=self.startExecute)
			self.buttonExec.grid(row=1, columnspan=1)
		

	def printBox(self, value):
		self.TextoBox.insert(tkinter.END, "\n"+str(value))
		self.TextoBox.see(tkinter.END)

	def printBoxRemote(self, value):
		self.TextoBox.after(1, self.printBox, str(value)+" - Estado del procesador {}".format(psutil.cpu_percent()))
	
	def runGraph(self):
		self.root.mainloop()
	
	def getServers(self):
		return self.servers

	#def executeRemote(self):
	def startExecute(self):
		self.buttonExec.config(state="disable")
		self.answer.set("Ejecutando...")
		self.startExecuteTime=time.time()
		self.executing=True
		self.numberOfExecutes=0
		self.executeLocal()
	
	def executeLocal(self):

		if(psutil.cpu_percent()>20 and self.startExecuteTime+10<=time.time() and not self.executingHelp):#Calcula el valor de la cpu
			self.executeHelp()
			self.executingHelp=True
		elif(self.executingHelp and self.busyWith is not None):
			self.numberOfExecutes+=1
			self.busyWith.printBoxRemote("Ejecutando vez {}, proveniente de {}%".format(self.numberOfExecutes, "http://"+self.ip+":"+str(self.puerto)))
				
		if(self.executing):
			self.numberOfExecutes+=1
			self.printBox("Ejecutando vez {}, estado procesador {}%".format(self.numberOfExecutes, psutil.cpu_percent()))
			self.buttonExec.after(1, self.executeLocal)
	
	def executeHelp(self):
		self.answer.set("Buscando recursos")
		serversAddres=self.conecction.getServers()
		servers=[]
		for i in serversAddres:
			servers.append(xmlrpc.client.ServerProxy(i))

		self.busyWith=None
		while self.busyWith is None:
			for i in servers:
				if(i.setProcess("http://"+self.ip+":"+str(self.puerto))):
					self.busyWith=i
					break
		self.printBox("Iniciado valor compartido {}".format(self.busyWith))
		self.answer.set("Ejecutando y Remoto")
		self.buttonExec.after(10000, self.cleanProcess)

	def setProcess(self, client):
		if(self.busyWith is None):
			self.answer.set("Ayudando a Ejecutar")
			self.busyWith=client
			self.executing=True
			self.printBox("Se ha dado compartido a {}".format(self.busyWith))
			return True
		self.printBox("Estoy ocupado, No se le puede compartir a {}".format(self.busyWith))
		return False

	def cleanProcess(self):
		self.printBox("Se ha terminado el compartido a {}".format(self.busyWith))
		if(self.tipo[:6]!="server" and self.tipo!="main"):
			self.busyWith.cleanProcess()
			self.buttonExec.config(state="normal")

		
		self.busyWith=None
		self.executing=False
		self.executingHelp=False
		self.answer.set("Ready")
		

			


	# Funciones del servidor para el cliente
	def register(self, ipServer, puertoServer):
		#value=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer)
		self.servers.append("http://"+ipServer+":"+puertoServer)
		self.printBox("Se ha registrado el servidor {}".format("http://"+ipServer+":"+puertoServer))

	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		if self.tipo=="main":
			self.server.register_function(self.register, 'register')
			self.server.register_function(self.getServers, 'getServers')
			self.server.register_function(self.setProcess, 'setProcess')
			self.server.register_function(self.cleanProcess, 'cleanProcess')
			self.server.register_function(self.printBoxRemote, 'printBoxRemote')

		elif self.tipo[:6]=="server":
			self.server.register_function(self.setProcess, 'setProcess')
			self.server.register_function(self.cleanProcess, 'cleanProcess')
			self.server.register_function(self.printBoxRemote, 'printBoxRemote')
			ipServer = str(input("Ingrese la ip del server principal\n"))
			puertoServer = str(input("ingrese el puerto del server principal\n"))
			self.conecction=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
			self.conecction.register(self.ip, str(self.puerto))
		else:
			#self.server.register_function(self.setTime, 'setTime')
			#self.server.register_function(self.getTime, 'getTime')
			ipServer = str(input("Ingrese la ip del server principal\n"))
			puertoServer = str(input("ingrese el puerto del server principal\n"))
			self.conecction=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
		self.server.serve_forever()

if __name__ == "__main__":
	tipoServer=str(input("El tipo de servidor\n"))
	ipServer = str(input("Ingrese la ip para el servidor\n"))
	puertoServer = int(input("ingrese el puerto para el servidor\n"))
	
	server=serverRPC(ipServer, puertoServer, tipoServer)
	hilo1=threading.Thread(target=server.runServer)
	hilo1.start()
	server.runGraph()
