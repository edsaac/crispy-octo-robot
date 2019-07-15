
#######################################################################
##Modify the file paths:

####INPUTS   ---
BOUNDARY="./Boundary/Boundary.shp"	        #Boundary SHP Polygon
SIZESMAP="./ElementSize/ElementSizesMap.shp"    #ElementSizes SHP Polygons
HARDLINE="./HardLines/Lines.shp"		#Hardlines SHP Lines
HARDPOIN="./HardPoints/PointsinDomain.shp"	#Hartpoints SHP Points

####PYTHON SCRIPTS ---
PYSCRIPT="./PY_SCRIPTS"				#Location of scripts

####OUTPUTS  ---
OUTFILE="./MyProject"				#Your Project Name

#######################################################################


#TempFiles ---
BOUND="./.Tboun.csv"
POINT="./.Tpoin.csv"
LINES="./.Tline.csv"

#Boundary SHP >> Boundary XY CSV #
$PYSCRIPT/SHP2GEO.py -i $BOUNDARY $SIZESMAP $BOUND

#Points in Surface SHP >> Points in Surface XY CSV #
$PYSCRIPT/SHP2GEO.py -v $HARDPOIN $POINT

#Points in Surface SHP >> Points in Surface XY CSV #
$PYSCRIPT/SHP2GEO.py -l $HARDLINE $LINES

# Boundary XY CSV >> Boundary GEO #
$PYSCRIPT/buildGEO.py -b $BOUND $OUTFILE.geo

# Points in Surface XY CSV >> Points in Surface GEO #
$PYSCRIPT/buildGEO.py -p $POINT $OUTFILE.geo

# Points in Surface XY CSV >> Lines in Surface GEO #
$PYSCRIPT/buildGEO.py -l $LINES $OUTFILE.geo

#Mesh generation with GMSH
~/Apps/gmsh-3.0.6/bin/gmsh -2 $OUTFILE.geo

#GMSH Mesh to T3S
$PYSCRIPT/MSH2T3S.py $OUTFILE.msh $OUTFILE.t3s

#######################################################################
rm -r ./.T*
