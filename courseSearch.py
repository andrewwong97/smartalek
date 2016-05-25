import requests
import re
import timeit

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup


def openIDFile(path):
	lines = open(str(path)).readlines()
	data = [i.split(" ") for i in lines]
	return data

def getCourseID(classNumber):
	"""
	Uses a webdriver to retrieve the HTML source of a course, which parse with BeautifulSoup
	Well, this is pretty useless, since the API queries for it anyways. Oh well, learned something.
	I guess it's pretty fast now...
	"""
	driver = webdriver.PhantomJS()
	driver.get("https://isis.jhu.edu/classes/")
	driver.find_element_by_id('ctl00_content_ucSchoolList_rptSchools_ctl03_cbSchool').click() # KSAS
	driver.find_element_by_id('ctl00_content_ucSchoolList_rptSchools_ctl11_cbSchool').click() # WSE
	driver.find_element_by_id('ctl00_content_txtCourseNumber').send_keys(classNumber) # Class Number Box
	semesters = Select(driver.find_element_by_id('ctl00_content_lbTerms'))
	semesters.deselect_all()
	semesters.select_by_value("Fall 2016")
	driver.find_element_by_id("ctl00_content_btnSearch").click() # Submit

	htmlSource = driver.page_source
	soup = BeautifulSoup(htmlSource, 'html.parser')
	blah_id = soup.find("td", class_="icon-none-16-right").a['id'][5:]
	driver.close()
	return blah_id

def getCourseInfo(idNum):
	url = "https://isis.jhu.edu/classes/ClassDetails.aspx?id=" + idNum;
	driver = webdriver.PhantomJS()
	driver.get(url)
	source = driver.page_source
	soup = BeautifulSoup(source, 'html.parser')
	driver.close()

	prereqElems = soup.find_all("a", class_= "linkPrereq_"+idNum)
	prereqs = [i.get_text()[:-3] for i in prereqElems]
	if len(prereqs)>0:
		return prereqs

	p = re.compile("((AS|EN)(\.\d{3})(\.\d{3}))")
	matches = p.findall(source)
	prereqs = []
	for m in matches:
		if m[0] not in prereqs:
			prereqs.append(m[0])
	return prereqs

def main():
	# -1 for chopping newline escape
	courses = {}
	for i in openIDFile('Fall2016.txt'):
		courses[i[0]] = i[1][:-1]
	for key in courses:
		print "%s requires: "%key, getCourseInfo(courses[key])




	
start = timeit.default_timer()
main()
print "Runtime: " + str(timeit.default_timer()-start)[:4] + ' seconds'
