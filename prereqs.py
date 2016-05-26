import requests
import re
import timeit
import json

from bs4 import BeautifulSoup


def openIDFile(path):
	lines = open(str(path)).readlines()
	data = [i.split(" ") for i in lines]
	return data

def getCourseInfo(idNum):
	url = "https://isis.jhu.edu/classes/ClassDetails.aspx?id=" + idNum;
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	prereqElems = soup.find_all("a", class_= "linkPrereq_"+idNum)
	prereqs = [i.get_text()[:-3] for i in prereqElems]
	if len(prereqs)>0:
		return prereqs

def main():
	courses = {}
	for i in openIDFile('Fall2016.txt'):
		courses[i[0]] = i[1][:-1]
	prereqs = {}
	for key in courses:
		if key not in prereqs:
			prereqs[key] = getCourseInfo(courses[key])
			print prereqs[key]
	with open("prereqs.json", "wb") as f:
		f.write(json.dumps(prereqs))
	f.close()

start = timeit.default_timer()
main()
print "Runtime: " + str(timeit.default_timer()-start)[:4] + ' seconds'
