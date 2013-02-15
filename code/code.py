import sys
from StanSennaClass import SenSta
import os
from nltk.corpus import propbank
from sennaProcessed import modifySenna
from stanfProcessed import modifyStanf
import en #for converting verbs into present tense
from stemming.porter2 import stem # for removing ing,ial ,...
from en import numeral
import re
from Visualizer import makeGephi
#------------------------------------------------------------------------------------------------------------------------------------
######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
#------------------------------------------------------------------------------------------------------------------------------------
#--- Finding all the tokens directly connected to verb, input is all tokens and Stanford parser output which cotains dependecies. output is rellist conatining all related tokens to verb.
#------------------------------------------------------------------
def verbRelatives(vlist,Stan):
	rellist=[]
	verb=vlist[0]
	#print "Stan",Stan
	#print "verb to rel : ",verb
	for item in Stan:
		tok1=item.values()[0][0]
		tok2=item.values()[0][1]
		#print "tok1-tok2 in rellist ",tok1,tok2
		if tok1.split("-")[0:-1][0]==verb.split("-")[0:-1][0] and tok2!= 'ROOT-0':
			
			rellist.append(tok2)
		elif tok2.split("-")[0:-1][0]==verb.split("-")[0:-1][0] and tok1!='ROOT-0':
			rellist.append(tok1)
	#print rellist
	return rellist
#------------------------------------------------------------------------------------------------------------------------------------
######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
#------------------------------------------------------------------------------------------------------------------------------------
#---- rolFinder gets the verb , makes it present tense using en library, and then by using propBank library finds all roles of the verb version.01. because senna doesn't provide the version of the verb ! I am assuming one 01 at the end of each verb. Output returns a dictionary of {"A0":"", "A1":""...}
#------------------------------------------------------------------
def roleFinder(verb):
	#--converting verb into its present tense
	print "verb**",verb
	targetverb=en.verb.present(verb)
	print "targetverb **** ",targetverb	
	propVerb=targetverb+".01"
	print propVerb
	allroles={}
	roles=propbank.roleset(propVerb)
	for role in roles.findall('roles/role'):
		role.attrib['descr']=role.attrib['descr'].replace(" ","-")
		allroles["A"+str(role.attrib['n'])]=role.attrib['descr']

	return allroles
#------------------------------------------------------------------------------------------------------------------------------------
######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
#------------------------------------------------------------------------------------------------------------------------------------

#----------------------------------------
#--- translating list of word connected to verb into triples, "vlist" is a list of all tokens in the "result" sentence , in this list the first item is always the verb of the sentence.  
#----------------------------------------
def translateSent(vlist,result,Poss):
	STs=[]


	#--- Stanford Translations Dictionary
	dictionary={"abbrev":"sameAs","acomp":"is","advmod":"moreDetail","agent":"by","amod":"is","appos":"sameAs","attr":"","csubjpass":"moreDetail","dobj":"object","iobj":"to","neg":"not", "nn":"--","nsubj":"subject", "nsubjpass":"subject","num":"number", "number":"currency","partmod":"moreDetail", "poss":"possession", "prep_on":"on","prep_in":"in","prep_by":"by","prep_since":"since", "prep_with":"with", "prep_at":"at","prep_after":"after","prep_for":"for","prep_of":"of","prep_to":"to","prep_from":"from" , "quantmode":"quantity", "tmod":"time"}

	#print "to check nmubers: ",vlist #vlist has all tokens involved with their location attached to them

	#--- SenSta class accepts a sentence written in a file format, so for every sentence being sent to translateSent() in "result" argument , the sentence is first saved into a file with base directory mentioned in "inputFile"
	
	#-- 1- writing the sentence in file.
	stanfile=open("/home/kimia/srl/python/SemanticRoleMiner/code/test_input.txt","w")
	stanfile.write(result)
	stanfile.close()


	sbj={}
	obj=[]
	i=0


	#-- 2- the first verb in vlist is the targetverb which is splited from its location of the main text. verb is set to default value of "not found".
	targetverb=vlist[0].split("-")[0:-1][0]

	
	verb="not found"

	#-- 3- processing stanford-parser and senna on the textfile, the results are store into 2 dictionaries , Stan and Senn
        inputFile="srl/python/SemanticRoleMiner/code"
	myTestFile=SenSta(inputFile)
	myTestFile.makeSenna()
	myTestFile.makeStanf()
	Stan= myTestFile.stanfDict['sen0'].values()
	Senn= myTestFile.sennaDict['sen0'].values()
	print "Senn: ",Senn
	thissent=[]
	thissent=result.split(" ")
	#-- 3.5 finding matches for date-pattern to merge all numbers into just 1 object connected to the target verb
	# sentence is in result string, so i have to find the domain of tokens. I can add the location of any tokens involved into this pattern in 1 list
	months={'January':01,'Jan':"01",'February':"02","Feb":"02","March":"03","Mar":"03","April":"04","Apr":"04","May":"05","June":06,"Jun":"06","July":"07","Jul":07,"August":"08","Aug":"08","September":"09","Sep":"09","October":"10","Oct":"10","November":"11","Nov":11,"December":"12","Dec":"12"}

	#datePatternDomain=[]
	dateObjects={}
	datepattern1=r"(\d{1,2}\s\w+\s\d{1,4})"
	match=re.findall(datepattern1,result)
	for item in match: # generalizing dates
		toks=str(item).split(" ")
		if toks[1] in months.keys():
			#print"+++++++", item #toks[0],toks[1],toks[2]
  			newTok=str(toks[0])+"/"+months[toks[1]]+"/"+str(toks[2])
			
			dateObjects[newTok]=(toks[0]+"-"+str(thissent.index(toks[0])+1),toks[1]+"-"+str(thissent.index(toks[1])+1),toks[2]+"-"+str(thissent.index(toks[2])+1))
	print "dates detected in sentence: ", dateObjects


	#--4  Senna Translation-----------------------------
	#--   4-1 Find roles , calling roleFinder with targetverb, example : targetverb="conducted-2" , allRoles={"A0":"conductor", "A1":".."..}
	allRoles={}	
	allRoles=roleFinder(targetverb) 

	#--  4-2 Finding relatives of a verb, all directly connected tokens are gathered in verbRel.
	verbRel=[]
	#print "**vlist ",vlist
	verbRel=verbRelatives(vlist,Stan)
	#print "*verbRel ",verbRel

	#-- 4-3 Discovering the arg labels senna has assigned to the tokens, all Args are gathered in roleDep example:[('testing-2', 'A1'), ('laboratories-8', 'A0'),...]
	roleDep=[]
	for item in Senn:#NER
		values=item.values()[0].values() #NER
		#print "values of senna:",values
		if values[2]!="O" and (values[2].split("-")[0]=="B" or values[2].split("-")[0]=="S"):
			tok1=item.keys()[0]
			tok2=values[2].split("-")[1:][0]
			print "**2222"
			print tok1," is ",tok2
			STs.append((str(tok1.split("-")[0])," is ",str(tok2.split("-")[0])))
		if item.keys()[0] in verbRel:
			if values[4]!='O': # ARG
				val1=item.keys()[0]
				val2=values[4].split("-")[-1]
				roleDep.append((val1,val2))
				
	#-- 4-4 Translating Args into rolesets, if the Arg is not in allRole list , it's printed itself. 
	for item in roleDep:
		token=item[0]
		role=item[1]
		number=token.split("-")[-1]

		if role in allRoles.keys():
	
			print "*ref*"
			if len(allRoles[role].split(","))>1:	#sometimes we have more than 1 role , I take the first one
				temp=allRoles[role].split(",")[0]	
				print token," is ",temp
				STs.append((str(token.split("-")[0])," is ",temp))

			else:
				print token," is ",allRoles[role]
				STs.append((str(token.split("-")[0]),"is",allRoles[role]))
		else:

			print "*555*"
			print token," is ",role
			STs.append((str(token.split("-")[0]),"is",role))



	#-- 5- Stan Translation-----------------------------------
	
	#-- 5-1 Stan list has all dependencies with the single-verb sentence. in this loop I'm finding the root of these depndenies as "verb" for further loops. 
	for item in Stan:
		#print item
		if item.keys()[0]=='root':
			verb=item.values()[0][1]
			print "verb as root:",verb
			break
			
	#print "**********",targetverb,verb
	#-- 5-2 in some cases there are no verb in sentence , this loop prints statements containing verb and the verb is the root.
	print "verbs: ",targetverb,verb.split("-")[0]
	if verb !="notfound" and targetverb==verb.split("-")[0]:
		for triple in Stan:
			pred=triple.keys()[0]
			tok1=triple.values()[0][0]
			tok2=triple.values()[0][1]
			number2=tok2.split("-")[-1]
			number1=tok1.split("-")[-1]

			#-- 5-2-1 finding the quivalent predicate from dictionary of stanford dependecnies.
			#--       also nsbj,nsujpass are gathered in sbj[] to make verb-dependencies with 
			#	  other tokens directly connected to the verb in obj[]. 
			if pred in dictionary.keys():
				if dictionary[pred]=="subject":	
					sbj[i]=(tok2,tok1)

				elif tok1==verb or tok2==verb:#collecting objects
					#print "tok1,tok2 : ",tok1,"---",tok2
					if tok1==verb:
						obj.append([pred,tok2])
					elif tok2==verb: 
						obj.append([pred,tok1]) 
				else:	

					print "**2222"
					print tok1," ",dictionary[pred]," ",tok2
					STs.append((str(tok1.split("-")[0]),dictionary[pred],str(tok2.split("-")[0])))
	

		#-- 5-2-2 printing statments withe predicate --verb-- among subjects and other objects directly connected to verb. 
		#--       the location of each token is mentioned but for the verb it's omitted.  
		for subject in sbj.values():
			for objects in obj:
				pred=dictionary[objects[0]]
				damnVerb=subject[1].split("-")[0]
				
				if str(pred)!="is-Arg1":

					tok1=subject[0]
					tok2=objects[1]

					print "**"
					print tok1," ",damnVerb+"-"+str(pred)," ",tok2
					STs.append((str(tok1.split("-")[0]),damnVerb+"-"+str(pred),str(tok2.split("-")[0])))
				else:
					tok1=subject[0]

					tok2=objects[1]

					print "*nbnbn5*"
					print tok1," ",damnVerb," ",tok2
					STs.append((str(tok1.split("-")[0]),damnVerb,str(tok2.split("-")[0])))

	#-- 5-2-3 some sentences in stanford doesn't detect a verb as root. 
	# 	  this is the loop for including relations in sentences without a verb-root
	else:
		for triple in Stan:
			pred=triple.keys()[0]
			tok1=triple.values()[0][0]
			tok2=triple.values()[0][1]
			#print pred,tok1,tok2
			if pred in dictionary.keys():
				pred=triple.keys()[0]			
				tok1=triple.values()[0][0]		
				tok2=triple.values()[0][1]
	
				print "*kklkhgh*"
				print tok1," ",dictionary[pred]," ",tok2
				STs.append((str(tok1.split("-")[0]),dictionary[pred],str(tok2.split("-")[0])))
	#print "to numerate: ",result
	sentlist=result.split(" ")
	#print sentlist
	#i=0
	newSTs=[]
	num1=0
	num2=0
	if len(Poss)>0:
		for item in STs:
			#print"&*&", item
			sw=0
			i=0
			if item[0] in sentlist: 
				num1=sentlist.index(item[0])+1
			
			if item[2] in sentlist: 
				num2=sentlist.index(item[2])+1
			
			#print num1,item[0],num2,item[2]
			#print len(Poss)
			for poss in Poss: #filling newSTs
				i+=1
				#print "--Pss",poss
				possID=poss[0]
				temp1=poss[1] #john
				temp2=poss[2] #brother
			
				if item[0]==possID and sw==0: # brother -- shopping
					#print "rmoved ",item," appended ",(temp2,item[1],item[2])
					#STs.remove(item)
					num3=sentlist.index(possID)+1
					tup=(temp2+"-"+str(num3),"of",temp1)
					token=item[2]
					if num2>0:				
						token=str(item[2])+"-"+str(num2)
					newSTs.append((temp2+"-"+str(num3),item[1],token))
					sw=1
					if tup not in newSTs:
							newSTs.append(tup)
				elif item[2]==possID and sw==0:
					#print "removed",item," appended ",(item[0],item[1],temp2)
					#STs.remove(item)
					token=item[0]
					if num1>0:				
						token=str(item[0])+"-"+str(num1)
					newSTs.append((token,item[1],temp2+"-"+str(num3)))
					num3=sentlist.index(possID)+1
					sw=1	
					tup=(temp2+"-"+str(num3),"of",temp1)
					if tup not in newSTs:
							newSTs.append(tup)	
				elif item[0]!=possID and item[2]!=possID and sw==0 and i==len(Poss):

					if item not in newSTs: 
						#print "not removed ",item
						t1=item[0]
						t2=item[2]
						if num1>0:
							t1=item[0]+"-"+str(num1)
						if num2>0:
							t2=item[2]+"-"+str(num2)
						newSTs.append((t1,item[1],t2))
			
				
	
	num1=0
	num2=0
	if len(newSTs)==0: #STs doesn't have numbers and this condition is when Poss is empty and newSTs is empty
		for item in STs:
			#print"&*&", item
			sw=0
			i=0
			if item[0] in sentlist: num1=sentlist.index(item[0])+1
			
			if item[2] in sentlist: num2=sentlist.index(item[2])+1

			if num2>0 and num1==0:	newSTs.append((str(item[0]),item[1],str(item[2])+"-"+str(num2)))		
			elif num1>0 and num2==0:newSTs.append((str(item[0])+"-"+str(num1),item[1],str(item[2])))			
			elif num1==0 and num2==0: newSTs.append((str(item[0]),item[1],str(item[2])))
			elif num1>0 and num2>0: newSTs.append((str(item[0])+"-"+str(num1),item[1],str(item[2])+"-"+str(num2)))
					
			
	#fixing Dates: dateObjects
	print "------------------------------------------------"
	remlist=[]
	print dateObjects
	if len(dateObjects)>0:
		length=len(newSTs)
		for i in range(0,length): # for not counting newly added tuples
			item=newSTs[i]
			tok1=item[0]
			pred=item[1]
			tok2=item[2]
			#i=newSTs.index(item)
			print item
			sw=0
			for date,vals in dateObjects.items():
				if (tok1==vals[0] or tok1==vals[1] or tok1==vals[2]) and ( tok2==vals[0] or tok2==vals[1] or tok2==vals[2]): # I don't want to include this tuple
					remlist.append(item)
				else:
					if tok1==vals[0] or tok1==vals[1] or tok1==vals[2] : 
						print "to remove:",item, " to append: ",(date,pred,tok2)
						if (date,pred,tok2) not in newSTs: newSTs.append((date,pred,tok2))
						remlist.append(item)
					elif tok2==vals[0] or tok2==vals[1] or tok2==vals[2]:
						print "to remove:",item, " to append: ",(tok1,pred,date)
						if (tok1,pred,date) not in newSTs : newSTs.append((tok1,pred,date))
						remlist.append(item)
		remlist=list(set(remlist))
		print "remlist: ",remlist
		print "before: ",newSTs
		for item in remlist:
			#print item
			newSTs.remove(item)
		newSTs=list(set(newSTs))	
		print "After: ",newSTs
	 
	return newSTs
#------------------------------------------------------------------------------------------------------------------------------------
######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
#------------------------------------------------------------------------------------------------------------------------------------
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%555%%%%%%%%%%%%%%%%%%%
def allTokens(argList,allDeps,VBNs,sent):
	tempList=argList.values()
	allToks=[]
	#print "*****************", VBNs
	print tempList
	verb=tempList[0].keys()[0].split("-")[-1]
	print "verb:", verb
	for item in tempList:
		arg=item.keys()[0]
		verb= arg.split("-")[-1]
		val=item.values()[0]
		#print val
		dep=val.keys()[0]
		toks=val.values()[0]
		tok1=toks[0][0]
		tok2=toks[1][0]
		# fixing verbLinks aurg issue
		pos=int(tok1.split("-")[-1])+2 # calculating the position for conj
		temp=str(dep.split("_")[-1]+"-"+str(pos))
		if dep=="conj_and" or dep=="conj_or" and temp not in allToks: 
			#print "pos",pos, dep.split("_")[-1]
			allToks.append(temp)
		#print "***loop1:",tok1.split("-")[0:-1][0]
		if tok1.split("-")[0:-1][0]==verb : 
			verb= toks[0][0]
			#print "****loop1: ", verb
			if tok1 not in allToks:
				allToks.append(tok1)
			if tok2 not in allToks and tok2 not in VBNs:
				allToks.append(tok2)
		#print "***loop2:",tok2.split("-")[0:-1][0]
		if tok2.split("-")[0:-1][0]==verb : 
			verb= toks[1][0]
			#print "***loop2: ",verb
			if tok2 not in allToks:
				allToks.append(tok2)
			if tok1 not in allToks and tok1 not in VBNs:
				allToks.append(tok1)
		if tok1.split("-")[0:-1] !=verb and tok2.split("-")[0:-1] !=verb:
			if tok1 not in VBNs and tok1 not in allToks:
				allToks.append(tok1)
			if tok2 not in VBNs and tok2 not in allToks:
				allToks.append(tok2)
		#-----------------------------
		
		
	#print allToks
	VLIST=verbLinks(verb,allDeps,VBNs) # all tokens connected to verb along with their continues dependencies till reaching a verb
	#print "again vlist: ",VLIST
	twoLists=list(set(allToks+VLIST))
	#print "both Lists :", twoLists #now two lists are merged
	#sts=[]
	if len(twoLists)>1:
		print twoLists
		result=scanVerb(sent,twoLists)
		print result

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#----------------------------------------
def verbLinks(vbn,deplist,VBNs):
	vlist=[]
	vlist.append(vbn)
	for item in vlist:
		#print "from vlist : ",item
		for dep in deplist:
			#print "checking dep: ",dep
			if item in dep:
				tok1=dep[0]
				tok2=dep[1]
				if (tok1 in VBNs and tok1!=vbn) or (tok2 in VBNs and tok2 !=vbn):
					skip=1
				else:
					tok1=dep[0]
					tok2=dep[1]
					if tok1 in vlist and tok2 not in vlist:
						vlist.append(tok2)
					elif tok2 in vlist and tok1 not in vlist:
						vlist.append(tok1)
	return vlist
#-----------------------------------------
#recreating the sentence from a list of related words to a verb from the original sentenc.
#
#
def scanVerb(sen,vlist):
	banlist=['by','from','and','in',',','of','with','on','at','under','to','after',"or","beyond","and"]
	doublewords=["becasue","instead","such","addition","due","all","rather","well"]
	doublewordlist=[["becasue","of"],["instead","of"], ["such","as"], ["due","to"],["all","but"],["rather","than"]  ]
	triplewords=["addition","well"]
	triplewordslist=[["in","addition","to"],["as","well","as"]]
	sen=sen.replace(","," , ") # should give the same sentence to stanford
	sen=sen.replace(".","")
	sen=sen.replace("  "," ")
	senlist= list(sen.split(" "))
	senlist = [word.strip() for word in senlist] #removing \n from the last toke of the sentence
	#print "senlist : ",senlist
	newsenlist=[]
	newsen=""
	#print vlist
	for i in range(0,len(senlist)):
		#print item,senlist.index(item)+1
		item=senlist[i]
		if item[-2:-1]=="\n": item=item.replace("\n","")
		index=i
		item=item+"-"+str(index+1)
		newsenlist.append(item)
	#print "newsenlist: ",newsenlist
	print "sentence list: ", newsenlist #now i have the whole sentence in form of a list , indexing words
	for item in newsenlist: 
		index=newsenlist.index(item)
		if item in vlist:
			#print item.split("-")[0]
			newsen+=str(item.split("-")[0])+" "
		elif item.split("-")[0] in banlist:
			if (index>0 and index<len(newsenlist)): #checking if preposition is between 2 related words
				if( newsenlist[index-1] in vlist and newsenlist[index+1] in vlist): 
					#print "1 ",item.split("-")[0]
					newsen+=str(item.split("-")[0])+" "
			if (index==0 or index==len(newsenlist)): #checking if preposition is before related words in the beginning or in the end
				if( newsenlist[index-1] in vlist or newsenlist[index+1] in vlist): 
					#print "2 ",item.split("-")[0]
					newsen+=str(item.split("-")[0])+" "

				
	return newsen+" ."

#-----------------------------------------

def gephiTranslate(Statements,gephiFile):
	#print Statements
	gephiFile.write("digraph sample {\n")
	#for key,val in Statements.items():
	#	#print val
	for item in Statements:
		node1=item[0]
		edge=item[1]
		node2=item[2]	
		print node1,edge,node2
		gephiFile.write("\""+node1+"\""+" -> "+"\""+node2+"\" "+"[ label = \""+str(edge)+"\" ];\n") 
  	gephiFile.write("}\n")

