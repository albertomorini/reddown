import os
import sys
import json
import hashlib
import requests
from PIL import Image
from bs4 import *


REDDIT_URL_SUBS="https://www.reddit.com/r/"
REDDIT_URL_USRS="https://www.reddit.com/u/"
####################################################################
#UTILITY

def serializeJSON(dir, filename, dataDictionary):
	with open(dir+"/"+filename,"a", encoding='utf-8') as fileToStore:
   		json.dump(dataDictionary, fileToStore, ensure_ascii=False)

def readJson(path):
	with open(path) as dataStored:
		return json.load(dataStored)

def doMD5(digest):
	return hashlib.md5(digest.encode()).hexdigest()


####################################################################
### REDDIT INTERFACE

#download the image provided a link
# @subreddit is the name of the subreddit we need to create the file's name
# eg. macsetups--md5(file).jpg
def downloadImage(link,subreddit):
	try:
		##TODO: optimize, check the content type and the encoding of data request
		extensionFile = link.rsplit(".",1)[1]
		if(extensionFile == "jpg" or extensionFile == "png" or extensionFile == "gif"):
			response = requests.get(link)
			fileName = subreddit+"--"+doMD5(link)
			print(fileName)
			##check if we can download also the complementar of that (like subs if user mode or user if subs mode)

			#create the folder if doesn't exists
			if(not os.path.exists("./dwn/")):
			    os.mkdir("./dwn/")

			file = open("dwn/"+fileName+"."+extensionFile, "wb")
			file.write(response.content) 
			file.close()

	except Exception as e:
		f = open("logs.txt","a")
		f.write("ERROR: "+e)
		f.close()
		pass


## given an url of a subs/user, fetch the posts then retrieve the link of the photos and download them
def processPosts(url):
	x = requests.get(url, headers = {'User-agent': 'alby bot 1.1'}).json()
	posts = x.get("data").get("children")
	for i in posts:
		subreddit= str(i.get("data").get("subreddit"))
		downloadImage(i.get("data").get("url_overridden_by_dest"), subreddit)


####################################################################
# add a subs to the dict
def addSub(target,mode,dictPref):
	dictPref["sub"][target]=mode
	return dictPref
#add a user to the dict
def addUser(target,mode,dictPref):
	dictPref["users"][target]=mode
	return dictPref

# convert the number into a type (hot/top/new etc)
# @mode is a integer between 1 and 3
# @return a string
def modeConverter(mode):
	res = None
	if(mode==1):
		res = "hot"
	elif(mode==2):
		res ="top"
	elif(mode==3):
		res = "new"
	return res


# create a dictionar
def createDict():
	target = int(input("1)subreddit \n2)reddit user\n > "))

	dictTargets = {"subreddit":{},"users":{}}
	choice = 1
	while int(choice)>0:
		if(target==1):
			tmpInsert= input("Add a subreddit: (eg. 'macstups')\n>")
			mode = int(input("1)hot \n2)top\n3)new \n > "))
			mode = modeConverter(mode)
			dictTargets.get("subreddit")[tmpInsert]=mode
			choice = input("To start downloading press 0\nTo add another subreddit press 1\nTo add user press 2\n > ")
			if(int(choice)==2):
				target=2
		else:
			tmpInsert= input("Add an user: (just the nickname)\n>")
			mode = int(input("1)hot \n2)top\n3)new \n > "))
			mode = modeConverter(mode)
			dictTargets.get("users")[tmpInsert]=mode
			choice = input("To start downloading press 0\nTo add another user press 1\nTo add a subreddit press 2\n > ")
			if(int(choice)==2):
				target=1

	return dictTargets

####################################################################

# split into: processing subreddit and processing users
# @dict is the dictionary holding the list of subs/mode and users/mode
def processDict(dict):
	for i in dict.get("subreddit"):
		print("downloading: " + i)
		processPosts(REDDIT_URL_SUBS+i+"/"+dict.get("subreddit")[i]+".json")

	for i in dict.get("users"):
		print("downloading: " + i)
		processPosts(REDDIT_URL_USRS+i+"/"+dict.get("subreddit")[i]+".json")



#start the program
def menu():
	pick=int(input("1) to load/create a preferences \n2) to download without create preferences file\n > "))
	
	if(pick==1):
		nameFile=input("insert the name of the preferences file : ") +".json"

		isValid=False
		while(not isValid and nameFile!="q"):
			if (os.path.exists("./"+nameFile)):
				loadJSON = readJson("./"+nameFile+".json")
				if(loadJSON!=None):
					print("loaded preferences.. processing!")
					processDict(loadJSON)
				else:
					print("Error.. switching to creating mode: ")
					dictTmp=createDict()
					serializeJSON("./",nameFile+".json",dictTmp)
					processDict(dictTmp)
			else:
				print("invalid path...\n retry (or insert q to quit)")
				nameFile=input("insert the name of the preferences file : ") +".json"

	elif(pick==2):
		processDict(createDict())


menu()
