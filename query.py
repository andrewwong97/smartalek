import requests
import json
import os
from datetime import date


def getNextTerm():
	"""
	Usage: getNextTerm() - uses current date to find the next term.
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

def respToDict():
	"""
	Returns dict of all current courses and their web IDs in WSE and KSAS
	"""
	catalog = {}

	if "response.json" not in os.listdir(os.getcwd()):
		getCurrentCatalog()
		respToDict()
	else:
		response = json.loads(open("response.json").read())
		for i in response:
			if i["OfferingName"] not in catalog.keys() and \
			 i["Level"]=="Lower Level Undergraduate" or i["Level"]=="Upper Level Undergraduate":
				catalog[i["OfferingName"]] = i["SSS_SectionsID"]
		return catalog


def queryToFile():
	term = getNextTerm()
	catalog = respToDict()
	if catalog!=-1:
		with open(term.replace(" ","")+".txt", "wb") as f:
			try:
				for key in catalog:
					f.write(key + " " + catalog[key] + "\n")
			except Exception:
				pass
		f.close()

queryToFile()