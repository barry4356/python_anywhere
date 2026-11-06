import pdfplumber
import re
import json

def parse_opr_pdf(pdf_path):
    data = {"Units": {}, "Keywords": {}, "SpellBooks": {"Human Empire Spells": {}}}
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

        # 1. Parse Keywords (Special Rules)
        # Assuming rules are on page 3 based on provided OCR
        rules_section = re.findall(r"SPECIAL RULES\n(.*?)\nAURA SPECIAL RULES", full_text, re.DOTALL)
        if rules_section:
            rules_list = re.split(r'\n(?=[A-Z][a-z]+(?:\s[A-Z][a-z]+)*:)', rules_section[0])
            for rule in rules_list:
                if ":" in rule:
                    name, desc = rule.split(":", 1)
                    data["Keywords"][name.strip()] = desc.strip().replace("\n", " ")

        # 2. Parse Spells
        spells_section = re.findall(r"ARMY SPELLS\n(.*?)$", full_text, re.DOTALL)
        if spells_section:
            spells = re.split(r'\n(?=[A-Z][a-z]+.*? \(\d+\):)', spells_section[0])
            for spell in spells:
                if "(" in spell and "):" in spell:
                    name_part, desc = spell.split("):", 1)
                    data["SpellBooks"]["Human Empire Spells"][name_part.strip() + ")"] = desc.strip().replace("\n", " ")

        # 3. Parse Units (Simplified extraction from Summary Table on Page 2)
        # This regex looks for Unit Name [Size] Quality Defense Equipment SpecialRules Points
        unit_rows = re.findall(r"([A-Za-z\s]+) \[(\d+)\] (\d+)\+ (\d+)\+ (.*?) (.*?) (\d+)pts", full_text)
        
        for name, size, qua, df, equip, rules, pts in unit_rows:
            unit_name = name.strip()
            
            # Extract Tough value from special rules if present
            tough_val = 1
            tough_match = re.search(r"Tough\((\d+)\)", rules)
            if tough_match:
                tough_val = int(tough_match.group(1))

            data["Units"][unit_name] = {
                "base_points": int(pts),
                "quality": int(qua),
                "defense": int(df),
                "tough": tough_val,
                "weapons": [e.strip() for e in equip.split(',')],
                "perks": [r.strip() for r in rules.split(',')],
                "upgrades": [], # Complex logic needed to link pg 4-9 upgrade blocks to units
                "models": int(size),
                "height": "",
                "class": ""
            }

        # 4. Parse Upgrades (Example for Battle Master - Page 4)
        # Real-world OPR parsing requires mapping "Upgrade with one" headers to specific units
        upgrade_blocks = re.findall(r"Upgrade with one\n(.*?)(?=\n[A-Z][a-z]|$)", full_text, re.DOTALL)
        if upgrade_blocks:
            choices = []
            for line in upgrade_blocks[0].strip().split('\n'):
                match = re.match(r"(.*?) \+(\d+)pts", line)
                if match:
                    name, price = match.groups()
                    choices.append({
                        "name": name.strip(),
                        "price": int(price),
                        "add_perks": [re.sub(r'\(.*?\)', '', name).strip()]
                    })
            
            if "Battle Master" in data["Units"]:
                data["Units"]["Battle Master"]["upgrades"].append({
                    "section": "Upgrade with one",
                    "unit_level": True,
                    "type": "CHOOSE_ONE",
                    "choices": choices
                })

    return data

# Usage
if __name__ == "__main__":
    # Replace with your actual file path
    # result = parse_opr_pdf("Human_Empire_v3.6.0.pdf")
    # print(json.dumps(result, indent=2))
    print("Script ready. Please ensure pdfplumber is installed and the PDF path is correct.")
