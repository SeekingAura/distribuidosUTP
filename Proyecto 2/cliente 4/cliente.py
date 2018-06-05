import threading
import time
import tkinter as tkinter
import tkinter.ttk as ttk
import xmlrpc.client
import sys
import os, shutil
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
		self.ownAddres="http://"+ip+":"+str(puerto)
		# used how name of server/client
		self.tipo=tipo
		self.ID=None
		# data about coneection to server
		self.conecction=None
		# list with name files from server
		self.filesList=[]
		# States on program
		self.reading=False
		self.writing=False
		self.fileReading=None
		self.serverReading=None
		
		self.filesPath="files"
		try:
			os.makedirs(self.filesPath)
			print("Created - files dir")
		except:
			print("Ready - files dir")
		self.filesCopyPath="copy"
		try:
			os.makedirs(self.filesCopyPath)
			print("Created - copy dir")
		except:
			print("ready Copy folder")
		#Clean copy Folder
		for the_file in os.listdir(self.filesCopyPath):
			file_path = os.path.join(self.filesCopyPath, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except Exception as e:
				print(e)

		#Tkinter
		self.root = tkinter.Tk()
		# Window name
		self.root.wm_title("archivos - "+tipo)
		# Scrollbar object
		scrollbar = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
		scrollbarH = tkinter.Scrollbar(self.root, orient=tkinter.HORIZONTAL)
		self.TextoBox = tkinter.Text(self.root, height=8, width=90, yscrollcommand=scrollbar.set)
		self.TextoBox2 = tkinter.Text(self.root, height=8, width=50, yscrollcommand=scrollbar.set)
		scrollbar.config(command=self.yview)
		scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		scrollbarH.config(command=self.xview)
		scrollbarH.pack(side=tkinter.BOTTOM, fill=tkinter.X)
		# set scrollbar on Text Box
		self.TextoBox.pack(side=tkinter.LEFT, fill=tkinter.Y)
		
		self.TextoBox2.pack(side=tkinter.LEFT, fill=tkinter.Y)
		# Set text box mode only read
		self.TextoBox2.config(state=tkinter.DISABLED)
		self.TextoBox.config(state=tkinter.DISABLED)
		# Set frame from Tkinter Object
		frame = tkinter.Frame(self.root)
		frame.pack()
		


		self.tree = ttk.Treeview(self.root)
		self.tree.configure(yscroll=scrollbar.set, xscroll=scrollbarH.set)
		self.tree.column("#0",minwidth=89*6, stretch=True)
		self.tree.heading('#0', text="Arbol de archivos", anchor='w')
		self.tree.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		
		
		
		self.buttonShowFile = tkinter.Button(frame, text='Show File', command=self.readFile)
		self.buttonShowFile.grid(row=2, columnspan=1)

		self.buttonWriteFile = tkinter.Button(frame, text='Write File', command=self.writeFile)
		self.buttonWriteFile.grid(row=3, columnspan=1)

		self.buttonSave = tkinter.Button(frame, text='Save', command=self.saveFile)
		self.buttonSave.grid(row=4, columnspan=1)
		
		self.buttonUpdate = tkinter.Button(frame, text='Update Files List', command=self.updateListBox)
		self.buttonUpdate.grid(row=5, columnspan=1)
		
		self.buttonDelete = tkinter.Button(frame, text='DELETE', command=self.deleteFileServer)
		self.buttonDelete.grid(row=6, columnspan=1)

		self.buttonCancel = tkinter.Button(frame, text='Cancel', command=self.cancelAction)
		self.buttonCancel.grid(row=7, columnspan=1)
		
		


		tkinter.Label(frame, text='Estado').grid(row=1, column=0)
		self.answer = tkinter.StringVar()
		tkinter.Label(frame, textvariable=self.answer).grid(row=1, column=1)
		
		#Temp value
		self.buttonCancel.config(state=tkinter.DISABLED)
		self.answer.set("Ready")
	
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


	def readFile(self):
		fileSelected=self.tree.selection()
		if(len(fileSelected)==1):
			fileID=fileSelected[0]
			parent=self.tree.parent(fileID)
			fileName=self.tree.item(fileID)['text']
			if(parent!=""):
				serverID=self.tree.item(parent)['text']
				serverName=self.conecction.getServerID(serverID)
				permission=self.conecction.getPermission(self.ownAddres, fileName, serverID)
				if(permission=="lectura" or permission=="escritura"):
					self.printBox1("Solicitado archivo {}".format(fileName))
					fileData, serverRead=self.conecction.getContent(fileName, serverName, self.ownAddres)
					self.printBox1("Obtenido archivo {}".format(fileName))
					
					self.fileReading=fileName
					self.serverReadingCopy=serverRead
					self.serverReading=serverName
					self.printBox2(fileData)
					self.reading=True
					self.buttonShowFile.config(state=tkinter.DISABLED)
					self.buttonWriteFile.config(state=tkinter.DISABLED)
					self.buttonSave.config(state=tkinter.DISABLED)
					self.buttonDelete.config(state=tkinter.DISABLED)
					self.buttonUpdate.config(state=tkinter.DISABLED)
					self.buttonCancel.config(state=tkinter.NORMAL)
				
					self.answer.set("Leyendo archivo")
				else:
					self.printBox1("ERROR, Permisos insuficientes")
		elif(len(fileSelected)==0):
			self.printBox1("No hay archivo seleccionado")
		else:
			self.printBox1("Hay mas de uno seleccionado")
	
	def writeFile(self):
		fileSelected=self.tree.selection()
		
		if(len(fileSelected)==1):
			fileID=fileSelected[0]
			parent=self.tree.parent(fileID)
			fileName=self.tree.item(fileID)['text']
			if(parent!=""):
				serverID=self.tree.item(parent)['text']
				serverName=self.conecction.getServerID(serverID)
				permission=self.conecction.getPermission(self.ownAddres, fileName, serverID)
				if(permission=="escritura"):
					if(self.conecction.setBusy(self.ownAddres, fileName, serverID)):#Set busy file
						self.printBox1("Solicitado archivo {}".format(fileName))
						fileData, serverRead=self.conecction.getContent(fileName, serverName, self.ownAddres)
						self.printBox1("Obtenido archivo {}".format(fileName))
						self.fileReading=fileName
						self.serverReadingCopy=serverRead
						self.serverReading=serverName
					 	
						self.printBox2(fileData)
						self.TextoBox2.config(state=tkinter.NORMAL)
						self.writing=True
						self.buttonShowFile.config(state=tkinter.DISABLED)
						self.buttonWriteFile.config(state=tkinter.DISABLED)
						self.buttonDelete.config(state=tkinter.DISABLED)
						self.buttonUpdate.config(state=tkinter.DISABLED)
						self.buttonSave.config(state=tkinter.NORMAL)
						self.buttonCancel.config(state=tkinter.NORMAL)
						self.answer.set("Editando archivo")

					else:
						self.printBox1("ERROR, El archivo no se puede editar, está ocupado")
				else:
					self.printBox1("ERROR, Permisos insuficientes para escribir el archivo {}".format(fileName))
			else:
				self.printBox1("ERROR Ha seleccionado es un directorio")
		elif(len(fileSelected)==0):
			self.printBox1("No hay archivo seleccionado")
		else:
			self.printBox1("Hay mas de uno seleccionado")

	def deleteFileServer(self):
		fileSelected=self.tree.selection()
		
		if(len(fileSelected)==1):
			fileID=fileSelected[0]
			parent=self.tree.parent(fileID)
			fileName=self.tree.item(fileID)['text']
			if(parent!=""):
				serverID=self.tree.item(parent)['text']
				self.printBox1("Solicitado borrado {}".format(fileName))
				permission=self.conecction.getPermission(self.ownAddres, fileName, serverID)
				if(permission=="escritura"):
					if(self.conecction.setBusy(self.ownAddres, fileName, serverID)):#Set busy file
						self.answer.set("Borrando Archivo")
						self.conecction.deleteFile(fileName, serverID)
						self.answer.set("Ready")
					else:
						self.printBox1("ERROR, El archivo no se puede borrar está ocupado")
				else:
					self.printBox1("ERROR, Permisos insuficientes para borrar el archivo {}".format(fileName))
		elif(len(fileSelected)==0):
			self.printBox1("No hay archivo seleccionado")
		else:
			self.printBox1("Hay mas de uno seleccionado")

	def modifyFile(self, fileName, fileData):
		fileEdit=open(self.filesPath+"/"+fileName, "w")
		fileEdit.write(fileData)
		fileEdit.close()

	def deleteCopy(self, fileName, serverID):
		#print("delete -> ", serverID)
		try:
			os.remove(self.filesCopyPath+"/"+str(serverID)+"/"+fileName)
		except:
			print("Ya estaba borrado")


	def deleteFile(self, fileName):
		#print("borrando -> ", fileName)
		try:
			os.remove(self.filesPath+"/"+fileName)
		except:
			print("Ya estaba borrado")

	def saveFile(self):
		self.answer.set("Guardando...")
		
		fileData=self.TextoBox2.get(1.0, tkinter.END)
		self.conecction.modifyFile(self.fileReading, fileData, self.serverReading)
		self.writing=False
		self.buttonShowFile.config(state=tkinter.NORMAL)
		self.buttonWriteFile.config(state=tkinter.NORMAL)
		self.buttonUpdate.config(state=tkinter.NORMAL)
		self.buttonDelete.config(state=tkinter.NORMAL)
		self.buttonSave.config(state=tkinter.DISABLED)
		self.buttonCancel.config(state=tkinter.DISABLED)
		self.printBox2("")
		self.printBox1("Guardado archivo {}".format(self.fileReading))
		self.fileReading=None
		self.serverReading=None
		self.serverReadingCopy=None
		self.answer.set("Ready")

	def cancelAction(self):
		if(self.writing):
			self.conecction.removeBusy(self.fileReading, self.serverReading)
		if(self.reading):
			self.conecction.closeFile(self.fileReading, self.serverReading, self.serverReadingCopy, self.ownAddres)
		self.writing=False
		self.reading=False
		self.printBox2("")
		self.printBox1("acción cancelada")
		self.buttonShowFile.config(state=tkinter.NORMAL)
		self.buttonWriteFile.config(state=tkinter.NORMAL)
		self.buttonUpdate.config(state=tkinter.NORMAL)
		self.buttonDelete.config(state=tkinter.NORMAL)
		self.buttonCancel.config(state=tkinter.DISABLED)
		self.fileReading=None
		self.serverReading=None
		self.serverReadingCopy=None


	def runGraph(self):
		self.root.mainloop()

	def updateCopy(self, fileName, serverID, fileData):
		print("Actualizando copias -> "+"[ "+time.asctime(time.localtime(time.time()))+"] ")
		try: 
			os.makedirs(self.filesCopyPath+"/"+str(serverID))
		except:
			print("Carpeta hecha")
		#+str(fileName)
		fileEdit=open(self.filesCopyPath+"/"+str(serverID)+"/"+fileName, "w")
		fileEdit.write(fileData)
		fileEdit.close()

	def updateListBox(self):
		DictTemp, IdsTemp=self.conecction.getFilesList()
		self.tree.delete(*self.tree.get_children())# Borra el arbol
		for i in IdsTemp:
			folder=self.tree.insert('', 'end', text=str(i))
			for j in DictTemp.get(IdsTemp.get(i)):
				self.tree.insert(folder, 'end', text=str(j))
		self.printBox1("Se ha actualizado la lista")

	def getFiles(self):
		files = [f for f in os.listdir(self.filesPath) if os.path.isfile(self.filesPath+"/"+f)]
		#files.remove(__file__)
		return files

	def getFile(self, fileName):
		fileText=open(self.filesPath+"/"+fileName, "r").read()
		return fileText

	def getFileCopy(self, fileName, serverID):
		fileText=open(self.filesCopyPath+"/"+str(serverID)+"/"+fileName, "r").read()
		return fileText

	def setID(self, ID):
		self.ID=str(ID)

	def registrarse(self):
		self.conecction.register(self.ip, str(self.puerto))
	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.getFiles, 'getFiles')
		self.server.register_function(self.getFile, 'getFile')
		self.server.register_function(self.getFileCopy, 'getFileCopy')
		self.server.register_function(self.setID, 'setID')
		self.server.register_function(self.updateCopy, 'updateCopy')
		self.server.register_function(self.modifyFile, 'modifyFile')
		self.server.register_function(self.deleteFile, 'deleteFile')
		self.server.register_function(self.deleteCopy, 'deleteCopy')
		self.server.register_function(self.printBox1, 'printBox1')
		self.server.register_function(self.updateListBox, 'updateListBox')
		ipServer = str(input("Ingrese la ip del server principal\n"))
		puertoServer = str(input("ingrese el puerto del server principal\n"))

		self.conecction=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
		self.buttonCancel.after(3000, self.registrarse)
		self.server.serve_forever()

if __name__ == "__main__":
	tipoServer=str(input("El tipo de cliente\n"))
	ipServer = str(input("Ingrese la ip para el cliente\n"))
	puertoServer = int(input("ingrese el puerto para el cliente\n"))
	server=serverRPC(ipServer, puertoServer, tipoServer)
	hilo1=threading.Thread(target=server.runServer)
	hilo1.start()
	server.runGraph()