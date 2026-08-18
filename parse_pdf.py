import pdfplumber 
import re
from process_data import creation_of_dictionary
from pandas_save import dataframe_construction_td_idf
import pandas as pd
from api import evaluate_primary_subjects, evaluation_of_ki_regarding_candidates
from risk_scaling import calculation_of_risk_score

#dateiauswahl fenster

# pfad = C:\Users\finnd\Documents\Informatik\Projektarbeit\Test_Contract\Vertrag1.pdf

#example_dictionary: dict = {

#   "filename" : "",
#   "contract_type" : "",
#   "probability_of_correctness_two" :  "",
#   "list_of_pages": []

#}

#don't know how to handle sentence which goes across to pages yet as well as specifc lines have to be integrated to 
#later integration of AI and short contract_type analysis if probability of correctness < 0.5
#creation of foundational contract data
def extract_text(pdf_path:str = r"C:\Users\finnd\Documents\Wirtschaftsinformatik\Informatik\Projektarbeit\Test_Contract\Vertrag1.pdf") -> dict:
    #pdf_path = input("Pfad zur PDF Datei: ")
    probability_of_correctness = 0
    pdf_path_copy: list = pdf_path.rsplit("\\")
    file_name = pdf_path_copy[len(pdf_path_copy)-1] #später direkt in main auslesen lassen und als input variable mitgeben sobald pipeline steht
    contract_sites: list = []
    full_text = []
    possible_contract_classification: str = ""
    with pdfplumber.open(pdf_path) as pdf:
    #    text: str = pdf.pages[0].extract_text()
        possible_contract_classification = pdf.pages[0].search(r"Distributor|Service|Outsourcing|License|Supply", case= False)
        for i in range(0, len(pdf.pages)):
            contract_sites.append([pdf.pages[i].extract_text(), pdf.pages[i].page_number])
            full_text.append(f"----------------Page{pdf.pages[i].page_number}----------------\n{pdf.pages[i].extract_text()}")
            pdf.pages[i].close()

    test_variable1 = "ABcdeF"
    test_variable2 = "abCDeFxyz"

    full_text = "\n\n".join(full_text)

    metadata_contract : dict = dict(filename = file_name, contract_type = possible_contract_classification[0]["text"],
                                    correctness_probability = 0, listlist_of_pages = contract_sites, whole_text = full_text)
    if possible_contract_classification:
        probability_of_correctness += 0.25
    if re.search(r"Distributor|Service|Outsourcing|License|Supply", file_name):
        probability_of_correctness += 0.5
    if possible_contract_classification[0]["text"].lower() in file_name.lower():
        probability_of_correctness += 0.25
    metadata_contract["correctness_probability"] = probability_of_correctness

    return metadata_contract

#Test zum Überprüfen ob richtige Seitenzahl erkannt 

#muss danach noch mit regulär formatierten Vertragsdokumenten bearbeitet werden

#first_page.text

extract_text()