import pandas as pd
import re
import os

class ExtractionMarqueModele:

    def __init__(self) :
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.abspath(os.path.join(script_directory, "..", "Data", "CarsDatabase", "modeles"))
        self.CarDB = pd.read_csv(data_directory + ".csv", delimiter=';')
        self.ListeDesMarques = self.CarDB['rappel_marque'].drop_duplicates().to_list()
      
    def extraire_marque(self, description): 
      description = description.upper()
      description = description.replace("é", "e")
      description = description.replace("É", "E")
      description = description.replace("Ë", "E")
      marquefinale = ['']
      for marque in self.ListeDesMarques:
          x= r'\b{}\b'.format(re.escape(marque))
          if re.search(x, description, re.IGNORECASE):
              marquefinale.append(marque)
      for marque in marquefinale:
          if 'GOLF' in marquefinale and 'VOLKSWAGEN' in marquefinale:
              return 'VOLKSWAGEN'
          if 'POLO' in marquefinale and 'VOLKSWAGEN' in marquefinale:
              return 'VOLKSWAGEN'
      return marquefinale[-1]
      
    def extraire_modele(self, description, marque):
        marque=marque.upper()
        modeles = self.CarDB[self.CarDB['rappel_marque'] == marque]['modele'].dropna().tolist()
        modeleFinale=['']
        description = description.replace("é","e")
        description= description.replace("É","E")
        description= description.replace("Ë","E")
        for modele in modeles:
            x= r'\b{}\b'.format(re.escape(modele))
            if re.search(x, description, re.IGNORECASE):
                modeleFinale.append(modele)
        return modeleFinale[-1]
    
    def extraire_marque_modele(self, dataFrame):
        dataFrame['description'] = dataFrame['description'].astype(str)
        dataFrame['Marque'] = dataFrame['description'].apply(lambda x : self.extraire_marque(x))
        dataFrame['Modele'] = dataFrame.apply(lambda row:self.extraire_modele(row['description'],row['Marque']),axis=1 )
        return dataFrame


if __name__ == "__main__":
    pass