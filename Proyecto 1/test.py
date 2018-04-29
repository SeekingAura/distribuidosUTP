import os
import random
# files = [f for f in os.listdir('.') if os.path.isfile(f)]
# files={"algo":{"aquel":{"boludo":"0"}}, "otro":"http1", "aquello":"http2", "algo:1":"http2"}
# listTest=["valorUno", "valorDos", "valorTres"]
# files.remove(__file__)
# server="http3"
# for i in files:
#     temp=""
#     for j in i:
#         if(j==":"):
#             break
#         else:
#             temp+=j
#     if(temp=="algo"):
#         print(files.get(i)==server)
# for i in range(100):
#     print(listTest[random.randint(0, 2)])
# files.pop("algo")
# print(files.get("algo").get("aquel"))
# print("http1" in files)

dicto={"values":{"esto":"algo"}, "aluk":{"esto":"YOLO"}}
print(dicto)
dicto.get("values").pop("esto")

print(dicto)
print(len(dicto.get("values")))



"""
import tkinter as tkinter

class Dialog():

	def __init__(self):
		self.root = tkinter.Tk()
		frame = tkinter.Frame(self.root)
		frame.pack()
		self.list = tkinter.Listbox(self.root, selectmode=tkinter.SINGLE, activestyle="dotbox")
		self.list.pack(fill=tkinter.BOTH, expand=1)
		#self.list.select_set=tkinter.SINGLE
		self.current = None
		self.poll() # start polling the list

	def poll(self):
		now = self.list.curselection()
		if now != self.current:
			self.list_has_changed(now)
			self.current = now
		self.list.after(250, self.poll)

	def list_has_changed(self, selection):
		if(len(selection)>0):
			print("selection is", self.list.get(selection[0]))
			self.list.activate(selection[0])
			self.list.activate(10)
			self.list.selection_clear(0, tkinter.END)
			self.list.selection_set(1, 1)
			self.list.selection_set(2, 2)
			#self.list.configure(state=tkinter.DISABLED)
			print("on disable is", self.list.get(tkinter.ACTIVE))
			#fileText=open(self.list.get(selection[0]), "r").read()
			#fileEdit=open(self.list.get(selection[0]), "w")
			#fileEdit.write(fileText+"\notra cosa mas")
			#fileEdit.close()
			#self.list.selection_clear(0, tkinter.END)
			
			# self.list.config(state=tkinter.DISABLED)

	def setList(self, item):
		x.list.delete(0, tkinter.END)#Borra TODO
		if(isinstance(item, list)):
			for i in item:
				self.list.insert(tkinter.END, i)

	def disable(self):
		self.list.state=tkinter.DISABLED
	def runGraph(self):
		self.root.mainloop()
x=Dialog()
files = [f for f in os.listdir('.') if os.path.isfile(f)]
files.remove(__file__)
files.sort()
x.setList(files)
x.runGraph()

print(":" in "el putas dos")
"""