from read_dataset import gain_access
import re
from risk_scaling import risk_field, risk_scoring
from collections import Counter #musste installiert werden
import pandas as pd #musste installiert werden
import nltk #musste installiert werden - momentan noch nicht in benutzung
from nltk.corpus import stopwords #nicht in Benutzung

right_dataset = {
     
    "sentence": [],
    "sentence_id": [],
    "risk_words": [], #words with counting
    "PMI_Score": [],

}


dataset = {

    "risk-word": [],
    "risk-sentence": [],
    "TF-IDF_characteristic": [],  #which technique of those two more important
    "word_id": []

}


dataset_financial = {

    "risk-word": [],
    "risk-sentence": [],
    "general_frequence" : [],
    "relative_frequence": [],
    "co-occurence": [],
    "subcategory": [] #müssen noch erstellt werden

}

dataset_operative = {

    "risk-word": [],
    "risk-sentence": [],
    "general_frequence" : [],
    "relative_frequence": [],
    "co-occurence": [],
    "subcategory": [] #müssen noch erstellt werden

}

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


def pre_processing(i: int, solo_words: bool, remove_stop_words: bool): #preprocesses the contract and either returns a list of all words - or sentences used in the contract
    contract_type: str
    parentcompany_of_contract: str
    content: str 
    
    stop_words = set(stopwords.words('english'))

    _, _, content = gain_access(i) #gain access fuction liefert contract_type, parentcompany_of_contract, content von vertrag

    content_low: str= content.lower() #transformiert content komplett in lower case

    content_strip: str = content_low.strip() #entfernt leerzeichen am anfang und am ende

    if solo_words: #unterteilt text in wörter

        content_replace = re.sub('\n|\t', "", content_strip) #entfernt newline and tab zeichen im text

        split_words = re.split(r"\s", content_replace) #teilt text nach leerzeichen

        while "" in split_words: #solange leerzeichen vorhanden

            split_words.remove("") #filtert alle leerzeichen im text raus

        if remove_stop_words:
             
            split_words_filtered = [word for word in split_words if word not in stop_words]

            return split_words_filtered

        return split_words
    
    else: #unterteilt text in sätze

        content_replace = re.sub('\s', "", content_strip) #entfernt newline, tab und leer zeichen im text

        content_further_seperated = re.split("\.", content_replace) #separiert content nach "."-zeichen

        return content_further_seperated



def filter(i: int): # filters the contract according to specific words, muss noch in direktes pdf reading umgewandelt werden

    possible_financial_arguments: list = []
    possible_financial_arguments_words: list = []

    possible_positive_arguments: list = []
    possible_positive_arguments_words: list = []

    possible_legal_arguments: list = []
    possible_legal_arguments_words: list = []

    possible_operative_arguments: list = []
    possible_operative_arguments_words: list = []

    content_further_seperated = pre_processing(i, False)

    legal_list : list = []

    #legal terms search
    for i in range(len(content_further_seperated)):
            if legal_list := re.findall(r"\bliabilit(y|ies)|liable(ness)|claim(s|ed|ing)|"
                r"cancel(led|ed|ling|ing|lation(s))|penal(ty|ties)|punitive|arbitrat(or(s)|ion(s))|media(te(d)|ting|tor(s)|tion(s))|"
                r"disput(es|ed|ing)|fail(ure(s)|ed|ing)|indemni(fy(ing)|fie(s|d)|fication|ty|ties)|" 
                r"force[-]majeure|act(s)ofgod|breach(es|ed|ing)|(hold|held)harmless|waiv(er(s)|e(d)|ing)|terminat(ion(s)|e(d)|ing)|"
                r"default(s|ed|ing)|sabotag(e(d)|ing)|war(s)|injunction(s)|restrain(ed|ing)|infring(e|ed|ing|ement(s))|"
                r"misconduct(ed|ing|s)|violat(ion(s)|e(d)|ing)\b", content_further_seperated[i], re.I):
                    right_dataset["risk-sentence"].append(content_further_seperated[i])
                    right_dataset["risk-words"].append(legal_list)
                    possible_legal_arguments.append(content_further_seperated[i])
                    possible_legal_arguments_words.append(legal_list)

    for i in range(len(content_further_seperated)):
        if legal_word := re.search(r"\bliabilit(y|ies)|liable(ness)|claim(s|ed|ing)|"
            r"cancel(led|ed|ling|ing|lation(s))|penal(ty|ties)|punitive|arbitrat(or(s)|ion(s))|media(te(d)|ting|tor(s)|tion(s))|"
            r"disput(es|ed|ing)|fail(ure(s)|ed|ing)|indemni(fy(ing)|fie(s|d)|fication|ty|ties)|" 
            r"force[-]majeure|act(s)ofgod|breach(es|ed|ing)|(hold|held)harmless|waiv(er(s)|e(d)|ing)|terminat(ion(s)|e(d)|ing)|"
            r"default(s|ed|ing)|sabotag(e(d)|ing)|war(s)|injunction(s)|restrain(ed|ing)|infring(e|ed|ing|ement(s))|"
            r"misconduct(ed|ing|s)|violat(ion(s)|e(d)|ing)\b", content_further_seperated[i], re.I):
                dataset_legal["risk-sentence"].append(content_further_seperated[i])
                dataset_legal["risk-word"].append(legal_word.group())
                possible_legal_arguments.append(content_further_seperated[i])
                possible_legal_arguments_words.append(legal_word.group())

    #financial terms search
    for i in range(len(content_further_seperated)):
        if financial_word := re.search(r"\bpay(able|s|d|ment(s)|(un|pre[- ])paid)|LC(s)|" 
            r"letter(s)ofcredit|(un)insur(ance(s)|e(s|d)|ing|able|ured)|(un)cover(age(s)|ed|ing)|indemni(fy(ing)|fie(s|d)|fication|ty|ties)|"
            r"damag(e(s|d)|ing)|repurchas(ing|e(s|d))|CPI(s)|ConsumerPriceInd(ex|ices)|"
            r"terminat(ion(s)|e(s|d)|ing)|default(s|ed|ing)|(infringe(ment(s)|(s|d))|infringing)|fee(s)|charg(e(s|d)|ing)|cover(age|ing|ed|s)|"
            r"los(s(es)|e|es|t|ing)|expense(s|d)\b", content_further_seperated[i], re.I):
                possible_financial_arguments.append(content_further_seperated[i])
                possible_financial_arguments_words.append(financial_word.group())


    #operative terms search
    for i in range(len(content_further_seperated)):
        if operative_word := re.search(r"\binspect(ion(s)|ing|ed|s|able)|delay(ing|ed|s)|(non-)exclusiv(ely|ity)|warrant(y|ies|ing|ed|s)|"
            r"(non-)confid(ential(ity)|e(s|d)|ing)|(low-)quali(ty|ties|f(ie(s|d)|y(ing)))|injunction(s)|restrain(s|ed|ing(order(s)))|"
            r"disclos(ure(s)|e(s|d)|ing)|misle(d|ad(ing|s))|untrue|omi(t(ted|ting|s)|ssion(s))\b", content_further_seperated[i], re.I):
                possible_operative_arguments.append(content_further_seperated[i])
                possible_operative_arguments_words.append(operative_word.group())

    #NEU - positive Bonus in Risk Scaling soon to be implemented

    # for i in range(len(content_further_seperated)):
    #     if positive_word := re.search(r"\blimited liability|liability shall not exceed|maximum liability|cap on liability\b", content_further_seperated[i], re.I):
    #            possible_positive_arguments.append(content_further_seperated[i])
    #            possible_positive_arguments_words.append(positive_word.group())


    risk_setting_fin = 5
    risk_setting_leg = 5
    risk_setting_op = 3

    total_risk_fin = risk_setting_fin * len(possible_financial_arguments)
    total_risk_leg = risk_setting_leg * len(possible_legal_arguments)
    total_risk_op = risk_setting_op * len(possible_operative_arguments)

    total_length = len(possible_operative_arguments) + len(possible_legal_arguments) + len(possible_financial_arguments)

    overall_risk = calculation_risk_score(total_risk_fin, total_risk_leg, total_risk_op, total_length)

    setting_dic_details()

    print(fr"legal:", "\n" , fr"{possible_legal_arguments}")
    print(fr"finacial:", "\n" , fr"{possible_financial_arguments}")
    print(fr"operative:", "\n" , fr"{possible_operative_arguments}")

    print("Approximate risk score: %f" % overall_risk)

    print(fr""" current Risk-Word: {dataset_legal.get("Risk-Word")[1]} for""", "\n", fr"""current Risk-Sentence: {dataset_legal.get("Risk-Sentence")[1]}""")



def most_used_words(): #analyses the most used words in the entire contract for a given list of contracts
    relevant_contracts: list = [0, 2, 16, 17, 24, 27, 31, 39, 41, 43, 53, 54, 55, 62, 65, 67, 68, 69, 70, 71, 75,
                                77, 78, 85, 88, 90, 91, 94, 99, 101, 103, 107, 111, 112, 115, 116, 120, 122, 132,
                                134, 136, 146, 153, 155, 158, 160, 163, 164, 167, 169, 171, 174, 175, 183, 188, 191,
                                194, 198, 200, 216, 219, 223, 224, 228, 230, 232, 235, 237, 239, 241, 242, 247, 248,
                                249, 254, 260, 262, 263, 265, 266, 280, 293, 297, 304, 306, 309, 310, 311, 313, 315,
                                325, 327, 337, 343, 345, 348, 356, 359, 366, 368, 369, 376, 378, 379, 385, 388, 391,
                                396, 398, 399, 400, 406, 413, 417, 429, 432, 436, 443, 447, 455, 457, 458, 460, 469,
                                471, 474, 478, 481, 486, 493, 498, 500, 505, 506]

    words_of_contract = pre_processing(31, True, True)

    counter = Counter(words_of_contract)

    totalcount_words = counter.total()

    most_used = counter.most_common(500)

    print(most_used)

def calculation_risk_score(financial: int, legal:int, operativ: int, length: int):
    return (financial+legal+operativ)/length #nochmal minus positive/length

def setting_dic_details():

     words_of_contract = pre_processing(31, True, True)

     counter = Counter(words_of_contract)

    # totalcount_words = counter.total()

    # relative_word_percentage = counter_current_word/totalcount_words


def td_idf(words_in_total: int):

    #wie oft einzelnes wort allgemein vorkommt durch allgemeine anzahl an wörtern

    #+ berechen einzelnes wort und allgemeine risikowörter

    #+ co-occurence berechnen: wieviele riskowörter in einem satz

    #+ positive dämpfung + prompt einbauen 

    #(+ optional bereits aufsetzen von DataFrame strukturen)
     
    return None

most_used_words() #-> needed for further construction of pre-processing filters





#filter(16)

#print(pre_processing(0, True))


    

    #filter liste nach teilen die zahlen beinhalten
    # for i in range(len(content_further_seperated)):
    #     if re.search(r"\d", content_further_seperated[i], re.I):
    #         possible_financial_arguments.append(content_further_seperated[i])

    # #filter liste nach teilen die legal terms beinhalten
    # for i in range(len(content_further_seperated)):
    #     if re.search(r"liability|termination|clause|condition", content_further_seperated[i], re.I):
    #         possible_legal_arguments.append(content_further_seperated[i])

    #print(content_further_seperated)
    #print(possible_financial_arguments)
   # print(possible_legal_arguments)

#filter(0)



