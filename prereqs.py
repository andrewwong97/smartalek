import requests
import re
import timeit
import json

from bs4 import BeautifulSoup


def openQuery(path):
	f = open(path).read()
	data = json.loads(f)
	return data

def getPrereqs(idNum):
	url = "https://isis.jhu.edu/classes/ClassDetails.aspx?id=" + idNum;
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	prereqElems = soup.find_all("a", class_= "linkPrereq_"+idNum)
	prereqs = [i.get_text()[:-3] for i in prereqElems] # -3 because of [+] text
	if len(prereqs)>0:
		return prereqs

def getDetails(idNum,attribute):
	f = open("response.json").read()
	data = json.loads(f)
	for i in data:
		if i["SSS_SectionsID"] == idNum:
			return i[attribute]

def write(data):
	with open("fixture.json", "wb") as f:
		f.write(json.dumps(data))
	f.close()

def makeFixture():

	rawData = openQuery('Fall2016.json')
	data = []

	index = 0
	for i in rawData:
		number = rawData[index]["Number"]
		ID = rawData[index]["ID"]
		prereqs = getPrereqs(ID)
		title = rawData[index]["Title"]
		instructors = getDetails(ID,"Instructors")
		if isinstance(instructors,list):
			instructors = instructors.split(",")
		else:
			instructors = [instructors]
		location = rawData[index]["Location"]
		credits = rawData[index]["Credits"]
		level = rawData[index]["Level"]
		data.append({
			"model": "app.Course",
			"pk": ID,
			"fields": {
				"Number": number,
				"ID": ID,
				"Prereqs": prereqs,
				"Title": title,
				"Instructors": instructors,
				"Location": location,
				"Credits": credits,
				"Level": level
			}
		})
		print number, prereqs
		index+=1
	write(data)
	
start = timeit.default_timer()
makeFixture()
print "Runtime: " + str(timeit.default_timer()-start)[:4] + ' seconds'
