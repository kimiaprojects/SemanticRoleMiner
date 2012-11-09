

#triples_file=open("~/srl")
def s_P_o(token2,rel,token1):
    
    print str(token2)+rel+str(token1)



def mainArg(token,mixedArgs):
    elements=mixedArgs.values()
    for temp in elements:
        if len(temp)!=0:
	   arg=temp.keys()[0]
           value=temp.values()
	   value=value[0]
           #print value 
           value=value.values()
           #print value[0][0]
           if token in value[0] and arg!="V":
              print (token,"is",arg)
              break
           
           #if part1==token or part2==token:
              #print token, arg
    print "----"



#-- Check if verb is negate or not
def checkNegate(verb,mixedArgs):
     elements = mixedArgs.values()
     neg=""
     #print elements
     #print "---"
     for temp in elements:
        if len(temp)!=0 and temp.keys()[0]=="V":
          value=temp.values()
          #print value[0].keys()
          if value[0].keys()[0]=="neg":
              neg="not"
              break
    # print arg
     return neg
     #print "----------------"

#-- Find direct Object for a given verb. these types of verbs usually have nsubj
def findObj(verb,mixedArgs):
    obj=[]
    elements= mixedArgs.values()
    for temp in elements:
        if len(temp)!=0 :
	   value=temp.values()
           value=value[0]           
           rel=value.keys()
           #print rel
           value=value.values()
           if verb in value[0] and rel[0]=="dobj":
              obj.append(value[0][1])
              
    return obj          

#-- Find hidden relations 

def inRel(token,mixedArgs):
    sbj=[]
    sbj.append(token)
    elements=mixedArgs.values()
    #find prep
    for temp in elements:
        #print temp
        if len(temp)!=0:
           value=temp.values()
           arg= temp.keys()
           arg=arg[0]
           value=value[0]
	   #print arg
           rel=value.keys()
           val=value.values()
           val=val[0]
           rel=rel[0]
           rel=rel.split("_")
	   #print rel[0]
	   #print val[0]
           if rel[0]=='prep' and val[0]==token:
              sbj.append(rel[1])
              sbj.append(val[1])
           

    return sbj


#-- I first extracted arg, rel, token1 and token2

def makeRel(mixedArgs):
    for elements in mixedArgs.values():
      #print elements #returns a dict
      negate=" " # this is my negate switch to recog verb 
      arg=elements.keys()
      #print arg
      if len(arg)!=0:
         arg=arg[0]
         #print "arg:"+str(arg)
         elements=elements[arg] # returns a list of dependency rel
         #print rel
         rel=elements.keys()
         rel=rel[0]
         #print rel   #relation retirieved
         elements=elements[rel] #a tuple of 2 tokens
         token1=elements[0]
         token2=elements[1]
         print token1 #each token along with their location
         print token2 
 
         if arg=="Link":
		#-- token1 is verb ; hence should be checked if it's negative or positive
		negate= checkNegate(token1,mixedArgs)
		if rel=="nsubjpass": #this relation makes token2 as main nsubject 
                       # sbj=inRel(token2,)    
		 	s_P_o(token2,"is"+negate,token1)
			#mainArg(token2,mixedArgs)
                elif rel=="nsubj":  #this relation takes verb as the name of relation and I need to search for object of the verb
                        obj=findObj(token1,mixedArgs)
                        for item in obj:
			   s_P_o(token2,str(negate)+str(token1),item)
                           mainArg(item,mixedArgs)
                        mainArg(token2,mixedArgs)
                        
         elif rel=="nn" or rel=="amod":
                s_P_o(token1,"is",token2)


#------------
# making St0-verb
def makeSt0(verb,Args):
    Arg0Found=0
    Arg1Found=0
    for item in Args:
        if item[0:2]=="A0":
           Arg0Found=1
        elif item[0:2]=="A1":
           Arg1Found=1
    if Arg0Found==1 and Arg1Found==1:
        St="A0-"+str(verb)+" "+str(verb)+" "+"A1-"+str(verb)
    elif Arg0Found==0 and Arg1Found==1:
        St="Null"+" "+str(verb)+" "+"A1-"+str(verb)
    elif Arg0Found==1 and Arg1Found==0:
        St="A0-"+str(verb)+" "+str(verb)+" "+"Null"
    else :
        St="NotFound"
    return St



   

def makeSt(target,verb,Args,ArgsDomain):
   dom=""
   dep=""
   #print str(target)+"-"+verb.split("-")[0], ArgsDomain.keys()
   for key,val in ArgsDomain.items():
       if (str(target)+"-"+verb.split("-")[0]) in key:
          dom=val
   if dom!="":
       #print dom[0],dom[1]            
       Args=Args.values()
       for item in Args:
          key=item.keys()[0]
          if key.split("-")[0]=="Link":
            #print item[key]
            k=item.values()
            k=k[0]
            dep=k.keys()[0]
            token1=k.values()[0][0][0]
            token2=k.values()[0][1][0]
            if token2==verb:
              if int(token1.split("-")[-1])>=int(dom[0]) and int(token1.split("-")[-1])<=int(dom[1]):
		 #print token1,dep
                 break
            else:
              #print token2,token2.split("-")[-1]
              if int(token2.split("-")[-1])>=int(dom[0]) and int(token2.split("-")[-1])<=int(dom[1]):
		 #print token2, dep
                 break

       return str(dep)+" "+str(target)+"-"+verb


