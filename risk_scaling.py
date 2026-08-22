import pandas as pd


risk_field: dict = {

        "operative": { #so mäßig alle wichtigen Sachen die sich um Ogranisation und Co. drehen
            "inspection", "delay", "exclusive", #bindet an jeweiligen Partner
            "warranty", "confidential", "quality|performance", #bindende Standards
            "injunction|restraining", "disclosure", #Handling von offengelegten Daten
            "misleading | untrue | omission" #Umgang mit irreführenden / ausgelassenen Informationen im Vertrag
        },

        "financial": { #alle Sachen die sich um diverse finanzielle Aspekte drehen
            "pay|payment", "credit/letter | LC | letter of credit" , #Zahlungsgarantie einer Bank
            "insurance|coverage", "indemnify", #entschädigen
            "damage", "repurchase", #Rückkaufpflicht
            "CPI | Consumer Price Index", #Vertragsklausel zur Inflationsanpassung
            "termination", #Beendigung Vertrag wenn {Bedingung} eintritt
            "default", "infringment|infringe", "fees", "coverage", #Haftungsausschluss
            "loss", "expenses" # Zusatzkosten

        },

        "legal": { #alle Sachen die rechtliche Bedingungen, Konsequenzen und Co. behandeln
            "liability", "claim", #beanspruchen
            "cancellation", "penalty", "arbitration|mediaton", #parties agree to settle possible disputes outside of court
            "dispute", "failure", "indemnify" # entschädigen,
            "force majeure | acts of god", #Leistungspflicht Befreiung aufgrund von unvorhergesehenen|externen Ereignissen (bspw. Naturkatastrophe = act of god)
            "breach", #Verstoß
            "hold harmless", #Partei verspricht anderer Partei von rechtliche, finanziellen Forderungen Dritter freizustellen
            "waiver", #Verzicht
            "termination", "default", #Verletzung Vertragspflicht = Vertrag kann sofort gekündigt werden
            "sabotage", "wars", "injunction|restraining", #Unterlassung von spezifischer Tätigkeit
            "infringment", #Verstoß
            "misconduct|violation" #Verletzung von Vertragsbedingungen
        }
    }

def merging_risk_tf_idf(Tf_IDF: pd.DataFrame, Risk_words: pd.DataFrame):
    raise NotImplementedError("function isn't declared yet")


def calculation_of_risk_score(df: pd.DataFrame, use_all_risks: bool, u_pri_le, u_pri_fi, u_pri_op): #evaluated_df: pd.DataFrame, u_pri_le, u_pri_fi, u_pri_op
    legal_risk_values = []
    financial_risk_values = []
    operative_risk_values = []
    #zeilen, welche relevant = 'False' haben, müssen vorher noch entfernt werden und dementsprechend sollten auch keine risk_score mit '0.0' drin sein, da diese als False deklariert sind in Spalte 'relevant'
    print(df)
    print("\n")
    df = df.sort_values("risk_value", ascending=False)
    if not (use_all_risks):
        df = df.groupby("risk_category").head()

    risk_values_dict = df.groupby("risk_category")["risk_value"].apply(list).to_dict()

    legal_risk_values = risk_values_dict.get("legal", [])
    financial_risk_values = risk_values_dict.get("financial", [])
    operative_risk_values = risk_values_dict.get("operative", [])

    first_risk_value_legal = (legal_risk_values.pop(0) if legal_risk_values else 0)
    first_risk_value_financial = (financial_risk_values.pop(0) if financial_risk_values else 0)
    first_risk_value_operative = (operative_risk_values.pop(0) if operative_risk_values else 0)

    legal_category_score = foundation_calculation(legal_risk_values)
    financial_category_score = foundation_calculation(financial_risk_values)
    operative_category_score = foundation_calculation(operative_risk_values)

    legal_category_score = min(10, (u_pri_le  * (0.5 * first_risk_value_legal + 0.5 * legal_category_score if legal_risk_values else first_risk_value_legal)))
    financial_category_score = min(10,(u_pri_fi * (0.5 * first_risk_value_financial + 0.5 * financial_category_score if financial_risk_values else first_risk_value_financial)))
    operative_category_score = min(10, (u_pri_op * (0.5 * first_risk_value_operative + 0.5 * operative_category_score if operative_risk_values else first_risk_value_operative)))

    median_categories = (legal_category_score + financial_category_score + operative_category_score)/3

    #anzahl der reihen pro kategorie rausschreiben
    #im anschluss diese an anzahl angepasst normalisieren
    print(df)
    print(legal_risk_values, "\n", financial_risk_values, "\n", operative_risk_values)
    print(f"Legal_risk = {round(legal_category_score, 2)} \nFinancial_risk: {round(financial_category_score, 2)} \n"
          f"Operative_risk = {round(operative_category_score, 2)} \nMedian = {round(median_categories, 2)}")
    
    return round(legal_category_score, 2), round(financial_category_score, 2),  round(operative_category_score, 2), round(median_categories, 2)

def foundation_calculation(risk_list): #C-Part of formula while pulling forward factor of user given priority/weight
    if len(risk_list) == 0:
        return 0
    else:
        sum_risks = 0
        amount_risks = 0 
        for i in range(len(risk_list)):
            if risk_list[i] == 0:
                continue
            else:
                sum_risks += risk_list[i]
                amount_risks += 1
        if amount_risks == 0:
            return 0
        return (sum_risks/amount_risks)

    
