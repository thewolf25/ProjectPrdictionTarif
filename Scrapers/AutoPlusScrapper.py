import sys
sys.path.append('D:\\PredictCarsPrice')
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
from math import ceil 
from Cleaning.ColumnStandardiser import ColumnsStandardiser
import pandas as pd 
import os

class ScrappAutoPlusTnOccasion:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.baseUrl = "https://www.auto-plus.tn/voitures-d-occasion/1/p/1"
        self.nativeUrl = "https://www.auto-plus.tn/voitures-d-occasion"
        
    def parsing_page_source(self, url:str):
        try:
            self.driver.get(url)
            time.sleep(4)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(2)
        return BeautifulSoup(self.driver.page_source, 'html.parser') if BeautifulSoup(self.driver.page_source, 'html.parser') else None
    
    def nextPage(self, soup):
        ul = soup.find('ul', {'class':'pagination'})
        lasthref = ul.find_all('a')
        return lasthref[-1]['href']
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        atags = soup.find('div', {'id': 'lastadslistbox'})
        links = atags.find_all('a')
        return list(set([a.get('href')[44:] for a in links])) 
    
    def extract_data(self, soup):
        data = {}
        description = soup.find('h1',{'class':'col-md-8 adstitle'}).text.strip()  
        dateDeLannonce = soup.find('div',{'class':'col-md-3 pull-right'}).span.text.strip()
        prix = soup.find('div',{'class':'col-md-3 prixUsed'}).text.strip()
        desc = soup.find('div',{'class':'content'}).text.strip()
        listUl = soup.find('ul',{'class':'optionsCont'})
        listLi = listUl.find_all('li')
        for li in listLi:
            spec_name = li.find('b').text.strip()
            spec_value = li.find('span').text.strip()
            data[spec_name] = spec_value
        data['description'] = description
        data['desc'] = desc
        data['prix'] = prix
        data['date de l"annonce'] = dateDeLannonce
        return data
    
    def scrape(self):
        all_Data = {}
        soup = self.parsing_page_source(self.baseUrl)
        nbreDannonce = int(soup.find('span', {'class': 'total'}).text.strip()[:-23])
        nbreDePage = ceil(nbreDannonce/10)
        listeDesVoitures = []
        for i in range(1, nbreDePage+1):
            listeDesVoitures.extend(self.extract_cars_urls(self.baseUrl[:len(self.baseUrl)-1]+str(i))) 
        try:
            
            for index, voiture in enumerate(listeDesVoitures, start = 1):
                soup = self.parsing_page_source(self.nativeUrl + voiture)
                data = self.extract_data(soup)
                all_Data[f'dict{index}']=data       
        finally: 
            self.driver.quit()
        return all_Data

    def auto_plus_scrapper_runner(self, OutputFileName):
        standardize = ColumnsStandardiser()
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.abspath(os.path.join(script_directory, "..", "Data", "DataPostScraping", "AutoPlus"))
        file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.scrape()
        dataStandardized = standardize.column_standardize(data)
        standardize.load_data_in_csv_file(dataStandardized, file_path)

    def auto_plus_columns_standardise(self, dataframe):
        dataframe = dataframe.rename(columns={"kilométrage:": "Kilometrage", "Mise en circulation :": "Annee", "Energie :":"Energie" ,"Boite vitesse :":"BoiteVitesse" ,"Puissance fiscal:":"PuissanceFiscale","prix":"Prix","Marque :":"Marque","Modèle :":"Modele"})
        dataframe = dataframe.drop(columns={"Etat du véhicule :", "description", "desc", 'date de l"annonce',"Unnamed: 0"})
        return dataframe  
      
    def run_whole_process(self):
        self.auto_plus_scrapper_runner('AutoPlusFilePostScrap')
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.abspath(
            os.path.join(script_directory, "..", "Data", "DataPostScraping", "AutoPlus",
                         "AutoPlusFilePostScrap"))

        AutoPlusFile = pd.read_csv(data_directory + '.csv', sep=';')
        AutoPlusData = self.auto_plus_columns_standardise(AutoPlusFile)
        data_directory = os.path.abspath(
            os.path.join(script_directory, "..", "Data", "DataPostCleaning", "AutoPlus",
                         "AutoPlusFilePostClean"))
        AutoPlusData.to_csv(data_directory + ".csv")


## MAIN ##
if __name__ == "__main__":
    AutoPlus = ScrappAutoPlusTnOccasion()
    AutoPlus.run_whole_process()     

