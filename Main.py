import json
from random import choice
import sys
from urllib import response
from black import TRANSFORMED_MAGICS
from scrapy import Selector
import requests
from playwright.sync_api import sync_playwright
from pymongo import MongoClient
from brroker import Myproxies
import subprocess
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


class Play_():
    def __init__(self):
        self.url = 'https://www.vehiclehistory.com/vin-check'
        #self.url = 'http://httpbin.org/ip'
        self.err = ['Timeout','ERR_PROXY_CONNECTION_FAILED','ERR_TUNNEL_CONNECTION_FAILED','ERR_CERT_AUTHORITY_INVALID','ERR_TIMED_OUT','ERR_CONNECTION_RESET','ERR_EMPTY_RESPONSE']
        self.one_time = True
        self.once = True
        self.vins = list()
        self.v = ''
        self.proxies = list()
        self.feature_list = ['Braking Assist','Blind Spot Monitoring','Adaptive Cruise Control','Lane Keep Assist','Lane Departure Warning','Automatic Breaking']

    def save_game(self):
        with open('remaining.json','w') as f:
            indx = self.vins.index(self.v)
            rem = self.vins[indx:-1]
            json.dump(rem,f)
            print('\n[+]File Saved..\n')

    def update_proxies(self):
        print('\n[+]Updating Proxies..\n')
        result_in_byte = subprocess.check_output("python3 brroker.py",shell=True).decode('utf-8')
        cleaned_list = result_in_byte.split('\n')
        self.proxies = list(filter(None,cleaned_list))

    def fetch_agent(self):
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        return user_agent_rotator.get_random_user_agent()

    def fetch_proxy(self):
        if self.proxies:
            proxy = self.proxies.pop()
            print(f'\nCurrent >> {proxy}')
            return proxy
        else:
            self.update_proxies()
            return self.fetch_proxy()
            
    def read_file(self):
        with open('10_.json','r') as f:
            content = json.load(f)
            self.vins = content

    def use_playwright(self):
        play_wright =  sync_playwright().start()
        browser = play_wright.chromium.launch(proxy={
            'server':f'{self.fetch_proxy()}',
        },headless=False)

        context = browser.new_context(user_agent=self.fetch_agent())
        page = context.new_page()
        page.set_default_timeout(60000)
        try:
            for vin in self.vins:
                self.v = vin
                if self.one_time:
                    self.one_time = False
                    page.goto(self.url)
                page.fill("//input[@class='VhInput-textField']",vin)
                page.click("//button[@class='VhButton VhButton--block VhButton--primary VhButton--large']")
                try:    
                    content = page.inner_html("//div[@class='VhModule VehicleSpecifications VhModule--medium']")
                except Exception as e:
                    print(f'\n\n[+]Continue {e}\n\n')
                    page.go_back()
                    continue
                else:
                    print('\n\n[+]Parsing\n\n')
                    self.parse(content)
                    page.go_back()
            # closing connection to the db
            self.client.close()   
            print('\nCon Closed') 
        except Exception as e:
            print(f'\nError >> {e}\n')
            if self.handle_err(e):
                print('\n[+]Trying another proxy\n')
                browser.close()
                play_wright.stop()
                self.one_time = True
                self.use_playwright()
            self.save_game()

    def handle_err(self,error):
        for err in self.err:
            if err in str(error):
                return True

    def parse(self,response):
        data_dict = dict()
        # converting str to selector object
        resp_selector = Selector(text=response)
        for section in resp_selector.xpath("//div[@class='VehicleSpecifications-section']"):
            if section.xpath("./h3/text()").get() == "Specifications":
                #print('\nVehicle Specifications')
                for spec in section.xpath(".//div[@class='EquipmentDetails-item']"):
                    title = spec.xpath(".//div[@class='EquipmentDetails-title']/text()").get()
                    value = spec.xpath(".//div[@class='EquipmentDetails-value']/text()").get()
                    data_dict[title.strip()] = value.strip()

            elif section.xpath("./h3/text()").get() == "Included Features":
                #print("\nIncluded Features")
                for feature in section.xpath(".//span[@class='IncludedFeatures-value']/text()").get():
                    if feature in self.feature_list:
                        data_dict[feature.strip()] = True
            else:
                pass
        self.save_to_db(data_dict)

    def create_con(self):
        self.collection = 'vehical_2015'
        mongo_uri = 'mongodb+srv://root:toor@cluster0.tdhpu.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
        mongo_db = 'vehical_DB'

        self.client = MongoClient(mongo_uri)
        self.db = self.client[mongo_db]
        
    
    def save_to_db(self,data):
        if self.once:
            self.once = False
            self.create_con()
        self.db[self.collection].insert_one(dict(data))
        print('Data Saved into DB')


play = Play_()
play.read_file()
play.use_playwright()





# import json
# from random import choice
# import sys
# from scrapy import Selector
# import requests
# from playwright.async_api import async_playwright
# from pymongo import MongoClient
# from brroker import Myproxies
# import subprocess
# import asyncio
# from random_user_agent.user_agent import UserAgent
# from random_user_agent.params import SoftwareName, OperatingSystem


# class Play_():
#     def __init__(self):
#         self.url = 'https://www.vehiclehistory.com/vin-check'
#         #self.url = 'http://httpbin.org/ip'
#         self.err = ['Timeout','ERR_PROXY_CONNECTION_FAILED','ERR_TUNNEL_CONNECTION_FAILED','ERR_CERT_AUTHORITY_INVALID','ERR_TIMED_OUT','ERR_CONNECTION_RESET']
#         self.one_time = True
#         self.once = True
#         self.vins = list()
#         self.v = ''
#         self.proxies = list()
#         self.feature_list = ['Braking Assist','Blind Spot Monitoring','Adaptive Cruise Control','Lane Keep Assist','Lane Departure Warning','Automatic Breaking']

#     def save_game(self):
#         with open('remaining.json','w') as f:
#             indx = self.vins.index(self.v)
#             rem = self.vins[indx:-1]
#             json.dump(rem,f)
#             print('\n[+]File Saved..\n')

#     def fetch_agent(self):
#         software_names = [SoftwareName.CHROME.value]
#         operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
#         user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
#         return user_agent_rotator.get_random_user_agent()

#     def update_proxies(self):
#         print('\n[+]Updating Proxies..\n')
#         result_in_byte = subprocess.check_output("python3 brroker.py",shell=True).decode('utf-8')
#         cleaned_list = result_in_byte.split('\n')
#         self.proxies = list(filter(None,cleaned_list))

#     def fetch_proxy(self):
#         try:
#             proxy = self.proxies.pop()
#             print(f'\nCurrent >> {proxy}')
#             return proxy
#         except IndexError:
#             self.update_proxies()
#             return self.fetch_proxy()

#     def read_file(self):
#         with open('10_.json','r') as f:
#             content = json.load(f)
#             self.vins = content

#     async def use_playwright(self):
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(proxy={
#                 'server':f'{self.fetch_proxy()}',
#             },headless=False)

#             context = await browser.new_context(user_agent=f'{self.fetch_agent()}')
#             page = await context.new_page()
#             page.set_default_timeout(60000)
#             try:
#                 for vin in self.vins:
#                     self.v = vin
#                     if self.one_time:
#                         self.one_time = False
#                         await page.goto(self.url)
#                     await page.fill("//input[@class='VhInput-textField']",vin)
#                     page.click("//button[@class='VhButton VhButton--block VhButton--primary VhButton--large']")
#                     if page.is_visible("//div[@class='VhModule VehicleSpecifications VhModule--medium']"):
#                         print('\n\n[+]Parsing\n\n')
#                         content = await page.inner_html("//div[@class='VhModule VehicleSpecifications VhModule--medium']")
#                         await self.parse(content)
#                         await  page.go_back()
#                     else:
#                         print('\n\n[+]Continue\n\n')
#                         await page.go_back()
#                         continue
                    
#                 # closing connection to the db
#                 self.client.close()   
#                 print('\nCon Closed') 
#             except (KeyboardInterrupt,Exception) as e:
#                 print(f'\nError >> {e}\n')
#                 if self.handle_err(e):
#                     print('\n[+]Trying another proxy')
#                     await browser.close()
#                     self.one_time = True
#                     await self.use_playwright()
#                 self.save_game()

#     def handle_err(self,error):
#         for err in self.err:
#             if err in str(error):
#                 return True
        

#     async def parse(self,response):
#         data_dict = dict()
#         # converting str to selector object
#         resp_selector = Selector(text=response)
#         for section in resp_selector.xpath("//div[@class='VehicleSpecifications-section']"):
#             if section.xpath("./h3/text()").get() == "Specifications":
#                 #print('\nVehicle Specifications')
#                 for spec in section.xpath(".//div[@class='EquipmentDetails-item']"):
#                     title = spec.xpath(".//div[@class='EquipmentDetails-title']/text()").get()
#                     value = spec.xpath(".//div[@class='EquipmentDetails-value']/text()").get()
#                     data_dict[title.strip()] = value.strip()

#             elif section.xpath("./h3/text()").get() == "Included Features":
#                 #print("\nIncluded Features")
#                 for feature in section.xpath(".//span[@class='IncludedFeatures-value']/text()").get():
#                     if feature in self.feature_list:
#                         data_dict[feature.strip()] = True
#             else:
#                 pass
#         self.save_to_db(data_dict)

#     def create_con(self):
#         self.collection = 'vehical_2015'
#         #mongo_uri = 'mongodb://localhost:27017'
#         mongo_uri = 'mongodb+srv://root:toor@cluster0.tdhpu.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
#         mongo_db = 'vehical_DB'

#         self.client = MongoClient(mongo_uri)
#         self.db = self.client[mongo_db]
        
    
#     def save_to_db(self,data):
#         if self.once:
#             self.once = False
#             self.create_con()
#         self.db[self.collection].insert_one(dict(data))
#         print('Data Saved into DB')


# play = Play_()
# play.read_file()
# asyncio.run(play.use_playwright())


# import json
# from os import sync
# from socket import create_connection
# import sys
# import time
# from scrapy.selector import Selector
# import requests
# from playwright.async_api import async_playwright
# from pymongo import MongoClient
# import asyncio

# class Play_():
#     def __init__(self):
#         self.url = 'https://www.vehiclehistory.com/vin-check'
#         self.one_time = True
#         self.once = True
#         self.vins = list()
#         self.v = ''
#         self.feature_list = ['Braking Assist','Blind Spot Monitoring','Adaptive Cruise Control','Lane Keep Assist','Lane Departure Warning','Automatic Breaking']

#     def save_game(self):
#         with open('remaining.json','w') as f:
#             indx = self.vins.index(self.v)
#             rem = self.vins[indx:-1]
#             json.dump(rem,f)
#             print('\nFile Saved')

#     def read_file(self):
#         with open('10_.json','r') as f:
#             content = json.load(f)
#             self.vins = content

#     async def use_playwright(self):
#         async with async_playwright() as p:
#             browser = await p.chromium.launch()
#             # adding headed useragent (not headless) in request
#             context = await browser.new_context(
#                 user_agent='Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Raspbian Chromium/74.0.3729.157 Chrome/74.0.3729.157 Safari/537.36'
#             )
#             page = await context.new_page()
#             try:
#                 for vin in self.vins:
#                     self.v = vin
#                     if self.one_time:
#                         self.one_time = False
#                         await page.goto(self.url)
#                     await page.fill("//input[@class='VhInput-textField']",vin)
#                     await page.click("//button[@class='VhButton VhButton--block VhButton--primary VhButton--large']")
#                     await page.is_visible("//div[@class='VhModule VehicleSpecifications VhModule--medium']")
#                     content = await page.inner_html("//div[@class='VhModule VehicleSpecifications VhModule--medium']")
#                     await self.parse(content)
#                     await page.go_back()
#                 # closing connection to the db
#                 self.client.close()   
#                 print('\nCon Closed') 
#             except Exception as e:
#                 print(f'\nError >> {e}\n')
#                 self.save_game()

#     async def parse(self,response):
#         data_dict = dict()
#         # converting str to selector object
#         resp_selector = Selector(text=response)
#         for section in resp_selector.xpath("//div[@class='VehicleSpecifications-section']"):
#             if section.xpath("./h3/text()").get() == "Specifications":
#                 #print('\nVehicle Specifications')
#                 for spec in section.xpath(".//div[@class='EquipmentDetails-item']"):
#                     title = spec.xpath(".//div[@class='EquipmentDetails-title']/text()").get()
#                     value = spec.xpath(".//div[@class='EquipmentDetails-value']/text()").get()
#                     data_dict[title.strip()] = value.strip()

#             elif section.xpath("./h3/text()").get() == "Included Features":
#                 #print("\nIncluded Features")
#                 for feature in section.xpath(".//span[@class='IncludedFeatures-value']/text()").get():
#                     if feature in self.feature_list:
#                         data_dict[feature.strip()] = True
#             else:
#                 pass
#         await self.save_to_db(data_dict)

#     async def create_con(self):
#         self.collection = 'vehical_2015'
#         mongo_uri = 'mongodb://localhost:27017'
#         mongo_db = 'vehical_DB'

#         self.client = MongoClient(mongo_uri)
#         self.db = self.client[mongo_db]
        
    
#     async def save_to_db(self,data):
#         if self.once:
#             self.once = False
#             await self.create_con()
#         self.db[self.collection].insert_one(dict(data))
#         print('Data Saved into DB')

# start = time.perf_counter()
# play = Play_()
# play.read_file()
# asyncio.run(play.use_playwright())
# print(time.perf_counter()-start)
