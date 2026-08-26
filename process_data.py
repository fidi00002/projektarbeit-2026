import re
import pandas as pd
from nltk.corpus import stopwords

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

#function only accepts key_words due to '*'
    #function only accepts key_words due to '*'
def pre_processing(*, text_given = str, solo_words: bool = False, remove_stop_words: bool = False): #preprocesses the contract and either returns a list of all words - or sentences used in the contract
    contract_type: str
    parentcompany_of_contract: str
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

    risk_word_df = risk_word_df.drop_duplicates(subset=["id", "word", "risk_category"])

    return risk_word_df


         


def filter(text: str = "", sentence_id: str = ""): # filters the contract according to specific words, muss noch in direktes pdf reading umgewandelt werden

    legal_list: list = re.findall(
        r"\b(?:"
        r"liabilit(?:y|ies)|liable(?:ness)?|"
        r"claim(?:s|ed|ing)?|"
        r"indemni(?:fy|fies|fied|fying|fication|ty|ties)|"
        r"defend\s+and\s+indemnify|"
        r"(?:hold|held)\s+harmless|"
        r"uncapped\s+liability|unlimited\s+liability|"
        r"limitation(?:s)?\s+of\s+liabilit(?:y|ies)|liability\s+cap(?:s)?|cap(?:s)?\s+on\s+liabilit(?:y|ies)|"
        r"damag(?:e|es|ed|ing)|"
        r"penal(?:ty|ties)|fine(?:s)?|sanction(?:s|ed|ing)?|"
        r"breach(?:es|ed|ing)?|"
        r"(?:event\s+of\s+)?default(?:s|ed|ing)?|" #Verzug
        r"fail(?:s|ed|ing|ure(?:s)?)?|"
        r"remed(?:y|ies)|"
        r"waiv(?:e|es|ed|er(?:s)?|ing)|"
        r"release(?:s|d|ing)?|"
        r"disclaim(?:s|ed|er(?:s)?|ing)?|"
        r"injunction(?:s)?|injunctive|"
        r"restrain(?:s|ed|ing)?|"
        r"terminat(?:e|es|ed|ing|ion(?:s)?)|"
        r"terminate\s+without\s+(?:cause|notice)|"
        r"immediate\s+termination|"
        r"cancel(?:s|led|ling|ed|ing|lation(?:s)?)?|"
        r"auto(?:matic)?\s+renewal|"
        r"disput(?:e|es|ed|ing)?|"
        r"arbitrat(?:e|es|ed|ing|ion(?:s)?|or(?:s)?)|"
        r"mediat(?:e|es|ed|ing|ion(?:s)?|or(?:s)?)|"
        r"litigat(?:e|es|ed|ing|ion(?:s)?)|"
        r"assign(?:s|ed|ing|ment(?:s)?)|"
        r"exclusiv(?:e|ely|ity)|"
        r"restrict(?:ed|ing|ion(?:s)?)|"
        r"no(?:n)?\s*competition(?:s)?|"
        r"patent(?:s)?|"
        r"copyright(?:s)?|"
        r"trademark(?:s)?|"
        r"infring(?:e|es|ed|ing|ement(?:s)?)|"
        r"misappropriat(?:e|es|ed|ing|ion(?:s)?)|"
        r"licens(?:e|es|ed|ing)|"
        r"sublicens(?:e|es|ed|ing)|"
        r"field\s+of\s+use|"
        r"exclusive\s+license|"
        r"irrevocable|perpetual|"
        r"confidential(?:ity)?|confidential\s+information(?:s)?|"
        r"disclos(?:e|es|ed|ing|ure(?:s)?)|"
        r"misconduct|"
        r"violat(?:e|es|ed|ing|ion(?:s)?)|"
        r"negligen(?:ce|t)|"
        r"fraud(?:ulent)?|"
        r"illegal|"
        r"unlawful|"
        r"audit(?:s|ed|ing)?|"
        r"audit\s+right(?:s)?|"
        r"right\s+of\s+refusal|"
        r"right\s+of\s+negotiation"
        r")\b", text, re.I)

    financial_list: list = re.findall(
        r"\b(?:"
        r"pay(?:s|able|ment(?:s)?|ing)?|"
        r"paid|unpaid|prepaid|prepayment(?:s)?|"
        r"payment\s+term(?:s)?|payment(?:s)?\s+due|"
        r"past\s+due|overdue|"
        r"invoice(?:s|d|ing)?|billing|billable|"
        r"price(?:s|d|ing)?|"
        r"purchase\s+price|"
        r"price\s+increase|"
        r"price\s+decrease|"
        r"price\s+adjustment|"
        r"price\s+restriction|"
        r"cost(?:s)?|"
        r"expense(?:s)?|"
        r"fee(?:s)?|"
        r"charg(?:e|es|ed|ing)|"
        r"surcharge(?:s)?|"
        r"reimburse(?:s|d|ment(?:s)?)?|"
        r"refund(?:s|ed|ing)?|"
        r"credit(?:s|ed)?|"
        r"margin(?:s)?|"
        r"royalt(?:y|ies)|"
        r"royalty\s+rate(?:s)?|"
        r"minimum\s+royalty|"
        r"license\s+fee(?:s)?|"
        r"milestone\s+payment(?:s)?|"
        r"upfront\s+(?:fee|payment)|"
        r"revenue\s+shar(?:e|es|ed|ing)|"
        r"profit\s+shar(?:e|es|ed|ing)|"
        r"commission(?:s)?|"
        r"sale(?:s)?\s+target(?:s)?|"
        r"sale(?:s)?\s+quota(?:s)?|"
        r"minimum\s+sale(?:s)?|"
        r"minimum\s+purchase(?:s)?|"
        r"minimum\s+order(?:s)?|"
        r"minimum\s+spend|"
        r"purchase\s+commitment(?:s)?|"
        r"chargeback(?:s)?|"
        r"purchase\s+order(?:s)?|"
        r"minimum\s+quantit(?:y|ies)|"
        r"forecast(?:s|ed|ing)?|"
        r"shortfall(?:s)?|"
        r"deficien(?:cy|cies)|"
        r"storage\s+cost(?:s)?|"
        r"shipping\s+cost(?:s)?|"
        r"dut(?:y|ies)|"
        r"damag(?:e|es|ed|ing)|"
        r"termination\s+fee(?:s)?|"
        r"cancellation\s+fee(?:s)?|"
        r"late\s+fee(?:s)?|"
        r"late\s+payment(?:s)?|"
        r"penal(?:ty|ties)|"
        r"indemni(?:fy|fies|fied|fying|fication|ty|ties)|"
        r"los(?:s|ses|e|es|t|ing)|"
        r"claim(?:s|ed|ing)?|"
        r"settlement(?:s)?|"
        r"insur(?:ance(?:s)?|e|es|ed|ing|er(?:s)?|able|ured)|"
        r"cover(?:age(?:s)?|ed|ing|s)?|"
        r"guarantee(?:s|d|ing)?|"
        r"LC(?:s)?|letter(?:s)?\s+of\s+credit|"
        r"CPI(?:s)?|consumer\s+price\s+ind(?:ex|ices)|"
        r"inflation|"
        r"exchange\s+rate(?:s)?|"
        r"currency|"
        r"foreign\s+exchange|FX|"
        r"tax(?:es|ation)?|"
        r"VAT|"
        r"sales\s+tax|"
        r"insolvenc(?:y|ies)|insolvent|"
        r"bankrupt(?:cy|cies)?|"
        r"solven(?:cy|t)|"
        r"creditworthiness"
        r")\b", text, re.I)

    operative_list: list = re.findall(
        r"\b(?:"
        r"perform(?:s|ed|ing|ance)?|non\s*performance|"
        r"service\s+level(?:s)?|service\s+level\s+agreement(?:s)?|SLA(?:s)?|"
        r"KPI(?:s)?|"
        r"performance\s+standard(?:s)?|"
        r"performance\s+target(?:s)?|"
        r"uptime|downtime|"
        r"availability|unavailability|"
        r"fail(?:s|ed|ing|ure(?:s)?)?|"
        r"delay(?:s|ed|ing)?|"
        r"late\s+delivery|"
        r"interruption(?:s)?|"
        r"disruption(?:s)?|"
        r"outage(?:s)?|"
        r"service\s+interruption|"
        r"service\s+failure|"
        r"suspend(?:s|ed|ing)?|suspension|"
        r"shutdown(?:s)?|"
        r"deliver(?:s|ed|ing|y|ies)|"
        r"shipment(?:s)?|shipping|"
        r"lead\s+time(?:s)?|"
        r"shortage(?:s)?|"
        r"supply\s+shortage(?:s)?|"
        r"allocation(?:s)?|"
        r"capacity|"
        r"production|"
        r"manufactur(?:e|es|ed|ing|er(?:s)?)|"
        r"backorder(?:s|ed)?|"
        r"forecast(?:s|ed|ing)?|"
        r"purchase\s+order(?:s)?|"
        r"minimum\s+order|minimum\s+quantity|"
        r"inspect(?:s|ed|ing|ion(?:s)?|able)?|"
        r"(?:low\s+)?qualit(?:y|ies)|"
        r"defect(?:s|ive)?|"
        r"(?:non\s+)?conform(?:s|ed|ing|ity)?|"
        r"specification(?:s)?|"
        r"reject(?:s|ed|ing|ion(?:s)?)?|"
        r"accept(?:s|ed|ing|ance)?|"
        r"warrant(?:s|ed|ing|y|ies)|"
        r"guarantee(?:s|d|ing)?|"
        r"repair(?:s|ed|ing)?|"
        r"replace(?:s|d|ment(?:s)?)?|"
        r"recall(?:s|ed|ing)?|"
        r"return(?:s|ed|ing)?|"
        r"remed(?:y|ies)|"
        r"(?:non\s*?)?exclusiv(?:e|ely|ity)|"
        r"disclos(?:e|es|ed|ing|ure(?:s)?)|"
        r"untrue|"
        r"omi(?:t|ts|tted|tting|ssion(?:s)?)|"
        r"restrain(?:s|ed|ing)?|"
        r"recovery\s+plan(?:s)?|"
        r"backup(?:s)?|"
        r"restore(?:s|d|ing)?|restoration|"
        r"outsource(?:s|d|ing)?|outsourcing|"
        r"supplier(?:s)?|vendor(?:s)?|"
        r"data\s+loss(?:es)?|"
        r"data\s+breach(?:es)?|"
        r"security\s+breach(?:es)?|"
        r"cyber(?:security)?|"
        r"system\s+failure(?:s)?|"
        r"system\s+availabilit(?:y|ies)?|"
        r"software\s+failure(?:s)?|"
        r"network\s+failure(?:s)?|"
        r"force\s+majeure|"
        r"act(?:s)?\s+of\s+god|"
        r"pandemic(?:s)?|"
        r"epidemic(?:s)?|"
        r"natural\s+disaster(?:s)?|"
        r"fire(?:s)?|flood(?:s|ed|ing)?|earthquake(?:s)?|"
        r"war(?:s)?|"
        r"terror(?:ism)?"
        r")\b", text, re.I)


    sentence_dataset[f"{sentence_id}"]["financial_risk_words"] = financial_list
    sentence_dataset[f"{sentence_id}"]["legal_risk_words"] = legal_list
    sentence_dataset[f"{sentence_id}"]["operative_risk_words"] = operative_list

    return None

#INAKTIV, nur benutzt für Regex Pattern Build Up

# def most_used_words(i : int): #analyses the most used words in the entire contract for a given list of contracts
#     relevant_contracts: list = [0, 2, 16, 17, 24, 27, 31, 39, 41, 43, 53, 54, 55, 62, 65, 67, 68, 69, 70, 71, 75,
#                                 77, 78, 85, 88, 90, 91, 94, 99, 101, 103, 107, 111, 112, 115, 116, 120, 122, 132,
#                                 134, 136, 146, 153, 155, 158, 160, 163, 164, 167, 169, 171, 174, 175, 183, 188, 191,
#                                 194, 198, 200, 216, 219, 223, 224, 228, 230, 232, 235, 237, 239, 241, 242, 247, 248,
#                                 249, 254, 260, 262, 263, 265, 266, 280, 293, 297, 304, 306, 309, 310, 311, 313, 315,
#                                 325, 327, 337, 343, 345, 348, 356, 359, 366, 368, 369, 376, 378, 379, 385, 388, 391,
#                                 396, 398, 399, 400, 406, 413, 417, 429, 432, 436, 443, 447, 455, 457, 458, 460, 469,
#                                 471, 474, 478, 481, 486, 493, 498, 500, 505, 506]

    
#     service_indices = [17, 24, 48, 53, 55, 58, 75, 78, 103, 122, 160, 179, 200, 210, 212, 235, 248, 278, 285, 309, 325,
#                         356, 385, 406, 455, 457, 460, 506]
    
#     distributor_indices = [0, 67, 85, 88, 89, 101, 120, 134, 136, 153, 155, 164, 167, 198, 216, 240, 260, 262, 265, 297,
#                            310, 311, 340, 345, 359, 366, 369, 379, 447, 458, 471, 493]
    
#     supply_indices = [2, 16, 54, 70, 107, 115, 143, 169, 183, 188, 219, 239, 242, 313, 376, 378, 399, 417]

#     outsourcing_indices = [41, 62, 65, 68, 69, 99, 132, 175, 266, 304, 337, 348, 391, 400, 443, 478, 481, 486]
    
#     license_indices = [27, 39, 43, 77, 94, 112, 146, 158, 163, 174, 191, 228, 230, 247, 249, 280, 306, 327, 343,
#                         368, 388, 396, 398, 413, 429, 432, 436, 445, 469, 474, 489, 500, 505]

#     words_of_contract = pre_processing(i, solo_words=True, remove_stop_words=True)

#     counter = Counter(words_of_contract)

#     totalcount_words = counter.total()

#     most_used = counter.most_common(500)

#     print(most_used)

#     return None




    











