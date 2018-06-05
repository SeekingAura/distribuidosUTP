import threading
import time
import tkinter as tkinter
import tkinter.ttk as ttk
import xmlrpc.client
import sys
import os
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
		self.servers={}#Servidores o bien clientes registrados
		self.serversControl={}#Servidores externos realcionados a este servidor
		self.serversOthers={}
		self.serversOthersID={}
		self.filesOthers={}
		self.serversID={}
		self.serversIDLen=[]
		self.serversIDFinal={}
		self.filesPermission={}
		self.filesBusy={}
		self.files={}#lista de archivos para listar y su pertenencia
		self.filesFinal={}
		self.filesCopy={}#Diccionario para reconocer la existencia de copias
		self.registers=0#identifier for clients/server register count
		self.fileReading=None
		self.serverReading=None
		self.serverReadingCopy=None
		self.ownAddress="http://"+self.ip+":"+str(self.puerto)


		self.OthersServers={}

		#Tkinter
		self.root = tkinter.Tk()
		self.root.wm_title("archivos - "+tipo)
		scrollbar = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
		scrollbarH = tkinter.Scrollbar(self.root, orient=tkinter.HORIZONTAL)
		self.TextoBox = tkinter.Text(self.root, height=8, width=50, yscrollcommand=scrollbar.set)
		self.TextoBox2 = tkinter.Text(self.root, height=8, width=50, yscrollcommand=scrollbar.set)
		scrollbar.config(command=self.yview)
		scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		scrollbarH.config(command=self.xview)
		scrollbarH.pack(side=tkinter.BOTTOM, fill=tkinter.X)
		
		self.TextoBox.pack(side=tkinter.LEFT, fill=tkinter.Y)
		self.TextoBox.config(state=tkinter.DISABLED)
		self.TextoBox2.pack(side=tkinter.LEFT, fill=tkinter.Y)
		self.TextoBox2.config(state=tkinter.DISABLED)
		frame = tkinter.Frame(self.root)
		frame.pack()
		
		self.tree = ttk.Treeview(self.root)
		self.tree.configure(yscroll=scrollbar.set, xscroll=scrollbarH.set)
		self.tree.column("#0",minwidth=89*6, stretch=True)
		self.tree.heading('#0', text="Arbol de archivos", anchor='w')
		self.tree.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		
		tkinter.Label(frame, text='Estado').grid(row=0, column=0)
		self.answer = tkinter.StringVar()
		self.answer.set("Ready")
		tkinter.Label(frame, textvariable=self.answer).grid(row=0, column=1)

		tkinter.Label(frame, text='RegisterServer').grid(row=1, column=0)
		self.command = tkinter.StringVar()
		tkinter.Entry(frame, textvariable=self.command).grid(row=1, column=1)
		self.buttonRegister = tkinter.Button(frame, text='Register', command=self.registerServer)
		self.buttonRegister.grid(row=2, column=1, columnspan=1)

		self.buttonShowFile = tkinter.Button(frame, text='Show File', command=self.showInfo)
		self.buttonShowFile.grid(row=2, columnspan=1)

		self.buttonCancel = tkinter.Button(frame, text='Cancel', command=self.cancelAction)
		self.buttonCancel.grid(row=3, column=0, columnspan=1)
		
		self.buttonUpdate = tkinter.Button(frame, text='Update Files', command=self.updateFilesAll)
		self.buttonUpdate.grid(row=3, column=1, columnspan=1)

		#self.buttonOthers = tkinter.Button(frame, text='Update Others', command=self.updateOthers)
		#self.buttonOthers.grid(row=4, column=0, columnspan=1)

		self.buttonSystem = tkinter.Button(frame, text='updateSystem', command=self.updateSystem)
		self.buttonSystem.grid(row=4, column=0, columnspan=1)

		self.buttonFilesData = tkinter.Button(frame, text='updateListBox', command=self.updateListBox)
		self.buttonFilesData.grid(row=4, column=1, columnspan=1)

		self.buttonSetupOthers = tkinter.Button(frame, text='setupOthers', command=self.setupOthers)
		self.buttonSetupOthers.grid(row=5, column=1, columnspan=1)


		#self.buttonShowBusy = tkinter.Button(frame, text='Select Busy Files', command=self.showBusy)
		#self.buttonShowBusy.grid(row=3, columnspan=1)

		

		

		#self.buttonShowBusy.config(state=tkinter.DISABLED)

		
		#Temp value

	
	def yview(self, *args):
		self.TextoBox.yview(*args)
		self.TextoBox2.yview(*args)
		self.tree.yview(*args)
	def xview(self, *args):
		self.tree.xview(*args)
	def printBox1(self, value):
		self.TextoBox.config(state=tkinter.NORMAL)
		self.TextoBox.insert(tkinter.END, "\n"+"[ "+time.asctime(time.localtime(time.time()))+"] "+str(value))
		self.TextoBox.see(tkinter.END)
		self.TextoBox.config(state=tkinter.DISABLED)
		
	def printBox2(self, value):
		self.TextoBox2.config(state=tkinter.NORMAL)
		self.TextoBox2.delete('1.0', tkinter.END)
		self.TextoBox2.insert(tkinter.END, str(value))
		self.TextoBox2.see(tkinter.END)
		self.TextoBox2.config(state=tkinter.DISABLED)
	

	def getServers(self):
		return self.servers

	def updateFilesFinal(self):
		self.printBox1("efectuando updateFilesFinal")
		self.filesFinal=self.files
		for l in self.serversControl:
			self.filesFinal=dict(self.filesFinal, **self.serversControl.get(l).getFiles())
		self.printBox1("efectuado updateFilesFinal")

	def updateServersIDFinal(self):
		self.printBox1("efectuando updateServersIDFinal")
		self.serversIDFinal=self.serversID
		self.serversIDLen=[]
		tempCount=self.registers
		for l in self.serversControl:
			serversIDTemp=self.serversControl.get(l).getServersID()
			self.serversIDLen.append(len(serversIDTemp))
			for i in serversIDTemp:
				self.serversIDFinal[str(int(i)+tempCount)]=serversIDTemp.get(i)
			tempCount+=len(serversIDTemp)
		self.printBox1("efectuado updateServersIDFinal")

	def setupOthers(self):
		for i in self.serversControl:
			self.OthersServers=self.serversControl.get(i).getServers()

	def updateFilesOthers(self):
		permissions=["lectura", "escritura", "ninguno"]
		print("haciendo filesothers")
		

		for k in self.OthersServers:
			for i in self.servers:#lista de direcciones de servidores
				#print("pasanado por i-> {}, del valor k-> {}".format(i, k))
				for j in self.OthersServers.get(k).getFiles():#Obtiene los archivos por cada servidor
					if not i in self.filesPermission:
						self.filesPermission[i]={}
					if not j in self.filesPermission.get(i):
						self.filesPermission[i][j]={}
						self.filesPermission[i][j][k]=permissions[random.randint(0, 2)]
					elif(not k in self.filesPermission.get(i).get(j)):#verificando si el servidor NO posee dicho archivo ó si aun no ha sido almacenado ese archivo del servidor proveniente (mismo nombre en dos maquinas)
						self.filesPermission[i][j][k]=permissions[random.randint(0, 2)]

	# def updateOthers(self):
	# 	self.answer.set("Actualizando archivos - otros")
	# 	self.serversOthers={}
	# 	self.filesOthers={}
	# 	tempCount=self.registers
	# 	print("self.serversControl -> ", self.serversControl)
	# 	for i in self.serversControl:
	# 		print("efectuar files others "+"[ "+time.asctime(time.localtime(time.time()))+"] ")
	# 		print("self.servers -> ", self.servers)
	# 		print("ob self.serversControl.get(i) ->", self.serversControl.get(i))
	# 		self.serversControl.get(i).updateFilesOthers(self.servers)
	# 		DictTemp, IdsTemp=self.serversControl.get(i).getFilesList()
	# 		for j in IdsTemp:
	# 			print("OJISIMO, serversOthers -> ", self.serversOthers)
	# 			print("ey, IdsTemp.get(i) -> ", IdsTemp.get(i))
	# 			self.serversOthers[IdsTemp.get(i)]=xmlrpc.client.ServerProxy(IdsTemp.get(i), allow_none=True)
			
	# 			self.serversOthersID[str(tempCount)]=IdsTemp.get(i)
	# 			tempCount+=1
	# 			self.filesOthers[IdsTemp.get(j)]=[]
	# 			for k in DictTemp.get(IdsTemp.get(j)):
	# 				self.filesOthers.get(IdsTemp.get(j)).append(k)
	# 	self.printBox1("Actualizado otros servidores")
	# 	self.answer.set("Ready")
		


	def registerSystem(self, Address):
		self.serversControl[Address]=xmlrpc.client.ServerProxy(Address, allow_none=True)
		self.printBox1("Agregado servidor -> {}".format(Address))
		self.buttonRegister.after(5000, self.updateFilesOthers)


	def registerServer(self):
		value=self.command.get().split(", ")
		if(len(value)==2):
			serverAddress, serverPort=value
			rpcDir=xmlrpc.client.ServerProxy("http://"+serverAddress+":"+serverPort, allow_none=True)
			try:
				self.answer.set("Registrando - otros")
				rpcDir.registerSystem(self.ownAddress)
				self.serversControl["http://"+serverAddress+":"+serverPort]=rpcDir
				self.buttonRegister.after(10000, self.registerSystem, "http://"+serverAddress+":"+serverPort)
			except Exception as e:
				self.printBox1("La dirección ingresada es no valida")
				print("error:\n ", e)
		else:
			self.printBox1("Formato incorrecto para Registrar")
		self.command.set("")
		self.answer.set("Ready")

	def showInfo(self):
		fileSelected=self.tree.selection()
		if(len(fileSelected)==1):
			fileID=fileSelected[0]
			parent=self.tree.parent(fileID)
			fileName=self.tree.item(fileID)['text']
			if(parent!=""):
				serverID=self.tree.item(parent)['text']
				serverName=self.getServerID(serverID)
				fileState=None
				fileContent, serverRead=self.getContent(fileName, serverName, self.ownAddress)
				self.fileReading=fileName
				self.serverReadingCopy=serverRead
				self.serverReading=serverName
				if(self.filesBusy.get(serverName).get(fileName) is None):
					fileState="No ocupado"
				else:
					fileState="Ocupado"
						
				self.printBox1("Archivo: {}\nGuardado en: {}\nEstado: {}\n#----------#\n".format(fileName, serverName, fileState))
				self.printBox2(fileContent)
			else:
				self.printBox1("tiene seleccionado es un folder")

		elif(len(fileSelected)==0):
			self.printBox1("No hay archivo seleccionado")
		else:
			self.printBox1("Hay mas de uno seleccionado")
		self.answer.set("Leyendo archivo")
	
	# def showBusy(self):
	# 	self.answer.set("Obteniendo Busy")
	# 	tempIndex=0
	# 	self.list.selection_clear(0, tkinter.END)
	# 	for i in self.filesBusy:
	# 		for j in self.filesBusy.get(i):
	# 			if(self.filesBusy.get(i).get(j) is not None):
	# 				self.list.selection_set(tempIndex, tempIndex)
	# 			tempIndex+=1
	# 	self.answer.set("Ready")


	def runGraph(self):
		self.root.mainloop()

	# def registerFile(self, serverDir, fileName):
	# 	serverName=self.servers.get(serverDir).getName()
	# 	try:
	# 		fileSave=open(self.folderStore+'/'+serverName+"/"+fileName, "w")
	# 	except:
	# 		os.makedirs(self.folderStore+'/'+serverName)
	# 		fileSave=open(self.folderStore+'/'+serverName+"/"+fileName, "w")
	# 	fileData=self.servers.get(serverDir).getFile(fileName)
	# 	fileSave.write(fileData)
	# 	fileSave.close()

		

	def register(self, ipServer, puertoServer):
		#value=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer)
		self.answer.set("Registrando cliente")
		self.servers["http://"+ipServer+":"+puertoServer]=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
		self.filesPermission["http://"+ipServer+":"+puertoServer]={}
		self.serversID[str(self.registers)]="http://"+ipServer+":"+puertoServer
		
		self.updateFilesAll()
		self.printBox1("Se ha registrado el servidor {}".format("http://"+ipServer+":"+puertoServer))
		self.servers.get("http://"+ipServer+":"+puertoServer).setID(self.registers)
		
		self.registers+=1


	def updateBusy(self):
		self.answer.set("actualizando Busy")
		for i in self.servers:#lista de direcciones de servidores
			for j in self.servers.get(i).getFiles():#Obtiene los archivos por cada servidor
				if not i in self.filesBusy:#verificando si el servidor NO posee dicho archivo
					self.filesBusy[i]={}
					self.filesBusy[i][j]=None
				elif not j in self.filesBusy.get(i):
					self.filesBusy[i][j]=None
				if(not i in self.files):
					self.files[i]=[j]
				elif(not j in self.files.get(i)):
					self.files[i].append(j)

	def updateFiles(self, machine):
		permissions=["lectura", "escritura", "ninguno"]
		self.answer.set("Actualizando permisos")
		for i in self.servers.get(machine).getFiles():
			if not i in self.filesPermission.get(machine):#verificando si el servidor NO posee dicho archivo
				self.filesPermission[machine][i]={}
				self.filesPermission[machine][i][machine]="escritura"
		for i in self.servers:#lista de direcciones de servidores
			for j in self.servers.get(i).getFiles():#Obtiene los archivos por cada servidor
				
				if not j in self.filesPermission.get(machine):
					self.filesPermission[machine][j]={}
					self.filesPermission[machine][j][i]=permissions[random.randint(0, 2)]
				elif(not i in self.filesPermission.get(machine).get(j)):#verificando si el servidor NO posee dicho archivo ó si aun no ha sido almacenado ese archivo del servidor proveniente (mismo nombre en dos maquinas)
					self.filesPermission[machine][j][i]=permissions[random.randint(0, 2)]


	def updateListExtern(self):
		self.updateFilesFinal()
		self.updateServersIDFinal()
		print("anunciando que actualicen")
		# for i in self.servers:
		# 	print("anunciando que actualice -> ", i)
		# 	self.servers.get(i).printBox1("Actualizado archivos del sistema")
	def updateSystem(self):
		print("HAGO OTHERS")
		self.updateFilesOthers()
		
		self.buttonUpdate.after(5000, self.updateFilesListData)

	def updateFilesAll(self):
		self.answer.set("Actualizando archivos")
		#self.buttonUpdate.config(state=tkinter.DISABLED)
		for i in self.servers:
			self.updateFiles(i)
		
		self.updateBusy()
		
		self.updateSetCopy()
		self.updateFilesCopy()
		self.updateListExtern()
		self.printBox1("Efectuado updateFilesAll")
		#self.buttonUpdate.after(5000, self.updateSystem)

	def updateFilesListData(self):
		print("haciendo fileslist data")
		for i in self.serversControl:
			self.serversControl.get(i).updateListExtern()
		self.printBox1("Archivos actualizados")
		for i in self.servers:
			self.servers.get(i).printBox1("Actualziación disponible")
		self.buttonUpdate.config(state=tkinter.ACTIVE)
		
		self.answer.set("Ready")
	
	def updateListBox(self):
		DictTemp, IdsTemp=self.getFilesList()
		self.tree.delete(*self.tree.get_children())# Borra el arbol
		for i in IdsTemp:
			folder=self.tree.insert('', 'end', text=str(i))
			for j in DictTemp.get(IdsTemp.get(i)):
				self.tree.insert(folder, 'end', text=str(j))
		self.printBox1("Se ha actualizado la lista")

	def updateSetCopy(self):
		for i in self.files:#
			if(not i in self.filesCopy):
				self.filesCopy[i]={}
				self.filesCopy[i][i]={}
			if len(self.servers)>2:
				while(len(self.filesCopy.get(i))<3):
					cant=random.randint(0, len(self.servers)-1)
					serverDir=[*self.servers.keys()][cant]
					if(i!=serverDir and (not serverDir in self.filesCopy.get(i))):
						self.filesCopy[i][serverDir]={}
				

	def updateFilesCopy(self):
		for i in self.filesCopy:#
			for j in self.filesCopy.get(i):
				for k in self.files.get(i):
					if(not k in self.filesCopy.get(i).get(j)):#Verificando si ya está copiado el archivo
						self.filesCopy[i][j][k]={}#i-> Servidor relacionado, j-> Servidor a donde copiar, k -> Archivo
						if(i!=j):
							self.servers.get(j).updateCopy(k, [*self.serversID.keys()][[*self.serversID.values()].index(i)], self.servers.get(i).getFile(k))

					
	def getFiles(self):
		return self.files

	def getServersID(self):
		return self.serversID

	def getFilesList(self):
		print("self.filesFinal -> ", self.filesFinal)
		print("self.serversIDFinal -> ", self.serversIDFinal)
		return [self.filesFinal, self.serversIDFinal]

	def getPermission(self, machine, fileName, serverID):
		serverName=self.serversIDFinal.get(serverID)
		return self.filesPermission.get(machine).get(fileName).get(serverName)

	def setBusy(self, machine, fileName, serverID):
		if(serverID>=self.registers):
			tempPos=self.registers
			for enum, i in enumerate(self.serversIDLen):#control para mas de 2 servidores
				if(serverID<=tempPos+i):
					indexPos=enum
					break
				else:
					tempPos+=i
			
				
			result=[*self.serversControl.values][indexPos].setBusy(machine, fileName, str(int(serverID)-tempPos))
			return result	
		else:
			serverName=self.serversID.get(serverID)
			
			if self.filesBusy.get(serverName).get(fileName) is None:
				self.filesBusy[serverName][fileName]=machine
				self.printBox1("se ha ocupado el archivo {}, ubicado en {}, por {}".format(fileName, serverName, machine))
				return True

			return False

	def removeBusy(self, fileName, serverName):
		if self.filesBusy.get(serverName).get(fileName) is not None:
			self.filesBusy[serverName][fileName]=None
			self.printBox1("Se ha dejado de ocupar el archivo {}, ubicado en {}".format(fileName, serverName))

		return False

	def modifyFile(self, fileName, fileData, serverFile):
		self.filesBusy[serverFile][fileName]=None
		self.printBox1("Modificado el archivo {} ubicado en {}".format(fileName, serverFile))
		for i in self.filesCopy.get(serverFile):
			self.servers.get(i).updateCopy(fileName, [*self.serversID.keys()][[*self.serversID.values()].index(serverFile)], fileData)
		self.servers.get(serverFile).modifyFile(fileName, fileData)

	def deleteFile(self, fileName, serverID):#Probablmente no funcione bien
		if(serverID>=self.registers):
			tempPos=self.registers
			for enum, i in enumerate(self.serversIDLen):#control para mas de 2 servidores
				if(serverID<=tempPos+i):
					indexPos=enum
					break
				else:
					tempPos+=i
			[*self.serversControl.values][indexPos].deleteFile(fileName, str(int(serverID)-tempPos))
		else:
			serverFile=self.serversID.get(serverID)
			for i in self.filesPermission:
				self.filesPermission.get(i).get(fileName).pop(serverFile)
				if(len(self.filesPermission.get(i).get(fileName))==0):
					self.filesPermission.get(i).pop(fileName)
					
			self.filesBusy.get(serverFile).pop(fileName)
			#if(len(self.filesBusy.get(serverFile))==0):#Este caso seria si se queda el servidor sin archivos
			#	self.filesBusy.pop(serverFile)
			self.printBox1("Borrado el archivo {} ubicado en {}".format(fileName, serverFile))
			for i in self.filesCopy.get(serverFile):
				self.servers.get(i).deleteCopy(fileName, serverID)
				self.filesCopy.get(serverFile).get(i).pop(fileName)
					

			self.servers.get(serverFile).deleteFile(fileName)
	
	def getServerID(self, serverID):
		return self.serversID.get(serverID)

	def getContent(self, fileName, serverName, serverWant):
		pos=[*self.serversIDFinal.values()].index(serverName)
		if(pos>=self.registers):
			tempPos=self.registers
			for enum, i in enumerate(self.serversIDLen):#control para mas de 2 servidores
				if(pos<=tempPos+i):
					indexPos=enum
					break
			fileContent, serverRead=[*self.serversControl.values][indexPos].getContent(fileName, serverName, serverWant)
			
		else:
			if(len(self.filesCopy.get(serverName))==3):
						
				min=5
				for i in self.filesCopy.get(serverName):
					if(len(self.filesCopy.get(serverName).get(i).get(fileName))<min):
						min=len(self.filesCopy.get(serverName).get(i).get(fileName))#search for min uses, opened file.
				while(True):
					numberRead=random.randint(0, 2)
					serverRead=[*self.filesCopy.get(serverName).keys()][numberRead]
					if(len(self.filesCopy[serverName][serverRead][fileName])<=min):
						break
			else:
				numberRead=0
				serverRead=[*self.filesCopy.get(serverName).keys()][numberRead]
			if(serverName!=serverRead):
				fileContent=self.servers.get(serverRead).getFileCopy(fileName, [*self.serversID.keys()][[*self.serversID.values()].index(serverName)])#######
				
			else:
				fileContent=self.servers.get(serverName).getFile(fileName)
			self.filesCopy[serverName][serverRead][fileName][serverWant]="Lectura"
		return fileContent, serverRead

	def closeFile(self, fileName, serverOwn, serverCopy, serverHave):
		self.filesCopy[serverOwn][serverCopy][fileName].pop(serverHave)

	def cancelAction(self):
		# self.reading=False
		self.printBox2("")
		self.printBox1("acción cancelada")
		self.buttonShowFile.config(state=tkinter.NORMAL)
		self.closeFile(self.fileReading, self.serverReading, self.serverReadingCopy, self.ownAddress)
		#self.buttonShowBusy.config(state=tkinter.NORMAL)
		self.buttonCancel.config(state=tkinter.DISABLED)
		self.fileReading=None
		self.serverReading=None
		self.serverReadingCopy=None
		self.answer.set("Ready")
		

	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.register, 'register')
		self.server.register_function(self.printBox1, 'printBox1')
		self.server.register_function(self.registerSystem, 'registerSystem')
		self.server.register_function(self.updateFilesOthers, 'updateFilesOthers')
		#self.server.register_function(self.updateOthers, 'updateOthers')
		self.server.register_function(self.updateListExtern, 'updateListExtern')
		self.server.register_function(self.getServersID, 'getServersID')
		self.server.register_function(self.getFiles, 'getFiles')
		self.server.register_function(self.getServers, 'getServers')
		self.server.register_function(self.getFilesList, 'getFilesList')
		self.server.register_function(self.getServerID, 'getServerID')
		self.server.register_function(self.getContent, 'getContent')
		self.server.register_function(self.getPermission, 'getPermission')
		self.server.register_function(self.setBusy, 'setBusy')
		self.server.register_function(self.closeFile, 'closeFile')
		self.server.register_function(self.modifyFile, 'modifyFile')
		self.server.register_function(self.removeBusy, 'removeBusy')
		self.server.register_function(self.deleteFile, 'deleteFile')

		self.server.serve_forever()

if __name__ == "__main__":
	tipoServer=str(input("El tipo de servidor\n"))
	ipServer = str(input("Ingrese la ip para el servidor\n"))
	puertoServer = int(input("ingrese el puerto para el servidor\n"))
	server=serverRPC(ipServer, puertoServer, tipoServer)
	hilo1=threading.Thread(target=server.runServer)
	hilo1.start()
	server.runGraph()