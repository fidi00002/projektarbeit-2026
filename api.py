from google import genai
from google.genai import types
from read_dataset import gain_access


def evaluate_contract(contract: str):
    content: str
    contract_type: str
    i: int = 0

    if contract is not None:
        content = contract
    else:
        contract_type, _, content = gain_access(i) #gain access fuction liefert contract_type, parentcompany_of_contract, content von vertrag

    client = genai.Client(api_key="AIzaSyAe3faGbj_LEeW5ZX5CQBM5i4zwMCixRrE")

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=(f"Analysiere mir bitte folgenden Vertrag: \n"
        #f"Vertragsart: {contract_type}"
        f"Vertragsinhalt: {content}"),
        config=types.GenerateContentConfig(
            system_instruction=("Du bist ein Contract Analysis Tool und betrachtest den Inhalt von den dir übergebenen Verträgen spezifisch angesichts möglicher Risiken. \n"
            "Nachdem du das getan hast, gibst du eine Gesamtbewertung zum allgemeinen Risiko des Vertrages von einer Skala von 1/10 ab und begründest diese mit entsprechenden Textverweisen. \n"
            "Abschließend erstellst du noch eine kurze Zusammenfassung der wichtigsten Punkte des Vertrages. Bitte achte auch drauf deinen Output möglichst gut geordnet zu gestalten,"
            "sodass dieser gut lesbar gestaltet und übersichtlich dargestellt ist."), #noch reinschreiben das gut geordnete ausgabe sein soll
            temperature=0.5 #später hier kompletter Prompt mit ausgefertigter Risikobewertungsskala rein
        )
    )

    return response.text 