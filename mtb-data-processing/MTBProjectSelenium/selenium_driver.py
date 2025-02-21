from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# selenium driver using Chrome browser
service = Service(executable_path="/usr/lib/chromium-browser/chromedriver")
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
print("Driver:")
print(driver)
print("\n")

# get the trip advisor review page and click buttons
#driver.get("https://www.tripadvisor.com/Airline_Review-d8729157-Reviews-Spirit-Airlines#REVIEWS")
driver.get("https://www.mtbproject.com/trail/912234/king-of-the-mountain-golden-eagle-loop")
more_buttons = driver.find_elements(By.CLASS_NAME, "btn")

# loop through the buttons and execute
for x in range(len(more_buttons)):
	if more_buttons[x].is_displayed():
		print("button " + str(x) + " displayed.")
		try:	
			driver.execute_script("arguments[0].click();", more_buttons[x])
		except Exception as e:
			print("error: " + e)
			continue	
		time.sleep(1)
page_source = driver.page_source	

# use beautiful soup to extract data from buttons??
# how do we perform login?

