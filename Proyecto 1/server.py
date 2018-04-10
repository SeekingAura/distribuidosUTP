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
	def __init__(self, ip="localhost", puerto=5500, tipo="main"):
		#Server Control
		self.server=SimpleXMLRPCServer((ip, puerto), requestHandler=RequestHandler, allow_none=True)
		self.server.register_introspection_functions()
		self.ip=ip
		self.puerto=puerto
		self.tipo=tipo
		self.conecction=None
		self.busyWith=None
		self.servers=[]

		#Tkinter
		self.root = tkinter.Tk()
		self.root.wm_title("archivos - "+tipo)
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

	def register(self, ipServer, puertoServer):
		#value=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer)
		self.servers.append("http://"+ipServer+":"+puertoServer)
		self.printBox("Se ha registrado el servidor {}".format("http://"+ipServer+":"+puertoServer))

	
	def runServer(self):
		print("corriendo server de tipo {}".format(self.tipo))
		if self.tipo=="main":
			self.server.register_function(self.register, 'register')

		elif self.tipo[:6]=="server":
			ipServer = str(input("Ingrese la ip del server principal\n"))
			puertoServer = str(input("ingrese el puerto del server principal\n"))
			
			
			self.conecction=xmlrpc.client.ServerProxy("http://"+ipServer+":"+puertoServer, allow_none=True)
			self.conecction.register(self.ip, str(self.puerto))
		elif(self.tipo[:7]=="cliente"):
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
	server=serverRPC(ipServer, puertoServer, tipoServer)
	hilo1=threading.Thread(target=server.runServer)
	hilo1.start()
	server.runGraph()