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
		self.ownAddres="http://"+ip+":"+str(puerto)
		# used how name of server/client
		self.tipo=tipo
		# data about coneection to server
		self.conecction=None
		# list with name files from server
		self.filesList=[]
		# States on program
		self.reading=False
		self.writing=False


		#Tkinter
		self.root = tkinter.Tk()
		# Window name
		self.root.wm_title("archivos - "+tipo)
		# Scrollbar object
		scrollbar = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
		# Text Box - Log server
		self.TextoBox = tkinter.Text(self.root, height=8, width=80, yscrollcommand=scrollbar.set)
		# Text Box - Text to edit
		self.TextoBox2 = tkinter.Text(self.root, height=8, width=80, yscrollcommand=scrollbar.set)
		# set scrollbar movement
		scrollbar.config(command=self.yview)
		# set scrollbar direction
		scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		# set scrollbar on Text Box
		self.TextoBox.pack(side=tkinter.LEFT, fill=tkinter.Y)
		
		self.TextoBox2.pack(side=tkinter.LEFT, fill=tkinter.Y)
		# Set text box mode only read
		self.TextoBox2.config(state=tkinter.DISABLED)
		self.TextoBox.config(state=tkinter.DISABLED)
		# Set frame from Tkinter Object
		frame = tkinter.Frame(self.root)
		frame.pack()
		
		self.list = tkinter.Listbox(self.root, selectmode=tkinter.SINGLE, yscrollcommand=scrollbar.set)
		self.list.pack(fill=tkinter.BOTH, expand=1)
		
		
		
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
		self.list.yview(*args)

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
	
	def setList(self, item):
		self.list.delete(0, tkinter.END)#Borra TODO
		if(isinstance(item, list)):
			for i in item:
				self.list.insert(tkinter.END, i)


	def readFile(self):
		fileSelected=self.list.curselection()
		if(len(fileSelected)==1):
			fileName=self.list.get(fileSelected[0])
			permission=self.conecction.getPermission(self.ownAddres, fileName)
			if(permission=="lectura" or permission=="escritura"):
				self.printBox1("Solicitado archivo {}".format(fileName))
				fileData=self.conecction.getFile(fileName)
				self.printBox1("Obtenido archivo {}".format(fileName))
				self.printBox2(fileData)
				self.reading=True
				self.list.activate(fileSelected[0])
				self.list.configure(state=tkinter.DISABLED)
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
		fileSelected=self.list.curselection()
		
		if(len(fileSelected)==1):
			fileName=self.list.get(fileSelected[0])
			self.printBox1("Solicitado archivo {} para escritura".format(fileName))
			permission=self.conecction.getPermission(self.ownAddres, fileName)
			if(permission=="escritura"):
				if(self.conecction.setBusy(self.ownAddres, fileName)):#Set busy file
					
					fileData=self.conecction.getFile(fileName)
					self.printBox1("Obtenido archivo {}".format(fileName))
					self.printBox2(fileData)
					self.TextoBox2.config(state=tkinter.NORMAL)
					self.writing=True
					self.list.activate(fileSelected[0])
					self.list.configure(state=tkinter.DISABLED)
					self.buttonShowFile.config(state=tkinter.DISABLED)
					self.buttonWriteFile.config(state=tkinter.DISABLED)
					self.buttonDelete.config(state=tkinter.DISABLED)
					self.buttonUpdate.config(state=tkinter.DISABLED)
					self.buttonSave.config(state=tkinter.NORMAL)
					self.buttonCancel.config(state=tkinter.NORMAL)
					self.list.activate(fileSelected[0])
					self.answer.set("Editando archivo")

				else:
					self.printBox1("ERROR, El archivo no se puede editar, está ocupado")
			else:
				self.printBox1("ERROR, Permisos insuficientes para escribir el archivo {}".format(fileName))
		elif(len(fileSelected)==0):
			self.printBox1("No hay archivo seleccionado")
		else:
			self.printBox1("Hay mas de uno seleccionado")

	def deleteFileServer(self):
		fileSelected=self.list.curselection()
		
		if(len(fileSelected)==1):
			fileName=self.list.get(fileSelected[0])
			self.printBox1("Solicitado borrado {}".format(fileName))
			permission=self.conecction.getPermission(self.ownAddres, fileName)
			if(permission=="escritura"):
				if(self.conecction.setBusy(self.ownAddres, fileName)):#Set busy file
					
					self.conecction.deleteFile(fileName)
					self.answer.set("Borrando Archivo")
				else:
					self.printBox1("ERROR, El archivo no se puede borrar está ocupado")
			else:
				self.printBox1("ERROR, Permisos insuficientes para borrar el archivo {}".format(fileName))
		elif(len(fileSelected)==0):
			self.printBox1("No hay archivo seleccionado")
		else:
			self.printBox1("Hay mas de uno seleccionado")

	def modifyFile(self, fileName, fileData):
		fileEdit=open(fileName, "w")
		fileEdit.write(fileData)
		fileEdit.close()

	def deleteFile(self, fileName):
		os.remove(fileName)

	def saveFile(self):
		self.answer.set("Guardando...")
		fileName=self.list.get(tkinter.ACTIVE)
		fileData=self.TextoBox2.get(1.0, tkinter.END)
		self.conecction.modifyFile(fileName, fileData)
		self.writing=False
		self.list.configure(state=tkinter.NORMAL)
		self.buttonShowFile.config(state=tkinter.NORMAL)
		self.buttonWriteFile.config(state=tkinter.NORMAL)
		self.buttonUpdate.config(state=tkinter.NORMAL)
		self.buttonDelete.config(state=tkinter.NORMAL)
		self.buttonSave.config(state=tkinter.DISABLED)
		self.buttonCancel.config(state=tkinter.DISABLED)
		self.printBox2("")
		self.printBox1("Guardado archivo {}".format(fileName))
		self.answer.set("Ready")

	def cancelAction(self):
		if(self.writing):
			fileName=self.list.get(tkinter.ACTIVE)
			self.conecction.removeBusy(fileName)
		self.writing=False
		self.reading=False
		self.printBox2("")
		self.printBox1("acción cancelada")
		self.buttonShowFile.config(state=tkinter.NORMAL)
		self.buttonWriteFile.config(state=tkinter.NORMAL)
		self.buttonUpdate.config(state=tkinter.NORMAL)
		self.buttonDelete.config(state=tkinter.NORMAL)
		self.buttonCancel.config(state=tkinter.DISABLED)
		self.list.config(state=tkinter.NORMAL)


	def runGraph(self):
		self.root.mainloop()

	def updateListBox(self):
		listaTemp=self.conecction.getFilesList()
		self.list.delete(0, tkinter.END)#Borra TODO
		for i in listaTemp:
			self.list.insert(tkinter.END, i)
		self.printBox1("Se ha actualizado la lista")

	def getFiles(self):
		files = [f for f in os.listdir('.') if os.path.isfile(f)]
		files.remove(__file__)
		return files

	def getFile(self, fileName):
		fileText=open(fileName, "r").read()
		return fileText

	def registrarse(self):
		self.conecction.register(self.ip, str(self.puerto))
	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		self.server.register_function(self.getFiles, 'getFiles')
		self.server.register_function(self.getFile, 'getFile')
		self.server.register_function(self.modifyFile, 'modifyFile')
		self.server.register_function(self.deleteFile, 'deleteFile')
		self.server.register_function(self.printBox1, 'printBox1')
		ipServer = str(input("Ingrese la ip del server principal\n"))
		puertoServer = str(input("ingrese el puerto del server principal\n"))

		self.conecction=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
		self.buttonCancel.after(1000, self.registrarse)
		self.server.serve_forever()

if __name__ == "__main__":
	tipoServer=str(input("El tipo de cliente\n"))
	ipServer = str(input("Ingrese la ip para el cliente\n"))
	puertoServer = int(input("ingrese el puerto para el cliente\n"))
	server=serverRPC(ipServer, puertoServer, tipoServer)
	hilo1=threading.Thread(target=server.runServer)
	hilo1.start()
	server.runGraph()