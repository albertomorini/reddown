import os
import sys
import json
import hashlib
import requests
from PIL import Image
from bs4 import *
import datetime as dt
import wget




REDDIT_URL_SUBS="https://www.reddit.com/r/"
REDDIT_URL_USRS="https://www.reddit.com/u/"

####################################################################
#UTILITY

def serializeJSON(dir, filename, dataDictionary):
	with open(dir+"/"+filename,"w", encoding='utf-8') as fileToStore:
   		json.dump(dataDictionary, fileToStore, ensure_ascii=False)

def readJson(path):
	with open(path) as dataStored:
		return json.load(dataStored)

def doMD5(digest):
	return hashlib.md5(digest.encode()).hexdigest()


def writeLog(scope,message):
	f = open("./reddown_log.txt","a")
	f.write(str(dt.datetime.now())+"-"+scope+"-"+str(message)+"\n")

####################################################################
### REDDIT INTERFACE

def isExtensionSupported(ext):
	supported=["jpg","png","gif","gifv"]
	if ext in supported:
		return True
	else:
		return False



def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename

#download the image provided a link
# @subreddit is the name of the subreddit we need to create the file's name
# eg. macsetups--md5(file).jpg
def downloadImage(urlImage,postTitle,subPosted,authorOP):
	try:
		extension = urlImage.rsplit(".",1)[1]
		if(isExtensionSupported(extension)):
			if(extension=="gifv"):
				#download_file(urlImage)
				print(urlImage)
			else:
				mediaToDownload = requests.get(urlImage).content
			fileName = postTitle[:30] + " - by ["+authorOP+"] on "+subPosted
			print(fileName)

			#create the folder if doesn't exists
			if(not os.path.exists("./dwn/")):
			    os.mkdir("./dwn/")

			
			file = open("dwn/"+fileName+"."+extension, "wb")
			file.write(mediaToDownload) 
			file.close()
				


	except Exception as e:
		writeLog("ERROR",e)


## given an url of a subs/user, fetch the posts then retrieve the link of the photos and download them
def processPosts(url):
	x = requests.get(url, headers = {'User-agent': 'alby bot 1.1'}).json()
	posts = x.get("data").get("children")
	for i in posts:
		dataBody = i.get("data") #get the data of the body
		subPosted= str(dataBody.get("subreddit"))
		authorOP = dataBody.get("author_fullname")
		postTitle = dataBody.get("title")
		urlImage = str(dataBody.get("url_overridden_by_dest"))
		if(not url == None):
			downloadImage(urlImage, postTitle, subPosted, authorOP)


####################################################################
# PREFERENCES STUFF (CREATING/UPDATING DICT)


# return the type (hot/top/new) given the number in the preferences
def modeConverter(mode):
	association = {
		1: "hot",
		2: "top",
		3: "new"
	}
	return association[mode]


# create or update the preferences given via parameters 
# @prefDict {dict} -> if empty we're in creation mode
def createUpdateDict(prefDict):
	choice = int(input("0) cancel \n1) subreddit \n2) user\n > "))

	if(prefDict==None):
		prefDict = {"subreddit":{},"users":{}}
	while choice>0:
		name = input("Insert the name to add: \n>")
		mode = int(input("1)hot \n2)top\n3)new \n > "))
		if(choice==1): ## add a sub
			prefDict.get("subreddit")[name]=modeConverter(mode)
		elif(choice==2): ##add a user
			prefDict.get("users")[name]=modeConverter(mode)
		
		choice = int(input("0) start download \n1) add a subreddit \n2) add a user\n > "))

	return prefDict

####################################################################

# split into: processing subreddit and processing users
# @dict is the dictionary holding the list of subs/mode and users/mode
def processPref(dict):
	for i in dict.get("subreddit"): ##process the subs
		print("downloading: " + i)
		processPosts(REDDIT_URL_SUBS+i+"/"+dict.get("subreddit")[i]+".json")

	for i in dict.get("users"): ##process the users
		print("downloading: " + i)
		processPosts(REDDIT_URL_USRS+i+"/"+dict.get("users")[i]+".json")



## print the menu to user, so chose how to manage the preferences (storing/updating/volatile)
def menu():
	pick=int(input("1) load a preferences \n2) create a preferences file \n3) update an preferences  \n4) to download without create a register\n > "))
	print("\n-----------------")
	

	if(pick==1): ## CREATING MODE
		nameFile=input("insert the name the preferences file: ") +".json"
		processPref(readJson("./"+nameFile))
	if(pick==2): ## CREATING MODE
		nameFile=input("insert the name the preferences file: ") +".json"
		dictTmp=createUpdateDict(None)
		serializeJSON("./",nameFile,dictTmp) #save the preferences
		processPref(dictTmp) # process the dict
	elif(pick==3): ## UPDATING 
		nameFile=input("insert the name the preferences file: ") +".json"
		isValid=False
		while(not isValid and nameFile!="q"):
			if (os.path.exists("./"+nameFile)):
				prefLoaded = readJson("./"+nameFile)
				newPreferences = createUpdateDict(prefLoaded)
				serializeJSON("./",nameFile,newPreferences)
				print("Updated! \n\t ...Downloading...")
				processPref(newPreferences)
			else:
				writeLog("WARNING","preferences not found with name: "+nameFile)
				print("Preferences not found with name: "+nameFile)
	elif(pick==4): ## NO STORE
		processPref(createUpdateDict(None))


#start the program
def main():
	print("Welcome on reddown")
	if(len(sys.argv)>1): #path passed
		processPref(readJson(sys.argv[1])) #process the dict passed by parameter
	else:
		menu()
	
main()
