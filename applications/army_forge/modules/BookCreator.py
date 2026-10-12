import json


emptyUpgradeSection = {
    "section": "COPY THE DESCRIPTION OF THIS UPGRADE SECTION FROM ARMY BOOK",
    "unit_level": "[true;false] DESCRIBES IF THIS UPGRADE APPLIES TO ONE MODEL OR WHOLE UNIT",
    "type": "[CHOOSE_MULTIPLE;CHOOSE_ONE] DETERMINES IF YOU GET TO PICK ONE UPGRADE OR MANY FROM LIST",
    "choices": []
}

emptyUpgradeChoice = {
    "name": "COPY CHOICE DESCRIPTION FROM ARMY BOOK",
    "price" : "COPY THE POINT COST OF THIS CHOICE FROM ARMY BOOK",
    "add_perks" : "LIST OF PERKS TO ADD TO UNIT IF THIS SELECTION IS CHOSEN (OPTIONAL)",
    "add_weapons" : "LIST OF WEAPONS TO ADD TO UNIT, IF THIS SELECTION CHOSEN (OPTIONAL)",
    "remove_weapons" : "LIST OF WEAPONS TO REMOVE FROM UNIT, IF THIS SELECTION CHOSEN (OPTIONAL)",
    "remove_x_weapons" : "STRING OF X WEAPONS; REMOVES SOME COPIES OF A WEAPON FROM UNIT (EG. 5X SWORDS BECOME 3X SWORDS)",
    "add_x_weapons" : "STRING OF X WEAPONS; ADDS SOME COPIES OF A WEAPON TO UNIT (EG. UNIT OF 5 MEN GET 4X SWORDS)",
    "add_tough" : "INT NUMBER OF TOUGH TO ADD TO EACH MODEL IN UNIT",
    "ID" : "UNIQUE INT IDENTIFYING THIS UPGRADE CHOICE",
    "enabled_by_id" : "ENABLING OPTIONS ID (INT); THIS OPTION ONLY ENABLED IF OPTION OF ID IS ENABLED"
}


def interactiveBookBuilder():
    bookName = input(f"What is a unique name for this army book? ")
    numberOfUnits = int(input(f"How many units does this army book have? "))
    numberOfSpells = int(input(f"How many Spells does this army's spellbook have? "))
    unitNames = []
    armyBook = {}
    armyBook['Units'] = {}
    try:
        for i in range(numberOfUnits):
            armyBookUnit = {}
            unitName = input(f"What is a unique name for unit {i+1}? ")
            if unitName in unitNames:
                print(f"ERROR: Name [{unitName}] already used in this army list")
                raise ("End and Save Early")
            unitNames.append(unitName)
            armyBookUnit['base_points'] = int(input(f"What is the base price (in points) of {unitName}? "))
            armyBookUnit['quality'] = int(input(f"What is the Qual rating of {unitName}? "))
            armyBookUnit['defense'] = int(input(f"What is the Def rating of {unitName}? "))
            tough = int(input(f"What is the Tough rating of {unitName}? "))
            if tough >= 2:
                armyBookUnit['tough'] = tough
            wepCount = int(input(f"How many weapons are assigned to {unitName}? "))
            armyBookUnit['weapons'] = []
            for j in range(wepCount):
                armyBookUnit['weapons'].append(f"EMPTY WEAPON {j+1}")
            perkCount = int(input(f"How many Special Rules / Perks / Keywords are assigned to {unitName}? "))
            armyBookUnit['perks'] = []
            for j in range(perkCount):
                armyBookUnit['perks'].append(f"PERK{j+1}")
            upgradeSectionCount = int(input(f"How many Upgrade Sections are in the army book for {unitName}? "))
            armyBookUnit['upgrades'] = []
            for j in range(upgradeSectionCount):
                upgradeSection = emptyUpgradeSection
                upgradeOptionCount = int(input(f"How many Upgrade Options are in the army book for {unitName} in upgrade section {j+1}? "))
                for i in range(upgradeOptionCount):
                    upgradeSection['choices'].append(emptyUpgradeChoice)
                armyBookUnit['upgrades'].append(upgradeSection)
            armyBookUnit['models'] = int(input(f"How many models are in the {unitName} unit? "))
            armyBookUnit['height'] = int(input(f"What is the model height for {unitName} models? "))
            armyBookUnit['class'] = input(f"What is the class for the {unitName} unit? (Heroes, Core Units, Artillery, etc.) ")
            armyBook['Units'][unitName] = armyBookUnit
    except:
        print("\nCaught Keyboard interrupt. Saving...")
    finally:
        filename = bookName.replace(' ','_') + '.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(armyBook, f, indent=2)


interactiveBookBuilder()