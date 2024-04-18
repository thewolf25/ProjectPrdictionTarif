import pandas as pd
import os
from math import ceil 
class importer: 
    
    def __init__(self) -> None:
        pass

    def import_csv_file(self,file_name):
        try: 
            dataframe = pd.read_csv(file_name)
            return dataframe
        except FileNotFoundError:
            print("le fihcier n'est pas trouvé.")
            return None 
        except Exception as e:
            print("Une erreur s'est produite lors de l'imporation du fichier csv: ", str(e))
            return None

    def merge_csv_files(self,dossierPath):

        listFileName=[f for f in os.listdir(dossierPath) if f.endswith('.csv')]
        listDataframe = []
        for file in listFileName:
            df = pd.read_csv(dossierPath+file)
            listDataframe.append(df)
        finalDataFrame = pd.concat(listDataframe)
        return finalDataFrame
    
    def merge_excel_files(self,dossierPath):
        listFileName=[f for f in os.listdir(dossierPath) if f.endswith('.xlsx')]
        listDataframe = []
        for file in listFileName:
            df = pd.read_excel(dossierPath+file,dtype="object")
            listDataframe.append(df)
        finalDataFrame = pd.concat(listDataframe)
        return finalDataFrame
    
    def removeUnnamed(self,dataframe):
        for i in dataframe.columns:
            if "Unnamed" in i:
                dataframe=dataframe.drop(columns=[i])
        return dataframe