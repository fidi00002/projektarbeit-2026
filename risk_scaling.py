import pandas as pd

def calculation_of_risk_score(df: pd.DataFrame, use_all_risks: bool, u_pri_le, u_pri_fi, u_pri_op): #evaluated_df: pd.DataFrame, u_pri_le, u_pri_fi, u_pri_op
    #zeilen, welche relevant = 'False' haben, müssen vorher noch entfernt werden und dementsprechend sollten auch keine risk_score mit '0.0' drin sein, da diese als False deklariert sind in Spalte 'relevant'
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

    
