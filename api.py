import openai
from openai import OpenAI
import json
from read_dataset import gain_access
import re

#WICHTIG: VOR UPLOAD TO GITHUB IMMER RAUSLÖSCHEN
Chat_GPT_Luna_Key: str = "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"

def evaluate_primary_subjects(contract: str = None, name: str = None):
    content: str

    content = contract

    stated_name = name

    print(name)

    client = OpenAI(api_key="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")

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            #kann auch noch strukturiert werden
            input=f"Bitte analysiere mir den folgenden Vertrag anhand dessen Vertragsparteien und der zugehörigen Haupt-/Nebenleistungspflichten und allgemeienr \
            Recht und Pflichten dieser, und gib gleichzeitig Verweise auf deine gefundenen Passagen, um dieser zu belegen. Vertragsinhalt: {content}",
            instructions = "Du bist ein Contract Analysis Tool und richtest in dieser Analyse deinen Fokus auf die einzelnen Vertragsparteien:. \n"
                "Bitte identifiziere für beide Vertragsparteien den Namen und die jeweilige Rolle im Vertrag z.B. Distributor, Licensor, Licensee, Supplier, Customer oder eine andere Rolle, welche aus diesem Vertrag hervorgeht. Gib beides bitte getrennt voneinander." \
                "Erfinde die Rolle auch nicht, sondern leite diese ausschließlich aus dem Verttrag ab."
                "Welche Haupt- und Nebenleistungspflichten haben die jeweiligen Vertragspartner und was sind die jeweiligen Rechte und Pflichten von dieser in diesem Vertragsverhältnis"
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
                                        "role": {
                                            "type": "string"
                                        },
                                        "role_description": {
                                            "type": "string"
                                        },
                                        "other_names": { #wird momentan noch nicht benutzt, eventuell später noch einbauen für genauere Zuordnung
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
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
                                        "role",
                                        "role_description",
                                        "other_names",
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

    distinct, relevant_company, irrelevant_company = can_distinct_individual(Company_1, Company_2, stated_name)

    if distinct:
        print(f"Bei den beiden Vertragspartner, um welches sich das zu behandelnde Vertragsdokument dreht, handelt es sich um: \n{relevant_company['name']} mit der Rolle {relevant_company['role']}, welche bedeutet {relevant_company['role_description']} \n{irrelevant_company['name']} mit der Rolle {irrelevant_company['role']}, welche bedeutet {irrelevant_company['role_description']}")
        print(f"{relevant_company['name']} hat folgende Verpflichtungen: \nHauptleistungspflichten: ")
        for i in range(len(relevant_company['main_obligations'])):
            print(f"{i}. {relevant_company['main_obligations'][i]}")
        print(f"{relevant_company}")

        return relevant_company, irrelevant_company
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

    content = contract

    client = OpenAI(api_key="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")

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
                                    "distributor agreement",
                                    "license agreement",
                                    "supply agreement",
                                    "service agreement",
                                    "outsourcing agreement"
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

    client = OpenAI(api_key="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")

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

def evaluation_of_ki_regarding_candidates(df, relevant_company_name, relevant_company_role, irrelevant_company_name, irrelevant_company_role, risk_category, relevant_scoring_prompt):
    category_df = df.loc[df["risk_category"] == risk_category, ["id", "page", "text", "risk_category", "risk_words"]].copy()
    html_category_df = category_df.to_html(index=False) 

    client = OpenAI(api_key="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")

    try:

        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=f"Du bist ein Contract Analysis Tool \
            Entscheide zunächst einmal für jede einzelne Zeile der übergebenen Tabelle für die Kategorie 'relevant', ob die jeweils angegebenen Sätze aus Sicht der Vertragspartei: {relevant_company_name}, welche die Rolle {relevant_company_role} innerhalb von diesem einnimmt und überhaupt relevant sind d.h. überhaupt ein Risiko für diese darstellen könnten \
            Falls diese nur ein Risiko für die Gegenpartei {irrelevant_company_name}, welche die Rolle {irrelevant_company_role} innerhalb des Vertrages einnimmt, darstellt kannst du diese für die Kategorie 'relevant' gerne auf False setzen \
            Falls dies zutrifft bewerte die Kategorie 'relevant' mit True ansonsten mit False \
            Falls du 'relevant' auf True gesetzt hast bewerte die Zeile anschließend orientiert anhand von folgendem Prompt: \
            {relevant_scoring_prompt} \
            Regeln zur Risikoskalierung: \
            Bewerte das Risiko anhand von folgenden fünf Komponenten, wobei jede Komponente ausschließlich einen ganzzahligen Wert zwischen 0 und 2 enthalten darf \
            \
            Severity: \
            0 = hat keine oder nur sehr geringe mögliche negative Auswirkungen\
            1 = mittelmäßig Auswirkungen, mit möglicher merklicher Auswirkung\
            2 = schwerwiegende bis absolut katastrophale Auswirkungen\
            \
            Scope_of_Impact: \
            0 = betrifft keine oder max. eine Leistung/Pflichten/Rechte innerhalb des Vertrages, ist also eng begrenzt\
            1 = betrifft mehrere Bereiche/Leistungen/Rechte oder Pflichten\
            2 = hat vertragsweite Auswirkungen besonders mit Folgen für die Kernleistung des Vertrages\
            \
            Reversibility: \
            0 = keine - oder kurzfristige Folgen, welche leicht korrigierbar sind und vollständig rückgängig gemacht werden können\
            1 = mittelfristige Folgen, welche nur teilweise - und mit größerem Aufwand reversibel sind\
            2 = langfristig Folgen, welche nur sehr schwer oder gar nicht rückgängig machbar sind\
            \
            Safety_Guard: \
            0 = viele ausreichende Schutzmechanismen, welche potentielle Gefahr gut eingrenzen\
            1 = nur teilweise vorhandene Schutzmechanismen, welche die potentielle Gefahr einigermaßen eingrenzen\
            2 = nur sehr wenige bis gar keine Schutzmechanismen, welche die potentielle Gefahr eingrenzen könnten\
            \
            Controllability: \
            0 = Risikokontrolle hängt allein von der ausgewählten, relevanten Vertragspartei ab und ist einfach zu kontrollieren\
            1 = Risikokontrolle liegt nicht allein in der Hand von der ausgewählten, relevanten Vertragspartei, ist nur eingeschränkt kontrollierbar und die Risikokontrolle ist damit nur teilweise vorhanden\
            2 = Risikokontrolle ist nur schwer oder gar nicht durch die ausgewählte, relevante Vertragspartei kontrollierbar\
            \
            Bewerte die einzelnen Komponenten völlig unabhängig voneinander, wenn möglich \
            Vergleiche am besten die einzelnen Sätze innerhalb derselben Risikokategorie miteinander, um unterschiedlich schweren Risiken möglichst auch unterschiedlich Bewertung zu zuteilen, wenn nötig \
            Zusätzliche Anmerkungen: \
            Bewerte bitte primär den tatsächlichen Inhalt des Satzes \
            Erfinde keine Risiken und allgemein nichts hinzu \
            Gib eine kurze Begründung deines zugeteilten Risikoscores mit maximal 1-3 Sätzen indem du vor allem darauf eingehst warum dieser Satz ein Risiko für unsere ausgewählte relevante Vertragspartei {relevant_company_name} mit Rolle {relevant_company_role} darstellen könnte. \
            Sollte dies wie oben angemerkt, nicht fall sein, indem es diese nicht betrifft oder kein Risiko für diese darstellt, stelle den Marker 'relevant' entsprechend bitte auf False",
            input=f"Analysiere folgende Tabelle, welche zu einem Vertrag erstellt wurde: {html_category_df}",
            reasoning={
                "effort": "medium" #none, low, medium, high, xhigh, max
            },
            text={
                "format": {
                    "type": "json_schema", 
                    "name": "risk_evaluation",
                    "strict": True, #KI soll Format zwingend beibehalten
                    "schema": {
                        "type": "object", 
                        "properties":{
                            "results": { #angegebene Vertragspartner des Dokumentes
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string"
                                        },
                                        "relevant": {
                                            "type": "boolean"
                                        },
                                        "components": {
                                            "type": "object",
                                            "properties": {
                                                "Severity": {
                                                    "type": "integer",
                                                    "minimum": 0,
                                                    "maximum": 2
                                                },
                                                "Scope_of_Impact": {
                                                    "type": "integer",
                                                    "minimum": 0,
                                                    "maximum": 2
                                                },
                                                "Reversibility": {
                                                    "type": "integer",
                                                    "minimum": 0,
                                                    "maximum": 2
                                                },
                                                "Safety_Guard": {
                                                    "type": "integer",
                                                    "minimum": 0,
                                                    "maximum": 2
                                                },
                                                "Controllability": {
                                                    "type": "integer",
                                                    "minimum": 0,
                                                    "maximum": 2
                                                }
                                            },
                                            "required": [
                                                "Severity",
                                                "Scope_of_Impact",
                                                "Reversibility",
                                                "Safety_Guard",
                                                "Controllability"
                                            ],
                                            "additionalProperties": False,
                                            "description": (
                                                "Build the scores of these categories ranking from 0 to 2"
                                                "So for each you got to decide if it's rather low, moderate or of high value"
                                            )
                                        },
                                        "reasoning": {
                                            "type": "string"
                                        }
                                    },
                                    "required": [ #bestimmt dass diese Items gegeben sein müssen
                                        "id",
                                        "relevant",
                                        "reasoning",
                                        "components"
                                    ],   
                                    "additionalProperties": False #die KI darf keine zusätzlichen Properties neben denen die definiert sind erzeugen                                                           
                                }
                            }
                        },
                        "required": [
                            "results"
                        ],   
                        "additionalProperties": False #die KI darf keine zusätzlichen Properties neben denen die definiert sind erzeugen
                    }  
                },
                "verbosity": "low" #gibt wieder wie lang bzw. ausführlich die Antwort sein soll
            },
            max_output_tokens=200000,
            store=False 
        )

    except openai.RateLimitError:
        print("Rate des aktuellen KI-Assistenten wurde überschritten")
        return None

    except openai.APIConnectionError:
        print("Verbindung konnte nicht hergestellt werden")
        return None

    except openai.APIError as error:
        print("Sonstiger Fehler aufgetreten:", error)
        return None

    results_dict = json.loads(response.output_text)

    results = results_dict["results"]

    for result in results:
        components = result["components"]
        condition_df = ((df["id"] == result["id"]) & (df["risk_category"] == risk_category))
        df.loc[condition_df, "relevant"] = result["relevant"]
        df.loc[condition_df, "severity"] = components["Severity"]
        df.loc[condition_df, "scope_of_impact"] = components["Scope_of_Impact"]
        df.loc[condition_df, "reversibility"] = components["Reversibility"]
        df.loc[condition_df, "safety_guard"] = components["Safety_Guard"]
        df.loc[condition_df, "controllability"] = components["Controllability"]
        df.loc[condition_df, "reasoning"] = result["reasoning"]

    df["risk_value"] = df[["severity", "scope_of_impact", "reversibility", "safety_guard", "controllability"]].sum(axis=1)

    return df 

def evaluation_of_tfidf_candidates(df_tfidf):
    tfidf_df = df_tfidf[["id", "page", "text"]].copy()
    html_tfidf_df = tfidf_df.to_html(index=False) 

    client = OpenAI(api_key="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")

    try:

        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=f"Prüfe für jede übergebene Vertragsstelle auf inhaltliche Verwertbarkeit. \
                           Das bedeutet relevant=True wird nur gesetzt wenn es sich um vollständige, verständliche und inhaltlich aussagekräftige Vertragsstellen handelt. \
                            Überschriften, Seitenangaben, Datumsangaben, Signaturen, unvollständige Satzfragmente und isolierte Bezeichnungen setzt du immer auf relevant=False. \
                            Anders als vorher bewertest du bitte kein Risiko. \
                            Beantworte jede übergebene ID genau einmal und begründe \
                            die Entscheidung mit einem kurzen Satz.",
            input=f"Analysiere folgende Tabelle, welche zu einem Vertrag erstellt wurde: {html_tfidf_df}",
            reasoning={
                "effort": "medium" #none, low, medium, high, xhigh, max
            },
            text={
                "format": {
                    "type": "json_schema", 
                    "name": "tfidf_candidates",
                    "strict": True, #KI soll Format zwingend beibehalten
                    "schema": {
                        "type": "object", 
                        "properties":{
                            "results": { #angegebene Vertragspartner des Dokumentes
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string"
                                        },
                                        "relevant": {
                                            "type": "boolean"
                                        },
                                        "reasoning": {
                                            "type": "string"
                                        }
                                    },
                                    "required": [ #bestimmt dass diese Items gegeben sein müssen
                                        "id",
                                        "relevant",
                                        "reasoning"
                                    ],   
                                    "additionalProperties": False #die KI darf keine zusätzlichen Properties neben denen die definiert sind erzeugen                                                           
                                }
                            }
                        },
                        "required": [
                            "results"
                        ],   
                        "additionalProperties": False #die KI darf keine zusätzlichen Properties neben denen die definiert sind erzeugen
                    }  
                },
                "verbosity": "low" #gibt wieder wie lang bzw. ausführlich die Antwort sein soll
            },
            max_output_tokens=5000,
            store=False 
        )

    except openai.RateLimitError:
        print("Rate des aktuellen KI-Assistenten wurde überschritten")
        return None

    except openai.APIConnectionError:
        print("Verbindung konnte nicht hergestellt werden")
        return None

    except openai.APIError as error:
        print("Sonstiger Fehler aufgetreten:", error)
        return None

    results_dict = json.loads(response.output_text)

    results = results_dict["results"]

    df = df_tfidf.copy()
    df["relevant"] = False
    df["reasoning"] =""

    for result in results:
        condition_df = df["id"] == result["id"]
        df.loc[condition_df, "relevant"] = result["relevant"]
        df.loc[condition_df, "reasoning"] = result["reasoning"]

    return df 


def can_distinct_individual(company1: dict, company2: dict, stated_individual: str):
    company1_name = remove_unnecessary(company1['name'])
    company2_name = remove_unnecessary(company2['name'])
    stated_individual = remove_unnecessary(stated_individual)

    match_1 = stated_individual in company1_name
    match_2 = stated_individual in company2_name

    if match_1 and not match_2:
        return True, company1, company2

    if match_2 and not match_1:
        return True, company2, company1

    print(company1['name'])
    print(company2['name'])
    print(stated_individual)

    print(company1_name)
    print(company2_name)

    return False, None, None

def remove_unnecessary(string: str):
    string = string.strip()
    string = string.lower()
    string = re.sub(r"\s+", "", string)
    return string

def ordering_of_risk_words():
    raise NotImplementedError("function hasn't been declared yet")

    
#evaluate_primary_subjects()
#determine_contract_type()
#contract_summary()