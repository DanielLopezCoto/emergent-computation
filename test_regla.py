#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
Autor: Daniel Lopez Coto

Este programa testea la regla seleccionada sobre 10000 CIs
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

@cronometro
def condIniciales(size=149,no_CIs=8000):
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
	
	return setCIs


class Automata:
	
	def __init__(self,numeroReglas=1,initSize=149,tiempo=None,initVector=None,initReglas=None):
	
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
		
		if initReglas == None:			# Si no hay reglas inicialmente, salimos
			print "No hay reglas que testear."
			sys.exit()
		else:							# Si ya hemos introducido las reglas, las inicializamos.
			self.setReglas = tuple(initReglas)
		
		if initVector == None:			# Si no hay un vector con los valores iniciales,
										# lo creamos.
			self.setVectores = condIniciales(self.size)
		else:							# Si lo hay, lo inicializamos.
			self.setVectores = initVector
		
		self.M_R = self.cambiarEstado(self.setReglas,self.time)
		salidaFitnessFun = self.fitnessFun(self.M_R)
		self.bondad = salidaFitnessFun[0]
		self.id_mejor_CI = salidaFitnessFun[1]

	@cronometro
	def cambiarEstado(self,regla,tiempo):
		""" Este metodo recibe como entrada un entero que corresponde a la cantidad de
		pasos de tiempo que se van a evaluar los estados de las celulas para cada regla."""
	
		self.setEstados = self.setVectores   # Lista que contiene el conjunto de estados para la regla
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


	@cronometro
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

		mejor_ajuste = max(conjuntoFitness)		# Valor del mejor ajuste para la regla metida.
		media = sum(conjuntoFitness)/len(conjuntoFitness)
		for j in xrange(len(conjuntoFitness)):
			if conjuntoFitness[j] == mejor_ajuste:
				id_mejor = j
				break
		
		return media,id_mejor



class AutomImagen:

	def __init__(self,Objeto=None):  # Objeto sera la clase automata con sus parametros iniciados.
		
		if Objeto == None:
			sys.exit()

		#self.Objeto = Objeto
		Objeto = Objeto
		self.nCI = len(Objeto.setVectores)
		time = Objeto.time
		self.bondad = Objeto.bondad
		self.m_r = Objeto.M_R
		self.id_CI = Objeto.id_mejor_CI
		self.dibujAutom()

	@cronometro
	def dibujAutom(self):
		print self.bondad
		ID = self.id_CI
		for i in xrange(self.nCI/80):
			c = (ID)   # tupla que dara el numero de la regla y de la CI para guardar la imagen.
			matrizEstados = self.m_r[ID]
			pylab.matshow(matrizEstados,cmap='binary')
			pylab.title("$ Celdas $")
			pylab.ylabel("$Pasos\ de\ tiempo$")
			pylab.savefig("Test_Regla_CI%i.eps" %c)
			pylab.close()
			# Aqui salvamos el automata seleccionado
			f = open('automata_CI %i.txt' %c,'w')
			fout = csv.writer(f,delimiter = '\t')
			fout.writerows(matrizEstados)
			f.close()

"""Esta parte del codigo sirve para que el programa se ejecute solo si el modulo
es llamado como programa y no al importarlo."""

if __name__ == '__main__':

	#print "¿Tienes reglas que importar? ([y]/n):"
	#respuesta = raw_input()

	#if respuesta != 'n':
		#print "Escribe el nombre del archivo con la extension."
		#archivo = raw_input()
	archivo = 'mejor_regla.txt'
	reglasImportadas = open(archivo,'r')
	setreglas = reglasImportadas.readlines()
	nreglas = len(setreglas)
	listaReglas = []
	regla = setreglas[0].split()
	for i in xrange(len(regla)):
		regla[i]=int(regla[i])

	automata = Automata(initReglas = regla)
#	else:
#		automata = Automata()

	AutomImagen(automata)
