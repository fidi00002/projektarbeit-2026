#from read_dataset import gain_access
import re
from collections import Counter #musste installiert werden
import pandas as pd #musste installiert werden
import nltk #musste installiert werden - momentan noch nicht in benutzung
from nltk.corpus import stopwords #nicht in Benutzung
#from pandas_save import pre_processing, dataframe_construction_td_idf

# sentence_dataset_represantation_example = {
     
#     sentence_id = {
#         "sentence_id": [],
#         "sentence": [],
#         "legal list": []
#         "financial list": []
#         "operative list": []
#         "page_number": [],
#         "line": []
#     }

# }

sentence_dataset = {} #benutztes dict in creation_of_dictionary

dataset_content = {

    "risk-word": [],
    "risk-sentence": [],
    "general_frequence" : [],
    "relative_frequence": [],
    "co-occurence": [],
    "subcategory": [] #müssen noch erstellt werden

}

dataset_positive = {

    "risk-word": [],
    "risk-sentence": [],
    "general_frequence" : [],
    "relative_frequence": [] #maybe ratio to risk words?

}

dataset_general_IMPORTANT = {
     
    "category_distribution": {
         
        "financial": 0,
        "legal": 0,
        "operative": 0

    },
    "most_used_words": [],
    "Words_per_categorie": [],
    "risk-score_in_total": []

}

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
    
#an dictionary structure mit einzelnen seiten denken
def creation_of_dictionary(metadata_contract: dict) -> pd.DataFrame:
    for z in range(len(metadata_contract["listlist_of_pages"])):
        splitup_text: str = pre_processing(text_given = metadata_contract["listlist_of_pages"][z][0])
        for i in range(len(splitup_text)):
            sentence_id: str = fr"""S{metadata_contract["listlist_of_pages"][z][1]}L{i}"""
            sentence_dataset[f"{sentence_id}"] = {}
            sentence_dataset[f"{sentence_id}"]["id"] = sentence_id
            filter(splitup_text[i], sentence_id) #adds list for financial, legal and operative risks
            sentence_dataset [f"{sentence_id}"]["text"] = splitup_text[i]
            sentence_dataset [f"{sentence_id}"]["page"] = metadata_contract["listlist_of_pages"][z][1]
    df = pd.DataFrame.from_dict(sentence_dataset, orient="index")
    df["risk_words_general"] = df[["financial_risk_words", "legal_risk_words", "operative_risk_words"]].apply(lambda row: sum(row, []), axis = 1) #zusammenfassen der einzelnen risk_words-spalten mittels sum auf listen '[]' und zeilen bezogen und axis=1 bedeutet zeile für zeile
    relevant_df = df[df["risk_words_general"].apply(lambda x: len(x)>0)] #neues df bei denen nur zeilen übernommen werden, welche risk words abgespeichert haben

    financial_df = (relevant_df[["id", "page", "text", "financial_risk_words"]].explode("financial_risk_words").rename(columns={"financial_risk_words": "word"}).dropna(subset=["word"]))
    financial_df["risk_category"] = "financial"

    legal_df = (relevant_df[["id", "page", "text", "legal_risk_words"]].explode("legal_risk_words").rename(columns={"legal_risk_words": "word"}).dropna(subset=["word"]))
    legal_df["risk_category"] = "legal"

    operative_df = (relevant_df[["id", "page", "text", "operative_risk_words"]].explode("operative_risk_words").rename(columns={"operative_risk_words": "word"}).dropna(subset=["word"]))
    operative_df["risk_category"] = "operative"

    risk_word_df = pd.concat([financial_df, legal_df, operative_df], ignore_index=True)

    #noch zusammenfügen von kategorien programmieren, also wenn wort doppelt vorkommt also in mehreren kategorien diese zusammenfügen statt dopplungen zu entfernen

    risk_word_df = risk_word_df.drop_duplicates(subset=["id", "word", "risk_category"])

    # with pd.option_context("display.max_rows", None):
    #     print(risk_word_df)

    return risk_word_df
    #print(relevant_df.columns)
    # print(df.columns)
        #print(df)


         


def filter(text: str = "", sentence_id: str = ""): # filters the contract according to specific words, muss noch in direktes pdf reading umgewandelt werden

    possible_financial_arguments: list = []
    possible_financial_arguments_words: list = []

    possible_positive_arguments: list = []
    possible_positive_arguments_words: list = []

    possible_legal_arguments: list = []
    possible_legal_arguments_words: list = []

    possible_operative_arguments: list = []
    possible_operative_arguments_words: list = []



    #legal terms search
    #for i in range(len(content_further_seperated)):
    legal_list: list = re.findall(r"\bliabilit(?:y|ies)|liable(?:ness)|claim(?:s|ed|ing)?|"
        r"cancel(?:led|ed|ling(?:s)?|ing|lation(?:s)?)?|penal(?:ty|ties)|punitive|arbitrat(?:or(?:s)?|ion(?:s)?)|media(?:te(?:d)?|ting|tor(?:s)?|tion(?:s)?)|"
        r"disput(?:e(?:s)?|ed|ing(?:s)?)|fail(?:ure(?:s)?|ed|ing(?:s)?)|indemni(?:fy(?:ing)?|fie(?:s|d)|fication|ty|ties)|" 
        r"force(?:[- ]+majeure)|act(?:(?:s)?\s*of\s*god)|breach(?:es|ed|ing)?|(?:hold|held)harmless|waiv(?:er(?:s)?|e(?:d)?|ing)|terminat(?:ion(?:s)?|e(?:d)?|ing)|"
        r"default(?:s|ed|ing)?|sabotag(?:e(?:d)?|ing)|war(?:s)?|injunction(?:s)?|restrain(?:ed|ing(?:s)?)|infring(?:e(?:s)?|ed|ing(?:s)?|ement(?:s)?)|"
        r"misconduct(?:ed|ing(?:s)?|s)?|violat(?:ion(?:s)?|e(?:d)?|ing)\b", text, re.I)

    #financial terms search
    financial_list: list = re.findall(r"\bpay(?:able|s|d|ment(?:s)?)?|(?:un[ -]|pre[- ]+)?paid|LC(?:s)?|" 
        r"letter(?:s)?\s+of\s+credit|insur(?:ance(?:s)|e(?:s|d)?|ing|able|ured)|cover(?:age(?:s)?|ed|ing)|indemni(?:fy(?:ing)?|fie(?:s|d)|fication|ty|ties)|"
        r"damag(?:e(?:s|d)?|ing)|repurchas(?:ing|e(?:s|d)?)|CPI(?:s)?|ConsumerPriceInd(?:ex|ices)|"
        r"terminat(?:ion(?:s)?|e(?:s|d)?|ing)|default(?:s|ed|ing)?|(infringe(?:ment(?:s)?|(?:s|d)?)?|infringing)|fee(?:s)?|charg(?:e(?:s|d)?|ing)|cover(?:age|ing(?:s)?|ed|s)|"
        r"los(?:s(?:es)?|e|es|t|ing)|expense(?:s|d)?\b", text, re.I)             

    #operative terms search
    operative_list: list = re.findall(r"\binspect(?:ion(?:s)?|ing|ed|s|able)?|delay(?:ing|ed|s)?|(?:non[- ])?exclusiv(?:ely|e|ity)|warrant(?:y|ies|ing|ed|s)|"
        r"(?:non[- ])?confid(?:ential(?:ity)?|e(?:s|d)?|ing)|(?:low[- ])?quali(?:ty|ties)|injunction(?:s)?|restrain(?:s|ed|ing\s*(?:order{0,1}(?:s)?)?)?|"
        r"disclos(?:ure(?:s)?|e(?:s|d)?|ing)|misle(?:d|ad(?:ing|s)?)|untrue|omi(?:t(?:ted|ting|s)?|ssion(?:s)?)\b", text, re.I)
                # possible_operative_arguments.append(content_further_seperated[i])
                # possible_operative_arguments_words.append(operative_word.group())

    sentence_dataset[f"{sentence_id}"]["financial_risk_words"] = financial_list
    sentence_dataset[f"{sentence_id}"]["legal_risk_words"] = legal_list
    sentence_dataset[f"{sentence_id}"]["operative_risk_words"] = operative_list

    return None


    #NEU - positive Bonus in Risk Scaling soon to be implemented

    # for i in range(len(content_further_seperated)):
    #     if positive_word := re.search(r"\blimited liability|liability shall not exceed|maximum liability|cap on liability\b", content_further_seperated[i], re.I):
    #            possible_positive_arguments.append(content_further_seperated[i])
    #            possible_positive_arguments_words.append(positive_word.group())


#CALCULATION OF RISK SCORE: IMPORTANT FOR LATER !!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # risk_setting_fin = 5
    # risk_setting_leg = 5
    # risk_setting_op = 3

    # total_risk_fin = risk_setting_fin * len(possible_financial_arguments)
    # total_risk_leg = risk_setting_leg * len(possible_legal_arguments)
    # total_risk_op = risk_setting_op * len(possible_operative_arguments)

    # total_length = len(possible_operative_arguments) + len(possible_legal_arguments) + len(possible_financial_arguments)

    # overall_risk = calculation_risk_score(total_risk_fin, total_risk_leg, total_risk_op, total_length)

    # setting_dic_details()

    # print(fr"legal:", "\n" , fr"{possible_legal_arguments}")
    # print(fr"finacial:", "\n" , fr"{possible_financial_arguments}")
    # print(fr"operative:", "\n" , fr"{possible_operative_arguments}")

    # print("Approximate risk score: %f" % overall_risk)

    # print(fr""" current Risk-Word: {dataset_legal.get("Risk-Word")[1]} for""", "\n", fr"""current Risk-Sentence: {dataset_legal.get("Risk-Sentence")[1]}""")



def most_used_words(i : int): #analyses the most used words in the entire contract for a given list of contracts
    relevant_contracts: list = [0, 2, 16, 17, 24, 27, 31, 39, 41, 43, 53, 54, 55, 62, 65, 67, 68, 69, 70, 71, 75,
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

    words_of_contract = pre_processing(i, solo_words=True, remove_stop_words=True)

    #counter = Counter(words_of_contract)

    #totalcount_words = counter.total()

    #most_used = counter.most_common(500)

    #print(most_used)

    return words_of_contract

def calculation_risk_score(financial: int, legal:int, operativ: int, length: int):
    return (financial+legal+operativ)/length #nochmal minus positive/length

def setting_dic_details():

     words_of_contract = pre_processing(31, True, True)

     counter = Counter(words_of_contract)

    # totalcount_words = counter.total()

    # relative_word_percentage = counter_current_word/totalcount_words




    











