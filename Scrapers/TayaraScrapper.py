#import sys
#sys.path.append('D:\\PredictCarsPrice')
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
from math import ceil 
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from Cleaning.BrandModelExtraction import ExtractionMarqueModele
import pandas as pd 
import os

class ScrappOccasionTayaraTn:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.baseUrl = "https://www.tayara.tn/ads/c/V%C3%A9hicules/Voitures/t/Occasion/?minPrice=10000&maxPrice=1000000000&page=1"
        self.nativeUrl = "https://www.tayara.tn"
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
    
    def nbre_de_page(self, soup):
        div = soup.find('data', {'class': 'block mt-1 text-sm lg:text-base font-bold text-info'}).text.strip()
        nbreDAnnonce = int(div[1:-19])
        nbreDePage = ceil(nbreDAnnonce/70)
        return nbreDePage
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        links = soup.find_all('a', {'target': '_blank'})
        liste = list(set([a.get('href') for a in links]))
        return [element for element in liste if '/item/' in element]
    
    def extract_data(self, soup):
        data = {}
        try: 
            dateDeLannonce = soup.find('div', {'class': 'flex items-center space-x-2 mb-1'}).text.strip() if soup.find('div',{'class':'flex items-center space-x-2 mb-1'}) else None
            mt4 = soup.find_all('div', {'class': 'mt-4'})
            if len(mt4) > 1:
                prix = mt4[1].find('data')['value']
            else:
                prix = None
            desc = soup.find('h1', {'class': 'text-gray-700 font-bold text-2xl font-arabic'}).text.strip() if soup.find('h1', {'class': 'text-gray-700 font-bold text-2xl font-arabic'}) else None
            description = soup.find('p', {'dir': 'auto', 'class': 'text-sm text-start text-gray-700 font-arabic whitespace-pre-line	 line-clamp-3'}).text.strip() if soup.find('p',{'class':'text-sm text-start text-gray-700 font-arabic whitespace-pre-line	 line-clamp-3'}) else None
            listCarac = soup.find_all('li', {'class': 'col-span-6 lg:col-span-3'})
            # listdiv=listCarac.find_all('div',{'class':'Annonce_flx785550__AnK7v'})
            for div in listCarac:
                spec_name = div.find('span',{'class':'text-gray-600/80 text-2xs md:text-xs lg:text-xs font-medium'}).text.strip() if div.find('span',{'class':'text-gray-600/80 text-2xs md:text-xs lg:text-xs font-medium'}) else None
                spec_value = div.find('span',{'class':'text-gray-700/80 text-xs md:text-sm lg:text-sm font-semibold'}).text.strip() if div.find('span',{'class':'text-gray-700/80 text-xs md:text-sm lg:text-sm font-semibold'}) else None
                data[spec_name] = spec_value
            data['date de l"annonce'] = dateDeLannonce
            data['desc'] = desc
            data['prix'] = prix
            data['description'] = description
        except AttributeError as e:
            print(f"An error occurred while extracting data: {e}")
        return data
    
    def scrape(self, PageInitiale, PageFinale):
        all_Data = {}
        listeDesVoitures = []
        for i in range(PageInitiale, PageFinale+1):
            listeDesVoitures.extend(self.extract_cars_urls(self.baseUrl[:104]+str(i)))
        try:
            for index, voiture in enumerate(listeDesVoitures, start=1):
                soup = self.parsing_page_source(self.nativeUrl + voiture)
                data = self.extract_data(soup)
                all_Data[f'dict{index}'] = data
        finally: 
            self.driver.quit()
        return all_Data
    
    def tayara_scrapper_runner(self,  OutputFileName):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.abspath(os.path.join(script_directory, "..", "Data", "DataPostScraping", "Tayara"))
        file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.scrape(self.pageInitiale, self.pageFinale)
        standardize = ColumnsStandardiser()
        dataStandardized = standardize.column_standardize(data)
        standardize.load_data_in_csv_file(dataStandardized, file_path)
    
    def tayara_columns_standardise(self, dataframe):    
        dataframe = dataframe.rename(columns={"Kilométrage": "Kilometrage", "Année": "Annee", "Carburant": "Energie", "Boite": "BoiteVitesse", "Puissance fiscale": "PuissanceFiscale", "prix": "Prix", "Modèle": "Modele", "Couleur du véhicule": "Couleur", "Type de carrosserie": "Carrosserie"})
        dataframe = dataframe.drop(columns={"Cylindrée", 'date de l"annonce', "description", "Etat du véhicule"})
        dataframe = dataframe.dropna(how='all')
        for i in dataframe.columns:
            if "Unnamed" in i:
                dataframe = dataframe.drop(columns=[i])
        return dataframe
    
    def tayara_missing_marque_modele(self, dataframe):
        extraction = ExtractionMarqueModele()
        dataframe['desc'] = dataframe['desc'].str.upper()
        dataframe.dropna(subset=["Modele", "desc", "Marque"], inplace=True)
        ## Si la valeur du colonne marque est null: extraire le marque depuis la description (colonne desc)
        maskMarque = dataframe['Marque'].isnull()
        dataframe.loc[maskMarque, 'Marque'] = dataframe.loc[maskMarque, 'desc'].apply(lambda x: extraction.extraire_marque(x))
        ## Si la valeur du colonne modele est null: extraire le modele depuis la description (colonne desc)
        dataframe = dataframe.dropna(subset=['Marque'])
        maskModele = dataframe['Modele'].isnull()
        dataframe.loc[maskModele, 'Modele'] = dataframe.loc[maskModele, ['desc', 'Marque']].apply(lambda row: extraction.extraire_modele(row['desc'], row['Marque']), axis=1)
        ## Si la valeur du colonne marque est Autres: extraire le marque depuis la description (colonne desc)
        maskMarque = dataframe['Marque'] == 'Autres'
        dataframe.loc[maskMarque, 'Marque'] = dataframe.loc[maskMarque, 'desc'].apply(lambda x: extraction.extraire_marque(x))
        ## Si la valeur du colonne modele est Autres: extraire le modele depuis la description (colonne desc)
        dataframe = dataframe.dropna(subset=['Marque'])
        maskModele = dataframe['Modele'] == 'Autres'
        dataframe.loc[maskModele, 'Modele'] = dataframe.loc[maskModele, ['desc', 'Marque']].apply(lambda row: extraction.extraire_modele(row['desc'], row['Marque']), axis=1)
        dataframe = dataframe.drop(columns={"desc"})
        return dataframe
    
    def run_whole_process(self):
        self.tayara_scrapper_runner('TayaraFilePostScrap')
        ## S'il y a plusieurs files csv qui viennent du scrapping du site tayara il faut utiliser la methode merge_csv_files du module fileImporter
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.abspath(os.path.join(script_directory, "..", "Data", "DataPostScraping", "Tayara", "TayaraFilePostScrap"))
        tayaraFile = pd.read_csv(data_directory + ".csv")
        tayaraData = self.tayara_columns_standardise(tayaraFile)
        data_directory = os.path.abspath(os.path.join(script_directory, "..", "Data", "DataPostCleaning", "FileTayaraPostClean" ))
        tayaraData.to_csv(data_directory + ".csv")


##MAIN##
if __name__ == "__main__":
    tayara = ScrappOccasionTayaraTn()
    tayara.pageInitiale = 1
    tayara.pageFinale = 1
    tayara.run_whole_process()
