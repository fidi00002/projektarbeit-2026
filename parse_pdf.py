import pdfplumber 

#dateiauswahl fenster

# pfad = C:\Users\finnd\Documents\Informatik\Projektarbeit\Test_Contract\Vertrag1.pdf

def extract_text(pdf_path:str) -> str:
    #pdf_path = input("Pfad zur PDF Datei: ")
    with pdfplumber.open(pdf_path) as pdf:
        text: str = pdf.pages[0].extract_text()
        for i in range(1,len(pdf.pages)):
            text = text + "\n" + pdf.pages[i] .extract_text()
    return text
        
def extract_potential_table(): #should check for table in the document and extract it if existing
       # table: Table = pdf.pages[0].extract_table()
    raise NotImplementedError("function isn't declared yet")

def extract_potential_image(): #should check for an image in the document and extract if exsiting
    raise NotImplementedError("function isn't declared yet")




#first_page.text