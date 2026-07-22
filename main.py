from parse_pdf import extract_text
from api import evaluate_contract
from docx import Document
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import *
from tkinter.scrolledtext import ScrolledText

# pfad = C:\Users\finnd\Documents\Informatik\Projektarbeit\Test_Contract\Vertrag1.pdf

#combines all important functions all together
# def execute(root: Tk, financial_scale: Scale, legal_scale: Scale, operative_scale: Scale):
    
#     finance = financial_scale.get()
#     legal = legal_scale.get()
#     operative = operative_scale.get()

#     root.destroy

#     return finance, legal, operative


def analyse_contract():
    #zuerst abfragen wie user risiko gewichten möchte wenn überhaupt
    #https://www.geeksforgeeks.org/python/python-gui-tkinter/
    #get entry value via .scale() or Spinbox() configuration

    #möglichkeit von benutzerdefinierten Risikogewichtungen
    root = tk.Tk()

    finance_current = tk.IntVar()
    legal_current =  tk.IntVar()
    operative_current = tk.IntVar()

    financial_scale = Scale(root, from_=0, to=10, bd=5, tickinterval=5, orient=HORIZONTAL, variable = finance_current)
    legal_scale = Scale(root, from_=0, to=10, bd=5, tickinterval=5, orient=HORIZONTAL, variable= legal_current)
    operative_scale = Scale(root, from_=0, to=10, bd=5, tickinterval=5, orient=HORIZONTAL, variable= operative_current)

    financial_scale.grid(row=2, column=1)
    legal_scale.grid(row=4, column=1)
    operative_scale.grid(row=6, column=1)

    financial_scale.set(5)
    legal_scale.set(5)
    operative_scale.set(3)

    root.title("Vertragsanalyse - Vorabstimmung")
    
    all_label = tk.Label(root, text="Would you like to customise the risk evaluation, or would you rather use the default settings?")
    fin_label = tk.Label(root, text="Financial")
    legal_label = tk.Label(root, text="Legal")
    operative_label = tk.Label(root, text="Operative")

    all_label.grid(row=0)
    fin_label.grid(row=2, column=0)
    legal_label.grid(row=4, column=0)
    operative_label.grid(row=6, column=0)

    # financial_scale = tk.Entry(root)
    # legal_scale = tk.Entry(root)
    # operative_scale = tk.Entry(root)

    # financial_scale.grid(row=2, column=1)
    # legal_scale.grid(row=4, column=1)
    # operative_scale.grid(row=6, column=1)

    button = tk.Button(root, text="insert", width=25, command=root.destroy)

    button.grid(row=8)

    #aktuelle werte werden nicht abgegriffen, sondern nur vorher gesetzte

    root.mainloop()

    finance: int = finance_current.get()
    legal: int = legal_current.get()
    operative: int = operative_current.get()

    save_dataset_risk(finance, legal, operative)

    #test ob variablen funktionieren
    print(fr"{str(finance)}", "\n", fr"{str(legal)}", "\n", fr"{str(operative)}")
    print(type(finance), type(legal), type(operative)) 

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
        #content_of_contract = extract_text(pdf_path) #extrahieren des textes mittels des pdf parsers
        #preprocessing(content_of_contract, finance, legal, operative)
        #evaluation: str = evaluate_contract(content_of_contract) #übersenden des textes an KI und Evaluation von diesem
        #print(evaluation)
    else:
        print("Pfad ist nicht vorhanden")
    #textfeld zur ausgabe von analyse
    # maybe .message function for formatted output
    # .progressbar for better visualisation of risk scaling? (optional, if enough time left)
    root2 = tk.Tk()
    root2.title("Vetragsanalyse")
    root2.geometry("1024x768")

    text = ScrolledText(root2)

    text.pack()

    text.insert("end", """Gerne, hier ist die Analyse des von Ihnen bereitgestellten "DISTRIBUTOR AGREEMENT" von LIMEENERGYCO.

**Gesamtbewertung des Risikos:** 6/10

**Begründung der Risikobewertung:**

Der Vertrag weist ein moderates Risiko auf, das sich aus einer Kombination von Faktoren ergibt, die sowohl Chancen als auch potenzielle Fallstricke für beide Parteien bergen.

*   **Exklusivität und Marktgebiet (Abschnitt 1.1, 1.6):** Die Exklusivität für den "Market" (Bundesstaat Illinois) ist ein Vorteil für den Distributor, birgt aber auch das Risiko, dass die Mindestabnahmemengen nicht erreicht werden und die Exklusivität entzogen wird. Die detaillierten Mindestmengen (1.6) sind ein klarer Indikator für das Risiko, diese nicht zu erfüllen.
*   **Vertragsdauer und Verlängerung (Abschnitt 1.3):** Eine anfängliche Laufzeit von 10 Jahren mit jährlichen Verlängerungsoptionen ist lang. Dies bietet Stabilität, aber auch das Risiko, dass eine Partei über einen längeren Zeitraum an eine ungünstige Vereinbarung gebunden ist.
*   **Preisgestaltung und Anpassung (Abschnitt 2.4):** Die Preisgestaltung ist an den Verbraucherpreisindex (CPI) gekoppelt, was eine gewisse Vorhersehbarkeit bietet. Das Recht des Unternehmens, Preise aus anderen Gründen anzupassen (basierend auf Kosten oder Marktnachfrage), birgt jedoch ein Risiko für den Distributor, wenn diese Anpassungen seine Gewinnmargen schmälern. Die Klausel, dass Preiserhöhungen aufgrund der Marktnachfrage "nicht so groß sein dürfen, dass sie den Distributor seines normalen und üblichen Gewinnmargen berauben" (2.4(B)), ist ein wichtiger Schutz für den Distributor, aber die Auslegung "normal und üblich" kann zu Streitigkeiten führen.
*   **Produktverbesserungen und neue Produkte (Abschnitt 3.1, 7):** Das Recht des Unternehmens, Produkte zu verbessern oder neue einzuführen, ist sowohl eine Chance als auch ein Risiko. Der Distributor hat ein Optionsrecht für neue Produkte (7.1), aber die Bedingungen werden in separaten Vereinbarungen festgelegt (7.3), was zu Unsicherheit führen kann. Die Möglichkeit, dass alte Produkte eingestellt werden, wenn neue besser oder preislich vergleichbar sind (3.1), kann die Produktpalette des Distributors beeinflussen.
*   **Gewährleistung und Haftung (Abschnitt 2.2, 2.6, 3.3, 3.4, 5.3):** Die Gewährleistung von 24 Monaten (3.3) ist Standard. Die Regelungen zur Fehlerbehebung und Kostentragung bei Mängeln (2.6(B), 3.4) sind relativ klar, aber die Möglichkeit, dass das Unternehmen die Verantwortung bestreitet (3.4), birgt ein Risiko. Die gegenseitige Freistellung (Indemnification) in Abschnitt 5.3 ist ein wichtiger Punkt zur Risikominimierung, aber die Auslegung von "Fahrlässigkeit oder Verschulden" kann zu Meinungsverschiedenheiten führen.
*   **Vertragsbruch und Kündigung (Abschnitt 4.2):** Die Kündigungsmöglichkeiten sind relativ standardmäßig, aber die 30-tägige Kündigungsfrist bei Nichterfüllung (4.2(b)) könnte für den Distributor knapp sein, wenn er einen Fehler nicht schnell beheben kann.
*   **Repurchase-Klausel (Abschnitt 4.4):** Die Option des Unternehmens, Produkte nach Vertragsende zurückzukaufen, ist ein potenzieller Schutz für den Distributor, aber die Bedingungen (nur auf Wunsch des Unternehmens, abzüglich Rabatte etc.) sind nicht vollständig zugunsten des Distributors gestaltet.
*   **Vertraulichkeit und Nicht-Wettbewerb (Abschnitt 3.6, 5.6, 5.7):** Die Klauseln zur Vertraulichkeit und zum Verbot der Anwerbung von Mitarbeitern und Kunden sind für das Unternehmen vorteilhaft, aber die 12- bzw. 18-monatigen Fristen nach Vertragsende können die Geschäftsmöglichkeiten des Distributors einschränken.

**Zusammenfassung der wichtigsten Punkte des Vertrages:**

Dieser "DISTRIBUTOR AGREEMENT" regelt die Beziehung zwischen Electric City Corp. ("Company") und Electric City of Illinois LLC ("Distributor") für den Vertrieb von "Energy Saver"-Produkten in Illinois.

*   **Exklusivität:** Der Distributor erhält die exklusive Vertriebsrechte für die Produkte in Illinois.
*   **Vertragslaufzeit:** Der Vertrag hat eine anfängliche Laufzeit von 10 Jahren, mit jährlichen Verlängerungsoptionen bis zu weiteren 10 Jahren.
*   **Mindestabnahmemengen:** Der Distributor muss bestimmte Mindestmengen an Produkten pro Jahr abnehmen, um seine Exklusivrechte zu behalten. Bei Nichterfüllung können die exklusiven Rechte neu bewertet werden, es sei denn, es liegt eine höhere Gewalt vor.
*   **Preisgestaltung:** Die Preise sind anfangs festgelegt und werden jährlich an den Verbraucherpreisindex (CPI) angepasst. Das Unternehmen kann Preise auch aus anderen Gründen anpassen, muss dabei aber die Gewinnmargen des Distributors berücksichtigen.
*   **Produktverbesserungen und neue Produkte:** Das Unternehmen kann Produkte verbessern oder neue einführen. Der Distributor hat ein Optionsrecht, diese ebenfalls exklusiv zu vertreiben, wobei die Konditionen in separaten Verträgen geregelt werden.
*   **Gewährleistung:** Das Unternehmen gewährt eine 24-monatige Garantie auf die Produkte. Die Kosten für die Behebung von Mängeln werden in der Regel vom Unternehmen getragen.
*   **Zahlungsbedingungen:** Der Distributor muss innerhalb von 30 Tagen nach Erhalt der Produkte bezahlen.
*   **Kündigung:** Der Vertrag kann aus wichtigem Grund (z.B. Zahlungsverzug, wesentliche Vertragsverletzung, Insolvenz) mit 30 Tagen Frist gekündigt werden.
*   **Rückkauf:** Nach Vertragsende hat das Unternehmen die Option, unverkaufte Produkte vom Distributor zurückzukaufen.
*   **Haftung und Freistellung:** Beide Parteien verpflichten sich zur gegenseitigen Freistellung bei Verstößen gegen den Vertrag, Fahrlässigkeit oder Verletzung von Schutzrechten Dritter. Das Unternehmen sichert zu, eine Produkthaftpflichtversicherung abzuschließen und den Distributor als zusätzlichen Versicherungsnehmer einzutragen.
*   **Vertraulichkeit und Wettbewerbsbeschränkungen:** Beide Parteien müssen vertrauliche Informationen schützen. Der Distributor unterliegt nach Vertragsende Beschränkungen bezüglich der Anwerbung von Mitarbeitern und Kunden des Unternehmens sowie dem Verkauf von Konkurrenzprodukten.
*   **Anwendbares Recht:** Das Recht des Staates Illinois gilt für diesen Vertrag.""") #benutzen von label damit user nicht ausversehen in die anzeige schreiben kann & font=()
    # label.config(anchor="center", font=("Times New Roman", 20, "bold"), relief="solid")
    root2.mainloop()
        # doc = Document()

        # # doc.add_page_break

        # doc.add_heading(f"Contract Analysis by Ki-Assistent")

        # doc.add_paragraph(evaluation)

        # doc.save(fr"C:\Users\finnd\Documents\Informatik\Projektarbeit\Analysis\Contract_Analysis_Ki-Assistant.docx")

def save_dataset_risk(finance_risk: int, legal_risk: int, operative_risk: int):

    return None



analyse_contract()

# für umgebung virtual environment oder docker?




