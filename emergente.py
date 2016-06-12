#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
Autor: Daniel Lopez Coto

Este programa pretende reproducir los resultados de la computacion emergente usando los
metodos de los automatas celulares unidimensionales.

Informacion util:
		- r = 3 (vecindad de orden 3)
		- D = 1 (automatas unidimensionales)
		- k = 2 (dos posibles estados: 0 o 1)
		- 2**(2*r+1) = Numero de bits necesarios para las reglas (en este caso 128 bites)
		- Numero de reglas: 100
		- Uso de algoritmos geneticos
		- Reglas de transicion totalisticas
		- Tamanio de los automatas (size) = 149

"""

import numpy as np
import random as rd
import csv
from matplotlib import pylab
import sys

import time as TIEMPO

""" Definimos un decorador, que nos dara el tiempo de ejecucion de la funcion
decorada """

def cronometro(funcion):
	def fun_a_ejecutar(*args):
		t1 = TIEMPO.time()
		resultado = funcion(*args)
		t2 = TIEMPO.time()
		T = t2 - t1
		nombre = funcion.__name__
		print("Tiempo de '%s': %g segundos" %(nombre,T))
		return resultado
	return fun_a_ejecutar

""" Clase automata que es la que creara las reglas, o en caso de haberas introducido
nosotros, las manejara; calculara el ajuste (fitness) de dichas reglas y las
ira modificando """

class Automata:
	
	def __init__(self,numeroReglas=20,initSize=149,tiempo=None,initVector=None,initReglas=None):
	
		""" Inicializamos los valores que vamos a necesitar en el programa. 
		Los parametros de entrada que permite son: Numero; tamaño del automata (numero
		de celdas); set inicial de condiciones iniciales y set de reglas, respectivamente. 
		'setReglas' es una lista que contiene las reglas (lista de listas).
		'setVectores' es una lista que contiene las configuraciones iniciales de las celdas (lista
		de listas)"""
		
		self.size = initSize 			# Numero de celdas que tendra el automata.
		self.noReglas = numeroReglas 	# Numero de reglas.
		self.time = tiempo
		if self.time == None:
			self.time = initSize * 2

		if initReglas == None:			# Si no hay reglas inicialmente, las creamos.
			self.setReglas = tuple(self.crearReglas(self.noReglas))
		else:							# Si ya hemos introducido las reglas, las inicializamos.
			self.setReglas = tuple(initReglas)
		
		if initVector == None:			# Si no hay un vector con los valores iniciales,
										# lo creamos.
			self.setVectores = condIniciales(self.size)
		else:							# Si lo hay, lo inicializamos.
			self.setVectores = initVector

	
	def crearReglas(self,noReglas):
		Rules = list(np.zeros(noReglas))	# Lista que almacena las diferentes reglas.

		for i in xrange(noReglas):
			rule = [] 				# Lista que contendra a la regla i-esima.
			for j in xrange(128):
				a = rd.random()		# En cada iteracion generamos un numero aleatorio entre 0 y 1
				if a > 0.5:
					rule.append(1)
				else:
					rule.append(0)
			
			Rules[i] = rule

		return Rules 			# Devuelve una lista de reglas, donde cada elemento es
									# una regla de 128 elementos 0s y 1s (es decir, una lista
									# de 128 elementos).

	def cambiarEstado(self,regla,tiempo):
		""" Este metodo recibe como entrada un entero que corresponde a la cantidad de
		pasos de tiempo que se van a evaluar los estados de las celulas para cada regla."""
	
		self.setEstados = self.setVectores[:]   # Lista que contiene el conjunto de estados para la regla
											 # introducida como parámetro,
											 # para cada CI, y para cada paso de tiempo.
		numEsta2Iniciales = len(self.setEstados)	# Almacena el numero de estados iniciales
											 # que correspondera con el numero de CIs.

		M_r = [[None]*tiempo for s in xrange(numEsta2Iniciales)]	# Matriz que almacena los estados para cada
												   # paso de tiempo, y para cada CI. Las filas son las diferentes
												   # CIs y las columnas los diferentes estados de tiempo.
												   # M_r[i] todos los estados de tiempo de la CI i-esima.
	  
		
		for i in xrange(numEsta2Iniciales):		# Iteramos sobre las Configuraciones Iniciales.
			estadoActual = self.setEstados[i][:]	  # Escogemos la CI i-esima.
			nuevoEstado = estadoActual[:]
			M_r[i][0] = estadoActual[:]

			for t in xrange(1,tiempo):			   # Iteramos sobre cada paso de tiempo.
				for j in xrange(-3,self.size-3):   # Iteramos sobre las posiciones.
					""" Codificamos la configuracion de vecinos en binario, y lo convertimos en un 
					numero. Dicho numero sera la posicion de la regla que estamos evaluando,
					y el valor que este almacenado en dicha posicion, sera asignado al nuevo
					estado de la celula j."""
					binario = '0b'+str(estadoActual[j-3])+str(estadoActual[j-2])+\
							str(estadoActual[j-1])+str(estadoActual[j])+\
							str(estadoActual[j+1])+str(estadoActual[j+2])+str(estadoActual[j+3])
					nuevoEstado[j] = regla[int(binario,2)]
				estadoActual = nuevoEstado[:]
				M_r[i][t] = [float(s) for s in estadoActual]
			
		return M_r			  # Devuele la matriz con todas las configuraciones de cada paso de tiempo, para
								# cada CI.


	def fitnessFun(self,confVectores):
		""" Este metodo recibe como entrada el set de configuraciones de las celulas
		en cada instante de tiempo para una regla concreta."""

		conjuntoFitness = []		 # Lista que almacena los ajustes para las diferentes CIs
		numElementos = self.size	 # Tamaño del automata
		numCIs = len(confVectores)   # Numero de CIs
		pasosTiempo = len(confVectores[0])	   # Numero de pasos de tiempo
		
		for i in xrange(numCIs):
			inicial = confVectores[i][0]
			suma = sum(inicial)/numElementos # Nos dice si la configuracion inicial tiene mas ceros o unos
			final = confVectores[i][-1]	# Obtenemos el ultimo paso de tiempo para la CI i-esima
			fit = sum(final)/numElementos  # Calcula el grado del ajuste
			if suma < 0.5:				  # Si el estado inicial tiene mas 0 que unos, cambia fit por 1-fit
				fit = 1 - fit
			conjuntoFitness.append(fit)

		ajuste = sum(conjuntoFitness)/len(conjuntoFitness)	  # Hace una media del valor del ajuste para las
		                                                    # diferentes CIs
		for j in xrange(len(conjuntoFitness)):
			if conjuntoFitness[j] == max(conjuntoFitness):
				id_mejor = j
				break
		
		return ajuste,id_mejor

	@cronometro
	def algoritmoGenetico(self,tiempo):
		""" Llama al metodo 'cambiarEstado' para crear los diferentes estados para cada intervalo
		de tiempo en cada CI. Llama a la 'fitnessFun' para calcular el grado de ajuste de la regla
		que queramos ver en ese momento. Iteramos sobre cada regla para obtener un vector
		con la calidad de cada una, y posteriormente poder realizar la seleccion de las mejores
		y eliminar las demas, de forma que podamos realizar el 'crossover' de las distintas reglas,
		asegurandonos obtener en cada nueva generacion reglas mejores."""

		contador = []			   # Lista que almacena el numero de la regla que cumple la condicion para ser
									# seleccionada
		limRegla = self.noReglas/4
		newReglas = []
		self.bondad = []
		self.M_R = [[[None]*tiempo for s in xrange(len(self.setVectores))] \
				for k in xrange(self.noReglas)]  
		# Lista que contendra todos los estados para cada paso de tiempo para cada CI de cada regla.
		# El elemento M_R[r] es el conjunto de todos los pasos de tiempo para todas las CIs en la regla r-esima.
		self.id_mejor_CI = [] # lista que contendrá índice de la CI que mejor ajusta la regla r

		for r in xrange(self.noReglas):		 # Evaluamos la bondad de cada regla.
			self.M_R[r] = self.cambiarEstado(self.setReglas[r],self.time)
			salidaFitnessFun = self.fitnessFun(self.M_R[r])
			self.bondad.append(salidaFitnessFun[0])
			#self.bondad.append(self.fitnessFun(self.M_R[r]))
			self.id_mejor_CI.append(salidaFitnessFun[1])


		maxima = max(self.bondad)			# Mira cual es el maximo de la bondad de las reglas
		for r in xrange(self.noReglas):
			if self.bondad[r] == maxima:
				contador.append(r)
				break
		for r in xrange(self.noReglas):
			if self.bondad[r] < maxima and self.bondad[r] >= 0.8*maxima:
				contador.append(r)
			if len(contador) == limRegla:
				break
		while len(contador) < limRegla:
			for r in xrange(self.noReglas):
				if self.bondad[r] > 0.5*maxima and self.bondad[r] < 0.8*maxima:
					contador.append(r)
				if len(contador) == limRegla:
					break
		print contador #borrar luego
		for i in contador:
			newReglas.append(self.setReglas[i])	   # Añade las reglas 

		# Escribimos las reglas actuales en un fichero
		ruls = open('reglas.txt','w')
		out = csv.writer(ruls,delimiter = '\t')
		out.writerows(self.setReglas)
		ruls.close()

		"""Ahora hay que hacer el crossover de reglas"""
		for r in xrange(-1,limRegla-1):
			a = newReglas[r]
			b = newReglas[r+1]
			c = newReglas[r+2]
			
			aNew = a[:]
			bNew = b[:]
			cNew = c[:]

			aNew[42:84],aNew[84:] = c[42:84], b[84:]
			bNew[42:84],bNew[84:] = a[42:84], c[84:]
			cNew[42:84],cNew[84:] = b[42:84], a[84:]

			# Añade las nuevas reglas
			newReglas.append(aNew)
			newReglas.append(bNew)
			newReglas.append(cNew)

		# Probabilidad de mutacion
		for r in xrange(len(newReglas)):
			if rd.random() <= 0.05:
				pos_mut = int(rd.random()*127)
				print pos_mut
				if newReglas[r][pos_mut] ==1:
					newReglas[r][pos_mut] = 0
				else :
					newReglas[r][pos_mut] = 1

		# Escribimos las nuevas reglas
		n_ruls = open('new_reglas.txt','w')
		n_out = csv.writer(n_ruls,delimiter = '\t')
		n_out.writerows(newReglas)
		n_ruls.close()

def condIniciales(size=149,no_CIs=100):
	""" Creamos un conjunto de 100 configuraciones iniciales para cada celula. 
	Los estados posibles son 0 o 1, repartidos de forma aleatoria siguiendo una
	distribucion uniforme en el intervalo (0,1)"""

	setCIs = []					# Lista vacia que contendra el conjunto 
								# de las 100 configuraciones iniciales.
	for i in xrange(no_CIs):
		vectIni = [] 			# Lista que contendra la configuracion inicial i-esima.
		for j in xrange(size):
			if rd.random() > 0.5:
				vectIni.append(1)
			else:
				vectIni.append(0)

		setCIs.append(vectIni)
	C = open('setCI.txt','w')
	Cout = csv.writer(C,delimiter = '\t')
	Cout.writerows(setCIs)
	C.close()
	return setCIs

class AutomImagen:

	def __init__(self,Objeto=None):  # Objeto sera la clase automata con sus parametros iniciados.
		
		if Objeto == None:
			sys.exit()

		#self.Objeto = Objeto
		Objeto = Objeto
		self.nCI = len(Objeto.setVectores)
		time = Objeto.time
		Objeto.algoritmoGenetico(time)
		self.bondad = Objeto.bondad
		self.m_r = Objeto.M_R
		self.id_CI = Objeto.id_mejor_CI
		self.dibujAutom()

	@cronometro
	def dibujAutom(self):
		maximo = max(self.bondad)
		print maximo
		for r in xrange(len(self.m_r)):
			if self.bondad[r] == maximo:
				regla = r
				ID = self.id_CI[r]
				break
		#for i in xrange(self.nCI):
		c = (regla,ID)   # tupla que dara el numero de la regla y de la CI para guardar la imagen.
		matrizEstados = self.m_r[r][ID]
		pylab.matshow(matrizEstados,cmap='binary')
		pylab.title("$ Celdas $")
		pylab.ylabel("$Pasos\ de\ tiempo$")
		pylab.savefig("Regla%i_CI%i.eps" %c)
		# Aqui salvamos el automata seleccionado
		f = open('automata_R%i_CI%i.txt' %c,'w')
		fout = csv.writer(f,delimiter = '\t')
		fout.writerows(matrizEstados)
		f.close()

"""Esta parte del codigo sirve para que el programa se ejecute solo si el modulo
es llamado como programa y no al importarlo."""

if __name__ == '__main__':

	print "¿Tienes reglas que importar? ([y]/n):"
	respuesta = raw_input()

	if respuesta != 'n':
		#print "Escribe el nombre del archivo con la extension."
		#archivo = raw_input()
		archivo = 'new_reglas.txt'
		reglasImportadas = open(archivo,'r')
		setreglas = reglasImportadas.readlines()
		nreglas = len(setreglas)
		listaReglas = []
		for l in xrange(nreglas):
			regla = setreglas[l].split()
			for i in xrange(len(regla)):
				regla[i]=int(regla[i])
			listaReglas.append(regla)
		automata = Automata(initReglas = listaReglas)
#		print "¿Tienes CIs que importar? (y/[n])"
#		resp = raw_input()
#		if resp == 'y':
#			ini_file = 'setCI.txt'
#			fCI = open(ini_file,'r')
#			filas = fCI.readlines()
#			nfilas = len(filas)
#			CIs = []
#			for l in xrange(nfilas):
#				fila = filas[l].split()
#				for i in xrange(len(fila)):
#					fila[i]=int(fila[i])
#				CIs.append(fila)
#			automata = Automata(initReglas = listaReglas, initVector = CIs)
#		else:
#			automata = Automata(initReglas = listaReglas)
	else:
		automata = Automata()

	AutomImagen(automata)

