from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time
import random
import csv
import logging


class selenium_Wunderground_Spider():
	# Global and Constants
	COL_NUMBER = {
		'day' : 1,
		'temperature' : 2,
		'dew' : 3,
		'humidity' : 4,
		'wind' : 5,
		'preassure' : 6,
		'precipitation' : 7
	}

	SEPARATOR = ";"
	MAX_ERRORS = 5 # Prevent exceptions full of errors
	count_errors = 0

	def __init__(self):
		self.SEPARATOR = ";"
		self.MAX_ERRORS = 5 # Prevent exceptions full of errors
		self.count_errors = 0
		dt = datetime.now()
		self.csv_file_name = "SeleSpider_WUnderground-" + str(dt.hour) + "." + str(dt.minute) + ".csv"
		print("Spider initialized. Results will be recorded to: " + self.csv_file_name)
		logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
		#					filename='log_filename.txt', 


	def start(self):
		try:
			## URL iterator values
			locations = [
#				"th/bangkok/VTBD",
#				"th/mueang-chiang-mai/VTCC",
#				"th/pattaya/VTBU",
#				"th/ko-pha-ngan/VTSM",
#				"vn/hanoi/VVNB",
				"vn/ho-chi-minh-city/VVTS",
#				"vn/hội-an/VVDN",
				"sg/singapore/WSSS",
				"id/jakarta/WIHH",
				"id/denpasar/WADD",
				"ph/davao-city/RPMD",
				"ph/dumaguete/RPVD",
				"ph/cebu-city/RPVM",
				"ph/manila/RPLL"
			]
			years = list(range(2014, 2019))
			months = list(range(1, 13))

			url_pattern = "https://www.wunderground.com/history/monthly/{0}/date/{1}-{2}"

			# Launch browser and start crawling
			browser = webdriver.Firefox()
			self.crawl(browser, url_pattern, locations, years, months)
		except KeyboardInterrupt:
			print("Execution interrupted by user")
			return


	def crawl(self, browser, url_pattern, locations, years, months):
		for loc in locations:
			for yy in years:
				for mm in months:
					try:
						url = url_pattern.format(loc,yy,mm)
						scraped = self.parse(browser, url)
						# Cancel crawling if no data
						self.printOut(loc, yy, mm, scraped)
					except ValueError:
						print("Runtime error: " + ValueError)
						self.count_errors = self.count_errors + 1
						continue
					finally:
						if self.count_errors > self.MAX_ERRORS:
							print("ERROR: Too many errors")
							break
		browser.close()



	def parse(self, browser, url):
		## Table/Row iterator
		noSuchElement_list = []
		result_rows = []

		# Wait up to 2 seconds to simulate human
		time.sleep(random.randint(0,2))
		browser.get(url) #time.sleep(3)
		# Wait 2-4 seconds to ensure everything loaded
		time.sleep(random.randint(2,4))

		for day in range(2, 33):
			data_row_raw = []
			# dbg_msg = "Processing day {0}".format(day)
			# logging.debug(dbg_msg)
			for col in range(1, 8):
				try:
					datum = self.getValue(browser, day, col)
					data_row_raw.append(datum) # To allow use of JOIN
				except NoSuchElementException:
					noSuchElement_list.append((day,col))
					continue
				except ValueError:
					print("ERROR inside loop: " + ValueError)
					self.count_errors = self.count_errors + 1
				finally:
					if self.count_errors > self.MAX_ERRORS:
						print("ERROR: Too many errors")
						return result_rows
			data_row_text = str(";".join(data_row_raw))
			if len(data_row_text) > 5:
				print("Full row: " + data_row_text)
				result_rows.append(data_row_text)

		print("noSuchElement_list = " + str(noSuchElement_list))
		return result_rows


	def getValue(self, browser, day, col):
	#	xpath_gen_element = '//div[@class="observation-table"]/table/tbody/tr/td[{0}]/table/tbody/tr[{1}]/td[{2}]'
		xpath_gen_element = '//div[@class="observation-table"]/table/tbody/tr/td[{0}]/table/tbody/tr[{1}]'


		xpath_element_rows_test = '//*[@id="inner-content"]/div[2]/div[3]/div/div[1]/div/div/city-history-observation/div/div[2]/table/tbody/tr/td[1]/table/tbody/tr'
		test_row_no = browser.find_elements_by_xpath(xpath_element_rows_test)
		if len(test_row_no) < 10:
			raise Exception("ERROR while parsing URL. Not enough rows found: " + len(test_row_no))
		
		xpath_element = xpath_gen_element.format(col, day)
		element = browser.find_element_by_xpath(xpath_element)
		value = element.text.strip().replace(" ", self.SEPARATOR)
		return value


	def printOut(self, loc, yy, mm, scraped):
		print ("******SCRAPED******")
		with open(self.csv_file_name, mode='a') as csv_file:
			csv_writter = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for line in scraped:
				csv_file.write(str(loc) + ";" + str(yy) + ";" + str(mm) + ";" + str(line) + "\r\n")
				print (str(loc) + ";" + str(yy) + ";" + str(mm) + ";" + str(line))
			csv_file.close()


spider = selenium_Wunderground_Spider()
spider.start()

