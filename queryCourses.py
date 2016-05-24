import requests
import json
from datetime import date


def getCurrentTerm():
	"""
	Usage: getCurrentTerm() - uses current date to find the next term.
	Currently does not support Intersession or Summer.

	Returns a string of current term
	"""
	currentMonth = int(date.today().strftime("%m"))
	currentYear = date.today().strftime("%Y")[0:4]
	nextYear = str(int(currentYear)+1)

	if currentMonth >= 1 and currentMonth < 9:
		return "Fall " + currentYear
	elif currentMonth >= 9 and currentMonth < 13:
		return "Spring " + nextYear

def queryCourses(currentTerm):
	"""
	Returns list of all current courses web IDs in WSE and KSAS
	"""
	schools = ["Whiting School of Engineering", "Krieger School of Arts and Sciences"]
	api_key = "Y7YXSplpQcXOWoyB4Z61tki74wNqHu8S"

	catalog = []
	for school in schools:
		r = requests.get("https://isis.jhu.edu/api/classes/" + school + \
			"/" + currentTerm + "?key=" + api_key)
		data = json.loads(r.content)
		for i in data:
			if i["SSS_SectionsID"] not in catalog:
				catalog.append(i["SSS_SectionsID"])
	return catalog

def queryToList():
	catalog = queryCourses(getCurrentTerm())
	return catalog

def queryToFile():
	catalog = queryCourses(getCurrentTerm())
	with open("out.txt", "wb") as f:
		for i in catalog:
			f.write(i + "\n")
			print i
	f.close()