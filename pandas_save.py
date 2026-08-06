import json
import re
from docx import Document
import pandas as pd
import numpy
from collections import Counter #musste installiert werden
import nltk #musste installiert werden - momentan noch nicht in benutzung
from nltk.corpus import stopwords #nicht in Benutzung

#speichern von DataFrames mit Kategorie, Risikowort, Risikosatz und allgemeiner Score des gepeicherten Mediums

#genaue Ausarbeitung allerdings noch unklar

#eventuell nur oder mit zusätzlich wörtern die auch "positiv" gewertet werden können und den entstehenden Risk Score nach unten drücken

dictionary = {}

with open("CUADv1.json" , "r", encoding = "utf-8") as file: #einlesen json datei
    summary = json.load(file)
    title_pattern = re.compile(r"[_-]+")
    

    #function only accepts key_words due to '*'
    def pre_processing(*, i: int = 1, text_given = str, solo_words: bool = False, remove_stop_words: bool = False): #preprocesses the contract and either returns a list of all words - or sentences used in the contract
        contract_type: str
        parentcompany_of_contract: str
        content: str 

        not_relevant = re.compile(fr"(Section|Clause|Schedule|Article|Exhibit|\((\w+|\d*)\)|\d*[.,;:_-]*\d*[,.-;:_]+\d*|[\$\%\&]+|I+|name|title|\d+|usd|co(?:.)?|ltd(?:.)?|\w{1})")

        relevant = re.compile(fr"\w{2,}")

        #relevant = re.compile(fr"\w{2,}")

        stop_words = set(stopwords.words('english'))

        #if not text_given:

        #    _, _, content = gain_access(i) #gain access fuction liefert contract_type, parentcompany_of_contract, content von vertrag

        #else:

        content = text_given

        content_low: str= content.lower() #transformiert content komplett in lower case

        content_strip: str = content_low.strip() #entfernt leerzeichen am anfang und am ende

        if solo_words: #unterteilt text in wörter

            content_replace = re.sub('\n|\t|\(|\)|"', "", content_strip) #entfernt newline and tab zeichen im text

            split_words = re.split(r"\s", content_replace) #teilt text nach leerzeichen

            while "" in split_words: #solange leerzeichen vorhanden

                split_words.remove("") #filtert alle leerzeichen im text raus

            if remove_stop_words:
                
                split_words_filtered = [word for word in split_words if word not in stop_words and not relevant.search(word) and not not_relevant.search(word)]

                return split_words_filtered

            return split_words
        
        else: #unterteilt text in sätze

            content_replace = re.sub('\s', " ", content_strip) #entfernt newline, tab und komprimiert diese zu normalen leerzeichen

            content_further_seperated = re.split("\.", content_replace) #separiert content nach "."-zeichen

            return content_further_seperated


    def dataframe_construction_td_idf(): #implements necessary DatFrames for relevant words
        relevant_contracts: list = [0, 2, 16, 17, 24, 27, 31, 39, 41, 43, 53, 54, 55, 62, 65, 67, 68, 69, 70, 71, 75, #indices of the relevant contract types
                                77, 78, 85, 88, 90, 91, 94, 99, 101, 103, 107, 111, 112, 115, 116, 120, 122, 132,
                                134, 136, 146, 153, 155, 158, 160, 163, 164, 167, 169, 171, 174, 175, 183, 188, 191,
                                194, 198, 200, 216, 219, 223, 224, 228, 230, 232, 235, 237, 239, 241, 242, 247, 248,
                                249, 254, 260, 262, 263, 265, 266, 280, 293, 297, 304, 306, 309, 310, 311, 313, 315,
                                325, 327, 337, 343, 345, 348, 356, 359, 366, 368, 369, 376, 378, 379, 385, 388, 391,
                                396, 398, 399, 400, 406, 413, 417, 429, 432, 436, 443, 447, 455, 457, 458, 460, 469,
                                471, 474, 478, 481, 486, 493, 498, 500, 505, 506]

    
        service_indices = [17, 24, 48, 53, 55, 58, 75, 78, 103, 122, 160, 179, 200, 210, 212, 235, 248, 278, 285, 309, 325,
                        356, 385, 406, 455, 457, 460, 506]
    
        distributor_indices = [0, 67, 85, 88, 89, 101, 120, 134, 136, 153, 155, 164, 167, 198, 216, 240, 260, 262, 265, 297,
                           310, 311, 340, 345, 359, 366, 369, 379, 447, 458, 471, 493]
    
        supply_indices = [2, 16, 54, 70, 107, 115, 143, 169, 183, 188, 219, 239, 242, 313, 376, 378, 399, 417]

        outsourcing_indices = [41, 62, 65, 68, 69, 99, 132, 175, 266, 304, 337, 348, 391, 400, 443, 478, 481, 486]
    
        license_indices = [27, 39, 43, 77, 94, 112, 146, 158, 163, 174, 191, 228, 230, 247, 249, 280, 306, 327, 343,
                        368, 388, 396, 398, 413, 429, 432, 436, 445, 469, 474, 489, 500, 505]

        #setup of basic foundation
        
        dataframe_foundation = []

        for i in range(len(service_indices)):
            output: dict = summary['data'][service_indices[i]] #erstellen von dictionary, dass Grundlage für DF bildet
            str; contract_title = output.get('title')
            paragraphs: list = (output.get('paragraphs'))
            for item in paragraphs:
                str; content = item['context']
            dataframe_foundation.append({
                "contract": f"C{service_indices[i]+1}", 
                "title": contract_title, #title Zeile
                "text": content #text Zeile
            })
        df = pd.DataFrame(dataframe_foundation)
        #df = df.set_index("contract")
        df["words"] = df["text"].apply(lambda x: pre_processing(text_given=x, solo_words=True, remove_stop_words=True)) #Erstellung einer von stop_words gefilterten Wort Zeile
        #save = df.iloc[1]["words"]

        #calculation of tf
        amount_of_words = df.iloc[[1]][["contract", "words"]].copy() #kopieren einer zeile des dataframes -> muss ersetzt werden
        amount_of_words["amount"] = len(df.iloc[1]["words"]) #anzahl wörter gesamt
        general_amount_of_words: int = amount_of_words["amount"].iloc[0] #kopieren des werts von gesamtanzahl wörter mit iloc[0] auch int typ, ansonsten pandas series

        #beispielwert eins durch spezifischen index ersetzen, bzw. vertragsdokument + gibt jedem word eine einzelne zeile 

        tf_single_words = amount_of_words.explode("words") #jedes einzelne wort bekommt einzelne zeile
        frequence_words = tf_single_words.groupby(["words"]).size() #anzahl der einzelnen gleichen wörter mit zeile als pandas series
        tf_df = frequence_words.reset_index()
        tf_df.columns = ["word", "amount_of_word"]
        tf_df["word_amount_overall"] = general_amount_of_words
        tf_df["tf"] = tf_df["amount_of_word"]/tf_df["word_amount_overall"] #calculation of tf



        #calculation of IDF
        df["words"] = df["words"].apply(set)
        amount_of_contracts = len(df)
        df_words = df.explode("words").dropna(subset=["words"]) #entfernt leere Zeilen, allerdings nur für Kategorie words
        word_share_in_contracts = df_words["words"].value_counts() #erstellen Pandas series mit Wert we oft Wort über Verträge verteilt vorkommt
        word_statistics = word_share_in_contracts.reset_index() #erstellt einen DatFrame aus dieser Series
        word_statistics.columns = ["word", "share"] #bennent die Spalten des DataFrames
        word_statistics["contract_proportion"] = amount_of_contracts/word_statistics["share"]
        word_statistics["idf-value"] = numpy.log10(word_statistics["contract_proportion"])
        #word_statistics = word_statistics.loc[word_statistics["share"]>=2].copy() #rausfiltern von einmal vorkommenden wörtern um "Company-Names und Co zu vermeiden, oder word dopplungen jeweils mit KI rausfiltern"
        print(word_statistics)
        print(tf_df)

        #calculation of TF-IDF
        merged_all_in_all = pd.merge(tf_df, word_statistics, on="word")
        merged_all_in_all["TF-IDF"] = merged_all_in_all["tf"]*merged_all_in_all["idf-value"]
        merged_all_in_all = merged_all_in_all.drop_duplicates(subset=["word"])
        merged_all_in_all = merged_all_in_all.sort_values(by="TF-IDF", ascending=False)


        print(merged_all_in_all)

        with pd.option_context("display.max_rows", None):
            print(merged_all_in_all)

        #merge of tf and idf

dataframe_construction_td_idf()