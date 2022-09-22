from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import csv
from time import sleep
import requests
import time
import hashlib
import os.path
import json
from ml_backend import *

#generate hash of profile link to be used for saving the json file.
def hashprofile(profile_link):
        import hashlib
        hash_object = hashlib.sha256(str(profile_link).encode('utf-8'))
        return hash_object.hexdigest()

def getfilepath(profile_link):
    return get_config('JSONPROFILEDATAPATH') + hashprofile(profile_link) + '.json'

def readjson(filepath):
    with open(filepath, "r") as rf:
        json_data = json.load(rf)
    return json_data

def writejson(profile_link, dictionary):
    with open(getfilepath(profile_link), "w") as outfile:
        json.dump(dictionary, outfile)

def getfromDBifexists(profile_link):
    fe = os.path.exists(getfilepath(profile_link))
    if (fe):
        return readjson(getfilepath(profile_link))
    return fe

class scrapperutility:
    def linkedin_extractor(self, profile_link, username, password, chromedriverexePath):

        content = getfromDBifexists(profile_link)
        if (content):
            return content

        list_of_name = []
        list_of_experience = []
        list_of_about = []
        list_of_address = []
        list_of_job_title = []
        list_of_description = []
        list_of_skills =[]

        sleep(2)
        s = Service(chromedriverexePath)
        driver = webdriver.Chrome(service=s)
        driver.get('https://www.linkedin.com')
        sleep(3)
        driver.find_element(By.ID, 'session_key').send_keys(username)
        driver.find_element(By.ID, 'session_password').send_keys(password)
        sleep(2)
        log_in_button = driver.find_element(By.CLASS_NAME, "sign-in-form__submit-button")
        sleep(1)
        log_in_button.click()
        sleep(15)

        try:
            driver.get(profile_link)
            sleep(15)
        #NAME
            name = driver.find_element(By.XPATH, "//h1[@class='text-heading-xlarge inline t-24 v-align-middle break-words']")
    #         list_of_name.append(name.text)
            name_text=name.text
            sleep(5)
        except:
            print('Error in profile: ', profile_link)
            list_of_name.append('')
            list_of_experience.append([])
            list_of_about.append([])
            list_of_address.append([''])
            list_of_job_title.append('')
            list_of_description.append([])
            list_of_skills.append([])

        
    # TITLE
        title = driver.find_element(By.XPATH, "//div[@class='text-body-medium break-words']")
    #     list_of_job_title.append(title.text)
        title_text=title.text
        
    # ADDRESS
        address = driver.find_elements(By.XPATH, "//span[@class='text-body-small inline t-black--light break-words']")
        location=[]
        for j in address:
            location.append(j.text)
            list_of_address.append(location)
        

    #-----------------------------------BeautifulSoup--------------------------
        src = driver.page_source
        doc = BeautifulSoup(src, 'html.parser')
        div = doc.find_all('section', class_='artdeco-card ember-view relative break-words pb3 mt2')

    # ABOUT
        about_section_present= False
        for section in div:
            about_section = section.find_all('div', {'id': 'about'})
            if len(about_section) != 0:
                about_section_present=True
                about_text= section.find_all('span', {'class': 'visually-hidden'})
                about_each=[]
                for bio in about_text:
                    about_each.append(bio.text)
                list_of_about.append(about_each)
                break;
        if about_section_present == False: 
            about_each=[]
            list_of_about.append(about_each)
            
    # CHECK FOR SKILL AND EXPERIENCE SECTION
        skill_section_present= False
        experience_section_present=False
        
        for section in div:
            skill_section = section.find_all('div', {'id': 'skills'})
            if len(skill_section) != 0:
                skill_section_present=True
                break
        
        for section in div:
            exp_section = section.find_all('div', {'id': 'experience'})
            if len(exp_section) != 0:
                experience_section_present=True
                break
        
        get_url = driver.current_url


    # EXPERIENCE

        if experience_section_present==True:
            sleep(3)
            driver.get(get_url+"details/experience")
            sleep(7)
            src2 = driver.page_source
            doc2 = BeautifulSoup(src2, 'html.parser')
            exp_list = doc2.find_all('li', {'class':'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
            
            experience_per_person=[]
            for each_exp in exp_list:
                text_line_list= each_exp.find_all('span', {'class': 'visually-hidden'})
                partition_list=[]
                for text_line in text_line_list:
                    partition_list.append(text_line.text)
                experience_per_person.append(partition_list)
            list_of_experience.append(experience_per_person)
            
            

    # SKILLS
    
        if skill_section_present==True:
            sleep(3)
            driver.get(get_url+"details/skills")
            driver.maximize_window()

            SCROLL_PAUSE_TIME = 0.8
    #-----------------------------------------------
            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

    #------------------------------------------------                
            print("Scrolling is over")   
            sleep(5)
            skill_each=[]
            src1 = driver.page_source
            doc1 = BeautifulSoup(src1, 'html.parser')
            div1 = doc1.find_all('li', {'class':'pvs-list__paged-list-item'}) 

            for li in div1:
                only_skill=[]
                skill_text= li.find_all('span', {'class': 'visually-hidden'})
                for skills in skill_text:
                    only_skill.append(skills.text)
                skill_each.append(only_skill[0])
            list_of_skills.append(list(set(skill_each)))

        elif skill_section_present == False: 
            skill_each=[]
            list_of_skills.append(skill_each)
            
    #     print(list_of_name)
    #     print(list_of_job_title) 
    #     print(list_of_address)
    #     print(list_of_about)
    #     print(list_of_experience)
    #     for m in list_of_skills:
    #         print(len(m),m)
        sleep(8)
        driver.quit()

    #     t2 = time.time()
    #     print('End-time: ', t2)
    #     print('Total time taken: ', (t2-t1)/60, 'minutes\t')

        experience=[]
        for exp in experience_per_person:
            for token in exp:
                experience.append(token)
            experience += ["."]
        experience = " ".join(experience)
        skills= ",".join(skill_each)
        #return 'name':name_text + title_text +" "+ about_each[1] + " " +  experience + " " + skills

        dictionaryoutput = {
             'name':name_text,
             'profile':title_text +" "+ about_each[1] + " " +  experience + " " + skills}

        writejson(profile_link, dictionaryoutput )
        return dictionaryoutput