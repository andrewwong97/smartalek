import requests
import timeit
import json

from bs4 import BeautifulSoup
from query import getNextTerm

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
	return []

def getDetails(idNum,attribute):
	f = open("cache/response.json").read()
	data = json.loads(f)
	for i in data:
		if i["SSS_SectionsID"] == idNum:
			return i[attribute]

def write(data):
	with open("cache/fixture.json", "wb") as f:
		f.write(json.dumps(data))
	f.close()	

def makeFixture():
	rawData = openQuery('cache/Fall2016.json')
	data = []
	allNumbers = {} # EN.600.120: 012, Number: pk

	index = 0
	largest = 0
	for i in rawData:
		number = rawData[index]["Number"]
		ID = rawData[index]["ID"]
		prereqs = getPrereqs(ID)
		prereqs = [i[:10] for i in prereqs]

		# Cleaning up some data
		for i in range(len(prereqs)):
			if len(prereqs[i]) != 10:
				try:
					dept = int(prereqs[i][0:3])
				except:
					dept = "None"
				if dept < 500: 
					prereqs[i] = "AS." + prereqs[i] 
				elif dept >= 500:
					prereqs[i] = "EN." + prereqs[i]
				elif dept == "None":
					prereqs.remove(prereqs[i])

		title = rawData[index]["Title"]
		instructors = getDetails(ID,"Instructors")
		if isinstance(instructors,list):
			instructors = instructors.split(",")
		else:
			instructors = [instructors]
		location = rawData[index]["Location"]
		try:
			credits = float(rawData[index]["Credits"])
		except:
			credits = 0
		level = rawData[index]["Level"]

		if number not in allNumbers:
			data.append({
				"model": "app.Course",
				"pk": index,
				"fields": {
					"number": number,
					"ID": ID,
					"prerequisites": prereqs, # replace with pk
					"title": title,
					"instructors": instructors,
					"location": location,
					"credits": credits,
					"level": level,
					"semester": getNextTerm()
				}
			})
			allNumbers[number] = index
			print number, prereqs
		index+=1
		largest = index

	for i in range(0,len(data)-1):
		prereq_pks = []

		for pre in data[i]["fields"]["prerequisites"]:
			if pre in allNumbers:
				prereq_pks.append(allNumbers[pre])
			else: # append empty prereq
				largest+=1
				data.append({
				"model": "app.Course",
				"pk": largest,
				"fields": {
					"number": pre, # next step: search jhu database for the data that corresponds to this course number
					"semester": getNextTerm()
					}
				})
				prereq_pks.append(largest)
				allNumbers[pre] = largest
		data[i]["fields"]["prerequisites"] = prereq_pks
		print "Primary Keys:", data[i]["fields"]["prerequisites"]
	write(data)

if __name__ == '__main__':
	start = timeit.default_timer()
	makeFixture()
	print "Runtime: " + str(timeit.default_timer()-start)[:4] + ' seconds'
