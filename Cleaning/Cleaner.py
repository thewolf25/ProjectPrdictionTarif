import numpy as np 
import datetime

class cleaner: 
    
    def __init__(self) -> None:
        pass
    
    def elimination_des_valeurs_aberrantes_prix(self, prix):
        # si le prix est ecrit aleatoirement par l'utilisateur ex:123456
        if len(prix)>3:
            if self.croissant(prix):
                return "0"
        if len(prix)>=8  and prix[-3:]!="000":
           return "0"
        else:  
            return prix
    
    def eliminate_unity_white_space(self, dataframe):
        
        colonnes_a_traiter = ['Prix']
        for colonne in colonnes_a_traiter:
            dataframe[colonne] = dataframe[colonne].str.replace('\s+','',regex=True)
            dataframe[colonne] = dataframe[colonne].str.replace('\D','', regex=True)
        return dataframe
    
    def trois_chiffres_consecutifs_egaux(self, ch):
        for i in range(len(ch) - 2):
            if ch[i] not in ['0','9'] and ch[i] == ch[i + 1] == ch[i + 2]:
                return True
        return False
    
    def croissant(self, prix):
        l=len(prix)
        for i in range(0,l-1):
            if (int(prix[i])+1!=int(prix[i+1])):
                return False
        return True
    
    def is_all_carac_are_same(self, ch):
        # ch=ch.astype(str)
        if len(ch)>1:
            for i in range(len(ch)-1):
                if ch[i]!=ch[i+1]:
                    return ch
            return "0"
        else: 
            return "0"
        
    def millime_en_dinar(self, prix):
        if len(prix)>6:
            return prix[:-3]  
        else :
            return prix
        
    def ajout_des_zero(self, ch):
        if len(ch)==3 or len(ch)==2:
            return (ch+'000')
        if len(ch)==4:
            return (ch+'0')
        if len(ch)>6:
            return "0"
        if len(ch)==7 and ch[6]=="0":
            return ch[:6]
        return ch
    
    def eliminer_pointvirgtiret_kilometrage(self, dataframe):
        dataframe["Kilometrage"]=dataframe["Kilometrage"].astype(str)
        dataframe["Kilometrage"] = dataframe["Kilometrage"].str.replace(',','')
        dataframe["Kilometrage"] = dataframe["Kilometrage"].str.replace('.','')
        dataframe["Kilometrage"] = dataframe["Kilometrage"].str.replace('-','')
        dataframe["Kilometrage"] = dataframe["Kilometrage"].str.replace(r'\D','')
        dataframe["Kilometrage"].replace('','0', inplace=True) 
        return dataframe
    
    def entier_plus_recurrent(self, colonne):
        recurrent = colonne.mode()
        if not recurrent.empty:
            return recurrent.iloc[0]
        else:
            return 0
        
    def imputation_de_valeur_nulle_puiss_fis(self, marque, modele, dataframe):
        dataframe.dropna(subset="PuissanceFiscale",inplace=True)
        data = dataframe.loc[(dataframe.Marque==marque) & (dataframe.Modele==modele),"PuissanceFiscale"]
        res = self.entier_plus_recurrent(data)
        return res

    def eliminer_lescarac_futile_puiss_fisc(self, dataframe):
        dataframe["PuissanceFiscale"]=dataframe["PuissanceFiscale"].str.replace('-','')
        dataframe["PuissanceFiscale"]=dataframe["PuissanceFiscale"].str.removeprefix('0.')        
        dataframe["PuissanceFiscale"]=dataframe["PuissanceFiscale"].astype(str).apply(lambda x : "0" if ("." in x)or ("," in x) else x )
        dataframe["PuissanceFiscale"] = dataframe["PuissanceFiscale"].str.replace('\D', '', regex=True)
        dataframe["PuissanceFiscale"] = dataframe["PuissanceFiscale"].apply(lambda x: x if len(x) <= 2 else '0')
        # dataframe=dataframe.loc[dataframe["PuissanceFiscale"]!=""]
        dataframe["PuissanceFiscale"] = dataframe["PuissanceFiscale"].astype(int)
        return dataframe
    
    def eliminer_pointvirgtiret_annee(self, annee):
        annee= annee.split(',')[-1]
        annee= annee.split('-')[-1]
        annee= annee.split('.')[-1] 
        return int(annee) if annee.isdigit() else 0
    
    def corriger_marque_modele(self, df):
        df.Marque = df.Marque.astype(str)
        df.Modele = df.Modele.astype(str)
        for i in range (0,len(df)):
            if df.Marque.iloc[i]:
                if "POLO" in df.Marque.iloc[i].upper() or "GOLF" in df.Marque.iloc[i].upper():
                    df.Modele.iloc[i]=df.Marque.iloc[i].upper()+df.Modele.iloc[i] if df.Modele.iloc[i]!="nan" else df.Marque.iloc[i].upper()
                    df.Marque.iloc[i]="VOLKSWAGEN"
        return df 
      
    def boite_manuelle_auto(self, BoiteVitesse):
        BoiteVitesse=BoiteVitesse.replace("Î","I").strip()
        BoiteVitesse=BoiteVitesse.replace(" ","")
        Auto=["AUTO","AUTOMATIQUE","AUTOMATIC"]
        Manuelle=["MANUELLE","BOITE5","BOITE6","MANUEL"]
        if BoiteVitesse in Manuelle:
            return "MANUELLE"
        elif BoiteVitesse in Auto:
            return "AUTOMATIQUE"
        else : 
            return "INCONNU"

    def nettoyer_col_annee(self, dataframe):
        dataframe = dataframe.drop(dataframe[dataframe['Annee'] == ""].index)
        dataframe['Annee'] = dataframe['Annee'].apply(lambda x: str(x))
        dataframe['Annee'] = dataframe['Annee'].apply(lambda x: self.eliminer_pointvirgtiret_annee(x))
        dataframe.loc[(dataframe.Annee>=100)&(dataframe.Annee<=999),'Annee']*=10
        dataframe.loc[(dataframe["Annee"]<=1900)|(dataframe["Annee"]>datetime.datetime.now().year),'Annee']=0
        return dataframe
    def nettoyer_col_kilometrage(self, dataframe):
        dataframe = self.eliminer_pointvirgtiret_kilometrage(dataframe)
        dataframe["Kilometrage"] = dataframe["Kilometrage"].apply(lambda x : self.is_all_carac_are_same(x))
        dataframe["Kilometrage"] = dataframe["Kilometrage"].apply(lambda x : self.ajout_des_zero(x))
        dataframe["Kilometrage"]=dataframe.Kilometrage.astype(int)
        return dataframe
    
    def nettoyer_marque(self, dataframe):
        dataframe["Marque"]=dataframe["Marque"].str.upper()
        dataframe= dataframe.dropna(subset="Marque")
        dataframe['Marque'] = dataframe['Marque'].apply(lambda x: 'MERCEDES-BENZ' if x.strip() == 'MERCEDES' else x)
        return dataframe
    
    def nettoyer_modele(self, dataframe):
        dataframe["Modele"]=dataframe["Modele"].str.upper()
        dataframe["Modele"]=dataframe["Modele"].str.replace(" ","")        
        dataframe=self.corriger_marque_modele(dataframe)
        dataframe["Modele"] = dataframe["Modele"].replace("nan", np.nan)
        dataframe.dropna(subset=["Modele"],inplace=True)
        return dataframe
    
    def nettoyer_puissance_fiscale(self, dataframe):
        dataframe["PuissanceFiscale"]=dataframe["PuissanceFiscale"].fillna("0")
        dataframe = self.eliminer_lescarac_futile_puiss_fisc(dataframe)
        dataframe['PuissanceFiscale'] = np.where(
            (dataframe['PuissanceFiscale'] >= 4) & (dataframe['PuissanceFiscale'] <= 50),
            dataframe['PuissanceFiscale'], 0)
        for i in range (0,len(dataframe)):
            if dataframe.PuissanceFiscale.iloc[i]==0:
                marque = dataframe.Marque.iloc[i]
                modele = dataframe.Modele.iloc[i]
                nouvelleValeur=self.imputation_de_valeur_nulle_puiss_fis(marque, modele, dataframe)
                dataframe.PuissanceFiscale.iloc[i] = nouvelleValeur
        return dataframe
    
    def nettoyer_boite_vitesse(self, dataframe):
        dataframe["BoiteVitesse"] = dataframe["BoiteVitesse"].str.upper()
        dataframe["BoiteVitesse"]=dataframe.BoiteVitesse.astype(str).apply(lambda x : self.boite_manuelle_auto(x))
        return dataframe
    
    def nettoyer_prix(self, dataframe):
        dataframe["Prix"] = dataframe["Prix"].str.replace('\D', '', regex=True)
        dataframe.Prix=dataframe.Prix.apply(lambda x : self.is_all_carac_are_same(x))
        dataframe.Prix=dataframe.Prix.apply(lambda x : self.elimination_des_valeurs_aberrantes_prix(x))
        dataframe.Prix=dataframe.Prix.apply(lambda x : self.millime_en_dinar(x))
        dataframe.Prix=dataframe.Prix.astype(int)
        dataframe= dataframe.loc[dataframe.Prix!=0]
        return dataframe
    
    def nettoyer_energie(self, data):
        data.Energie=data.Energie.str.upper()
        data.Energie=data.Energie.str.replace(" ","")
        data.Energie=data.Energie.str.replace("(","")
        data.Energie=data.Energie.str.replace(")","")
        data.Energie=data.Energie.str.replace("N.C","INCONNU")
        data.Energie=data.Energie.fillna("INCONNU")
        return data
    
    def nettoyer_couleur(self, dataframe):
        dataframe.Couleur.fillna("AUTRE",inplace=True)
        dataframe.Couleur=dataframe.Couleur.str.upper()
        return dataframe
    
    def nettoyer_carrosserie(self, dataframe):
        dataframe.Carrosserie.fillna("INCONNU",inplace=True)
        dataframe.Carrosserie=dataframe.Carrosserie.str.upper()
        dataframe.Carrosserie=dataframe.Carrosserie.str.replace(" ","")
        return dataframe
