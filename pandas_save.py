import json
import re
import pandas as pd
import numpy
from nltk.corpus import stopwords

with open("CUADv1.json" , "r", encoding = "utf-8") as file: #einlesen json datei
    summary = json.load(file)
    title_pattern = re.compile(r"[_-]+")
    

    #function only accepts key_words due to '*'
    def pre_processing(*, text_given = str, solo_words: bool = False, remove_stop_words: bool = False): #preprocesses the contract and either returns a list of all words - or sentences used in the contract
        content: str 

        not_relevant = re.compile(fr"\b(Section|Clause|Schedule|Article|Exhibit|\((\w+|\d*)\)|\d*[.,;:_-]*\d*[,.-;:_]+\d*|[\$\%\&]+|I+|name|title|\d+|usd|co(?:.)?|ltd(?:.)?|i{{2,}}|\d*\w*\d+\w*\d*\b)") #rausfiltern von irrelevanten Zeichen und Bezeichnungen, also auch Absatzmarkern
        #-> + removal von zahlen + wörtern die mit zahlen zusammenhängen wie "no.18"

        stop_words = set(stopwords.words('english'))

        content = text_given

        content_low: str= content.lower() #transformiert content komplett in lower case

        content_strip: str = content_low.strip() #entfernt leerzeichen am anfang und am ende

        if solo_words: #unterteilt text in wörter

            content_replace = re.sub('\n|\t|\(|\)|\"|\'|\.|\/|&|-', "", content_strip) #entfernt newline and tab zeichen im text, als auch irrelevante Zeichen an Wörtern wie "'/&-()

            split_words = re.split(r"\s", content_replace) #teilt text nach leerzeichen

            while "" in split_words: #solange leerzeichen vorhanden

                split_words.remove("") #filtert alle leerzeichen im text raus

            if remove_stop_words:
                
                split_words_filtered = [word for word in split_words if word not in stop_words and not not_relevant.search(word) and not (len(word) == 1 and word.isalpha())] #schmeißt alle stopwords, irrelevanten Zeichen, sowie einzelne Buchstaben raus

                return split_words_filtered

            return split_words
        
        else: #unterteilt text in sätze

            content_replace = re.sub("\s+", " ", content_strip) #entfernt newline, tab und komprimiert diese zu normalen leerzeichen

            content_further_seperated = re.split("\.\s*", content_replace) #separiert content nach "."-zeichen

            return content_further_seperated


    def dataframe_construction_td_idf(metadata_contract: dict): #implements necessary DatFrames for relevant words

        #relevant_contracts als auch die test_... listen dienen nur der besseren orientierung, in benutzung für die berechnung der IDF Werte
        #stehen nur die indice listen

        relevant_contracts: list = [0, 2, 17, 24, 27, 31, 39, 41, 43, 53, 54, 55, 62, 65, 68, 69, 70, 71, 75, #indices of the relevant contract types
                                77, 78, 85, 88, 90, 91, 94, 101, 103, 107, 111, 112, 115, 116, 120, 122, 132,
                                134, 136, 153, 155, 158, 160, 163, 164, 167, 171, 174, 175, 183, 188, 191,
                                194, 198, 200, 216, 219, 223, 224, 228, 230, 232, 235, 237, 239, 241, 242, 247,
                                249, 254, 260, 262, 263, 266, 280, 293, 297, 304, 309, 310, 311, 313, 315,
                                325, 327, 343, 348, 359, 366, 368, 369, 376, 379, 388,
                                396, 398, 399, 400, 406, 413, 417, 429, 432, 443, 447, 455, 457, 458, 460, 469,
                                471, 474, 478, 481, 486, 493, 498, 500, 505, 506]

    
        service_indices = [17, 24, 48, 53, 55, 58, 75, 78, 103, 122, 160, 179, 200, 210, 212, 235, 278, 285, 309, 325,
                           406, 455, 457, 460, 506]
    
        distributor_indices = [0, 85, 88, 89, 101, 120, 134, 136, 153, 155, 164, 167, 198, 216, 240, 260, 262, 297,
                           310, 311, 340, 359, 366, 369, 379, 447, 458, 471, 493]
    
        supply_indices = [2, 54, 70, 107, 115, 143, 183, 188, 219, 239, 242, 313, 376, 399, 417]

        outsourcing_indices = [41, 62, 65, 68, 69, 132, 175, 266, 304, 348, 400, 443, 478, 481, 486]
    
        license_indices = [27, 39, 43, 77, 94, 112, 158, 163, 174, 191, 228, 230, 247, 249, 280, 327, 343,
                        368, 388, 396, 398, 413, 429, 432, 445, 469, 474, 489, 500, 505]

        test_license = [436, 306, 146]

        test_distributor = [67, 345, 265]

        test_outsourcing = [337, 99, 391]

        test_service = [385, 356, 248]

        test_supply = [378, 169, 16]

        #setup of basic foundation

        contract_indices = {
            "service agreement": service_indices,
            "distributor agreement": distributor_indices,
            "supply agreement": supply_indices,
            "outsourcing agreement": outsourcing_indices,
            "license agreement": license_indices
        }

        selected_indices = contract_indices.get(metadata_contract["contract_type"].lower())

        if selected_indices is None:
            raise ValueError("Fehler bei Korpus-Matching")

        sentence_dataset = {}

        for z in range(len(metadata_contract["listlist_of_pages"])):
            splitup_text: str = pre_processing(text_given = metadata_contract["listlist_of_pages"][z][0])
            page_number = metadata_contract["listlist_of_pages"][z][1]
            for i in range(len(splitup_text)):
                sentence_id = f"S{page_number}L{i}" #durch Variable ersetzt wie Alex vorgeschlagen -> noch in process_data übernehmen
                sentence_dataset[sentence_id] = {}
                sentence_dataset[sentence_id]["id"] = sentence_id
                sentence_dataset [sentence_id]["text"] = splitup_text[i]
                sentence_dataset [sentence_id]["page"] = page_number #durch Variable ersetzt wie Alex vorgeschlagen -> noch in process_data übernehmen
        df = pd.DataFrame.from_dict(sentence_dataset, orient="index")      

        df["words"] = df["text"].apply(lambda x: pre_processing(text_given=x, solo_words=True, remove_stop_words=True)) #Erstellung einer von stop_words gefilterten Wort Zeile

        #calculation of tf
        all_words = df["words"].explode() #pandas series jedes wort einzelner eintrag
        general_amount_of_words: int = len(all_words) #zählen alle einträge für amount of all words
        frequence_words = all_words.value_counts()
        tf_df = frequence_words.reset_index()
        tf_df.columns = ["word", "amount_of_word"]
        tf_df["word_amount_overall"] = general_amount_of_words
        tf_df["tf"] = tf_df["amount_of_word"]/tf_df["word_amount_overall"] #calculation of tf


        #calculation of IDF
        idf_foundation = [] #entwurf des vorherigen dataframes diesmal allerdings nur als foundation für den idf score
        for i in range(len(selected_indices)): #evtl. später zu globalem score ändern
            output = summary["data"][selected_indices[i]]
            paragraphs = output.get("paragraphs") 
            for item in paragraphs:
                content = item["context"]
            idf_foundation.append({
                "contract": f"C{selected_indices[i] + 1}",
                "text": content
            })
        idf_df = pd.DataFrame(idf_foundation)
        idf_df["words"] = idf_df["text"].apply(lambda x: pre_processing(text_given = x, solo_words= True, remove_stop_words= True))
            

        idf_df["words"] = idf_df["words"].apply(set)
        amount_of_contracts = len(idf_df)
        df_words = idf_df.explode("words").dropna(subset=["words"]) #entfernt leere Zeilen, allerdings nur für Kategorie words
        word_share_in_contracts = df_words["words"].value_counts() #erstellen Pandas series mit Wert we oft Wort über Verträge verteilt vorkommt
        word_statistics = word_share_in_contracts.reset_index() #erstellt einen DatFrame aus dieser Series
        word_statistics.columns = ["word", "share"] #bennent die Spalten des DataFrames
        word_statistics["contract_proportion"] = amount_of_contracts/word_statistics["share"]
        word_statistics["idf-value"] = numpy.log10(word_statistics["contract_proportion"])

        #calculation of TF-IDF
        merged_all_in_all = pd.merge(tf_df, word_statistics, on="word")
        merged_all_in_all["TF-IDF"] = merged_all_in_all["tf"]*merged_all_in_all["idf-value"]
        merged_all_in_all = merged_all_in_all.drop_duplicates(subset=["word"])

        merged_all_in_all = merged_all_in_all[merged_all_in_all["TF-IDF"] != 0] #removes every row where the 'TF-IDF' value is equal to zero

        #jedem wort, id + zugehörige page zuteilen

        word_locations = (df[["id", "page", "text", "words"]].explode("words").rename(columns={"words": "word"}))
        word_locations = word_locations.drop_duplicates(subset=["id", "word"])

        tf_idf_relevant = pd.merge(merged_all_in_all[["word", "TF-IDF"]], word_locations, on="word", how="inner")

        return tf_idf_relevant

    def assign_tf_idf_percentile_scaling(percentile: float): #matching according levels to tf-idf scoring
        if pd.isna(percentile):
            return "value not available"
        if percentile >= 0.90:
            return "very high"
        if percentile >= 0.75:
            return "high"
        if percentile >= 0.50:
            return "moderate"

        return "low"

    def calculate_whole_sentence_tfidf(tfidf_df: pd.DataFrame): #berechnung des tf-idf scores für ganzen satz mittels formel
        word_df = tfidf_df[["id", "page", "text", "word", "TF-IDF"]].copy()
        word_df["TF-IDF"] = (pd.to_numeric(word_df["TF-IDF"], errors="coerce").fillna(0.0)) #falls kein TF-IDF Wert gegeben durch 0.0 ersetzt
        word_df = (word_df.dropna(subset=["word"]).drop_duplicates(subset=["id", "page", "word"]))
        sentence_df = (word_df.groupby(["id", "page", "text"], as_index=False).agg(tfidf_sum=("TF-IDF", "sum"), word_count=("word", "nunique")))
        sentence_df["tfidf_sentence_score"] = (sentence_df["tfidf_sum"]/sentence_df["word_count"]) #berechnung/erstellung der eigentlichen formel-spalte

        #genauere berechnung perzentile 

        sentence_df["tfidf_percentile"] = float("nan") #leere percentile spalte wird angelegt
        positive_scores = sentence_df["tfidf_sentence_score"] > 0 #berechnet den rang nur für positive werte -> damit sätze die wert von 0 haben nicht ins gewicht fallen
        sentence_df.loc[positive_scores, "tfidf_percentile"] = (sentence_df.loc[positive_scores, "tfidf_sentence_score"].rank(pct=True)) #berechnung des anteils (percentil)
        sentence_df["tfidf_level"] = (sentence_df["tfidf_percentile"].apply(assign_tf_idf_percentile_scaling)) #mapping of scaling to values
        return sentence_df

    def attach_tfidf_to_risks(risk_df: pd.DataFrame, sentence_tfidf_df: pd.DataFrame): #hinzufügen von berechneten td-idf werten an gefundenen risikowörtern
        grouped_risk_df = (risk_df.groupby(["id", "page", "text", "risk_category"], as_index=False).agg(risk_words=("word", lambda words: list(dict.fromkeys(words))))) #gruppen nach kategorien und lambda entfernt doppelte wörter
        sentence_information = sentence_tfidf_df[["id", "page", "tfidf_sentence_score", "tfidf_percentile", "tfidf_level"]]
        ultimate_risk_df = pd.merge(grouped_risk_df, sentence_information, on=["id", "page"], how="left")
        return ultimate_risk_df
