import socket
import operator
import re
import random
import threading
import time
import tkinter as tkinter

class UDPSocketServerMain: 
	def __init__(self, ipServer, puertoServer, ipClient, puertoClient, tipo="server", rol=""):
		self.sockServer=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Server para comunicar a servidores
		self.sockServer.bind((ipServer, puertoServer))
		self.sockServer.settimeout(5)#Establecer tiempo limite de espera en segundos por cada recvfrom
		self.sockClient=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Server para comunicar a clientes
		self.sockClient.bind((ipClient, puertoClient))
		self.sockClient.settimeout(5)
		self.tipo=tipo
		self.rol=rol
		self.salas={}

		#Tkinter
		self.root = tkinter.Tk()
		self.root.wm_title(tipo+rol)
		scrollbar = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
		self.TextoBox = tkinter.Text(self.root, height=8, width=80, yscrollcommand=scrollbar.set)
		self.TextoBox2 = tkinter.Text(self.root, height=8, width=80, yscrollcommand=scrollbar.set)
		scrollbar.config(command=self.yview)
		scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		
		self.TextoBox.pack(side=tkinter.LEFT, fill=tkinter.Y)
		self.TextoBox2.pack(side=tkinter.LEFT, fill=tkinter.Y)
		frame = tkinter.Frame(self.root)
		frame.pack()
		
		
		
		tkinter.Label(frame, text='Send to Server').grid(row=0, column=0)
		self.command1 = tkinter.StringVar()
		tkinter.Entry(frame, textvariable=self.command1).grid(row=0, column=1)
		tkinter.Label(frame, text='Estado').grid(row=1, column=0)
		self.answer1 = tkinter.StringVar()
		tkinter.Label(frame, textvariable=self.answer1).grid(row=1, column=1)
		button = tkinter.Button(frame, text='Send', command=self.sendCom1)
		button.grid(row=2, columnspan=2)
		self.serverDato=""


		tkinter.Label(frame, text='Send to Client').grid(row=3, column=0)
		self.command2 = tkinter.StringVar()
		tkinter.Entry(frame, textvariable=self.command2).grid(row=3, column=1)
		tkinter.Label(frame, text='Estado').grid(row=4, column=0)
		self.answer2 = tkinter.StringVar()
		tkinter.Label(frame, textvariable=self.answer2).grid(row=4, column=1)
		button = tkinter.Button(frame, text='Send', command=self.sendCom2)
		button.grid(row=5, columnspan=2)
		self.clientDato=""
		#Temp value
		self.opReq=False
	def yview(self, *args):
		self.TextoBox.yview(*args)
		self.TextoBox2.yview(*args)

	def printBox1(self, value):
		self.TextoBox.insert(tkinter.END, "\n"+str(value))
		self.TextoBox.see(tkinter.END)
	def printBox2(self, value):
		self.TextoBox2.insert(tkinter.END, "\n"+str(value))
		self.TextoBox2.see(tkinter.END)

		
	def sendCom1(self):
		value=self.command1.get()
		self.answer1.set("processing...")
		self.serverDato=value
		self.command1.set("")
		#self.answer1.set("Ready")
		self.opReq=True
		
	def sendCom2(self):
		value=self.command2.get()
		self.answer2.set("processing...")
		self.clientDato=value
		self.command2.set("")
		#self.answer2.set("Ready")
	def runGraph(self):
		self.root.mainloop()

	#Server functions
	def sendMsg(self, rol="", tipo="", message="", addres="", trys=int(5), sock=""):
		time.sleep(1)
		if isinstance(message, str):
			message=self.rol+":"+self.tipo+":"+message+":"
		elif isinstance(message, bytes):
			message=self.rol+":"+self.tipo+":"+message.decode('utf-8')+":"
		else:
			if(self.sockServer==sock):
				self.printBox1("ERROR - Data type to send can't work")
			elif(self.sockClient==sock):
				self.printBox2("ERROR - Data type to send can't work")
			else:
				print("ERROR - Data type to send can't work")
			return False
		for i in range(trys):
			
			if(self.sockServer==sock):
				self.printBox1("mensaje enviado - {} - a {}".format(message, addres))
			elif(self.sockClient==sock):
				self.printBox2("mensaje enviado - {} - a {}".format(message, addres))
			else:
				print("mensaje enviado - {} - a {}".format(message, addres))
			sock.sendto(message.encode('utf-8'), addres)
			try:
				tempMensaje, tempAddr=sock.recvfrom(1024)
				# print("tempm", tempMensaje)
				if(tempMensaje.decode('utf-8')=="recibido"):
					return True
			except socket.timeout:
				if(self.sockServer==sock):
					self.printBox1("hubo un error")
				elif(self.sockClient==sock):
					self.printBox2("hubo un error")
				else:
					print("hubo un error")
				
				time.sleep(1)
				continue
		
		if(self.sockServer==sock):
			self.printBox1("Intentos superados, no fue posible enviar")
		elif(self.sockClient==sock):
			self.printBox2("Intentos superados, no fue posible enviar")
		else:
			print("Intentos superados, no fue posible enviar")
		return False
			
	def recieveMsg(self, size=int(1024), trys=int(5), sock=""):
		for i in range(trys):
			try:
				if(self.opReq):
					break
				data, addr = sock.recvfrom(size)
				
				if(self.sockServer==sock):
					self.printBox1("Mensaje recibido - {} - de {}".format(data.decode('utf-8'), addr))
				elif(self.sockClient==sock):
					self.printBox2("Mensaje recibido - {} - de {}".format(data.decode('utf-8'), addr))
				else:
					print("Mensaje recibido - {} - de {}".format(data.decode('utf-8'), addr))
				rol=None
				tipo=None
				mensaje=None
				temp=""
				for i in data.decode('utf-8'):
					if(i!=":"):
						temp+=i
					elif (rol is None and i==":"):
						rol=temp
						temp=""
					elif(tipo is None and i==":"):
						tipo=temp
						temp=""
					elif(mensaje is None and i==":"):
						mensaje=temp
						temp=""
				sock.sendto("recibido".encode('utf-8'), addr)
				return (rol, tipo, mensaje, addr)
			except socket.timeout:
				
				if(self.sockServer==sock):
					self.printBox1("Tiempo de espera superado")
				elif(self.sockClient==sock):
					self.printBox2("Tiempo de espera superado")
				else:
					print("Tiempo de espera superado")
				continue
		return ("", "", "", "")
	
	def getAddres(self, message):
		addres, port=message.split(", ")
		addres=str(addres)
		port=int(port)
		return (addres, port)


	def runServerServers(self):
		#print("servidor iniciado")
		self.printBox1("servidor iniciado")
		data=""
		while True:
			#print("Esperando por nuevos servidores")
			self.printBox1("Esperando por nuevos servidores")
			rolClient, tipoClient, mensajeClient, addrClient=self.recieveMsg(sock=self.sockServer)
			if(mensajeClient=="registrar"):
				if(tipoClient in [*self.salas]):
					#print(self.salas[tipoClient][0]["addres"][0])
					
					self.sendMsg(self.salas[tipoClient][0]["rol"], self.salas[tipoClient][0]["tipo"], "registre nuevo", self.salas[tipoClient][0]["addres"][0], sock=self.sockServer)
					self.sendMsg(rolClient, tipoClient, "agregado", addrClient, sock=self.sockServer)
					rolTemp, tipoTemp, mensajeTemp, addrTemp=self.recieveMsg(sock=self.sockServer)
					#print("recibiendo de registre nuevo", mensajeTemp)
					ip, port=self.getAddres(mensajeTemp)
					addres=(ip, port)
					self.sendMsg(self.salas[tipoClient][0]["rol"], self.salas[tipoClient][0]["tipo"], str(ip)+", "+str(port), self.salas[tipoClient][0]["addres"][0], sock=self.sockServer)
					self.salas[tipoClient].append({"rol":rolClient, "tipo":tipoClient, "addres": [addrClient, addres]})
					#print("estado de salas \n", self.salas[tipoClient])
				else:
					self.sendMsg(rolClient, tipoClient, "nueva sala", addrClient, sock=self.sockServer)
					rolClient, tipoClient, mensajeClient, addrClient=self.recieveMsg(sock=self.sockServer)
					ip, port=self.getAddres(mensajeClient)
					addres=(ip, port)
					self.salas[tipoClient]=[]
					self.salas[tipoClient].append({"rol":rolClient, "tipo":tipoClient, "addres": [addrClient, addres]})
			elif(mensajeClient=="borrar"):
				if(tipoClient in [*self.salas] and rolClient=="admin"):
					for i in self.salas[tipoClient]:
						self.sendMsg(i["rol"], i["tipo"], "expulsar", i["addres"][0], sock=self.sockServer)
					self.salas.pop(tipoClient)
			elif(mensajeClient=="expulsar"):
				if(tipoClient in [*self.salas]  and rolClient=="admin"):
					rolExp, tipoExp, mensajeExp, addrExp=self.recieveMsg(sock=self.sockServer)
					if(addrExp==addrClient):
						ip, port=self.getAddres(mensajeTemp)
						addres=(ip, port)
						temp=-1
						for enum, i in enumerate(self.salas[tipoClient]):
							if(i["addres"][1]==addres):
								temp=enum
								# print("valor de pos de borrado", temp)
								break
						if(temp!=-1):
							self.salas[tipoClient].pop(temp)
						

	def runServerClients(self):
		while True:
			#print("Esperando por operaciones de cliente")
			self.printBox2("Esperando por operaciones de cliente")
			rolClient, tipoClient, mensajeClient, addrClient=self.recieveMsg(sock=self.sockClient)
			if(mensajeClient in [*self.salas]):
				self.sendMsg(rolClient, tipoClient, "Almacene", addrClient, sock=self.sockClient)
				for i in self.salas[mensajeClient]:
					self.sendMsg(rolClient, tipoClient, str(i["addres"][1][0])+", "+str(i["addres"][1][1]), addrClient, sock=self.sockClient)
				self.sendMsg(rolClient, tipoClient, "fin", addrClient, sock=self.sockClient)
				operando=False
				for i in range(10):
					rolTemp, tipoTemp, mensajeTemp, addrTemp=self.recieveMsg(sock=self.sockClient)
					if(mensajeTemp=="operar"):
						operando=True
						break
				if(operando):
					self.sendMsg(rolTemp, tipoTemp, "operando", addres=self.salas[mensajeClient][0]["addres"][0], sock=self.sockClient)#
			elif(tipoClient=="cliente"):
				self.sendMsg(rolTemp, tipoTemp, "No es un servidor registrado, los que hay son:", addrTemp, sock=self.sockClient)
				for i in [*self.salas]:
					self.sendMsg(rolTemp, tipoTemp, str(i), addrTemp, sock=self.sockClient)
				self.sendMsg(rolTemp, tipoTemp, "fin", addrTemp, sock=self.sockClient)
			
					

						
class UDPSocketServerSuma(UDPSocketServerMain):
	def __init__(self, ipServer, puertoServer, ipClient, puertoClient,  tipo="server", rol=""):
		UDPSocketServerMain.__init__(self, ipServer, puertoServer, ipClient, puertoClient,  tipo)
		self.operar=False
		self.servers=[[self.sockClient.getsockname(), False]]
		

	def MathSuma(self, value1, value2):
		return float(value1)+float(value2)

	def runServerServers(self):
		
		print("server suma iniciado")
		#self.printBox1("server suma iniciado")
		# registrarme
		print("registrandose a un grupo")
		while True:
			ipServerMain=input("ingrese la ip del server principal")
			portServerMain=input("ingrese el puerto del server principal")
			addresMain=(ipServerMain, int(portServerMain))
			self.sendMsg(message="registrar", addres=addresMain, sock=self.sockServer)
			rolTemp, tipoTemp, mensajeTemp, addrTemp=self.recieveMsg(sock=self.sockServer)
			if(mensajeTemp=="nueva sala"):
				self.rol="admin"
				self.root.wm_title(self.tipo+self.rol)
				clientAddres=self.sockClient.getsockname()
				self.sendMsg(message=str(clientAddres[0])+", "+str(clientAddres[1]), addres=addresMain, trys=int(5), sock=self.sockServer)
				break
			elif(mensajeTemp=="agregado"):
				self.rol="operador"
				self.root.wm_title(self.tipo+self.rol)
				clientAddres=self.sockClient.getsockname()
				self.sendMsg(message=str(clientAddres[0])+", "+str(clientAddres[1]), addres=addresMain, trys=int(5), sock=self.sockServer)
				break
		print("registrado, ahora modo operacional")
		while True:
			#if(self.rol=="admin"):
				#comando=input("ingrese el comando")
				
			
			#print("esperando intrucción de servidor")
			self.printBox1("esperando intrucción de servidor")
			rolTemp, tipoTemp, mensajeTemp, addrTemp=self.recieveMsg(sock=self.sockServer)
			if(mensajeTemp=="expulsar"):
				#print("el servidor principal le ha sacado del grupo de servidores")
				print("EXPULSADO!")
				raise SystemExit(1)
				break
			elif(mensajeTemp=="registre nuevo"):
				rolTemp, tipoTemp, mensajeTemp, addrTemp=self.recieveMsg(sock=self.sockServer)
				ip, port=self.getAddres(mensajeTemp)
				addres=(ip, port)
				self.servers.append([addres, False])
				#self.sendMsg(message="agregado", addres=addres, sock=self.sockServer)
			elif(mensajeTemp=="listo"):
				temp=None
				for enum, i in enumerate(self.servers):
					if(addrTemp==i[0]):
						temp=enum
				if temp is not None:
					self.servers[temp][1]=False
			elif(mensajeTemp=="operando"):
				if(self.rol=="admin"):
					ready=False
					while not(ready):
						temp=random.randint(1,len(self.servers)-1)
						if(not(self.servers[temp][1])):
							self.servers[temp][1]=True
							ready=True
							for enum, i in enumerate(self.servers):
								if(enum==temp and enum!=0):
									self.sendMsg(message="si", addres=i[0], trys=int(5), sock=self.sockServer)
								else:
									self.sendMsg(message="no", addres=i[0], trys=int(5), sock=self.sockServer)
			elif(self.serverDato!=""):
				if(self.serverDato[0:8]=="expulsar"):
					self.answer1.set("Expulsando")
					self.sendMsg(message="expulsar", addres=addresMain, trys=int(5), sock=self.sockServer)
					print("valor ", self.serverDato[9:])
					ip, port=self.serverDato[9:].split(", ")
					self.sendMsg(message=self.serverDato[9:], addres=addresMain, trys=int(5), sock=self.sockServer)
					temp=0
					for i in self.servers:
						#print("comparando este {} con {}".format(i[0], (ip, int(port))))
						if(i[0]==(ip, int(port))):
							break
						temp+=1
					#print("temp value {} len value {}".format(temp, len(self.servers)))
					if(len(self.servers)>temp):
						self.servers.pop(temp)
						self.sendMsg(message="expulsar", addres=(ip, int(port)), trys=int(5), sock=self.sockServer)
					else:
						self.sendMsg(message="nada", addres=(ip, int(port)), trys=int(5), sock=self.sockServer)
					
				self.serverDato=""
				self.opReq=False


		
	def runServerClients(self):
		#print("Esperando registro...")
		self.printBox2("Esperando registro...")
		while self.rol=="":
			pass
		#print("Registro detectado")
		self.printBox2("Registro detectado")
		while True:
			#print("Esperando operaciones")
			self.printBox2("Esperando operaciones")
			rolClient, tipoClient, mensajeClient, addrClient=self.recieveMsg(sock=self.sockClient)
			if(mensajeClient=="operar"):
				rolTemp, tipoTemp, mensajeTemp, addrTemp=self.recieveMsg(sock=self.sockClient)
				if mensajeTemp=="si":
					result=""
					for i in range(5):
						#print("esperando por valores de operación")
						self.printBox2("esperando por valores de operación")
						rolTemp, tipoTemp, mensajeTemp, addrTemp=self.recieveMsg(sock=self.sockClient)
						#print("valores de operando", addrTemp, addrClient)
						self.printBox2("valores de operando {} {}".format(str(addrTemp), str(addrClient)))
						if(addrTemp==addrClient):
							x, y=mensajeTemp.split(", ")
							result=self.MathSuma(x,y)
							break
					self.sendMsg(message=str(result), addres=addrTemp, trys=int(5), sock=self.sockClient)
				elif(mensajeTemp=="no"):
					rolTemp, tipoTemp, mensajeTemp, addrTemp=self.recieveMsg(sock=self.sockClient)
					#print("rechazando mensaje")
					self.printBox2("rechazando mensaje")
			
if __name__ == '__main__':
	tipo=input("ingrese el tipo de servidor")
	ipServer = input("Ingrese la ip del server -> ")
	puertoServer = int(input("ingrese el puerto del server -> "))
	ipServer2 = input("Ingrese la otra ip del server -> ")
	puertoServer2 = int(input("ingrese el otro puerto del server -> "))
	print("server IP:", ipServer)
	print("server port:", puertoServer)
	print("server IP:", ipServer2)
	print("server port:", puertoServer2)
	servidor=globals()["UDPSocketServer"+tipo.title()](ipServer, puertoServer, ipServer2, puertoServer2, tipo)
	hilo1=threading.Thread(target=servidor.runServerServers)
	hilo2=threading.Thread(target=servidor.runServerClients)
	hilo1.start()
	hilo2.start()
	servidor.runGraph()
	
	
