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
		self.servers={}
		self.serversID={}
		self.filesPermission={}
		self.filesBusy={}
		self.files={}#lista de archivos para listar y su pertenencia
		self.filesCopy={}#Diccionario para reconocer la existencia de copias
		self.registers=0#identifier for clients/server register count
		self.fileReading=None
		self.serverReading=None
		self.serverReadingCopy=None
		self.ownAddress="http://"+self.ip+":"+str(self.puerto)

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
		
		

		self.buttonShowFile = tkinter.Button(frame, text='Show File', command=self.showInfo)
		self.buttonShowFile.grid(row=2, columnspan=1)

		#self.buttonShowBusy = tkinter.Button(frame, text='Select Busy Files', command=self.showBusy)
		#self.buttonShowBusy.grid(row=3, columnspan=1)

		self.buttonUpdate = tkinter.Button(frame, text='Update Files', command=self.updateFilesAll)
		self.buttonUpdate.grid(row=4, columnspan=1)

		self.buttonCancel = tkinter.Button(frame, text='Cancel', command=self.cancelAction)
		self.buttonCancel.grid(row=5, columnspan=1)

		#self.buttonShowBusy.config(state=tkinter.DISABLED)

		tkinter.Label(frame, text='Estado').grid(row=1, column=0)
		self.answer = tkinter.StringVar()
		self.answer.set("Ready")
		tkinter.Label(frame, textvariable=self.answer).grid(row=1, column=1)
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

	
	def updateFilesAll(self):
		self.answer.set("Actualizando archivos")
		self.buttonUpdate.config(state=tkinter.DISABLED)
		for i in self.servers:
			self.updateFiles(i)
		
		self.updateBusy()
		self.updateListBox()
		self.updateSetCopy()
		self.updateFilesCopy()
		
		self.buttonUpdate.after(5000, self.updateFilesListData)

	def updateFilesListData(self):
		for i in self.servers:
			self.servers.get(i).printBox1("Actualizando archivos del sistema")
			self.servers.get(i).updateListBox()
		self.printBox1("Archivos actualizados")
		self.buttonUpdate.config(state=tkinter.ACTIVE)
		self.updateListBox()
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

					

	def getFilesList(self):
		return [self.files, self.serversID]

	def getPermission(self, machine, fileName, serverID):
		serverName=self.serversID.get(serverID)
		return self.filesPermission.get(machine).get(fileName).get(serverName)

	def setBusy(self, machine, fileName, serverID):
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

	def deleteFile(self, fileName, serverID):
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
		print("serverName -> ", serverName)
		print("serverRead -> ", serverRead)
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
		if self.tipo=="main":
			self.server.register_function(self.register, 'register')
			self.server.register_function(self.getFilesList, 'getFilesList')
			self.server.register_function(self.getServerID, 'getServerID')
			self.server.register_function(self.getContent, 'getContent')
			self.server.register_function(self.getPermission, 'getPermission')
			self.server.register_function(self.setBusy, 'setBusy')
			self.server.register_function(self.closeFile, 'closeFile')
			self.server.register_function(self.modifyFile, 'modifyFile')
			self.server.register_function(self.removeBusy, 'removeBusy')
			self.server.register_function(self.deleteFile, 'deleteFile')

		else:
			print("Hay errores")
			raise SystemExit(1)
		self.server.serve_forever()

if __name__ == "__main__":
	tipoServer=str(input("El tipo de servidor\n"))
	ipServer = str(input("Ingrese la ip para el servidor\n"))
	puertoServer = int(input("ingrese el puerto para el servidor\n"))
	server=serverRPC(ipServer, puertoServer, tipoServer)
	hilo1=threading.Thread(target=server.runServer)
	hilo1.start()
	server.runGraph()