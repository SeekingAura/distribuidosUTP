import tkinter as tkinter
import threading
import time
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import ntplib
class Clock():
	def __init__(self, tk, date="11/03/2018", tiempo="00:00:00"):
		horas, minutos, segundos=map(int, tiempo.split(":"))
		dia, mes, anio=map(int, date.split("/"))
		t = (anio, mes, dia, horas, minutos, segundos, 1, 48, 0)
		self.base=time.mktime(t)+time.clock()#en windows pone el valor 0 como 19:00
		self.newTime=self.base
		self.sincTime=False
		self.sincCount=20
		self.sincTemp=-5
		self.freeze=False
		self.correction=0.0
		self.tk=tk
	
	def getStrTime(self):
		TimeClock=time.clock()
		timeValue=TimeClock+self.base
		if(self.sincTime):
			if(TimeClock+self.base<=TimeClock+self.newTime):
				self.sincTime=False
				self.sincTemp=-5
				if(self.freeze):
					self.freezeTime()
				self.base=self.newTime
				self.tk.printBox("Está sincronizado")
			elif(self.sincTemp<self.sincCount):
				self.sincTemp+=1
				if(self.sincTemp<0):
					if(self.freeze):
						self.freezeTime()
				else:
					if(not(self.freeze)):
						self.freezeTime()
			else:
				self.sincTemp=-5
		
		if(self.freeze):
			return None
		else:
			timeValue=time.clock()+self.base
			tempTime=time.asctime(time.localtime(timeValue))
			return tempTime[11:19]+"\n"+tempTime[0:4]+tempTime[8:10]+"/"+tempTime[4:6]+"/"+tempTime[20:24]
	
	def getTime(self):
		return time.clock()+self.base

	def setTime(self, date="11/03/2018", tiempo="00:00:00", valueFloat=None):
		if(self.freeze):
			self.freezeTime()
		self.sincTime=False
		TimeClock=time.clock()
		if(valueFloat is None):
			horas, minutos, segundos=map(int, tiempo.split(":"))
			dia, mes, anio=map(int, date.split("/"))
			t = (anio, mes, dia, horas, minutos, segundos, 1, 48, 0)
			
			self.newTime=time.mktime(t)-TimeClock
			
		else:
			self.newTime=valueFloat-TimeClock

		if(self.newTime+TimeClock<time.clock()+self.base):
			self.sincTime=True
			self.tk.printBox("El tiempo nuevo es menor")
			self.tk.answer.set("sincronizando")
		else:
			self.base=self.newTime
			self.tk.printBox("El tiempo nuevo es mayor")
			self.tk.answer.set("ready")


	def freezeTime(self):
		if(self.freeze):
			self.base=self.correction-time.clock()
		else:
			self.correction=time.clock()+self.base
		self.freeze=not(self.freeze)
	

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2',)


class serverRPC:
	def __init__(self, ip="localhost", puerto=5500, tipo="main"):
		#Server Control
		self.server=SimpleXMLRPCServer((ip, puerto), requestHandler=RequestHandler, allow_none=True)
		self.server.register_introspection_functions()
		self.ip=ip
		self.puerto=str(puerto)
		self.tipo=tipo
		self.conecction=None
		self.servers=[]
		self.dataClock=[]
		#Tkinter
		self.root = tkinter.Tk()
		self.root.wm_title("timer-"+tipo)#da el titulo a la ventana
		
		scrollbar = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
		scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

		self.TextoBox = tkinter.Text(self.root, height=8, width=80, yscrollcommand=scrollbar.set)
		self.TextoBox.pack(side=tkinter.LEFT, fill=tkinter.Y)
		
		frame = tkinter.Frame(self.root)
		frame.pack()
		
		self.clock = tkinter.Label(self.root, font=('times', 20, 'bold'), bg='white')
		self.clock.pack(fill=tkinter.BOTH, expand=1)
		self.clockTime=Clock(self)
		self.clock.config(text=self.clockTime.getStrTime())

		tkinter.Label(frame, text='Send to Server').grid(row=0, column=0)
		self.command = tkinter.StringVar()
		tkinter.Entry(frame, textvariable=self.command).grid(row=0, column=1)
		tkinter.Label(frame, text='Estado').grid(row=1, column=0)
		self.answer = tkinter.StringVar()
		tkinter.Label(frame, textvariable=self.answer).grid(row=1, column=1)
		
		button = tkinter.Button(frame, text='Send', command=self.sendCom)
		button.grid(row=2, columnspan=2)
		
		button = tkinter.Button(frame, text='Sinc Web', command=self.sincClock)
		button.grid(row=3, columnspan=1)

		button = tkinter.Button(frame, text='Stop', command=self.stopClock)
		button.grid(row=3, columnspan=2)
		
		
		
		button = tkinter.Button(frame, text='Sinc AllClock', command=self.sincAll)
		button.grid(row=2, columnspan=1)
		
		self.buttonReg=None
		if(tipo!="main"):
			self.buttonReg = tkinter.Button(frame, text='Register', command=self.registrar)
			self.buttonReg.grid(row=4, columnspan=1)
		self.updateClock()

	def printBox(self, value):
		self.TextoBox.insert(tkinter.END, "\n"+str(value))
		self.TextoBox.see(tkinter.END)
	
	def sendCom(self):
		date, tiempo=self.command.get().split(" ")
		self.clockTime.setTime(date, tiempo)
		self.answer.set("processing...")
		#self.serverDato=value
		self.command.set("")
		#self.answer1.set("Ready")
		#self.opReq=True

	def updateClock(self):
		newTime=self.clockTime.getStrTime()
		if(newTime is not None):
			self.clock.config(text=newTime)
			# calls itself every 200 milliseconds
			# to update the time display as needed
		# could use >200 ms, but display gets jerky
		#if(self.clockTime.freeze):
		#	self.printBox("esta freeze")
		self.clock.after(200, self.updateClock)
	
	def runGraph(self):
		self.root.mainloop()
	
	def stopClock(self):
		self.clockTime.freezeTime()

	def getAddres(self):
		return (self.ip, self.puerto)

	# Server functions
	def getTime(self):
		return self.clockTime.getTime()
	
	def sincClock(self):
		if(self.conecction is not None):
			if(not self.clockTime.sincTime):
				self.conecction.sinc((self.ip, self.puerto))
				value=self.conecction.getTime()
				self.clockTime.setTime(valueFloat=value)
				self.printBox("Sincronizando del servidor")
			else:
				self.printBox("ya hay un evento de sinc activo")
		else:
			self.printBox("Sincronizando en la web")
			c = ntplib.NTPClient()
			response = c.request('time4.google.com', version=3) 
			value = response.tx_time
			self.clockTime.setTime(valueFloat=value)
			

	def setTime(self, value):
		self.clockTime.setTime(valueFloat=value)
		


	# Funciones del servidor para el cliente
	def register(self, ipServer, puertoServer):
		value=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer)
		if(self.tipo=="main"):
			for i in self.servers:
				print("registrando en {} la dir {} {}".format(i.getAddres(), ipServer, puertoServer))
				i.register(ipServer, puertoServer)
				ip, puerto=i.getAddres()
				print("registrando la dir {} {}".format(ip, puerto))
				value.register(ip, puerto)
		self.servers.append(value)
		self.printBox("Se ha registrado el servidor {}".format("http://"+ipServer+":"+puertoServer))
	
	def registrar(self):
		self.conecction.register(self.ip, self.puerto)
		self.buttonReg.state=tkinter.DISABLED
		
	def sincAll(self):
		self.dataClock.append(self.conecction.getTime())
		for i in self.servers:
			self.dataClock.append(i.getTime())
		lastSize=len(self.dataClock)
		lastnewSize=0
		while lastSize!=lastnewSize:
			lastSize=len(self.dataClock)
			if(len(self.dataClock)==0):
				break
			timeMedia=self.desvEst()
			lastnewSize=len(self.dataClock)
		self.setTime(timeMedia+time.clock())
		timeValue=timeMedia+time.clock()
		tempTime=time.asctime(time.localtime(timeValue))
		
		self.printBox("Cambiando a tiempo -> {}".format(tempTime[11:19]+"\n"+tempTime[0:4]+tempTime[8:10]+"/"+tempTime[4:6]+"/"+tempTime[20:24]))
		self.dataClock=[]
		self.clock.after(5000, self.sincAll)

		
	def desvEst(self):
		self.printBox("Calcuando desviación")
		totalTime=0
		if len(self.dataClock)==1:
			return self.dataClock[0]
		for i in self.dataClock:
			totalTime+=i
		media=totalTime/(len(self.dataClock))
		tempSum=0
		for i in self.dataClock:
			tempSum+=(i-media)**2
		desvEstandar=(1/((len(self.dataClock))*tempSum))**(1/2)
		tempvalues=[]
		for enum, i in enumerate(self.dataClock):
			if(i<media-desvEstandar*2 or i>media+desvEstandar*2):
				tempvalues.append(enum)
		for enum, i in enumerate(tempvalues):
			self.dataClock.pop(i-enum) 
		return media

		

	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		if self.tipo=="main":
			self.server.register_function(self.register, 'register')
			self.server.register_function(self.getTime, 'getTime')
		else:
			self.server.register_function(self.register, 'register')
			self.server.register_function(self.getTime, 'getTime')
			self.server.register_function(self.getAddres, 'getAddres')
			ipServer = str(input("Ingrese la ip del server principal"))
			puertoServer = str(input("ingrese el puerto del server principal"))
			self.conecction=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)			
		self.server.serve_forever()

if __name__ == "__main__":
	tipoServer=str(input("El tipo de servidor"))
	ipServer = str(input("Ingrese la ip para el servidor"))
	puertoServer = int(input("ingrese el puerto para el servidor"))
	
	server=serverRPC(ipServer, puertoServer, tipoServer)
	hilo1=threading.Thread(target=server.runServer)
	hilo1.start()
	server.runGraph()
