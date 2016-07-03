import requests
import json
import os
import time
from datetime import date

from bs4 import BeautifulSoup

API_KEY = "Y7YXSplpQcXOWoyB4Z61tki74wNqHu8S"

# Getting current data, adding it to database
# take some code from query.py
# 1. Query if not cached
# 2. create Course objects
# 3. find prereqs, then create a fixture. 
# 4. The current fixture is not very efficient and frankly doesn't even work at all

# Basically instead of creating intermediate files, 
# create fixture by reading the response all in one go

class Course():
	def __init__(self, data):
		self.Number = data["Number"][:10]
		self.ID = data["ID"][:6]
		self.Title = data["Title"]
		self.Location = data["Location"]
		try:
			self.Credits = float(data["Credits"])
		except:
			self.Credits = 0.0
		self.Level = data["Level"]
		try:
			self.Instructors = data["Instructors"].split(",")
		except:
			self.Instructors = [data["Instructors"]]
		self.Prerequisites = []
		self.Semester = data["Semester"]
		self.pk = data["pk"]

def getNextTerm():
	"""
	Usage: getNextTerm() - uses current date to find the next term.
	Dates are based on course selection periods.
	Currently does not support Intersession or Summer.

	:return a string of current term (e.g. Fall 2016)
	"""
	currentMonth = int(date.today().strftime("%m"))
	currentYear = date.today().strftime("%Y")[0:4]
	nextYear = str(int(currentYear)+1)

	if currentMonth >= 3 and currentMonth < 11:
		# [3,10]
		return "Fall " + currentYear
	elif (currentMonth >= 11 and currentMonth < 13) or currentMonth < 3:
		# [11,12] and [1,2]
		return "Spring " + nextYear

def getCurrentCatalog():
	""" Query the ISIS API for current term courses """
	catalog = []
	schools = ["Whiting School of Engineering", "Krieger School of Arts and Sciences"]

	for school in schools:
		r = requests.get("https://isis.jhu.edu/api/classes/" + school + \
			"/" + getNextTerm() + "?key=" + API_KEY)
		response = json.loads(r.content)
		for i in response:
			if i not in catalog:
				catalog.append(i)
	with open("cache/" + getNextTerm().replace(" ", "") + "_courses.json",'wb') as f:
		f.write(json.dumps(catalog))
	f.close()

def createCatalog():
	""" 
	Parse current response, put it in Course objects in a dictionary of course numbers 
	:return dict of course objects
	"""
	catalog = {}
	temp = []
	
	# Initialize for error catching block to work
	response = []	
	try:
		response = json.loads(open("cache/" + getNextTerm().replace(" ", "") + "_courses.json").read())
	except Exception, e:
		getCurrentCatalog()
		createCatalog()

	# Make sure the response is current
	if response[0]["Term"] != getNextTerm():
		getCurrentCatalog()
		createCatalog()

	index = 0
	for i in response:
		if i["OfferingName"] not in temp and i["Level"]=="Lower Level Undergraduate" or i["Level"]=="Upper Level Undergraduate":
			catalog[i["OfferingName"]] = Course({
				"Number": i["OfferingName"],
				"ID": i["SSS_SectionsID"],
				"Title": i["Title"],
				"Location": i["Location"],
				"Credits": i["Credits"],
				"Level": i["Level"],
				"Instructors": i["Instructors"],
				"Semester": i["Term"],
				"pk": index
			})
			temp.append(i["OfferingName"]) # list of courses that are already added
			index += 1
	return catalog


def getPrereqs(idNum):
	url = "https://isis.jhu.edu/classes/ClassDetails.aspx?id=" + idNum;
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	prereqElems = soup.find_all("a", class_= "linkPrereq_"+idNum)
	prereqs = [i.get_text()[:-3] for i in prereqElems] # -3 because of [+] text
	if len(prereqs)>0:
		return prereqs
	return []

def searchForCourse(courseNum):
	""" Search for latest occurence of course and gets its data """
	return 1
	return "Fixes need to be done"
	try:
		courseNum = courseNum.replace(".","")
		courseNum = requests.utils.quote(courseNum)
		url = 'https://isis.jhu.edu/api/classes/' + courseNum + '/' + '?key='

		r = requests.get(url + API_KEY)
		data = json.loads(r.content)
		latest = data[-1]
		return latest
	except:
		return 1

def writeFixture():
	""" 
	Writes initial course data for Django 

	To do: fix request speed by saving all course data from Spring 2009 into a repsonse file different from 
	Fall2016_courses.json

	Then, look for this course number in that data (much, much faster than sending each request to ISIS server)
	There's probably a better way to do this search, but we'll deal with that later.


	"""
	data = []
	catalog = createCatalog()
	largest = 0

	for key in catalog:
		if catalog[key].pk > largest:
			largest = catalog[key].pk

	for key in catalog.keys():
		catalog[key].Prerequisites = getPrereqs(catalog[key].ID) 
		pks = []
		for pre in catalog[key].Prerequisites: 
			if pre in catalog:
				pks.append(catalog[pre].pk)
			else:
				new = searchForCourse(pre) # This request is taking too long. See solution at method docs top
				if new != 1:
					largest += 1
					catalog[pre] = Course({
						"Number": new["OfferingName"],
						"ID": new["SSS_SectionsID"],
						"Title": new["Title"],
						"Location": new["Location"],
						"Credits": new["Credits"],
						"Level": new["Level"],
						"Instructors": new["Instructors"],
						"Semester": new["Term"],
						"pk": largest
					})
					pks.append(largest)
				else:
					largest += 1
					catalog[pre] = Course({
						"Number": pre,
						"ID": "None",
						"Title": "None",
						"Location": "None",
						"Credits": "None",
						"Level": "None",
						"Instructors": "None",
						"Semester": "None",
						"Prerequisites": [],
						"pk": largest
					})
					pks.append(largest)
		catalog[key].Prerequisites = pks
		print key, catalog[key].Prerequisites


	for key in catalog:
		data.append({
			"model": "app.Course",
			"pk": catalog[key].pk,
			"fields": {
				"number": catalog[key].Number,
				"ID": catalog[key].ID,
				"title": catalog[key].Title,
				"instructors": catalog[key].Instructors,
				"location": catalog[key].Location,
				"credits": catalog[key].Credits,
				"level": catalog[key].Level,
				"semester":  catalog[key].Semester,
			}
		})


	with open("cache/fixture.json", "wb") as f:
		f.write(json.dumps(data))
	f.close()	

if __name__ == '__main__':
	start = time.time()
	writeFixture()
	print "Runtime: %f seconds" %(time.time()-start)
	
