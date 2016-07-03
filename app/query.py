# DO NOT CONTINUE EDITING, BAD PRACTICE
# DEPRECATE THIS METHOD
# 1. Query if not cached
# 2. create Course objects
# 3. find prereqs, then create a fixture. 
# 4. The current fixture is not very efficient and frankly doesn't even work at all


def createCatalog():
	"""
	Returns list of all current courses and their attributes in WSE and KSAS undergrad

	"""
	catalog = []
	temp = []
	response = []

	if response[0]["Term_IDR"] != getNextTerm():
		getCurrentCatalog()
		createCatalog

	try:
		response = json.loads(open("response.json").read())
	except Exception, e:
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
	"""
	You need to remove queryToFile and createCatalog and instead integrate that with prereqs.py
	"""
	term = getNextTerm()
	catalog = createCatalog()
	if catalog!=-1:
		with open("cache/" + term.replace(" ","") + ".json", "wb") as f:
			try:
				f.write(json.dumps(catalog))
			except Exception:
				pass
		f.close()

queryToFile()