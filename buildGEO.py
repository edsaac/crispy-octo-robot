import csv, sys, os, shutil

##INPUT File
pathToCSVFile = str(sys.argv[2])

##OUTPUT File
pathToGEOFile = str(sys.argv[3])

def getCommaFile(fileName, row = -1, col= -1):
    #Read csv file
    while True:
        try: 
            rawPointFile = open(fileName)
            rawPointFile = list(csv.reader(rawPointFile))
            break
        except FileNotFoundError:
            print("CSV file could not be found")

    #Return a single row
    while row != -1 and col == -1:
        try:
            return rawPointFile[row]
        except IndexError:
            print("Row could not be found")

    #Return a single column
    while row == -1 and col != -1:
        try:
            colFile=[]
            for row in range(len(rawPointFile)):
                colFile.append(rawPointFile[row][col])
            return colFile
        except IndexError:
            print("Column could not be found")

    #Return a single value
    while row != -1 and col != -1:
        try:
            return rawPointFile[row][col]
        except IndexError:
            print("Item could not be found")
def getColumn(xID):
    try:
        header = getCommaFile(pathToCSVFile,row=0)
        return(header.index(xID))
    except ValueError:
        print("X column could not be found")
def resetFile(nameFile):
    with open(nameFile,"w") as outFile:
        outFile.write('P=0;\nL=0;\nLL=0;\nPS=0;\n\n')
        outFile.close()
def appendFile(appendy, nameFile = pathToGEOFile):
    with open(nameFile,"a") as outFile:
        for i in range(len(appendy)):
            outFile.write(str(appendy[i]))
        outFile.close()
def buildGEOPoints(X,Y,Z=[],I=[],R=[]):
    ligne=['']
    for item in range(len(X)):
        i1 = int(I[item])
        x1 = float(X[item])
        y1 = float(Y[item])
        z1 = float(Z[item])
        r1 = float(R[item])
        ligne.append("Point(P+" + str(i1) + ") = {" \
                 + str(x1) +\
             "," + str(y1) +\
             "," + str(z1) +\
             "," + str(r1) + "};" + '\n'
                 )
    #ligne.append("\n" + "P=" + str(len(X)) + ";\n")
    return ligne
def buildGEOLines(I,L1,L2):
    ligne=['']
    for item in range(len(I)):
        i1 = int(I[item])
        l1 = int(L1[item])
        l2 = int(L2[item])
        ligne.append("Line(L+" + str(i1) + ") = {P+" \
                    + str(l1) +\
             ", P+" + str(l2) + "};" + '\n'
                 )
    #ligne.append("\n" + "L=" + str(len(I)) + ";\n")
    return ligne
def addLastIndex(parameter, quantity = 0, recursive = False):
    if recursive == False:
        indicator = str(parameter) + " = " + str(quantity) + ";\n" 
        appendFile(indicator)
    else:
        indicator = str(parameter) + " = " + str(parameter) + " + " + str(quantity) + ";\n" 
        appendFile(indicator)
    return
def setColumn(column):
    result = []
    k = 0
    for i in range(len(column)):
        if column[i] not in result :
            result.append(column[i])
            k+=1
    return result

###############################################
xColumnID = "X_m"
yColumnID = "Y_m"
rColumnID = "R_m"
holeColID = "vertex_par"
lineColID = "DN"
paragraphSeparator = ['\n',"/**********************************/",'\n\n']
###############################################

execMode = str(sys.argv[1]).lower()

#Extract X coordinates
xCoord = getCommaFile(pathToCSVFile,col=getColumn(xColumnID))
xCoord.remove(xColumnID)

#Extract Y coordinates
yCoord = getCommaFile(pathToCSVFile,col=getColumn(yColumnID))
yCoord.remove(yColumnID)

#Extract Z coordinates #modificar?
zCoord = list(range(len(xCoord)))
for i in range(len(zCoord)):
    zCoord[i] = float(zCoord[i])*0
zCoord = list(zCoord)

#Create Index
iCoord = list(range(1,len(xCoord)+1))

#Extract Refinement values
rCoord = getCommaFile(pathToCSVFile,col=getColumn(rColumnID))
rCoord.remove(rColumnID)


########### EXECUTION CASES ###########
# Boundary Mode 

if execMode in ["b", "boundary"]:

    #Extract hole flager
    holeCol = getCommaFile(pathToCSVFile,col=getColumn(holeColID))
    holeCol.remove(holeColID)
    print(str(holeCol))

    #Initialize file
    resetFile(pathToGEOFile)
    
    #Get topology
    holeListID = list(set(holeCol))
    holeListID.sort()
    
    holeIndex = []
    for hole in holeListID :
        holeIndex.append(holeCol.index(hole))
    holeIndex.append(len(holeCol))

    print(str(holeIndex))
    print(str(holeListID))
    
    for hole in range(len(holeListID)) :
        start = holeIndex[hole]
        end   = holeIndex[hole+1]-1
        GEO_Points = buildGEOPoints( \
            xCoord[start:end],\
            yCoord[start:end],\
            zCoord[start:end],\
            iCoord[start:end],\
            rCoord[start:end]\
                )
        appendFile(GEO_Points)
        
        #Convert to GEO Lines
        LINES1 = list(iCoord[start:end])
        LINES2 = list((iCoord[start+1:end]))+[iCoord[start]]
        INDEXLINES = list(iCoord[start:end])

        GEO_Lines = buildGEOLines(INDEXLINES,LINES1,LINES2)
        appendFile(GEO_Lines)

        #Generate GEO Line Loop
        GEO_Loops = ["Line Loop (LL+" + \
            str(hole+1) + ") = {L+" + \
            str(min(INDEXLINES)) + " ... L+" +  \
            str(max(INDEXLINES)) + "};\n"\
                ]
        appendFile(GEO_Loops)
        appendFile(paragraphSeparator)

    #Generate GEO Plane Surface
    appendFile(paragraphSeparator)
    GEO_Surface = ["Plane Surface (PS+1) = {" + \
        str(min(iCoord)) + " ... " + \
        str(len(holeListID)) + "};\n"\
            ]
    appendFile(GEO_Surface)
    
    #Update index starts
    appendFile(paragraphSeparator)
    addLastIndex("P",str(max(iCoord)))
    addLastIndex("L",str(max(INDEXLINES)))
    addLastIndex("LL",str(hole))
    addLastIndex("PS",str(len(GEO_Surface)))
    appendFile(paragraphSeparator)

elif execMode in ["p", "pointsinsurface"]:
    #Convert to GEO Points   
    GEO_Points = buildGEOPoints(xCoord,yCoord,zCoord,iCoord,rCoord)
    appendFile(GEO_Points)

    #Add as points in Surface
    appendFile(paragraphSeparator)
    GEO_PointsInSurface = ["Point {P+1 ... P+" + str(max(iCoord)) +\
        "} In Surface { 1 } ;\n"]
    appendFile(GEO_PointsInSurface)
    
    #Update index starts
    appendFile(paragraphSeparator)
    addLastIndex("P",str(len(GEO_Points)),True)
    appendFile(paragraphSeparator)

elif execMode in ["l", "linesinsurface"]:
    
    #Extract line identifier
    lineCol = getCommaFile(pathToCSVFile,col=getColumn(lineColID))
    lineCol.remove(lineColID)
    print(str(lineCol))

    #Get topology
    lineListID = setColumn(lineCol)
    
    lineIndex = []
    for line in lineListID :
        lineIndex.append(lineCol.index(line))
    lineIndex.append(len(lineCol))

    print(str(lineIndex))
    print(str(lineListID))
    
    for line in range(len(lineListID)) :
        start = lineIndex[line]
        end   = lineIndex[line+1] #Inclusive range []
        GEO_Points = buildGEOPoints( \
            xCoord[start:end],\
            yCoord[start:end],\
            zCoord[start:end],\
            iCoord[start:end],\
            rCoord[start:end]\
                )
        appendFile(GEO_Points)
        
        #Convert to GEO Lines

        LINES1 = list(iCoord[start:end-1])
        LINES2 = list(iCoord[start+1:end])
        INDEXLINES = list(iCoord[start:end-1])

        GEO_Lines = buildGEOLines(INDEXLINES,LINES1,LINES2)
        appendFile(GEO_Lines)

        #Add as Lines in Surface
        appendFile(paragraphSeparator)
        GEO_LinesInSurface = ["Line {L+" + str(min(INDEXLINES)) + \
            " ... L+" + str(max(INDEXLINES)) +\
            "} In Surface { 1 } ;\n"]
        appendFile(GEO_LinesInSurface)
    
    #Update index starts
    appendFile(paragraphSeparator)
    addLastIndex("P",str(max(iCoord)),True)
    addLastIndex("L",str(max(INDEXLINES)),True)
    appendFile(paragraphSeparator)