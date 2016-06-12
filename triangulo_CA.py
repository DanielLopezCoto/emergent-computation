#!/usr/bin/python

# Copyright Carlos Mestre Gonzalez 2008

import sys
try:
  import Image
except:
  print "You need python-imaging package"
  sys.exit()
import cStringIO

class Automaton:
  vector = []
  def __init__(self,rulesInput,initSize=256,defaultState='0',initialVector=None):
    self.numberRule = rulesInput
    n = Denary2Binary(rulesInput)
    
    self.createRule((8-len(n))*'0' + n)

    if initialVector == None:
      self.defaultState = defaultState
      self.size = initSize
      self.vector = [self.defaultState]*self.size
    else:
      self.vector = initialVector
      self.size = len(initialVector)

  def createRule(self,binary):
     self.rules = {"000": binary[7],"001":binary[6],"010":binary[5],"011":binary[4],
                    "100":binary[3],"101":binary[2],"110":binary[1],"111":binary[0]}


  def changeState(self):
    nextStep = self.vector[:]
    for i in xrange(self.size-1):
      nextStep[i] = str(self.rules[self.vector[i-1]+self.vector[i]+self.vector[i+1]])

    # esta linea pone las condiciones de contorno para el ultimo elemento
    nextStep[-1] = str(self.rules[self.vector[-2]+self.vector[-1]+self.vector[0]])

    self.vector = nextStep 

def Denary2Binary(n):
  if n == 0: return ''
  return Denary2Binary(n>>1) + str(n % 2) 

class AutomatonImage:
  buffer = cStringIO.StringIO()
  
  width = 0
  height = 0

  def __init__(self,autoObj=None,iter=None):

    if autoObj != None and iter != None:
      self.name = "automata-rule%s.jpg" % autoObj.numberRule
      for i in xrange(iter):
       self.writeVector(autoObj.vector)
       autoObj.changeState()
      self.saveImage()
        
  def writeVector(self,vector):

    self.height = self.height + 1
    self.width = len(vector)
    for i in xrange(len(vector)):
      self.writePixel(vector[i])

  def writePixel(self,value):

    if value == '0':
      self.buffer.write('\xff\xff\xff')
    else:
      self.buffer.write('\x00\x00\x00')

  def saveImage(self):
    imagen = Image.fromstring("RGB",(self.width,self.height),self.buffer.getvalue())
    imagen.save(self.name,"JPEG")
  

if __name__ == "__main__":
  # Default size of the initial automata
  size = 500
  mVector = (' '.join('0'*size)).split()
  # The midle of the vector must be 1
  mVector[(size/2)+1]='1'

  if len(sys.argv) > 1:
    try:
      n = int(sys.argv[1])
    except:
      print "Second parameter must be an integer"
      sys.exit()
  else:
    n = raw_input("Rule number: ")
    try:
      n = int(n)
    except:
      print "Must be an integer"
      sys.exit()

  myAutom = Automaton(n,initialVector=mVector)
  AutomatonImage(myAutom,(size/2))

