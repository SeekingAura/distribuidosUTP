import os
import tkinter as tkinter
import tkinter.ttk as ttk

class App():
	def __init__(self):
		self.root = tkinter.Tk()
		self.root.wm_title("probando")
		self.tree = ttk.Treeview(self.root)
		#ysb = ttk.Scrollbar(self.root, orient='vertical', command=self.tree.yview)
		#xsb = ttk.Scrollbar(self.root, orient='horizontal', command=self.tree.xview)
		#self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
		#self.tree.column("#0",minwidth=89*6, stretch=True)

		self.tree.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		#ysb.grid(row=0, column=1, sticky='ns')
		#xsb.grid(row=1, column=0, sticky='ew')
		frame = tkinter.Frame(self.root)
		frame.pack()

		self.buttonShowFile = tkinter.Button(frame, text='Show File', command=self.getValue)
		self.buttonShowFile.grid(row=1, columnspan=1)
		self.buttonDeleteFile = tkinter.Button(frame, text='D File', command=self.delete)
		self.buttonDeleteFile.grid(row=2, columnspan=1)
		self.buttonWriteFile = tkinter.Button(frame, text='W File', command=self.make)
		self.buttonWriteFile.grid(row=3, columnspan=1)

		
		#self.tree.heading('#0', text="titulo", anchor='w')
		x=self.tree.insert('', 'end', text="yolo")
		
		self.tree.insert(x, 'end', text="dos")
		self.tree.insert(x, 'end', text="uno")
		self.tree.insert(x, 'end', text="tres")
		#self.tree.config(state="disabled")
	def getValue(self):
		item=self.tree.selection()
		print("YOLSAD -Z ", item)
		parent=self.tree.parent(item)
		print("parent ->", parent)
		print("parent ->", parent!="")
		print("item ->", item)
		if(parent):
			print(self.tree.item(parent)['text'])
			print(self.tree.item(item)['text'])
		else:
			print(self.tree.item(item)['text'])
	def delete(self):
		self.tree.delete(*self.tree.get_children())
	def make(self):
		x=self.tree.insert('', 'end', text="Again")
		self.tree.insert(x, 'end', text="tumas")


#path_to_my_project = os.getcwd()
app = App()
app.root.mainloop()