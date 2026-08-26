import pdfplumber 
import re
from api import determine_contract_type

def extract_text(pdf_path:str) -> dict:
    pdf_path_copy: list = pdf_path.rsplit("\\")
    file_name = pdf_path_copy[len(pdf_path_copy)-1] #später direkt in main auslesen lassen und als input variable mitgeben sobald pipeline steht
    contract_sites: list = []
    full_text = []
    possible_contract_classification: str = ""
    with pdfplumber.open(pdf_path) as pdf:
        possible_contract_classification = pdf.pages[0].search(r"Distributor Agreement|Service Agreement|Outsourcing Agreement|License Agreement|Supply Agreement", case= False) #versuchen titel abzugreifen
        
        for i in range(0, len(pdf.pages)):
            contract_sites.append([pdf.pages[i].extract_text(), pdf.pages[i].page_number])
            full_text.append(f"----------------Page{pdf.pages[i].page_number}----------------\n{pdf.pages[i].extract_text()}")
            pdf.pages[i].close()

    full_text = "\n\n".join(full_text)

    possible_contract_classification = (possible_contract_classification[0]["text"] if possible_contract_classification else None)

    file_name_classification = re.search(r"Distributor Agreement|Service Agreement|Outsourcing Agreement|License Agreement|Supply Agreement", file_name, re.I)

    file_name_classification = (file_name_classification.group(0) if file_name_classification else None)

    correct = 0


    if file_name_classification and possible_contract_classification:
        if (file_name_classification.lower() == possible_contract_classification.lower()):
            correct = 1

    print(file_name_classification.lower() if file_name_classification else "Nicht im Dateinamen gefunden", "\n")

    print(possible_contract_classification.lower() if possible_contract_classification else "Kein klassifizierbarer Titel gefunden", "\n")

    if correct:
        contract_classification = file_name_classification
    else:
        contract_classification = determine_contract_type(full_text)
    
    metadata_contract : dict = dict(filename = file_name, contract_type = contract_classification,
                                    listlist_of_pages = contract_sites, whole_text = full_text)

    return metadata_contract