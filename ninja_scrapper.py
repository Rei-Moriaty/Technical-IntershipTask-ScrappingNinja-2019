from seleniumrequests import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re

from bs4 import BeautifulSoup as bs
import urllib.request

university_links = []
driver = Firefox()
class Scraper:
    def __init__(self, n):
        self.url = 'https://poetsandquants.com/wp-admin/admin-ajax.php'
        self.data = {'action' : 'sdac_smp_process_filters', 'filter_by' : '', 'action' : 'sdac_smp_process_filters', 'ranking' : 'any', 'view' : 'view-a-z-programs', 'paged' : n, 'school[user_typing]' : ''} 
        self.delay = 10
        self.response = ''

    def load_url(self):
        self.response = driver.request('POST', 'https://poetsandquants.com/wp-admin/admin-ajax.php', data = self.data)
        #print(self.response)
        try:
            pass
            #wait = WebDriverWait(driver, self.delay)
            #print(self.response.text)
            #wait.until(EC.presence_of_element_located((By.ID, "program-list")))
            # print('Page is Ready')
        except TimeoutException:
            print('Loading took too much time')
    
    
    def get_university_links(self):
        soup = bs(self.response.text, 'lxml')
        universities_divs = soup.findAll('li', {'class', 'non-sponsored'})
        for university_div in universities_divs:
            university_link = university_div.find('a')
            #print(university_link)
            university_links.append(university_link['href'])




for i in range(1, 61):
    scraper = Scraper(i)
    scraper.load_url()
    scraper.get_university_links()
    print(i,'/',60,end='\r')
    
print('\nAll links fetched\n')
with open('university_data.csv', 'w') as f:
    f.write('"University Name,School Name,Program  Title",Program Type,Tuition,Program Length,Program Start,Delivery Method,Email,Phone Number,Address,Program Information\n')
    i = 1
    for link in university_links:
        print(i, '/', len(university_links),end='\r')
        university_response = driver.request('GET', link)
        soup = bs(university_response.text, 'lxml')
        title = '"'+soup.find('h1', {'class' : 'entry-title'}).text+'"'
        prog_profile = soup.find('div', {'id' : 'program-profile'})
        prog_stats = prog_profile.find('div', {'id' : 'program-stats'})
        list_of_ps = prog_stats.findAll('p')
        prog_type = '"'+list_of_ps[0].text.split(':')[1].strip()+'"'
        tuition = '"'+list_of_ps[1].text.split(':')[1].strip()+'"'
        prog_length = '"'+list_of_ps[2].text.split(':')[1].strip()+'"'
        prog_start = '"'+list_of_ps[3].text.split(':')[1].strip()+'"'
        del_method = '"'+list_of_ps[4].text.split(':')[1].strip()+'"'
        email = list_of_ps[6].find('a')['href'].split(':')[1].strip()
        phone_no = list_of_ps[7].text.strip()
        #print(phone_no)
        if not re.sub(r'[" "|"?"|+|-]','',phone_no).isdigit():
            phone_no = ''
            #print('\n',title,'doesn\'t contain phno\n')
        if phone_no == '':
            address = '"'+', '.join([s.text for s in list_of_ps[7].findAll('span', {'class': 'smp-address'})])+'"'
        else:
            address = '"'+', '.join([s.text for s in list_of_ps[8].findAll('span', {'class': 'smp-address'})])+'"'
        try:
            prog_info = prog_profile.find('div', {'id' : 'logo-buttons'}).findAll('p')[1].find('a')['href']
        except:
            try:
                prog_info = prog_profile.find('div', {'id' : 'logo-buttons'}).findAll('p')[0].find('a')['href']
            except:
                prog_info = ''
        f.write(','.join([title, prog_type,tuition,prog_length,prog_start,del_method,email,phone_no,address,prog_info]) + '\n')
        i += 1
print('\nData written to file successfully\n')
driver.close()
