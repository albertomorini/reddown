import os
import sys
import json
import requests
import datetime as dt

####################################################################
# CONSTANT
REDDIT_URL_SUBS="https://www.reddit.com/r/"
REDDIT_URL_USRS="https://www.reddit.com/u/"
ExtensionSupported=["jpg","png","gif","gifv","mp4"]

####################################################################
#UTILITY

def serializeJSON(dir, filename, dataDictionary):
	with open(dir+"/"+filename,"w", encoding='utf-8') as fileToStore:
   		json.dump(dataDictionary, fileToStore, ensure_ascii=False)

def readJson(path):
	with open(path) as dataStored:
		return json.load(dataStored)

def readJsonData(rawData):
	return json.load(rawData)

def writeLog(scope,message):
	f = open("./reddown_log.txt","a")
	f.write(str(dt.datetime.now())+"-"+scope+"-"+str(message)+"\n")

####################################################################
### REDDIT INTERFACE

## WORKAROUND FOR IMGUR GIFV
def processGifv(urlIMGUR):
	''' TODO: try with json content-type
	tmp = readJsonData(requests.get(urlIMGUR).json())
	tmp = readJsonData(tmp.get("reddit_video_preview"))
	print(tmp.get("fallback_url")+"\n\n\n")
	print("----")
	'''
	contentGifv = requests.get(urlIMGUR).content # the request return us the HTML page
	mp4url = str(str(contentGifv).split('meta property="og:video:secure_url"  content="')[1]).split('" />')[0] # retrieve the url of mp4 video
	return mp4url


#download the image provided a link
# @subreddit is the name of the subreddit we need to create the file's name
# eg. macsetups--md5(file).jpg
def downloadImage(mediaURL,postTitle,authorOP):
	extension = mediaURL.rsplit(".",1)[1]
	if(extension in ExtensionSupported):
		if(extension=="gifv"): # workaround for git
			mediaToDownload= requests.get(processGifv(mediaURL)).content
			extension="mp4" # we'll store a MP4
		else:
			mediaToDownload = requests.get(mediaURL).content
		
		fileName = postTitle[:40] + " - by [" + authorOP + "]"
	
		print(fileName)

		#create the folder if doesn't exists
		if(not os.path.exists("./dwn/")):
			os.mkdir("./dwn/")
		
		file = open("dwn/"+fileName+"."+extension, "wb")
		file.write(mediaToDownload) 
		file.close()
				


## given an url of a subs/user, fetch the posts then retrieve the link of the photos and download them
def processPosts(url):
	x = requests.get(url, headers = {'User-agent': 'alby bot 1.1'}).json()
	try:
		if(x.get("kind")=="Listing"):
			posts = x.get("data").get("children")

			for i in posts:
				dataBody = i.get("data") #get the data of the body
				print(dataBody)
				authorOP = dataBody.get("author_fullname").replace("/","-")
				postTitle = dataBody.get("title").replace("/","-")
				mediaURL = str(dataBody.get("url_overridden_by_dest"))
				if(not url == None):
					downloadImage(mediaURL, postTitle, authorOP)
	except Exception as e:
		writeLog("ERROR","user/subs probably doesn't exists "+url)



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
