import pdfplumber 
import re
from process_data import creation_of_dictionary

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
    possible_contract_classification: str = ""
    with pdfplumber.open(pdf_path) as pdf:
    #    text: str = pdf.pages[0].extract_text()
        possible_contract_classification = pdf.pages[0].search(r"Distributor|Service|Outsourcing|License|Supply", case= False)
        for i in range(0, len(pdf.pages)):
            contract_sites.append([pdf.pages[i].extract_text(), pdf.pages[i].page_number])
            pdf.pages[i].close()

    test_variable1 = "ABcdeF"
    test_variable2 = "abCDeFxyz"

    metadata_contract : dict = dict(filename = file_name, contract_type = possible_contract_classification[0]["text"],
                                    correctness_probability = 0, listlist_of_pages = contract_sites)
    if possible_contract_classification:
        probability_of_correctness += 0.25
    if re.search(r"Distributor|Service|Outsourcing|License|Supply", file_name):
        probability_of_correctness += 0.5
    if possible_contract_classification[0]["text"].lower() in file_name.lower():
        probability_of_correctness += 0.25
    metadata_contract["correctness_probability"] = probability_of_correctness
    #print(contract_sites)
    #print(contract_sites[4][1],  "\n",  contract_sites[16][0], "\n", contract_sites[1][0], "\n", contract_sites[9][1])
    #print(pdf.metadata)
    #print(possible_contract_classification[0]["text"])
    #print(metadata_contract)
    #print(metadata_contract["listlist_of_pages"][17][1])
    #print(len(pdf.pages))

    #print(metadata_contract)
    creation_of_dictionary(metadata_contract)
    
    return metadata_contract
        
def extract_potential_table(): #should check for table in the document and extract it if existing
       # table: Table = pdf.pages[0].extract_table()
    raise NotImplementedError("function isn't declared yet")

def extract_potential_image(): #should check for an image in the document and extract if exsiting
    raise NotImplementedError("function isn't declared yet")


#Test zum Überprüfen ob richtige Seitenzahl erkannt 

#muss danach noch mit regulär formatierten Vertragsdokumenten bearbeitet werden

#first_page.text

extract_text()