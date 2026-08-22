from parse_pdf import extract_text
from docx import Document
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import pandas as pd
from parse_pdf import extract_text
from process_data import creation_of_dictionary
from pandas_save import dataframe_construction_td_idf, attach_tfidf_to_risks, calculate_whole_sentence_tfidf 
from api import evaluate_primary_subjects, evaluation_of_ki_regarding_candidates, evaluation_of_tfidf_candidates, contract_summary
from risk_scaling import calculation_of_risk_score

# pfad = C:\Users\finnd\Documents\Informatik\Projektarbeit\Test_Contract\Vertrag1.pdf


def analyse_contract():
    #zuerst abfragen wie user risiko gewichten möchte wenn überhaupt
    #https://www.geeksforgeeks.org/python/python-gui-tkinter/
    #get entry value via .scale() or Spinbox() configuration

    #möglichkeit von benutzerdefinierten Risikogewichtungen
    root = tk.Tk()

    finance_current = tk.IntVar()
    legal_current =  tk.IntVar()
    operative_current = tk.IntVar()

    priority_text = {
         1: "Sehr geringe Priorität",
         2: "Geringe Priorität",
         3: "Neutral",
         4: "Hohe Priorität",
         5: "Sehr hohe Priorität"
    }

    score_mapping ={
        1: 0.8,
        2: 0.9,
        3: 1.0,
        4: 1.1,
        5: 1.2
    }

    finance_text = tk.StringVar(value=priority_text[3])
    legal_text = tk.StringVar(value=priority_text[3])
    operative_text = tk.StringVar(value=priority_text[3])

    company_name = tk.StringVar() #NEU

    #add heading with meaning for numbers above

    financial_scale = Scale(root, from_=1, to=5, orient=HORIZONTAL, width=20, length=240, showvalue=False, tickinterval=2, variable = finance_current, command= lambda value: finance_text.set(priority_text[int(float(value))]))
    legal_scale = Scale(root, from_=1, to=5, orient=HORIZONTAL, width=20, length=240, showvalue=False, tickinterval=2, variable = legal_current, command= lambda value: legal_text.set(priority_text[int(float(value))]))
    operative_scale = Scale(root, from_=1, to=5, orient=HORIZONTAL, width=20, length=240, showvalue=False, tickinterval=2, variable = operative_current, command= lambda value: operative_text.set(priority_text[int(float(value))]))
    company_entry = tk.Entry(root, textvariable=company_name, width=40)

    tk.Label(root, textvariable=finance_text).grid(row=2, column=1)
    tk.Label(root, textvariable=legal_text).grid(row=4, column=1)
    tk.Label(root, textvariable=operative_text).grid(row=6, column=1)

    financial_scale.grid(row=3, column=1)
    legal_scale.grid(row=5, column=1)
    operative_scale.grid(row=7, column=1)
    company_entry.grid(row=1, column=1) #NEU

    financial_scale.set(3)
    legal_scale.set(3)
    operative_scale.set(3)

    root.title("Vertragsanalyse - Vorabstimmung")
    
    all_label = tk.Label(root, text="Would you like to customise the risk evaluation, or would you rather use the default settings?")
    fin_label = tk.Label(root, text="Financial")
    legal_label = tk.Label(root, text="Legal")
    operative_label = tk.Label(root, text="Operative")

    com_label = tk.Label(root, text="Name of your Company (please exactly as written in the contract)") #NEU

    # def add_labels(row):
    #     label_under_scale = tk.Frame(root)
    #     label_under_scale.grid(row=row, column=1, sticky="ew")

    #     tk.Label(label_under_scale, text="Sehr geringe Priorität").pack(side="left")
    #     tk.Label(label_under_scale, text="Neutral").pack(side="left", expand=True)
    #     tk.Label(label_under_scale, text="Sehr hohe Priorität").pack(side="right")


    all_label.grid(row=0)
    com_label.grid(row=1, column=0)
    fin_label.grid(row=2, column=0)
    legal_label.grid(row=4, column=0)
    operative_label.grid(row=6, column=0)

    # add_labels(3)
    # add_labels(5)
    # add_labels(7)

    button = tk.Button(root, text="insert", width=25, command=root.destroy)

    button.grid(row=8)

    root.mainloop()

    finance_textual: str = priority_text[finance_current.get()]
    legal_textual: str = priority_text[legal_current.get()]
    operative_textual: str = priority_text[operative_current.get()]

    finance: float = score_mapping[finance_current.get()]
    legal: float = score_mapping[legal_current.get()]
    operative: float = score_mapping[operative_current.get()]
    company_name: str = company_name.get()

    root3 = tk.Tk()

    root3.title("Bitte Vertragsdatei auswählen")
    root3.withdraw()
    path_existing = False
    while True:
        filename = fd.askopenfilename(
            title="Bitte Vertragsdatei auswählen",
            filetypes= [("PDFs", "*.pdf")],
            initialdir= "." #später ändern zu C:/Users
        )
        if filename:
            realname = filename.rsplit("/")
            last = realname[len(realname)-1]
            again = messagebox.askyesno(
                title="Überprüfung",
                message=fr"Handelt es sich bei {last} um die richtige Datei?",
            )
            if again:
                path_existing = True
                pdf_path = filename
                break
            else:
                retry = messagebox.askyesno(
                    title="Überprüfung",
                    message=fr"Wollen Sie denn Vorgang wiederholen?",
                )
                if retry:
                    continue
                else:
                    break
        else:
            again2 = messagebox.askretrycancel(
                title="Dateifehler",
                message="Die Dateiauswahl wurde abgebrochen. Möchten Sie diese wiederholen?"
            )
            if again2:
                continue
            else:
                print("Keine Datei ausgewählt")
                break
    root3.destroy()
    #check ob abfrage geklappt
    if path_existing:
        pdf_path = filename #pdf datei pfad des vertragsdokumentes
    else:
        print("Pfad ist nicht vorhanden")
        return None
    #textfeld zur ausgabe von analyse

    #HIER ENDET DIE ABFRAGE NACH DEM DATEIEN PFAD

    #HIER BEGINNT DER AUFRUF DER BEARBEITENDEN FUNKTIONEN

    metadata_contract: pd.DataFrame = extract_text(pdf_path)

    risk_df = creation_of_dictionary(metadata_contract)
    tfidf_df = dataframe_construction_td_idf(metadata_contract)

    tfidf_sentence_df= calculate_whole_sentence_tfidf(tfidf_df)

    #gruppierung nach top 20% kandidaten

    all_tfidf_values_df = tfidf_sentence_df.copy()
    tfidf_candidate_df = all_tfidf_values_df[all_tfidf_values_df["tfidf_percentile"] >= 0.75].copy()
    tfidf_candidate_df = tfidf_candidate_df.sort_values("tfidf_sentence_score", ascending=False).reset_index(drop=True)
    with pd.option_context("display.max_rows", None):
        print(tfidf_candidate_df)

    relevant_company, irrelevant_company = evaluate_primary_subjects(contract=metadata_contract["whole_text"], name=company_name)

    tfidf_candidate_df_evaluated = evaluation_of_tfidf_candidates(tfidf_candidate_df, relevant_company, irrelevant_company)
    with pd.option_context("display.max_rows", None):
        print(tfidf_candidate_df_evaluated)

    tfidf_candidate_only_relevant = tfidf_candidate_df_evaluated[tfidf_candidate_df_evaluated["relevant"] == True].copy()

    highest5_tfidf_values = (tfidf_candidate_only_relevant.nlargest(5, "tfidf_sentence_score").reset_index(drop=True))

    with pd.option_context("display.max_rows", None):
        print(highest5_tfidf_values)

    ultimate_info_df_with_groupings = attach_tfidf_to_risks(risk_df, tfidf_sentence_df)

    with pd.option_context("display.max_rows", None):
        print(ultimate_info_df_with_groupings)

    ultimate_info_df_with_groupings["relevant"] = False
    ultimate_info_df_with_groupings["risk_value"] = -1
    ultimate_info_df_with_groupings["severity"] = -1
    ultimate_info_df_with_groupings["scope_of_impact"] = -1
    ultimate_info_df_with_groupings["reversibility"] = -1
    ultimate_info_df_with_groupings["safety_guard"] = -1
    ultimate_info_df_with_groupings["controllability"] = -1
    ultimate_info_df_with_groupings["reasoning"] = ""

    legal_prompt = "Berücksichtige insbesondere Haftung, Schadensersatz, (vorzeitige) Kündigungsrechte, Gewährleistungsrechte-/ und pflichten, unklar formulierte rechtliche Regelungen, beschränkungen ausschlüsse bestehender Rechte und unklar oder unsauber formulierte rechtliche Regelungen"
    financial_prompt = "Berücksichtige insbesondere (mögliche) Zahlungsverpflichtungen, Vertragsstrafen, welche bspw. bei nichterfüllung von bedingungen eintreten können, zusätzliche oder schwer kalkulierbare Kosten, Umsatz- oder Ertragsverlust, Schadensersatz und Haftungskosten sowie sonstige finanzielle Belastungen"
    operative_prompt = "Berücksichtige insbesondere (mögliche) Einschränkungen des Betriebs, Liefer- und Leistungspflichten, Exklusivitätsbindungen, Qualitäts- und Gewährleistungsforderungen, Abhängikeiten von der anderen Vertragspartei sowie Risken, welche durch Verzögerungen oder Leistungsausfälle entstehen können"

    ultimate_df_with_scoring = evaluation_of_ki_regarding_candidates(ultimate_info_df_with_groupings, relevant_company['name'], relevant_company['role'], irrelevant_company['name'], irrelevant_company['role'], "legal", legal_prompt) #eventuell noch runterbrechen auf nur dictionary übergeben
    ultimate_df_with_scoring = evaluation_of_ki_regarding_candidates(ultimate_info_df_with_groupings, relevant_company['name'], relevant_company['role'], irrelevant_company['name'], irrelevant_company['role'], "financial", financial_prompt) #und dieses nochmal selbst in aufrufender funktion
    ultimate_df_with_scoring = evaluation_of_ki_regarding_candidates(ultimate_info_df_with_groupings, relevant_company['name'], relevant_company['role'], irrelevant_company['name'], irrelevant_company['role'], "operative", operative_prompt) #auslesen

    with pd.option_context("display.max_rows", None):
        print(ultimate_df_with_scoring[["severity", "scope_of_impact", "reversibility", "safety_guard", "controllability", "risk_value"]])

    ultimate_df_with_scoring = ultimate_df_with_scoring[ultimate_df_with_scoring["relevant"] == True].copy() #rausläschen aller als 'False' eingestuften und damit nicht relevanten Risiken

    highest_risk_values = ultimate_df_with_scoring.sort_values("risk_value", ascending=False)

    top5_per_category = highest_risk_values.groupby("risk_category", as_index=False).head(5).reset_index(drop=True)

    legal_top_risks = top5_per_category[top5_per_category["risk_category"] == "legal"]
    financial_top_risks = top5_per_category[top5_per_category["risk_category"] == "financial"]
    operative_top_risks = top5_per_category[top5_per_category["risk_category"] == "operative"]

    legal_risk_score, financial_risk_score, operative_risk_score, median_risk_score = calculation_of_risk_score(ultimate_df_with_scoring, True, legal, finance, operative)

    contract_sum = contract_summary(metadata_contract['whole_text'])

    # all_in_all_results = {
    #     "selected_company": relevant_company,
    #     "selected_company_role": relevant_company['role'],
    #     "selected_company_main_obligations": relevant_company['main_obligations'],
    #     "selected_company_secondary_obligations": relevant_company['secondary_obligations'],
    #     "selected_company_individual_rights": relevant_company['individual_rights'],
    #     "selected_company_individual_responsibilities": relevant_company['individual_responsibilities'],
    #     "counterparty": irrelevant_company,
    #     "counterparty_role": irrelevant_company['role'],
    #     "counterparty_main_obligations": irrelevant_company['main_obligations'],
    #     "counterparty_secondary_obligations": irrelevant_company['secondary_obligations'],
    #     "counterparty_individual_rights": irrelevant_company['individual_rights'],
    #     "counterparty_individual_responsibilities": irrelevant_company['individual_responsibilities'],
    #     "contract_type": metadata_contract['contract_type'],
    #     "summary": contract_sum,
    #     "top_5_tfidf": highest5_tfidf_values,
    #     "top_5_risks": top5_per_category,
    #     "risk_score": {
    #         "legal": legal_risk_score,
    #         "financial": financial_risk_score,
    #         "operative": operative_risk_score,
    #         "median": median_risk_score
    #     },
    #     "User_Gewichtungen": {
    #         "legal":legal,
    #         "financial": finance,
    #         "operative": operative
    #     }
    # }

    tfidf_output = []

    for row in highest5_tfidf_values.itertuples(index=False):
        tfidf_output.append(
            f"{row.text}"
            f"Relevanz: {row.tfidf_level}\n"
            f"Begründung: {row.reasoning}\n"
            f"Fundstelle: Seite {row.page}\n"
        )

    legal_risk_text: list = risk_output_construction(legal_top_risks)
    financial_risk_text: list = risk_output_construction(financial_top_risks)
    operative_risk_text: list = risk_output_construction(operative_top_risks)

    tfidf_output_text = "\n\n".join(tfidf_output)

    relevant_company_description = company_setup(relevant_company)
    irrelevant_company_description = company_setup(irrelevant_company)

    print(highest5_tfidf_values, "\n")

    print(top5_per_category)

    #HIER BEGINNT DIE AUSGABE DES OUTPUT FENSTERS

    root2 = tk.Tk()
    root2.title("Vetragsanalyse")

    text = ScrolledText(root2, wrap=tk.WORD)

    text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    final_analysis_as_text = f"Vertragsanalyse \n\nDatei: {last} \n\nVertragspartei: {relevant_company['name']} ({relevant_company['role']})\nDie Risikobewertung folgt aus der Sicht dieser Partei\n\nGegenspieler: {irrelevant_company['name']} ({irrelevant_company['role']})\n\nVertragsart: {metadata_contract['contract_type']}\n\n\
Risikowert: {median_risk_score} \n\nSetzt sich zusammen aus: \n\n Rechtlichem Risiko: {legal_risk_score} \n Finanziellem Risiko: {financial_risk_score}\n Operativem Risiko: {operative_risk_score} \n\n\
Zusammenfassung: \n{contract_sum}\n\n\
    Rechte und Pflichten der beiden Firmen: \n\n{relevant_company_description} \n\n{irrelevant_company_description} \n\n\
    Die folgenden Sätze stellen das größte Risiko der einzelnen Kategorien dar: \n\nRechtlich: \n\n {legal_risk_text} \n\n\
    Finanziell: \n\n {financial_risk_text} \n\nOperativ: \n\n{operative_risk_text} \n\n\
    Dazu folgen die Sätze, welche laut berechneten TF-IDF Werten statistisch besonders auffällig sind: \n\n{tfidf_output_text} \n\n"

    #später hier genauen text aus allen funktionen zusammenstellen

#     final_analysis_as_text = """Gerne, hier ist die Analyse des von Ihnen bereitgestellten "DISTRIBUTOR AGREEMENT" von LIMEENERGYCO.

# **Gesamtbewertung des Risikos:** 6/10

# **Begründung der Risikobewertung:**

# Der Vertrag weist ein moderates Risiko auf, das sich aus einer Kombination von Faktoren ergibt, die sowohl Chancen als auch potenzielle Fallstricke für beide Parteien bergen.

# *   **Exklusivität und Marktgebiet (Abschnitt 1.1, 1.6):** Die Exklusivität für den "Market" (Bundesstaat Illinois) ist ein Vorteil für den Distributor, birgt aber auch das Risiko, dass die Mindestabnahmemengen nicht erreicht werden und die Exklusivität entzogen wird. Die detaillierten Mindestmengen (1.6) sind ein klarer Indikator für das Risiko, diese nicht zu erfüllen.
# *   **Vertragsdauer und Verlängerung (Abschnitt 1.3):** Eine anfängliche Laufzeit von 10 Jahren mit jährlichen Verlängerungsoptionen ist lang. Dies bietet Stabilität, aber auch das Risiko, dass eine Partei über einen längeren Zeitraum an eine ungünstige Vereinbarung gebunden ist.
# *   **Preisgestaltung und Anpassung (Abschnitt 2.4):** Die Preisgestaltung ist an den Verbraucherpreisindex (CPI) gekoppelt, was eine gewisse Vorhersehbarkeit bietet. Das Recht des Unternehmens, Preise aus anderen Gründen anzupassen (basierend auf Kosten oder Marktnachfrage), birgt jedoch ein Risiko für den Distributor, wenn diese Anpassungen seine Gewinnmargen schmälern. Die Klausel, dass Preiserhöhungen aufgrund der Marktnachfrage "nicht so groß sein dürfen, dass sie den Distributor seines normalen und üblichen Gewinnmargen berauben" (2.4(B)), ist ein wichtiger Schutz für den Distributor, aber die Auslegung "normal und üblich" kann zu Streitigkeiten führen.
# *   **Produktverbesserungen und neue Produkte (Abschnitt 3.1, 7):** Das Recht des Unternehmens, Produkte zu verbessern oder neue einzuführen, ist sowohl eine Chance als auch ein Risiko. Der Distributor hat ein Optionsrecht für neue Produkte (7.1), aber die Bedingungen werden in separaten Vereinbarungen festgelegt (7.3), was zu Unsicherheit führen kann. Die Möglichkeit, dass alte Produkte eingestellt werden, wenn neue besser oder preislich vergleichbar sind (3.1), kann die Produktpalette des Distributors beeinflussen.
# *   **Gewährleistung und Haftung (Abschnitt 2.2, 2.6, 3.3, 3.4, 5.3):** Die Gewährleistung von 24 Monaten (3.3) ist Standard. Die Regelungen zur Fehlerbehebung und Kostentragung bei Mängeln (2.6(B), 3.4) sind relativ klar, aber die Möglichkeit, dass das Unternehmen die Verantwortung bestreitet (3.4), birgt ein Risiko. Die gegenseitige Freistellung (Indemnification) in Abschnitt 5.3 ist ein wichtiger Punkt zur Risikominimierung, aber die Auslegung von "Fahrlässigkeit oder Verschulden" kann zu Meinungsverschiedenheiten führen.
# *   **Vertragsbruch und Kündigung (Abschnitt 4.2):** Die Kündigungsmöglichkeiten sind relativ standardmäßig, aber die 30-tägige Kündigungsfrist bei Nichterfüllung (4.2(b)) könnte für den Distributor knapp sein, wenn er einen Fehler nicht schnell beheben kann.
# *   **Repurchase-Klausel (Abschnitt 4.4):** Die Option des Unternehmens, Produkte nach Vertragsende zurückzukaufen, ist ein potenzieller Schutz für den Distributor, aber die Bedingungen (nur auf Wunsch des Unternehmens, abzüglich Rabatte etc.) sind nicht vollständig zugunsten des Distributors gestaltet.
# *   **Vertraulichkeit und Nicht-Wettbewerb (Abschnitt 3.6, 5.6, 5.7):** Die Klauseln zur Vertraulichkeit und zum Verbot der Anwerbung von Mitarbeitern und Kunden sind für das Unternehmen vorteilhaft, aber die 12- bzw. 18-monatigen Fristen nach Vertragsende können die Geschäftsmöglichkeiten des Distributors einschränken.

# **Zusammenfassung der wichtigsten Punkte des Vertrages:**

# Dieser "DISTRIBUTOR AGREEMENT" regelt die Beziehung zwischen Electric City Corp. ("Company") und Electric City of Illinois LLC ("Distributor") für den Vertrieb von "Energy Saver"-Produkten in Illinois.

# *   **Exklusivität:** Der Distributor erhält die exklusive Vertriebsrechte für die Produkte in Illinois.
# *   **Vertragslaufzeit:** Der Vertrag hat eine anfängliche Laufzeit von 10 Jahren, mit jährlichen Verlängerungsoptionen bis zu weiteren 10 Jahren.
# *   **Mindestabnahmemengen:** Der Distributor muss bestimmte Mindestmengen an Produkten pro Jahr abnehmen, um seine Exklusivrechte zu behalten. Bei Nichterfüllung können die exklusiven Rechte neu bewertet werden, es sei denn, es liegt eine höhere Gewalt vor.
# *   **Preisgestaltung:** Die Preise sind anfangs festgelegt und werden jährlich an den Verbraucherpreisindex (CPI) angepasst. Das Unternehmen kann Preise auch aus anderen Gründen anpassen, muss dabei aber die Gewinnmargen des Distributors berücksichtigen.
# *   **Produktverbesserungen und neue Produkte:** Das Unternehmen kann Produkte verbessern oder neue einführen. Der Distributor hat ein Optionsrecht, diese ebenfalls exklusiv zu vertreiben, wobei die Konditionen in separaten Verträgen geregelt werden.
# *   **Gewährleistung:** Das Unternehmen gewährt eine 24-monatige Garantie auf die Produkte. Die Kosten für die Behebung von Mängeln werden in der Regel vom Unternehmen getragen.
# *   **Zahlungsbedingungen:** Der Distributor muss innerhalb von 30 Tagen nach Erhalt der Produkte bezahlen.
# *   **Kündigung:** Der Vertrag kann aus wichtigem Grund (z.B. Zahlungsverzug, wesentliche Vertragsverletzung, Insolvenz) mit 30 Tagen Frist gekündigt werden.
# *   **Rückkauf:** Nach Vertragsende hat das Unternehmen die Option, unverkaufte Produkte vom Distributor zurückzukaufen.
# *   **Haftung und Freistellung:** Beide Parteien verpflichten sich zur gegenseitigen Freistellung bei Verstößen gegen den Vertrag, Fahrlässigkeit oder Verletzung von Schutzrechten Dritter. Das Unternehmen sichert zu, eine Produkthaftpflichtversicherung abzuschließen und den Distributor als zusätzlichen Versicherungsnehmer einzutragen.
# *   **Vertraulichkeit und Wettbewerbsbeschränkungen:** Beide Parteien müssen vertrauliche Informationen schützen. Der Distributor unterliegt nach Vertragsende Beschränkungen bezüglich der Anwerbung von Mitarbeitern und Kunden des Unternehmens sowie dem Verkauf von Konkurrenzprodukten.
# *   **Anwendbares Recht:** Das Recht des Staates Illinois gilt für diesen Vertrag."""

    text.insert("end", final_analysis_as_text) #benutzen von label damit user nicht ausversehen in die anzeige schreiben kann & font=()
    # label.config(anchor="center", font=("Times New Roman", 20, "bold"), relief="solid")
    lines = final_analysis_as_text.splitlines()

    text.config(height=min(max(len(lines), 10), 40), width=100, state="disabled")
    
    root2.mainloop()

def risk_output_construction(risk_df):
    output = []
    for rank, row in enumerate(risk_df.itertuples(index=False), start=1):
        output.append(
            #f"{rank}. {row.risk_category.capitalize()} - Risk"
            f"{rank}. Vertragsstelle: {row.text} - Risiko: {row.risk_value}/10\n"
            f"Begründung: {row.reasoning}\n"
            f"Unterfaktoren: \n"
            f"Severity {row.severity}/2, "
            f"Scope {row.scope_of_impact}/2, "
            f"Reversibility {row.reversibility}/2, "
            f"Protection {row.safety_guard}/2, "
            f"Controllability {row.controllability}/2\n"
            f"TF-IDF-Relevanz: {row.tfidf_level}\n"
            f"Fundstelle: Seite {row.page}"
        )
    return "\n\n".join(output)

def company_setup(company):
    text = f"Name: {company['name']}\n\n"
    text += f"Mit folgende Verpflichtungen: \n\nHauptleistungspflichten: \n"
    for i in range(len(company['main_obligations'])):
            text += f"{i+1}. {company['main_obligations'][i]}\n"
    text += f"\nNebenleistungspflichten: \n"
    for i in range(len(company['secondary_obligations'])):
            text += f"{i+1}. {company['secondary_obligations'][i]}\n"
    text += f"\nRechte:\n"
    for i in range(len(company['individual_rights'])):
            text += f"{i+1}. {company['individual_rights'][i]}\n"
    text += f"\nWeitere Pflichten und Verantwortlichkeiten: \n"
    for i in range(len(company['individual_responsibilities'])):
            text += f"{i+1}. {company['individual_responsibilities'][i]}\n"

    return text

    


analyse_contract()




