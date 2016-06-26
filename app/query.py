import requests
import json
import os
from datetime import date


def getNextTerm():
	"""
	Usage: getNextTerm() - uses current date to find the next term.
	Dates are based on course selection periods.
	Currently does not support Intersession or Summer.

	Returns a string of current term
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
	Caches current term response.json course catalog
	"""
	catalog = []
	schools = ["Whiting School of Engineering", "Krieger School of Arts and Sciences"]
	api_key = "Y7YXSplpQcXOWoyB4Z61tki74wNqHu8S"

	for school in schools:
		r = requests.get("https://isis.jhu.edu/api/classes/" + school + \
			"/" + getNextTerm() + "?key=" + api_key)
		response = json.loads(r.content)
		for i in response:
			if i not in catalog:
				catalog.append(i)
	with open("response.json",'wb') as f:
		f.write(json.dumps(catalog))
	f.close()

def createCatalog():
	"""
	Returns list of all current courses and their attributes in WSE and KSAS undergrad
	"""
	catalog = []
	temp = []
	response = []

	try:
		response = json.loads(open("response.json").read())
	except Exception or response[0]["Term_IDR"] != getNextTerm():
		getCurrentCatalog()
		createCatalog()

	for i in response:
		if i["OfferingName"] not in temp and i["Level"]=="Lower Level Undergraduate" or i["Level"]=="Upper Level Undergraduate":
			catalog.append({
				"Number": i["OfferingName"],
				"ID": i["SSS_SectionsID"],
				"Title": i["Title"],
				"Location": i["Location"],
				"Credits": i["Credits"],
				"Level": i["Level"]
			})
			temp.append(i["OfferingName"])
	return catalog


def queryToFile():
	term = getNextTerm()
	catalog = createCatalog()
	if catalog!=-1:
		with open(term.replace(" ","")+".json", "wb") as f:
			try:
				f.write(json.dumps(catalog))
			except Exception:
				pass
		f.close()

queryToFile()