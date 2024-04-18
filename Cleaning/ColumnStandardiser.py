import csv


class ColumnsStandardiser:

    def __init__(self) -> None:
          pass 
    
    def column_standardize(self, Jsondata):
        #Etape 1 : Extraire toutes les clés des dictionnaires existant 
        all_keys = set()
        for dic in Jsondata.values():
            all_keys.update(dic.keys())
        # Étape 2 : Pour chaque dictionnaire, ajouter les clés manquantes avec des valeurs nulles
        for d in Jsondata.values():
            for key in all_keys:
                if key not in d:
                    d[key] = None
        return Jsondata
    
    def load_data_in_csv_file(self, Jsondata, csv_file):
        if not Jsondata:
            return"Le dictionnaire est vide."
        # Récupérer les clés du premier dictionnaire pour utiliser comme en-têtes de colonnes
        columns = list(Jsondata.values())[0].keys()
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            # Écrire les en-têtes de colonnes
            writer.writeheader()
            # Écrire les données dans le fichier CSV
            for key, data in Jsondata.items():
                writer.writerow(data)
        print(f"Les données ont été écrites dans {csv_file}")