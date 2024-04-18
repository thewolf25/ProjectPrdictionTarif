# import sys
# sys.path.append('D:\\PredictCarsPrice')
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from selenium.common.exceptions import WebDriverException
from Cleaning.BrandModelExtraction import ExtractionMarqueModele
import pandas as pd 
import os

class ScrapperAutomobileTnOcc:
    
    def __init__(self):
        self.driver =webdriver.Chrome()
        self.baseUrl = 'https://www.automobile.tn/fr/occasion/s=sort!date'
        self.pageInitiale = 1
        self.pageFinale = 2
        
    def parsing_page_source(self, url):
        try:
            self.driver.get(url)
            time.sleep(4)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(2)
        return BeautifulSoup(self.driver.page_source,'html.parser') if BeautifulSoup(self.driver.page_source,'html.parser') else None
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        atags = soup.find_all('a', {'class': 'occasion-link-overlay'})
        return [a.get('href')[12:] for a in atags]
    
    def extract_data(self, soup):
        data = {}
        atags = soup.find('div', {'class': 'box d-none d-md-block'})
        listeDescCaract = atags.find_all('li')
        for li_tag in listeDescCaract:
            spec_name = li_tag.find('span', {'class': 'spec-name'}).text.strip()
            spec_value = li_tag.find('span', {'class': 'spec-value'}).text.strip()
            data[spec_name] = spec_value
        
        Modele = soup.find('h1').text.strip()
        Prix = soup.find('div', {'class': 'price'}).text.strip()
        data['Modele'] = Modele
        data['Prix'] = Prix
        
        atagsSpec = soup.find('div', {'class': 'col-md-6 mb-3 mb-md-0'})
        listeDesSpecification = atagsSpec.find_all('li')
        for li_tag in listeDesSpecification:
            spec_name = li_tag.find('span', {'class': 'spec-name'}).text.strip()
            spec_value = li_tag.find('span', {'class': 'spec-value'}).text.strip()
            data[spec_name] = spec_value
        
        return data
    
    def scrape(self, pageInit, pageFinal):
        urls=[]
        try:
            for i in range(pageInit,pageFinal+1):
                urls.extend(self.extract_cars_urls(self.baseUrl+'/'+str(i)+'?sort=date'))
            all_Data={}
            for index, url in enumerate(urls, start = 1):
                soup = self.parsing_page_source(self.baseUrl+url)
                data = self.extract_data(soup)
                all_Data[f'dict{index}'] = data
        finally:
            self.driver.quit()
        return all_Data
    
    def automobile_tn_scrapper_runner(self, OutputFileName):
        standardize = ColumnsStandardiser()
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.abspath(os.path.join(script_directory, "..", "Data", "DataPostScraping", "AutomobileTn"))
        file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.scrape(self.pageInitiale, self.pageFinale)
        dataStandardized = standardize.column_standardize(data)
        standardize.load_data_in_csv_file(dataStandardized, file_path)
    
    def automobile_tn_columns_standardise(self, dataframe):
        dataframe= dataframe.rename(columns={"Kilométrage": "Kilometrage", "Mise en circulation": "Annee", "Énergie": "Energie", "Boite vitesse":"BoiteVitesse" ,"Puissance fiscale":"PuissanceFiscale","Couleur extérieure":"Couleur"})
        dataframe = dataframe.drop(columns={"Couleur intérieure", "Date de l'annonce", "Nombre de places", "Nombre de portes", "Transmission","Sellerie"})
        return dataframe
    
    def automobile_tn_missing_marque_modele(self, dataframe):
        extraction = ExtractionMarqueModele()
        dataframe['Marque'] = dataframe['Description'].apply(lambda x: extraction.extraire_marque(x))
        dataframe['Modele'] = dataframe.apply(lambda row: row['Description'].replace(row['Marque'], '').strip(), axis=1)
        dataframe = dataframe.drop(columns={"Description"})
        dataframe = dataframe.dropna(subset=['Marque'])
        dataframe['Modele'] = dataframe.apply(lambda row: extraction.extraire_modele(row['Modele'], row['Marque']), axis=1)
        return dataframe
    
    def run_whole_process(self):
        self.pageInitiale = 1
        self.pageFinale = 2
        self.automobile_tn_scrapper_runner("FileAutomobileTnPostScrap")
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.abspath(os.path.join(script_directory,
                                                      "..", "Data", "DataPostScraping", "AutomobileTn",
                                                      "FileAutomobileTnPostScrap"))
        AutomobileTnFile = pd.read_csv(data_directory + '.csv')
        AutomobileTnData = self.automobile_tn_columns_standardise(AutomobileTnFile)
        data_directory = os.path.abspath(os.path.join(script_directory, "..", "Data", "DataPostCleaning",
                                                      "AutomobileTn", "FileAutomobileTnPostClean"))
        AutomobileTnData.to_csv(data_directory + ".csv")


## MAIN ##
if __name__ == "__main__":
    AutomobileTn = ScrapperAutomobileTnOcc()
    AutomobileTn.run_whole_process()      


