#!usr/bin/env python
# -*- encoding: utf-8 -*-

from matplotlib import pylab


print "Introduce el nombre del automata a leer."
archivo = 'automata_CI_490.txt' #raw_input()
f = open(archivo, 'r')
filas = f.readlines()
nfilas = len(filas)
m = [] # Matriz del automata
for i in xrange(nfilas):
	fila = filas[i].split()
	longfila=len(fila)
	for j in xrange(longfila):
		fila[j] = int(float(fila[j]))
	m.append(fila)

m_new = []
new_fila = []
for r in xrange(nfilas):
	n_elem = len(m[r])
	fila_actual = m[r][:]
	elto = fila_actual[:]
	new_elto = elto[:]
	for i in xrange(-3,n_elem-3):
		izq_suma = elto[i-3] + elto[i-2] + elto[i-1]
		der_suma = elto[i+1] + elto[i+2] + elto[i+3]
		suma = izq_suma + der_suma
		if suma == 3:
			new_elto[i] = 1
		else:
			new_elto[i] = 0
	new_fila.append(new_elto)

m_new = new_fila[:]

print (m_new[0][0])

pylab.matshow(m_new,cmap='binary')
pylab.title("Celdas")
pylab.ylabel("Tiempo")
pylab.savefig("Filtrado.eps")
pylab.show()
#pylab.close()
