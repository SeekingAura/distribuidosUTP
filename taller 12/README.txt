Centralizado:
	Mantiene una tabla de uso: una entrada por cada estación de trabajo con valor de inicio de cero, esa tiene
		* Nombre o id de la estación
		* valor de entrada: indica que tantos usos lleva, es decir cuantas veces se le ha dado un procesador donde se suma a medida que se le asigna procesadores y se le resta a medida de que NO fue posible darle procesador
	La estación pide un procesador al controlador y este lo asigna si está disponible. Sino, pone la solicitud en cola.
	
Hay un servidor que solo se encarga de brindar las direciones y tiene la tabla de usos y la cola de procesos; los clientes cada uno puede brindar procesamiento, solo puede ayudar a uno solo al tiempo y solo puede ayudar cuando tiene menos del 70% ocupado de cpu (la cpu será simulada con valores random del 0 al 100 que cambiará mientras NO esté ayudando)