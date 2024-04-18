#import sys
#sys.path.append('D:\\PredictCarsPrice')
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from Cleaning.BrandModelExtraction import ExtractionMarqueModele
import pandas as pd
import os

class ScrappAutoPrixOccasion:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.baseUrl = "https://www.autoprix.tn/recherche?min_price=4000&max_price=200000&cp=1&sortby=date&is_sold=true&is_price=true&nb=1"
        self.nativeUrl = "https://www.autoprix.tn"
        self.PageInitiale = 1
        self.PageFinale = 2

    def parsing_page_source(self, url):
        try:
            self.driver.get(url)
            time.sleep(4)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(2)
        return BeautifulSoup(self.driver.page_source, 'html.parser') if BeautifulSoup(self.driver.page_source,'html.parser') else None
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        links = soup.find_all('a', {'class': 'black--text'})
        return list(set([a.get('href') for a in links if a.get('href')!='/estimation']))
    
    def extract_data(self, soup):
        data = {}
        try: 
            MarqueModele = soup.find('h1',{'class':'font-weight- title mb-1'}).text.strip() if soup.find('h1',{'class':'font-weight- title mb-1'}) else None  
            dateDeLannonce = soup.find('div',{'class':'col col-6'}).b.text.strip() if soup.find('div',{'class':'col col-6'}) and soup.find('div',{'class':'col col-6'}).b else None
            prix = soup.find('span',{'class':'font-weight-black headline'}).text.strip() if soup.find('span',{'class':'font-weight-black headline'}) else None 
            desc = soup.find('p',{'class':'body-2 black--text px-2 pb-1'}).text.strip() if soup.find('p',{'class':'body-2 black--text px-2 pb-1'}) else None
            listCarac = soup.find('div',{'class':'row elevation-0 row_4 transparent'})
            listdiv = listCarac.find_all('div')
            for h5b in listdiv:
                spec_name = h5b.find('h5', {'class': 'caption'}).text.strip() if h5b.find('h5', {'class': 'caption'}).text.strip() else None
                spec_value = h5b.find('b', {'class': 'body-1 font-weight-bold'}).text.strip() if h5b.find('b',{'class':'body-1 font-weight-bold'}) else None
                data[spec_name] = spec_value
            data['description']=MarqueModele
            data['desc'] = desc
            data['prix'] = prix
            data['date de l"annonce'] = dateDeLannonce
        except AttributeError as e:
            print(f"An error occurred while extracting data: {e}")
        return data
    
    def scrape(self, pageInitiale, pageFinale):
        all_Data = {}
        # soup = self.parsing_page_source(baseUrl)
        listeDesVoitures=[]
        for i in range(pageInitiale,pageFinale+1):
            listeDesVoitures.extend(self.extract_cars_urls(self.baseUrl[:69]+str(i)+self.baseUrl[70:]))
        try:
            for index, voiture in enumerate(listeDesVoitures, start=1):
                soup = self.parsing_page_source(self.nativeUrl+voiture)
                data = self.extract_data(soup)
                all_Data[f'dict{index}']=data       
        finally: 
            self.driver.quit()
        return all_Data
    
    def auto_prix_scrapper_runner(self, OutputFileName):
        standardize = ColumnsStandardiser()
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.abspath(os.path.join(script_directory, "..", "Data", "DataPostScraping", "AutoPrix"))
        file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.scrape(self.PageInitiale, self.PageFinale)
        dataStandardized = standardize.column_standardize(data)
        standardize.load_data_in_csv_file(dataStandardized, file_path)
    
    def auto_prix_columns_standardise(self, dataframe):
        extraction=ExtractionMarqueModele()
        dataframe= dataframe.rename(columns={"Kilométrage":"Kilometrage","Année":"Annee", "Carburant":"Energie" ,"Boite":"BoiteVitesse" ,"Puissance":"PuissanceFiscale","prix":"Prix"})
        dataframe = dataframe.drop(columns={'date de l"annonce'})
        dataframe = dataframe.dropna(how='all')
        dataframe = extraction.extraire_marque_modele(dataframe)
        dataframe = dataframe.drop(columns={'description','desc'})   
        return dataframe
    
    def run_whole_process(self):
        self.auto_prix_scrapper_runner("AutoPrixFilePostScrap")
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.abspath(
            os.path.join(script_directory, "..", "Data", "DataPostScraping", "AutoPrix",
                         "AutoPrixFilePostScrap"))
        autoPrixFile = pd.read_csv(data_directory + '.csv')
        data_directory = os.path.abspath(
            os.path.join(script_directory, "..", "Data", "DataPostCleaning", "AutoPrix",
                         "AutoPrixFilePostClean"))
        autoPrixData = self.auto_prix_columns_standardise(autoPrixFile)
        autoPrixData.to_csv(data_directory + ".csv")


## MAIN ##
if __name__ == "__main__":
    autoPrixScrapper = ScrappAutoPrixOccasion()
    autoPrixScrapper.PageInitiale = 1
    autoPrixScrapper.PageFinale = 2
    autoPrixScrapper.run_whole_process()     

