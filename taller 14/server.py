import threading
import time
import tkinter as tkinter
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
		self.filesPermission={}
		self.filesBusy={}
		self.filesList=[]
		self.folderStore="files"


		#Tkinter
		self.root = tkinter.Tk()
		self.root.wm_title("archivos - "+tipo)
		scrollbar = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
		self.TextoBox = tkinter.Text(self.root, height=8, width=80, yscrollcommand=scrollbar.set)
		self.TextoBox2 = tkinter.Text(self.root, height=8, width=80, yscrollcommand=scrollbar.set)
		scrollbar.config(command=self.yview)
		scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		
		self.TextoBox.pack(side=tkinter.LEFT, fill=tkinter.Y)
		self.TextoBox.config(state=tkinter.DISABLED)
		self.TextoBox2.pack(side=tkinter.LEFT, fill=tkinter.Y)
		self.TextoBox2.config(state=tkinter.DISABLED)
		frame = tkinter.Frame(self.root)
		frame.pack()
		
		self.list = tkinter.Listbox(self.root, selectmode=tkinter.SINGLE, yscrollcommand=scrollbar.set)
		self.list.pack(fill=tkinter.BOTH, expand=1)
		

		self.buttonShowFile = tkinter.Button(frame, text='Show File', command=self.showInfo)
		self.buttonShowFile.grid(row=2, columnspan=1)

		self.buttonShowBusy = tkinter.Button(frame, text='Select Busy Files', command=self.showBusy)
		self.buttonShowBusy.grid(row=3, columnspan=1)

		self.buttonUpdate = tkinter.Button(frame, text='Update Files', command=self.updateFilesAll)
		self.buttonUpdate.grid(row=4, columnspan=1)

		self.buttonCancel = tkinter.Button(frame, text='Cancel', command=self.cancelAction)
		self.buttonCancel.grid(row=5, columnspan=1)

		self.buttonShowBusy.config(state=tkinter.DISABLED)

		tkinter.Label(frame, text='Estado').grid(row=1, column=0)
		self.answer = tkinter.StringVar()
		self.answer.set("Ready")
		tkinter.Label(frame, textvariable=self.answer).grid(row=1, column=1)
		#Temp value

		
	
	def yview(self, *args):
		self.TextoBox.yview(*args)
		self.TextoBox2.yview(*args)
		self.list.yview(*args)

	def printBox1(self, value):
		self.TextoBox.config(state=tkinter.NORMAL)
		self.TextoBox.insert(tkinter.END, "\n"+time.asctime(time.localtime(time.time()))+str(value))
		self.TextoBox.see(tkinter.END)
		self.TextoBox.config(state=tkinter.DISABLED)

	def printBox2(self, value):
		self.TextoBox2.config(state=tkinter.NORMAL)
		self.TextoBox2.delete('1.0', tkinter.END)
		self.TextoBox2.insert(tkinter.END, str(value))
		self.TextoBox2.see(tkinter.END)
		self.TextoBox2.config(state=tkinter.DISABLED)


	def showInfo(self):
		fileSelected=self.list.curselection()
		if(len(fileSelected)==1):
			fileName=self.list.get(fileSelected[0])
			fileNumber=0
			if(":" in fileName):
				fileName, fileNumber=fileName.split(":")
				fileNumber=int(fileNumber)
			serverContentFile=None
			fileState=None
			for enum, i in enumerate(self.filesBusy.get(fileName)):
				if(enum==fileNumber):
					fileContent=self.servers[i].getFile(fileName)
					serverContentFile=i
					if(self.filesBusy.get(fileName).get(i) is None):
						fileState="No ocupado"
					else:
						fileState="Ocupado"
			self.printBox1("Archivo: {}\nGuardado en: {}\nEstado: {}\n#----------#\n".format(fileName, serverContentFile, fileState))
			self.printBox2(fileContent)

		elif(len(fileSelected)==0):
			self.printBox1("No hay archivo seleccionado")
		else:
			self.printBox1("Hay mas de uno seleccionado")
		self.answer.set("Leyendo archivo")
	
	def showBusy(self):
		self.answer.set("Obteniendo Busy")
		tempIndex=0
		self.list.selection_clear(0, tkinter.END)
		for i in self.filesBusy:
			for j in self.filesBusy.get(i):
				if(self.filesBusy.get(i).get(j) is not None):
					self.list.selection_set(tempIndex, tempIndex)
				tempIndex+=1
		self.answer.set("Ready")


	def runGraph(self):
		self.root.mainloop()

	def registerFile(self, serverDir, fileName):
		serverName=self.servers.get(serverDir).getName()
		try:
			fileSave=open(self.folderStore+'/'+serverName+"/"+fileName, "w")
		except:
			os.makedirs(self.folderStore+'/'+serverName)
			fileSave=open(self.folderStore+'/'+serverName+"/"+fileName, "w")
		fileData=self.servers.get(serverDir).getFile(fileName)
		fileSave.write(fileData)
		fileSave.close()



	def register(self, ipServer, puertoServer):
		#value=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer)
		self.answer.set("Registrando cliente")
		self.servers["http://"+ipServer+":"+puertoServer]=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
		self.filesPermission["http://"+ipServer+":"+puertoServer]={}
		self.updateFilesAll()
		self.printBox1("Se ha registrado el servidor {}".format("http://"+ipServer+":"+puertoServer))
		self.answer.set("Ready")


	def updateBusy(self):
		self.answer.set("actualizando Busy")
		for i in self.servers:#lista de direcciones de servidores
			for j in self.servers.get(i).getFiles():#Obtiene los archivos por cada servidor
				if not j in self.filesBusy:#verificando si el servidor NO posee dicho archivo
					self.filesBusy[j]={}
					self.filesBusy[j][i]=None
					self.registerFile(i, j)
				elif not i in self.filesBusy.get(j):
					self.filesBusy[j][i]=None
					self.registerFile(i, j)

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

	def updateFilesList(self):
		self.answer.set("actualizando lista")
		listTemp=[]
		for i in self.filesBusy:
			for enum, j in enumerate(self.filesBusy.get(i)):
				if(enum==0):
					listTemp.append(i)
				else:
					listTemp.append(i+":"+str(enum))
		self.filesList=listTemp
	
	def updateFilesAll(self):
		self.answer.set("Actualizando archivos")
		for i in self.servers:
			self.updateFiles(i)
		
		self.updateBusy()
		self.updateFilesList()
		self.updateListBox()
		
		self.answer.set("Ready")
		self.buttonUpdate.after(1000, self.updateFilesListData)

	def updateFilesListData(self):
		for i in self.servers:
			self.servers.get(i).printBox1("Hay actualización disponible de archivos")
		self.printBox1("Archivos actualizados")
	
	def updateListBox(self):
		listaTemp=self.getFilesList()
		self.list.delete(0, tkinter.END)#Borra TODO
		for i in listaTemp:
			self.list.insert(tkinter.END, i)

	def getFilesList(self):
		return self.filesList

	def getPermission(self, machine, fileName):
		fileNumber=0
		if(":" in fileName):
			fileName, fileNumber=fileName.split(":")
			fileNumber=int(fileNumber)
		for enum, i in enumerate(self.filesBusy.get(fileName)):#Busy is a static list
			if(enum==fileNumber):
				return self.filesPermission.get(machine).get(fileName).get(i)

	def setBusy(self, machine, fileName):
		fileNumber=0
		if(":" in fileName):
			fileName, fileNumber=fileName.split(":")
			fileNumber=int(fileNumber)
		for enum, i in enumerate(self.filesBusy.get(fileName)):
			if(enum==fileNumber):
				if self.filesBusy.get(fileName).get(i) is None:
					self.filesBusy[fileName][i]=machine
					self.printBox1("se ha ocupado el archivo {}, ubicado en {}, por {}".format(fileName, i, machine))
					return True
				else:
					break

		return False

	def removeBusy(self, fileName):
		fileNumber=0
		if(":" in fileName):
			fileName, fileNumber=fileName.split(":")
			fileNumber=int(fileNumber)
		for enum, i in enumerate(self.filesBusy.get(fileName)):
			if(enum==fileNumber):
				if self.filesBusy.get(fileName).get(i) is not None:
					self.filesBusy[fileName][i]=None
					self.printBox1("Se ha dejado de ocupar el archivo {}, ubicado en {}".format(fileName, i))
					return True
				else:
					break

		return False

	def modifyFile(self, fileName, fileData):
		fileNumber=0
		if(":" in fileName):
			fileName, fileNumber=fileName.split(":")
			fileNumber=int(fileNumber)
		for enum, i in enumerate(self.filesBusy.get(fileName)):
			if(enum==fileNumber):
				serverFile=i
				self.filesBusy[fileName][i]=None
		self.printBox1("Modificado el archivo {} ubicado en {}".format(fileName, serverFile))
		serverName=self.servers.get(serverFile).getName()
		fileSave=open(self.folderStore+'/'+serverName+"/"+fileName, "w")
		fileSave.write(fileData)
		fileSave.close()
		self.servers.get(serverFile).modifyFile(fileName, fileData)

	def deleteFile(self, fileName):
		fileNumber=0
		if(":" in fileName):
			fileName, fileNumber=fileName.split(":")
			fileNumber=int(fileNumber)
		for enum, i in enumerate(self.filesBusy.get(fileName)):
			if(enum==fileNumber):
				serverFile=i
				break
		for i in self.filesPermission:
			self.filesPermission.get(i).get(fileName).pop(serverFile)
			if(len(self.filesPermission.get(i).get(fileName))==0):
				self.filesPermission.get(i).pop(fileName)
				
		self.filesBusy.get(fileName).pop(serverFile)
		if(len(self.filesBusy.get(fileName))==0):
			self.filesBusy.pop(fileName)
		self.printBox1("Borrado el archivo {} ubicado en {}".format(fileName, serverFile))
		serverName=self.servers.get(serverFile).getName()
		os.remove(self.folderStore+'/'+serverName+"/"+fileName)
		self.servers.get(serverFile).deleteFile(fileName)

	



	def getFile(self, fileName):
		fileNumber=0
		serverFile=None
		if(":" in fileName):
			fileName, fileNumber=fileName.split(":")
			fileNumber=int(fileNumber)
		for enum, i in enumerate(self.filesBusy.get(fileName)):
			if(enum==fileNumber):
				serverFile=i
		self.printBox1("Brindado información del archivo {} ubicado en {}".format(fileName, serverFile))
		serverName=self.servers.get(serverFile).getName()
		fileData=open(self.folderStore+'/'+serverName+"/"+fileName, "r").read()
		return fileData
		

	def cancelAction(self):
		# self.reading=False
		self.printBox2("")
		self.printBox1("acción cancelada")
		self.buttonShowFile.config(state=tkinter.NORMAL)
		self.buttonShowBusy.config(state=tkinter.NORMAL)
		self.buttonCancel.config(state=tkinter.DISABLED)
		self.answer.set("Ready")
		

	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		if self.tipo=="main":
			self.server.register_function(self.register, 'register')
			self.server.register_function(self.getFilesList, 'getFilesList')
			self.server.register_function(self.getFile, 'getFile')
			self.server.register_function(self.setBusy, 'setBusy')
			self.server.register_function(self.getPermission, 'getPermission')
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