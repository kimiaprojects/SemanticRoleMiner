#Goal : For each sentence args for a root are investigated


def findPreds(sentence):
    preds={}
    #print sentence
    #print senna.keys()
    counter=0
    for senKey,senVal in sentence.items():
        token=senVal.keys()
        cols=senVal.values()
	cols=cols[0]
        #print cols
        tok_keys=cols.keys()
        tok_tags=cols.values()
        for col, tag in cols.items():
            if tag[-1]=="V" :
               preds[counter]=[]
               preds[counter].append(token)
               preds[counter].append(str(col))
               counter+=1
    return preds
#-----------------------------------------------------------------

def findDomain(args):

    elements= args.values()
    #print elements
    domains={}
    for key,val in args.items():
        first=val[0][0]
        first=first.split("-")
        first=first[1]
        #print first
        last=val[-1][0]
        last=last.split("-")
        last=last[1]
        #print last
        domains[key]=[]
        domains[key].append(first)
        domains[key].append(last)
    return domains    
   
#------------------------------------------------------------------

def findArg(verb,targetDict,targetCol):
    
     tokenLabels={}
     Labels={}
    #---Testing function arguments Perfect working
     #print verb
     #print targetDict
     root=verb.split("-")
     index=root[1]
     root=root[0]
     

     #--Finding the target column for retreiving correct args
     targetColumn='Null'
     for element_id in targetDict[int(index)][str(verb)]:
         #print element_id
         #print targetDict[int(index)]["reported-17"][element_id]
         take=targetDict[int(index)][str(verb)][element_id]   
         if take[-1]=="V":
            #print element_id
            targetColumn=element_id
     

     #--having all args for all tokens  
     for item in targetDict.values():
         val=item.values()
         token=item.keys()
         #print token
	 val=val[0]
	 #print "bol"+str(targetColumn)
         
         arg=val[int(targetCol)]
	 if arg!="O":
	 	arg=arg.split("-")
         	arg=arg[1]
                myArg=arg+"-"+root
		#print myArg 
		if myArg in tokenLabels:
		   tokenLabels[myArg].append(token)
		else:
		   tokenLabels[myArg]=[]
		   tokenLabels[myArg].append(token) 
          
     #tokenLabels['Tanks']='A0'
     return tokenLabels

#-------------------------------------------------------------------------------------------

def findParts(targetTuple,AR,root):
    newAR=""
    #print "targettuple"+str(targetTuple)
    dep=targetTuple[0]
    part1=targetTuple[1]
    #print "dep"+str(dep)
    sw1=0
    sw2=0
    part2=targetTuple[2]
    #print part1, part2
    #print AR
    verbconnection=0
    for arg in AR:
       newAR=""
       
       for tup in AR[arg]:
          
           if tup[0]==part1[0] and str(tup[1])==part1[1]: #finding first match
               sw1=1 
               #print arg, arg[0]
               #print tup[0]
	       if arg[0]=="V":
                  verbconnection=1
                  #print "1"
                  #print "hi"
		  #newAR="V-"+str(root)
           elif tup[0]==part2[0] and str(tup[1])==part2[1]: #finding second match
               sw2=1
               #print  arg, arg[0]
               #print tup[0]
               if arg[0]=="V":
                  verbconnection=1
                  #print "1"
		  #newAR="V-"str(root)
           if sw1==1 and sw2==1:
	       break # good point to break out of loop as the first matching case is found

       if sw1==1 and sw2==1 : # means 2 parts are found
           #print arg, part1, part2       #             A1   ['debris', '11'] ['contamination', '17']
           #print dep, arg, part1 , part2 #  conj_and   A1   ['debris', '11'] ['contamination', '17']
           #print verbconnection  
	   if verbconnection==1: 
               newAR="Link-"+str(root)
           else :
               newAR=arg
           #print part1
	  
	   break
    return newAR
#-----------------------------------------------------------
def mixDepArg(ST,AR):
     mixDict={}
     counter=0
     temp=[]
     #print AR
     for val in ST.values():
       #print val
       dep=val.keys()
       dep=dep[0]
       tokens=val.values()
       tokens=tokens[0]
       part1=[]
       part1.append(tokens[0])
       part2=[]
       part2.append(tokens[1])
      # print dep,part1,part2
       for ar,val in AR.items():
           print val
           if part1 in val and part2 in val:
              d={}
              d[dep]=(part1,part2)
              #print d
              a={}
              a[ar]=d
              mixDict[counter]=a
              counter+=1
	   elif part1 in val: 
              print "hi" 
           
     if mixDict!="Null":
        return mixDict       


