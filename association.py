import pdfplumber
import re
from datetime import datetime



def procesar_documento(document_path):
    result = {
        "current_date": "",
        "group_number": "",
        "group_name": "",
        "subscriber_name": "",
        "subscriber_id": "",
        "patient_name": "",
        "relationship": "",
        "birth_date": "",
        "effective_date": "",
        "termination_date": "",
        "wait_period": "",
        "benefit_year": "",
        "how2_benefits": "",
        "enhanced_dental": "",
        "ortho_waiting_period": "",
        "individual_annual_deductible": {"ppo": "", "premier": "", "non_par": ""},
        "individual_remaining_annual_deductible": {"ppo": "", "premier": "", "non_par": ""},
        "family_annual_deductible": {"ppo": "", "premier": "", "non_par": ""},
        "family_remaining_annual_deductible": {"ppo": "", "premier": "", "non_par": ""},
        "individual_annual_max": {"ppo": "", "premier": "", "non_par": ""},
        "remaining_annual_max": {"ppo": "", "premier": "", "non_par": ""},
        "ortho_lifetime_max": {"ppo": "", "premier": "", "non_par": ""},
        "ortho_remaining_lifetime_max": {"ppo": "", "premier": "", "non_par": ""}
    }

    with pdfplumber.open(document_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

        # Expresiones regulares para extraer datos
        patterns = {
            "current_date": r"Today's Date: (.+?)\n",
            "group_number": r"Group Number: (.+?)\n",
            "group_name": r"Group Name: (.+?) Individual Annual Deductible:",
            "subscriber_name": r"Subscriber Name: (.+?) Remaining Annual Deductible:",
            "subscriber_id": r"Subscriber ID: (.+?) Family Annual Deductible:",
            "patient_name": r"Patient Name: (.+?) Remaining Annual Deductible:",
            "relationship": r"Relationship: (.+?) Individual Annual Max:",
            "birth_date": r"Birth Date: (.+?) Remaining Annual Max:",
            "effective_date": r"Effective Date: (.+?) Ortho Lifetime Max:",
            "termination_date": r"Termination Date: (.+?) Ortho Remaining Lifetime Max:",
            "benefit_year": r"Benefit Year: (.+?)\n",
            "how2_benefits": r"Score\)\s*\n\s*(.*?)\s*\nThis outline",
            "enhanced_dental": r"Enhanced Dentals: (.+?)\n",
            "ortho_waiting_period": r"Ortho Wait Period Ends: (.+?)\n"
        }

        benefit_patterns = {
            "Individual Annual Deductible": r".*Individual Annual Deductible: (.+?)\n",
            "individual_remaining_annual_deductible": r"Subscriber Name: .*Remaining Annual Deductible: (.+?)\n",
            "Family Annual Deductible": r".*Family Annual Deductible: (.+?)\n",
            "family_remaining_annual_deductible": r"Patient Name: .*Remaining Annual Deductible: (.+?)\n",
            "Individual Annual Max": r".*Individual Annual Max: (.+?)\n",
            "remaining_annual_max": r".*Remaining Annual Max: (.+?)\n",
            "Ortho Remaining Lifetime Max": r".*Ortho Remaining Lifetime Max: (.+?)\n",
            "Ortho Lifetime Max": r".*Ortho Lifetime Max: (.+?)\n",
        }

        # Expresiones regulares para extraer plan summary
        plan_summary_patterns = {
            "deductible": r"Non-Participating\s*\n\s*(.*?)\s*\nThe information",
            "class_i_preventive_and_diagnostic_services": r"Class I Preventive and Diagnostic Services\s*\d+% \d+% \d+%\s*(.+?)Class II",
            "class_ii_basic_services": r"Class II Basic Services\s*\d+% \d+% \d+%\s*(.+?)Class III",
            "class_iii_major_restorative_services": r"Class III Major Restorative Services\s*\d+% \d+% \d+%\s*Crowns\s*(.+?)Implants",
            "implants": r"Implants\s*\d+% \d+% \d+%\s*(.+?)Orthodontic Services",
            "orthodontic_services_child": r"Orthodontic Services Child Only\s*\d+% \d+% \d+%\s*(.+?)Dependents",
            "dependents": r"Dependents\s*(.+?)\nHOW® Benefits",
            "how2_benefits": r"Score\)\s*\n\s*(.*?)\s*\nThis outline",
        }

        # Extraer datos básicos
        for key, pattern in patterns.items():
            match = re.search(pattern, full_text)
 
            if match:
                result[key] = match.group(1).strip()
                if key == "how2_benefits":
                    result[key] = result[key].replace("®", "")

        # Extraer datos de beneficios con múltiples valores

        for key, pattern in benefit_patterns.items():
            match = re.search(pattern, full_text)
    
            if match:
                values = [v.strip() for v in match.group(1).split(" ") if v.strip()]
                if len(values) == 3:
                    mapped_key = key.lower().replace(" ", "_")
                    result[mapped_key] = {
                        "ppo": values[0].replace("$", ""),
                        "premier": values[1].replace("$", ""),
                        "non_par": values[2].replace("$", "")
                    }

        for key, pattern in plan_summary_patterns.items():
            match = re.search(pattern, full_text, re.DOTALL)
            if match:
                result[key] = match.group(1).strip().replace("\n", " ")
            else:
                if key == "how2_benefits" and "how2_benefits" in result and result["how2_benefits"] == "":
                    result[key] = "No"

        # Limpieza final
        result["wait_period"] = f"{result.get('wait_period', '')} Ortho" if result.get('wait_period') == "None" else ""
        result["enhanced_dental"] = result["enhanced_dental"].replace("Dentals:", "").strip()

    return result

