from subprocess import call
for line in open("requirements.txt", "r"): 
	line=line.strip()
	if ( line and not line[0]=="#" ): 
		call([ "pip", "install", line] )
