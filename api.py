import openai
from openai import OpenAI
import json
from read_dataset import gain_access
import re

#WICHTIG: VOR UPLOAD TO GITHUB IMMER RAUSLÖSCHEN
Chat_GPT_Luna_Key: str = ""

def evaluate_primary_subjects(contract: str = None, name: str = None):
    content: str
    contract_type: str
    i: int = 0

    if contract is not None:
        content = contract
    else:
        contract_type, _, content = gain_access(i) #gain access fuction liefert contract_type, parentcompany_of_contract, content von vertrag

    if name is not None:
        stated_name = name
    else:
        stated_name = "Electric"

    client = OpenAI(api_key="")

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            #kann auch noch strukturiert werden
            input=f"Bitte analysiere mir den folgenden Vertrag anhand dessen Vertragsparteien und der zugehörigen Haupt-/Nebenleistungspflichten und allgemeienr \
            Recht und Pflichten dieser, und gib gleichzeitig Verweise auf deine gefundenen Passagen, um dieser zu belegen. Vertragsinhalt: {content}",
            instructions = "Du bist ein Contract Analysis Tool und richtest in dieser Analyse deinen Fokus auf die einzelnen Vertragsparteien:. \n"
                "Wie heißen diese, bitte gib den Namen in kurzer Form an ohne irgendwelchen zusätzlichen Infos, allerdings schreib kurz die Rolle die diese Partei im Vertrag einnimmt in Klammern '()' hintendran?" \
                "Welche Haupt- und Nebenleistungspflichten haben diese und was sind die jeweiligen Rechte und Pflichten dieser in diesem Vertragsverhältnis"
                "Bitte erstelle die einzelne Verweise und Kategorien möglichst übersichtlich, dass man diese einfach lesen und verstehen kann"
                "und diese übersichtlich dargestellt und gestaltet sind.", #noch reinschreiben das gut geordnete ausgabe sein soll
            reasoning={ #wie sehr soll Luna nachdenken
                "effort": "medium" #none, low, medium, high, xhigh, max
            },
            text={
                "format": {
                    "type": "json_schema", 
                    "name": "contract_metadata",
                    "strict": True, #KI soll Format zwingend beibehalten
                    "schema": {
                        "type": "object", 
                        "properties":{
                            "contract_partners": { #angegebene Vertragspartner des Dokumentes
                                "type": "array",
                                "minItems": 2, #begrenzt die Anzahl der ausgegebenen Vertragspartner auf zwei, genau zweí
                                "maxItems": 2,

                                "items": {
                                    "type": "object", 
                                    "properties": {
                                        "name": {
                                            "type": "string"
                                        },
                                        "main_obligations":{ #Hauptleistungspflichten
                                            "type": "array",
                                            "items":{
                                                "type": "string"
                                            }
                                        },
                                        "secondary_obligations":{ #Nebenleistungspflichten
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "individual_rights":{ #Rechte
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "individual_responsibilities":{
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        }
                                    },
                                    "required": [ #bestimmt dass diese Items gegeben sein müssen
                                        "name",
                                        "main_obligations",
                                        "secondary_obligations",
                                        "individual_rights",
                                        "individual_responsibilities"
                                    ],   
                                    "additionalProperties": False #die KI darf keine zusätzlichen Properties neben denen die definiert sind erzeugen                                                           
                                }
                            }
                        },
                        "required": [
                            "contract_partners"
                        ],   
                        "additionalProperties": False #die KI darf keine zusätzlichen Properties neben denen die definiert sind erzeugen
                    },  
                },
                "verbosity": "low" #gibt wieder wie lang bzw. ausführlich die Antwort sein soll
            }, 
            max_output_tokens=5000, #bestimmt das maximum für den output an tokens
            store=False #verhindert dass Daten für die Ausgabe serverseitig gespeichert werden
            #functionc calling kann mittels Tools gesteuert werden, Luna kriegt instructions welchen input, output wert die funktion bekommt, und wie diese
            #funktioniert um besser mit dem Ouput arbeiten zu können
            #evtl. file search verwenden, falls nötig
            #alles auch übrigens in tools kann auch web_search erlauben
            #max_tool_calls = 5 bestimmt wieviele Aufrufe insgesamt stattfinden dürfen
        )

    #ausgabe ist zwar gültiges JSON, muss allerdings mittels JSON Bib dann ggf. in Dictionary oder DataFrame zur genaueren Ausgabe umgewandelt werden
    
    except openai.RateLimitError:
        print("Rate des aktuellen KI-Assistenten wurde überschritten")
        return None

    except openai.APIConnectionError:
        print("Verbindung konnte nicht hergestellt werden")
        return None

    except openai.APIError as error:
        print("Sonstiger Fehler aufgetreten:", error)
        return None

    #kann aber ggf. auch noch in eine JSON Datei umgewandelt werden, kommt drauf an womit sich besser arbeiten lässt
    # -> dann entscheiden ob als einfaches dictionary oder als JSON Datei weiterverwenden durch entsprechende Formatierung
    result_dictionary: dict = json.loads(response.output_text) #erstellt aus dem Json String Object ein Dictionary mit den entsprechenden Daten

    Company_1 = result_dictionary["contract_partners"][0]
    Company_2 = result_dictionary["contract_partners"][1]

    if can_distinct_individual(Company_1['name'], Company_2['name'], stated_name):
        print(f"Bei den beiden Vertragspartner, um welches sich das zu behandelnde Vertragsdokument dreht, handelt es sich um: \n{Company_1['name']} \n{Company_2['name']}")
        print(f"{Company_1['name']} hat folgende Verpflichtungen: \nHauptleistungspflichten: ")
        for i in range(len(Company_1['main_obligations'])):
            print(f"{i}. {Company_1['main_obligations'][i]}")

        return result_dictionary
    else:
        print("Stated Company either false or inaccurate, try again by stating the name more detailed")
    #Identification_of_output = response.id #gibt dem output jeweils eine konkrete zuordnung, kann neue anfrage mittels previous_response_id mit alter verbinden
    #Token_verbrauch = response.usage
    #eventuell in Prompt Caching schauen, wenn immer wieder den gleichen StandardText am mitschicken -> kosten sparen


#Content hier bitte später auf erste Seite des Vertrages begrenzen, ganze Übergabe des Vertrages ist unnötig
def determine_contract_type(contract: str = None):
    content: str
    contract_type: str
    i: int = 0

    if contract is not None:
        content = contract
    else:
        contract_type, _, content = gain_access(i) #gain access fuction liefert contract_type, parentcompany_of_contract, content von vertrag

    client = OpenAI(api_key="")

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            #kann auch noch strukturiert werden
            input=f"Ordne mir den folgenden Vertrag bitte zu einer der folgenden Kategorien zu: 'License Agreement', 'Distributor Agreement', 'Supply Agreement', \
            'Outsourcing Agreement', 'Service Agreement', Vertragsinhalt: {content}",
            instructions = "Du bist ein Contract Analysis Tool und richtest in dieser Analyse deinen Fokus auf die Bestimmung der Vertragsart. \n"
                "Bitte ordne den Vertrag ausschließlich einer der angegebenen Vertragskategorien zu und halte dich unbedingt an das angegebene Format",
            reasoning={ #wie sehr soll Luna nachdenken
                "effort": "low" #none, low, medium, high, xhigh, max
            },
            #kann mittels JSON Strukturiert werden, sodass eine JSON String Ausgabe erfolgt und abgefangen werden kann
            # -> dann entscheiden ob als einfaches dictionary oder als JSON Datei weiterverwenden durch entsprechende Formatierung
            text={
                "format": {
                    "type": "json_schema",
                    "name": "contract_category",
                    "strict": True, #KI soll Format zwingend beibehalten
                    "schema": {
                        "type": "object", #bestimmt die Anwtort als JSON Object zurückgegeben werden muss -> structured
                        #enum kann hier genutzt werden um KI nur bestimmte Werte als Antwortmöglichkeit zu geben
                        "properties":{
                            "contract_type": { #Contract_Type des Vertragsdokuments
                                "type": "string",
                                "enum": [
                                    "Distributor Agreement",
                                    "License Agreement",
                                    "Supply Agreement",
                                    "Service Agreement",
                                    "Outsourcing Agreement"
                                ]
                            },
                        },  
                        "required": [
                            "contract_type"
                        ],   
                        "additionalProperties": False #die KI darf keine zusätzlichen Properties neben denen die definiert sind erzeugen
                    },
                },
                "verbosity": "low" #gibt wieder wie lang bzw. ausführlich die Antwort sein soll
            }, 
            max_output_tokens=100, #bestimmt das maximum für den output an tokens
            store=False #verhindert dass Daten für die Ausgabe serverseitig gespeichert werden
            #functionc calling kann mittels Tools gesteuert werden, Luna kriegt instructions welchen input, output wert die funktion bekommt, und wie diese
            #funktioniert um besser mit dem Ouput arbeiten zu können
            #evtl. file search verwenden, falls nötig
            #alles auch übrigens in tools kann auch web_search erlauben
            #max_tool_calls = 5 bestimmt wieviele Aufrufe insgesamt stattfinden dürfen
            #
        )

    #ausgabe ist zwar gültiges JSON, muss allerdings mittels JSON Bib dann ggf. in Dictionary oder DataFrame zur genaueren Ausgabe umgewandelt werden
    
    except openai.RateLimitError:
        print("Rate des aktuellen KI-Assistenten wurde überschritten")
        return None

    except openai.APIConnectionError:
        print("Verbindung konnte nicht hergestellt werden")
        return None

    except openai.APIError as error:
        print("Sonstiger Fehler aufgetreten:", error)
        return None

    #kann aber ggf. auch noch in eine JSON Datei umgewandelt werden, kommt drauf an womit sich besser arbeiten lässt
    contract_kind: dict = json.loads(response.output_text) #erstellt aus dem Json String Object ein Dictionary mit den entsprechenden Daten

    contract_classification = contract_kind['contract_type']

    print(f"Bei dem Vertrag handelt es sich um ein {contract_classification}")

    return contract_classification

def contract_summary(contract: str = None):
    content: str
    contract_type: str
    i: int = 0

    if contract is not None:
        content = contract
    else:
        contract_type, _, content = gain_access(i) #gain access fuction liefert contract_type, parentcompany_of_contract, content von vertrag

    client = OpenAI(api_key="")

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            #kann auch noch strukturiert werden
            input=f"Gib mir bitte eine kompakte Zusammenfassung von den zentralen Inhalten des folgenden Vertrags: {content}",
            instructions = "Du bist ein Contract Analysis Tool und richtest in dieser Analyse deinen Fokus auf die Zusammenfassung zentraler Inhalte des Vertrages. \n"
                "Konzentriere dich hier wirklich auf die wichtigsten Aspekte, sodass du eine möglichst kurze Antwort geben kannst",
            reasoning={ #wie sehr soll Luna nachdenken
                "effort": "low" #none, low, medium, high, xhigh, max
            },
            #kann mittels JSON Strukturiert werden, sodass eine JSON String Ausgabe erfolgt und abgefangen werden kann
            # -> dann entscheiden ob als einfaches dictionary oder als JSON Datei weiterverwenden durch entsprechende Formatierung
            text={ 
                "format": {
                    "type": "json_schema",
                    "name": "contract_summary",
                    "strict": True, #KI soll Format zwingend beibehalten
                    "schema": {
                        "type": "object", #bestimmt die Anwtort als JSON Object zurückgegeben werden muss -> structured
                        "properties":{
                            "summary": { #Zusammenfassung des Vertragsdokumentes
                                "type": "string"
                            },
                        },  
                        "required": [
                            "summary"
                        ],   
                        "additionalProperties": False #die KI darf keine zusätzlichen Properties neben denen die definiert sind erzeugen
                    },
                },
                "verbosity": "low" #gibt wieder wie lang bzw. ausführlich die Antwort sein soll
            }, 
            max_output_tokens=3000, #bestimmt das maximum für den output an tokens
            store=False #verhindert dass Daten für die Ausgabe serverseitig gespeichert werden
            #functionc calling kann mittels Tools gesteuert werden, Luna kriegt instructions welchen input, output wert die funktion bekommt, und wie diese
            #funktioniert um besser mit dem Ouput arbeiten zu können
            #evtl. file search verwenden, falls nötig
            #alles auch übrigens in tools kann auch web_search erlauben
            #max_tool_calls = 5 bestimmt wieviele Aufrufe insgesamt stattfinden dürfen
        )

    #ausgabe ist zwar gültiges JSON, muss allerdings mittels JSON Bib dann ggf. in Dictionary oder DataFrame zur genaueren Ausgabe umgewandelt werden
    
    except openai.RateLimitError:
        print("Rate des aktuellen KI-Assistenten wurde überschritten")
        return None

    except openai.APIConnectionError:
        print("Verbindung konnte nicht hergestellt werden")
        return None

    except openai.APIError as error:
        print("Sonstiger Fehler aufgetreten:", error)
        return None

    #kann aber ggf. auch noch in eine JSON Datei umgewandelt werden, kommt drauf an womit sich besser arbeiten lässt
    contract_central_aspects: dict = json.loads(response.output_text) #erstellt aus dem Json String Object ein Dictionary mit den entsprechenden Daten

    contract_summary = contract_central_aspects['summary']

    print(f"Eine kurze Zusammenfassung der zentralen Aspekte des Vertragsdokumentes: \n {contract_summary}")

    return contract_summary

def can_distinct_individual(company1: str, company2: str, stated_individual: str):
    company1 = remove_unnecessary(company1)
    company2 = remove_unnecessary(company2)
    stated_individual = remove_unnecessary(stated_individual)

    counter = 0

    if stated_individual in company1:
        counter += 1

    if stated_individual in company2:
        counter += 1

    return counter == 1

def remove_unnecessary(string: str):
    string = string.strip()
    string = string.lower()
    string = re.sub(r"\s+", "", string)
    return string
    



evaluate_primary_subjects()
#determine_contract_type()
#contract_summary()