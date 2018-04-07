import threading
import time
import tkinter as tkinter
import xmlrpc.client
import sys
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2',)


class serverRPC:
	def __init__(self, ip="localhost", puerto=5500, tipo="main", procesadorGhz=1.0, ramMB=8192 ):
		#Server Control
		self.server=SimpleXMLRPCServer((ip, puerto), requestHandler=RequestHandler, allow_none=True)
		self.server.register_introspection_functions()
		self.ip=ip
		self.puerto=puerto
		self.tipo=tipo
		self.conecction=None
		self.busyWith=None
		self.servers=[]
		self.procesadorGhz=procesadorGhz
		self.ramMB=ramMB
        
        #Tkinter
		self.root = tkinter.Tk()
		self.root.wm_title("machine-"+tipo)#da el titulo a la ventana
		
		scrollbar = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
		scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

		self.TextoBox = tkinter.Text(self.root, height=8, width=80, yscrollcommand=scrollbar.set)
		self.TextoBox.pack(side=tkinter.LEFT, fill=tkinter.Y)
		
		frame = tkinter.Frame(self.root)
		frame.pack()
		

		tkinter.Label(frame, text='Procesador (Ghz)').grid(row=0, column=0)
		self.BoxProcesador = tkinter.DoubleVar()
		tkinter.Entry(frame, textvariable=self.BoxProcesador).grid(row=0, column=1)
		tkinter.Label(frame, text='Ram (MB)').grid(row=0, column=2)
		self.BoxRAM = tkinter.DoubleVar()
		tkinter.Entry(frame, textvariable=self.BoxRAM).grid(row=0, column=3)
		tkinter.Label(frame, text='Estado').grid(row=1, column=0)
		self.answer = tkinter.StringVar()
		tkinter.Label(frame, textvariable=self.answer).grid(row=1, column=1)
		self.buttonSend=None
		if(tipo[:6]!="server" and tipo!="main"):
			self.buttonSend = tkinter.Button(frame, text='Send', command=self.sendCom)
			self.buttonSend.grid(row=2, columnspan=2)
		
		

	def printBox(self, value):
		self.TextoBox.insert(tkinter.END, "\n"+str(value))
		self.TextoBox.see(tkinter.END)
	
	def sendCom(self):
		valueProcesador=self.BoxProcesador.get()
		valueRAM=self.BoxRAM.get()
		if(valueProcesador is not None and valueRAM is not None):
			serverToGet=self.conecction.getExecuter(valueProcesador, valueRAM, "http://"+self.ip+":"+str(self.puerto))
			self.BoxProcesador.set("")
			self.BoxRAM.set("")
			if(serverToGet is not None):
				self.busyWith=xmlrpc.client.ServerProxy(serverToGet)
				self.buttonSend.after(5000, self.cleanProcess())
				#self.buttonExec.after(5000, self.execute)
				



		#date, tiempo=self.command.get().split(" ")
		self.answer.set("processing...")
		#self.serverDato=value
		
		#self.answer1.set("Ready")
	
	def runGraph(self):
		self.root.mainloop()
	

	def getStatus(self):
		return self.procesadorGhz, self.ramMB


	def getExecuter(self, procesadorGhz=1.0, ramMB=8192, machine=""):
		self.printBox("Buscando equipo con procesador {} Ghz y ram {} MB".format(procesadorGhz, ramMB))
		servers=[]
		
		for i in self.servers:
			servers.append([xmlrpc.client.ServerProxy(i), i])
		
		#machineConecction=xmlrpc.client.ServerProxy(machine)
		serverToAsign=None
		trys=0
		while serverToAsign is None:
			for i in servers:
				procesador, ram=i[0].getStatus()
				if(procesadorGhz<procesador and ramMB<ram):
					if(i[0].setProcess(machine)):
						serverToAsign=i[1]
						self.printBox("Se ha encontrado un servidor")
						break
			if(trys>=10):
				self.printBox("No hay servidores disponibles para lo recibido")
				break
			else:
				trys+=1
		if(serverToAsign is not None):
			self.printBox("Entregado valor compartido {}".format(machine))
			return serverToAsign
			#self.buttonExec.after(5000, self.execute)
		else:
			self.printBox("No hay disponible")
		
		
		
		#else:
		#	self.printBox("Terminado valor compartido con {}".format(self.busyWith))
		#	self.busyWith.cleanProcess()
		#	self.busyWith=None

	def setProcess(self, client):
		if(self.busyWith is None):
			self.busyWith=client
			self.printBox("Se ha dado compartido a {}".format(self.busyWith))
			return True
		self.printBox("Estoy ocupado, No se le puede compartir a {}".format(self.busyWith))
		return False

	def cleanProcess(self):
		self.printBox("Se ha terminado el compartido a {}".format(self.busyWith))
		if(self.tipo[:7]=="cliente"):
			self.busyWith.cleanProcess()
			self.busyWith=None
		else:
			self.busyWith=None

			


	# Funciones del servidor para el cliente
	def register(self, ipServer, puertoServer):
		#value=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer)
		self.servers.append("http://"+ipServer+":"+puertoServer)
		self.printBox("Se ha registrado el servidor {}".format("http://"+ipServer+":"+puertoServer))

	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		if self.tipo=="main":
			self.server.register_function(self.register, 'register')
			self.server.register_function(self.getExecuter, 'getExecuter')

		elif self.tipo[:6]=="server":
			self.server.register_function(self.setProcess, 'setProcess')
			self.server.register_function(self.getStatus, 'getStatus')
			self.server.register_function(self.cleanProcess, 'cleanProcess')
			ipServer = str(input("Ingrese la ip del server principal\n"))
			puertoServer = str(input("ingrese el puerto del server principal\n"))
			
			
			self.conecction=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
			self.conecction.register(self.ip, str(self.puerto))
		elif(self.tipo[:7]=="cliente"):
			#self.server.register_function(self.setTime, 'setTime')
			#self.server.register_function(self.getTime, 'getTime')
			ipServer = str(input("Ingrese la ip del server principal\n"))
			puertoServer = str(input("ingrese el puerto del server principal\n"))
			self.conecction=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
		else:
			print("Hay errores")
			raise SystemExit(1)
		self.server.serve_forever()

if __name__ == "__main__":
	tipoServer=str(input("El tipo de servidor\n"))
	ipServer = str(input("Ingrese la ip para el servidor\n"))
	puertoServer = int(input("ingrese el puerto para el servidor\n"))
	procesador=None
	ram=None
	if(tipoServer[:6]=="server"):
		procesador = float(input("indique la frecuencia del procesador de este dispositivo \n"))
		ram = float(input("indique la cantidad de ram (MB) de este dispositivo\n"))
	server=serverRPC(ipServer, puertoServer, tipoServer, procesador, ram)
	hilo1=threading.Thread(target=server.runServer)
	hilo1.start()
	server.runGraph()
