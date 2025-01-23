## Name    : getTuftsCourses.py
## Author  : Tygan Chin
## Purpose : Scrapes undergraduate course data from Tufts' SIS page and saves 
##           the data in a json file named courses.json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import json

# json formatting
elements = {
    'courseName' : 'DERIVED_CRSECAT_DESCR200',
    'career': "SSR_CRSE_OFF_VW_ACAD_CAREER$0", 
    'shus' : "DERIVED_CRSECAT_UNITS_RANGE$0", 
    'grading' : "SSR_CRSE_OFF_VW_GRADING_BASIS$0", 
    'component' : "DERIVED_CRSECAT_DESCR$0", 
    'needed' : "DERIVED_CRSECAT_DESCR50$0", 
    'campus' : "CAMPUS_TBL_DESCR$0",
    'academicGroup' : 'ACAD_GROUP_TBL_DESCR$0',
    'attributes' : 'DERIVED_CRSECAT_SSR_CRSE_ATTR_LONG$0',
    'description' : 'SSR_CRSE_OFF_VW_DESCRLONG$0'
}
section = {
    'section': 'CLASS_SECTION$',
    'combined': 'CLASS_COMBINED$',
    'session' : 'CLASS_SESSION$',
}
sectionDetails = {
    'day' : 'MTGPAT_DAYS$',
    'start' : 'MTGPAT_START$',
    'end' : 'MTGPAT_END$',
    'room' : 'MTGPAT_ROOM$',
    'instructor' : 'MTGPAT_INSTR$',
    'dates' : 'MTGPAT_DATES$',
}

# program timer
start_time = time.time()

# Set up chrome options 
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--incognito")

# retrieves the individual details of a single class
def getDetails():
    
    # get overall class details
    wait.until(EC.visibility_of_element_located((By.ID, "SSR_CRSE_OFF_VW_ACAD_CAREER$0")))
    dictionary = {}
    for key, element in elements.items():
        try:
            dictionary[key] = shortWait.until(EC.visibility_of_element_located((By.ID, element))).text
        except:
            dictionary[key] = ''

    # get section information if applicable
    if driver.find_elements(By.ID, "DERIVED_SAA_CRS_SSR_PB_GO"):

        # reveal section information
        element = wait.until(EC.visibility_of_element_located((By.ID, "DERIVED_SAA_CRS_SSR_PB_GO")))
        element.click()
        time.sleep(3)

        # calculate number of sections
        gridNums = driver.find_elements(By.CLASS_NAME, "PSGRIDCOUNTER")
        numSections = int(gridNums[0].text.split(' ')[-1])

        sections = []
        k = 0
        p = 0
        for j in range(numSections):
            currSec = {}
            for key, element in section.items():
                try:
                    currSec[key] = shortWait.until(EC.visibility_of_element_located((By.ID, element + str(k)))).text
                except:
                    currSec[key] = ''

            try:
                container = driver.find_element(By.ID, f"win0divCLASS_STATUS${k}")
                image_element = container.find_element(By.TAG_NAME, "img")
                currSec['status'] = image_element.get_attribute("src").split('_')[3]
            except:
                currSec['status'] = ''
            
            for r in range(int(gridNums[(j + 1) * 2].text.split(' ')[-1])):
                for key, element in sectionDetails.items():
                    try:
                        currSec[key] = shortWait.until(EC.visibility_of_element_located((By.ID, element + str(p)))).text
                    except:
                        currSec[key] = ''
                p += 1
            
        
            k += 1
            sections.append(currSec)
        dictionary['sections'] = sections
    else:
        dictionary['sections'] = None

    # click back
    element = wait.until(EC.visibility_of_element_located((By.ID, "DERIVED_SAA_CRS_RETURN_PB")))
    element.click()

    print(dictionary['courseName'])

    return dictionary

# open site and scrape all class data in alphabetical order of department (new webpage used for each letter)
courses = []
for c in range(ord('A'), ord('Z') + 1):

    # Set up the WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)
    shortWait = WebDriverWait(driver, 1)

    # Open the webpage
    url = "https://sis.it.tufts.edu/psp/paprd/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.SSS_BROWSE_CATLG.GBL?pslnkid=TFP_COURSE_CATALOG&PORTALPARAM_PTCNAV=TFP_COURSE_CATALOG&EOPP.SCNode=EMPL&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=TFP_GUEST&EOPP.SCLabel=Tufts%20Course%20Catalogs&EOPP.SCFName=TFP_COURSE_CATALOGS&EOPP.SCSecondary=true&EOPP.SCPTfname=TFP_COURSE_CATALOGS&FolderPath=PORTAL_ROOT_OBJECT.TFP_TUFTS.TFP_GUEST.TFP_COURSE_CATALOGS.TFP_COURSE_CATALOG&IsFolder=false"
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    # Switch to the iframe (if needed)
    driver.switch_to.frame("ptifrmtgtframe") 

    # Wait for the dropdown to be visible
    dropdown_element = wait.until(EC.visibility_of_element_located((By.ID, "DERIVED_SSS_BCC_ACAD_CAREER")))

    # Create a Select object
    select = Select(dropdown_element)

    # Select by visible text
    select.select_by_value("ASEU")
    selected_option = select.first_selected_option.text

    # click letter 
    while True:
        try:
            element = driver.find_element(By.ID, f'DERIVED_SSS_BCC_SSR_ALPHANUM_{chr(c)}')
            element.click()
            break
        except:
            continue
    time.sleep(2)

    # expand all classes
    try:
        element = wait.until(EC.visibility_of_element_located((By.ID, 'DERIVED_SSS_BCC_SSS_EXPAND_ALL$97$')))
        element.click()
    except:
        continue
    
    # ensure classes are visible
    while True:
        try:
            element = driver.find_element(By.ID, f"CRSE_TITLE$0")
            break
        except:
            continue
    
    # get details of all elements
    i = 0
    while True:
        try:

            element = wait.until(EC.visibility_of_element_located((By.ID, f"CRSE_TITLE${i}")))
            element.click()
            time.sleep(1)

            if driver.find_elements(By.ID, "CAREER$0"):
                w = 0
                while True:
                    try:
                        element = wait.until(EC.visibility_of_element_located((By.ID, f"CAREER${w}")))
                        element.click()
                        courses.append(getDetails())
                        w += 1
                    except:
                        element = wait.until(EC.visibility_of_element_located((By.ID, "DERIVED_SSS_SEL_RETURN_PB")))
                        element.click()
                        break
            else:
                courses.append(getDetails())
            i += 1
        except:
            break

    # Close the browser
    driver.quit()

# write course info to json
with open("courses.json", "w") as file:
    json.dump(courses, file, indent=4)

# report time
print(time.time() - start_time)