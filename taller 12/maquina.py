import threading
import time
import tkinter as tkinter
import xmlrpc.client
import sys
import random
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer


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
		self.procesador=0
		self.servers={}
		self.colaProceso=[]

		#Control Tkinter
		self.executing=False
		self.executingHelp=False
		self.needHelp=False
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
		

		
		self.aswerInfo=tkinter.Label(frame, text='Estado').grid(row=1, column=0)
		self.answer = tkinter.StringVar()
		tkinter.Label(frame, textvariable=self.answer).grid(row=1, column=1)
		self.buttonExecute=None
		if(tipo!="main"):
			self.buttonExecute = tkinter.Button(frame, text='Execute', command=self.startExecute)
			self.buttonExecute.grid(row=2, columnspan=2)
		

	def printBox(self, value):
		self.TextoBox.insert(tkinter.END, "\n"+str(value))
		self.TextoBox.see(tkinter.END)
	
	def printBoxRemote(self, value):
		self.TextoBox.after(250, self.printBox, str(value))
		
	def getServer(self, serverToGet):
		if(serverToGet is not None):
			self.buttonExecute.after(10000, self.cleanProcess)
			return xmlrpc.client.ServerProxy(serverToGet, allow_none=True)
		else:
			return None

	def setProcesador(self):
		self.procesador=random.randint(0, 100)
		print(self.procesador)
		self.TextoBox.after(1000, self.setProcesador)

	def runGraph(self):
		self.root.mainloop()
	

	def getStatus(self):
		if(not self.executingHelp and not self.busyWith):
			return self.procesador
		else:
			return 100

	def startExecute(self):
		self.answer.set("Ejecutando...")
		self.executing=True
		self.numberOfExecutes=0
		self.buttonExecute.config(state="disable")
		self.executeLocal()

	def executeLocal(self):
		if(self.busyWith is not None and self.executing and not self.executingHelp):
			self.numberOfExecutes+=1
			self.busyWith.printBoxRemote("Ejecutando vez {}, proveniente de {}%".format(self.numberOfExecutes, "http://"+self.ip+":"+str(self.puerto)))
			
					
		if(self.executing):
			self.numberOfExecutes+=1
			self.printBox("Ejecutando vez {}".format(self.numberOfExecutes))
			self.buttonExecute.after(250, self.executeLocal)
	
		if(self.procesador>=70 and not self.executingHelp and self.busyWith is None):
			self.needHelp=True
		if(self.needHelp):#garantiza que siga solicitnado ayuda tras cada ejecución
			self.busyWith=self.getServer(self.conecction.getExecuter("http://"+self.ip+":"+str(self.puerto)))
			if(self.busyWith is not None):
				self.needHelp=False
			#self.printBox("Obtenido ayuda de {}".format(self.numberOfExecutes))
			
	def showTable(self):
		self.printBox("Estado de tabla:")
		for i in self.servers:
			self.printBox(i+" -> "+str(self.servers.get(i)))
	def getExecuter(self, machine):
		
		self.printBox("Buscando equipo Disponible para -> {}".format(machine))
		self.showTable()
		
		servers=[]
		
		for i in self.servers:
			servers.append([xmlrpc.client.ServerProxy(i), i])
		
		serverToAsign=None
		#Get min value
		temp=None
		if(len(self.colaProceso)>0):
			temp=self.servers.get(self.colaProceso[0])
			for i in self.colaProceso:
				newTemp=self.servers.get(i)
				if(newTemp<temp):
					temp=newTemp

		if(temp is not None):
			if(self.servers.get(machine)>temp):
				self.printBox("No hay disponible - dado por la prioridad y cola")
				if(not machine in self.colaProceso):
					self.colaProceso.append(machine)
					self.servers[machine]-=1
				return None
		
		serverToAsign=None
		for i in servers:
			procesador=i[0].getStatus()
			if(procesador<70):
				if(i[0].setProcess("http://"+self.ip+":"+str(self.puerto))):
					serverToAsign=i[1]
					self.printBox("Se ha encontrado un servidor")
					break
		
		if(serverToAsign is not None):
			self.printBox("Entregado valor compartido {}".format(machine))
			if(machine in self.colaProceso):
				self.colaProceso.remove(machine)
				
			self.servers[machine]+=1
			self.showTable()
			return serverToAsign
		else:
			if(not machine in self.colaProceso):
				self.colaProceso.append(machine)
				self.servers[machine]-=1
				self.showTable()
			self.printBox("No hay disponible")
			return None
		

	def setProcess(self, client):
		if(self.executingHelp is False):
			self.printBox("Se ha dado compartido a {}".format(client))
			self.executingHelp=True
			return True
		self.printBox("Estoy ocupado, No se le puede compartir a {}".format(self.busyWith))
		return False

	def cleanProcess(self):
		self.printBox("Se ha terminado el compartido")
		if(self.busyWith is not None and not isinstance(self.busyWith, str)):
			self.busyWith.cleanProcess()
			

		
		self.busyWith=None
		self.executing=False
		self.executingHelp=False
		self.buttonExecute.config(state="normal")
		self.answer.set("Ready")

			


	# Funciones del servidor para el cliente
	def register(self, ipServer, puertoServer):
		#value=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer)
		self.servers["http://"+ipServer+":"+puertoServer]=0
		self.printBox("Se ha registrado el servidor {}".format("http://"+ipServer+":"+puertoServer))

	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		if self.tipo=="main":
			self.server.register_function(self.register, 'register')
			self.server.register_function(self.getExecuter, 'getExecuter')

		else:
			self.server.register_function(self.setProcess, 'setProcess')
			self.server.register_function(self.getStatus, 'getStatus')
			self.server.register_function(self.cleanProcess, 'cleanProcess')
			self.server.register_function(self.printBoxRemote, 'printBoxRemote')
			ipServer = str(input("Ingrese la ip del server principal\n"))
			puertoServer = str(input("ingrese el puerto del server principal\n"))
			
			
			self.conecction=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
			self.conecction.register(self.ip, str(self.puerto))
			self.setProcesador()
		self.server.serve_forever()

if __name__ == "__main__":
	tipoServer=str(input("El tipo de servidor\n"))
	ipServer = str(input("Ingrese la ip para el servidor\n"))
	puertoServer = int(input("ingrese el puerto para el servidor\n"))
	server=serverRPC(ipServer, puertoServer, tipoServer)
	hilo1=threading.Thread(target=server.runServer)
	hilo1.start()
	server.runGraph()
