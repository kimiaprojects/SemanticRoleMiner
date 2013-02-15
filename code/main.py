import sys
import os
from StanSennaClass import SenSta
from sennaProcessed import modifySenna
from stanfProcessed import modifyStanf
from code import verbRelatives,roleFinder,translateSent,verbLinks,scanVerb,allTokens,gephiTranslate
import re
from FindPropArg import Find_Pred_Arg_Root,Find_ArgDom_MixArgDep
#------------------------------------------------------------------------------------------------------------------------------------
######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
#------------------------------------------------------------------------------------------------------------------------------------
#-- 1- starting point: a processed sentence is taken from stanford parser, this sentence is in natural form. the same happens for senna.
#-- 2- by using senna file I collect all tokens marked as VB in one list "VBNS"
#-- 3- all dependencies along with the name-of-relation , token1 and token2 are then collected from stanford file in "Preps".
#-- 4-  
#-- 5- for each verb in VBNs all tokens are collected in a vlist, the sentence is then recreated from the original sentence by scanVerb function, and is sent #      to translateSent to build statements. 



if __name__=="__main__":

	#1
	sentence=open("/home/kimia/srl/python/SemanticRoleMiner/code/input/test_input.txt","r")	

	sent=sentence.readline()
	sentence.close()

	OrgSent=sent
	#handling 's

	inputFile="srl/python/SemanticRoleMiner/code/input"
	myTestFile=SenSta(inputFile)
	myTestFile.makeStanf()	
	stanfile="/home/kimia/srl/python/SemanticRoleMiner/code/input"+"/stanoutput.txt"
	Stan=modifyStanf(stanfile)

	# Fixing 's, using poss dependecy
	Poss=[]
	for key,val in Stan.items():
	    for i, prep in val.items():
		pred=prep.keys()[0]
		rel=prep.values()[0]
		token1=rel[0]
		token2=rel[1]
		if pred=="poss":
			Poss.append((str(token2.split("-")[0])+str(token1.split("-")[0]),str(token2.split("-")[0]),str(token1.split("-")[0])))
			#print "***********Posessins: ",Poss
			sent=sent.replace(str(token2.split("-")[0])+"'s "+str(token1.split("-")[0]),str(token2.split("-")[0])+str(token1.split("-")[0]))
	#print sent



	#find and replace Captial Names attached
	pattern1=r"\s\s" # removing extra spaces
	pattern2=r"(\"|\'|\s\s|\_)"
	pattern3=r"([A-Z]\w+\s)" # Captial Names

	match=re.findall(pattern2,sent) #symbols
	for item in match:
		toks=item.split(" ")
		newtok=" "
		sent=sent.replace(item,newtok)
	#print "symbls removed : ",sent

	match=re.findall(pattern3,sent) #capitals
	
	match=match[0:-1]   # the last token in pattern usually captures a low letter name 
	templist=sent.split(" ")
	print templist
	if len(match)>1:
		for item in match:
			toks=item.split(" ")
			check=templist.index(toks[0])+1
			#print templist[check], templist[check][0].isupper()
			if templist[check][0].isupper(): 
				print "()()()()",toks
				newtok=''.join(toks)
				sent=sent.replace(item,newtok)
			
	



	#print sent
	sentence=open("/home/kimia/srl/python/SemanticRoleMiner/code/input/test_input.txt","w")	
	sentence.write(sent)
	sentence.close()

	inputFile="srl/python/SemanticRoleMiner/code/input"
	myTestFile=SenSta(inputFile)
	myTestFile.makeSenna()
	myTestFile.makeStanf()
	sennafile="/home/kimia/srl/python/SemanticRoleMiner/code/input"+"/sennaoutput.txt"
	
	stanfile="/home/kimia/srl/python/SemanticRoleMiner/code/input"+"/stanoutput.txt"
	
	

	#2
	Senna=modifySenna(sennafile)
	#print Senna['sen0']
	
	VBNs=[]
	for sen,val in Senna.items():
		for num,token in val.items():
			for a,b in token.items():
				if b[1][0:2]=="VB":
					VBNs.append(a)

	#print VBNs
	#3
	Stan=modifyStanf(stanfile)
	Preps={}
	for key,val in Stan.items():
	    for i, prep in val.items():
		pred=prep.keys()[0]
		rel=prep.values()[0]
		token1=rel[0]
		token2=rel[1]
		if token1 in VBNs:
		   Preps[token1]=(pred,token2)
		elif token2 in VBNs:
		   Preps[token2]=(pred,token1)
	
	#4
	vals=Stan.values()[0]
	temp=vals.values() 
	#print "*" 
	allDeps=[] 
	for v in temp:
		a=(v.values()[0][0],v.values()[0][1])
		if a not in allDeps:
			#print a
			allDeps.append(a)

	#print "allDeps ", allDeps

	#5
	sen=[]
	#print VBNs
	output=open("/home/kimia/srl/python/SemanticRoleMiner/code/input/results.txt",'w')
	output.write("-Complete Sentence is: \n"+OrgSent+"\n")
	output.write("----------------------------------------------------------------------\n")
	output.write("----------------------------------------------------------------------\n")
	
	SennaStan=open("/home/kimia/srl/python/SemanticRoleMiner/code/input/Stan_Senna_results.txt",'w')





	sentNumber=0
	AllSTs={}
	gephiFile=open("/home/kimia/srl/python/SemanticRoleMiner/code/input/gephi.dot","w")
	for vbn in VBNs:
		#vbn="isolated-18"
		#print"to be :  "

		vlist=verbLinks(vbn,allDeps,VBNs)
		#print "to be vlist:",vlist
		#print "vlist: ",vlist

		if len(vlist)>1:
		#	print vlist
			STs=[]
			result=scanVerb(sent,vlist)
			print "result: ",result # here is the new sentece, segmented from the original one.
			#-- writing each sentence along with their triples in results.txt
			output.write(str(sentNumber)+"-"+result+"\n\n")
			SennaStan.write(str(sentNumber)+"-"+result+"\n\n")
			sen.append(result)
			STs=translateSent(vlist,result,Poss)
			for st in STs: output.write("      "+str(st[0])+"  "+str(st[1])+"  "+str(st[2])+"\n")
			
			output.write("          --------------------------------------------------          \n")

			#-- writing each sentence stanford output in Stan_Senna_results.txt
			stanfile=open("/home/kimia/srl/python/SemanticRoleMiner/code/stanoutput.txt","r")
			text=stanfile.read()
			stanfile.close()
			SennaStan.write("-Stanford Output: ----------------------------------------------------\n")
			SennaStan.write(text)
			#-- writing each sentence ssenna output in Stan_Senna_results.txt
			sennafile=open("/home/kimia/srl/python/SemanticRoleMiner/code/sennaoutput.txt","r")
			text=sennafile.read()
			sennafile.close()
			SennaStan.write("--Senna Output:------------------------------------------------------ \n")
			SennaStan.write(text)
			SennaStan.write("----------------------------------------------------------------------\n")
			AllSTs[sentNumber]=STs
			sentNumber+=1
			gephiTranslate(STs,gephiFile)
			#print "Statements:",STs
	
	SennaStan.close()
	output.close()
	gephiFile.close()
	
	#---fixing input file for this process has modified it
	sentence=open("/home/kimia/srl/python/SemanticRoleMiner/code/input/test_input.txt","w")	
	sentence.write(OrgSent)
	sentence.close()

