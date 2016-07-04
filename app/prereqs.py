import requests
import json
import os
import time
from datetime import date

from bs4 import BeautifulSoup

API_KEY = "Y7YXSplpQcXOWoyB4Z61tki74wNqHu8S"

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
	""" 
	Query the ISIS API for current term courses 
	:return 0 if already exists
	:return 1 if error
	:return 2 if successfully wrote new json file for current term courses
	"""
	try:
		open("coursedata/" + getNextTerm().replace(" ", "") + "_courses.json","rb")
		return 0
	except:
		pass

	try:
		catalog = []
		schools = ["Whiting School of Engineering", "Krieger School of Arts and Sciences"]

		for school in schools:
			r = requests.get("https://isis.jhu.edu/api/classes/" + school + \
				"/" + getNextTerm() + "?key=" + API_KEY)
			response = json.loads(r.content)
			for i in response:
				if i not in catalog:
					catalog.append(i)
		with open("coursedata/" + getNextTerm().replace(" ", "") + "_courses.json",'wb') as f:
			f.write(json.dumps(catalog))
		f.close()
		return 2
	except:
		return 1

def createCatalog(filename="coursedata/" + getNextTerm().replace(" ", "") + "_courses.json"):
	""" 
	Parse current response, put it in Course objects in a dictionary of course numbers 
	:param filename (default next term's courses)
	:return dict of course objects
	"""
	catalog = {}
	temp = []
	
	# Initialize for error catching block to work
	response = []	
	try:
		response = json.loads(open(filename).read())
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
	""" 
	Parses HTML webpage for prerequisites given SSS_SectionsID. To do:
	find a way to make it more accurate. 
	:param idNum, which is the ISIS database ID for each course
	:return list of prerequisites OfferingName
	"""
	url = "https://isis.jhu.edu/classes/ClassDetails.aspx?id=" + idNum;
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	prereqElems = soup.find_all("a", class_= "linkPrereq_"+idNum)
	prereqs = [i.get_text()[:-3] for i in prereqElems] # -3 because of [+] text
	if len(prereqs)>0:
		return prereqs
	return []

def searchForCourse(courseNum):
	""" Search for an occurence of course in master and gets its data """
	try:
		matches = []
		data = json.loads(open("coursedata/master.json","rb").read())
		for i in data:
			if i["OfferingName"] == courseNum:
				return i
				# matches.append(i)     ### this is 4000 times slower, but may be more accurate
		# return matches[-1]            ### possibly introduce an (if year > 2010) if needed.
	except Exception,e:
		print e
		return 1

def saveMaster():
	""" 
	Saves master course data from Spring 2009 to now
	:return 0 if success
	:return 1 if error, prints errors
	"""
	try:
		data = []
		coursenums = []
		schools = ["Whiting School of Engineering", "Krieger School of Arts and Sciences"]

		for s in schools:
			url = "https://isis.jhu.edu/api/classes/"
			url += s + "?key=" + API_KEY
			r = requests.get(url)
			response = json.loads(r.content)
			for i in response:
				if i["OfferingName"] not in coursenums:
					data.append(i)
					coursenums.append(i["OfferingName"])
					print i["OfferingName"]
		with open("coursedata/master.json","wb") as f:
			f.write(json.dumps(data))
		return 0
	except Exception, e:
		print "Error: ", e
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
	master_catalog = createCatalog("coursedata/master.json")
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
				new = searchForCourse(pre) 
				try:
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
				except:
					largest += 1
					catalog[pre] = Course({
						"Number": pre,
						"ID": "",
						"Title": "",
						"Location": "",
						"Credits": "",
						"Level": "",
						"Instructors": "",
						"Semester": "",
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


	with open("coursedata/fixture.json", "wb") as f:
		f.write(json.dumps(data))
	f.close()	

if __name__ == '__main__':
	start = time.time()
	writeFixture()
	print "Runtime: %f seconds" %(time.time()-start)
	
