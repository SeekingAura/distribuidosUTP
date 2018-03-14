- Algoritmo de Berkeley: - Taller 8:
	* Servidor realiza un muestreo periódico preguntándole a las máquinas su hora
	* Se saca un promedio y se envia esa nueva hora a TODAS las maquinas descartandolos valores que estén muy alejados de la media (2 desviaciones estandar)
	* Se debe tener en cuenta el caso de que la hora que recibe sea menor correr mas lento el reloj
	Es decir uno es servidor le pide horas a todos los demas servidores saca un promedio (incluyendo la propia de el) y le envia la nueva hora