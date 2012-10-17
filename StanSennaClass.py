#for using terminal , calling senna and stanford parser
import os
from sennaProcessed import modifySenna
from stanfProcessed import modifyStanf

class SenSta:

   inputFile="Null"
   sennaOutFile="/home/kimia/srl/python/SemanticRoleMiner/test/senna"
   stanOutFile ="/home/kimia/srl/python/SemanticRoleMiner/test/stan"
   sennaDict={}
   stanfDict={}
   def __init__(self,arg):
	self.inputFile=arg


   def makeSenna(self):
        #running senna to generate sennaoutput 
        cmd=os.system('cd /home/kimia/srl/senna \n ./senna <'+self.inputFile+'> '+self.sennaOutFile+'output1.txt')
        self.sennaDict=modifySenna(self.sennaOutFile+'output1.txt')
        return self.sennaDict 

   def makeStanf(self):
        cmd=os.system('cd /home/kimia/srl/stanford-parser/ \n ./lexparser.sh '+self.inputFile+' >'+self.stanOutFile+'output1.txt')
        self.stanfDict=modifyStanf(self.stanOutFile+'output1.txt')
        return self.stanfDict


