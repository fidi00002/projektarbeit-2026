import pandas as pd

#speichern von DataFrames mit Kategorie, Risikowort, Risikosatz und allgemeiner Score des gepeicherten Mediums

#genaue Ausarbeitung allerdings noch unklar

#eventuell nur oder mit zusätzlich wörtern die auch "positiv" gewertet werden können und den entstehenden Risk Score nach unten drücken

dataset_legal = {

    "Risk-Word": [],
    "Risk-Sentence": [],
    "General_Frequence" : [],
    "Co-occurence": [],
    "subcategory": []

}

dataset_financial = {

    "Risk-Word": [],
    "Risk-Sentence": [],
    "General_Frequence" : [],
    "Co-occurence": [],
    "subcategory": []

}

dataset_operative = {

    "Risk-Word": [],
    "Risk-Sentence": [],
    "General_Frequence" : [],
    "Co-occurence": [],
    "subcategory": []

}

dataset_content = {

    "Risk-Word": [],
    "Risk-Sentence": [],
    "General_Frequence" : [],
    "Co-occurence": [],

}

dataset_positive = {

    "Risk-Word": [],
    "Risk-Sentence": [],
    "General_Frequence" : [],
    "Co-occurence": []

}

dataset_general_IMPORTANT = {

    "most_used words": [],
    "Words per categorie": [],
    "individual risk-score": []

}