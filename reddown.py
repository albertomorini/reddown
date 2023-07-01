import os
import sys
import json
import hashlib
import requests
from PIL import Image
from bs4 import *
import datetime as dt


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
	f = open("./reddown.txt","a")
	f.write(dt.datetime.now()+"-"+scope+"-"+message)

####################################################################
### REDDIT INTERFACE

#download the image provided a link
# @subreddit is the name of the subreddit we need to create the file's name
# eg. macsetups--md5(file).jpg
def downloadImage(urlImage,postTitle,subPosted,authorOP):
	try:
		extensionFile = urlImage.rsplit(".",1)[1]
		if(extensionFile == "jpg" or extensionFile == "png" or extensionFile == "gif"):
			imageContent = requests.get(urlImage).content
			fileName = postTitle[:10] + "by ["+authorOP+"] on "+subPosted
			print(fileName)
			##check if we can download also the complementar of that (like subs if user mode or user if subs mode)

			#create the folder if doesn't exists
			if(not os.path.exists("./dwn/")):
			    os.mkdir("./dwn/")

			file = open("dwn/"+fileName+"."+extensionFile, "wb")
			file.write(imageContent) 
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
		downloadImage(str(dataBody.get("url_overridden_by_dest"), postTitle, subPosted, authorOP)


####################################################################
# PREFERENCES STUFF (CREATING/UPDATING DICT)


# convert the number into a type (hot/top/new etc)
# @mode is a integer between 1 and 3
# @return a string
def modeConverter(mode):
	association = {
		1: "hot",
		2: "top",
		3: "new"
	}
	return association[mode]


# create a dictionar
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
def processDict(dict):
	for i in dict.get("subreddit"): ##process the subs
		print("downloading: " + i)
		processPosts(REDDIT_URL_SUBS+i+"/"+dict.get("subreddit")[i]+".json")

	for i in dict.get("users"): ##process the users
		print("downloading: " + i)
		processPosts(REDDIT_URL_USRS+i+"/"+dict.get("users")[i]+".json")



## print the menu to user, so chose how to manage the preferences (storing/updating/volatile)
def menu():
	pick=int(input("1) create a preferences file \n2) update an preferences  \n3) to download without create a register\n > "))
	print("\n-----------------")
	if(pick==1): ## CREATING MODE
		nameFile=input("insert the name the preferences file: ") +".json"
		dictTmp=createUpdateDict(None)
		serializeJSON("./",nameFile,dictTmp) #save the preferences
		processDict(dictTmp) # process the dict
	elif(pick==2): ## UPDATING 
		nameFile=input("insert the name the preferences file: ") +".json"
		isValid=False
		while(not isValid and nameFile!="q"):
			if (os.path.exists("./"+nameFile)):
				prefLoaded = readJson("./"+nameFile)
				newPreferences = createUpdateDict(prefLoaded)
				serializeJSON("./",nameFile,newPreferences)
				print("Updated! \n\t ...Downloading...")
				processDict(newPreferences)
			else:
				writeLog("WARNING","preferences not found with name: "+nameFile)
				print("Preferences not found with name: "+nameFile)
	elif(pick==3): ## NO STORE
		processDict(createUpdateDict(None))


#start the program
def main():
	print("Welcome on reddown")
	if(len(sys.argv)>1): #path passed
		processDict(readJson(sys.argv[1])) #process the dict passed by parameter
	else:
		menu()
	
main()
