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


def displayArmyBook(filename):
    army_book = {}
    with open (filename, 'r') as jsonFile:
        army_book = json.load(jsonFile)
    print("Name[size] \t\t\t Qua \tDef \t Equipment \t\t\t\t\t\t\t\t Special Rules \t\t\t\t\t\t\t Cost")
    units = army_book['Units']
    for unit_name in army_book['Units']:
        unit = army_book['Units'][unit_name]
        unit_name_count = str(f"{unit_name} [{unit['models']}]")
        print(f"{unit_name_count:<24}\t {unit['quality']}+ \t{unit['defense']}+ \t {str(unit['weapons']):<64} \t {str(unit['perks']):<56} \t {unit['base_points']}")
    while(True):
        selection = input("\nN - View Next Section (Upgrades); Q - Quit\n")
        if selection.lower().strip() == 'q':
            return
        elif selection.lower().strip() == 'n':
            break
    for unit_name in army_book['Units']:
        unit = army_book['Units'][unit_name]
        print(f"\n\n\n\t{unit_name} [{str(unit['models'])}] - {unit['base_points']} pts")
        print(f"\t{unit['quality']}+ \t{unit['defense']}+\n")
        for weapon in unit['weapons']:
            print(f"{weapon}")
        print()
        perks = ''
        for perk in unit['perks']:
            perks += perk + ','
        perks = perks.strip(',')
        print(perks+'\n')
        for section in unit['upgrades']:
            print('\t'+section['section'])
            for choice in section['choices']:
                print(f"+{choice['price']}pts {choice['name']}")
        while(True):
            selection = input("\nN - View Next Unit; Q - Quit\n")
            if selection.lower().strip() == 'q':
                return
            elif selection.lower().strip() == 'n':
                break

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


def ArmyBookChecker(filename):
    try:
        army_book = {}
        valid = True
        with open (filename, 'r') as jsonFile:
            army_book = json.load(jsonFile)
        if "Units" not in army_book.keys():
            print(f"ERROR: {filename} Missing 'Units' section")
            valid = False
        for unit_key in army_book.get("Units",[]):
            unit = army_book["Units"].get(unit_key)
            base_points = int(unit.get('base_points'))
            if not base_points:
                print(f"ERROR: {filename}: {unit_key} includes invalid Point Cost")
                valid = False
            #Check for perks strings in keywords lists TODO
            upgrades = unit.get('upgrades')
            for upgrade in upgrades:
                if 'section' not in upgrade.keys():
                    print(f"ERROR: {filename}: {unit_key}: Missing Upgrade Section Field")
                    print(json.dumps(upgrade, indent=2))
                    valid = False
                type = upgrade.get('type')
                if type != "CHOOSE_ONE" and type != "CHOOSE_MULTIPLE":
                    print(f"ERROR: {filename}: {unit_key}: Invalid Upgrade Type")
                    print(json.dumps(upgrade, indent=2))
                    valid = False
                for choice in upgrade.get('choices'):
                    if 'remove_weapons' in choice.keys():
                        for rmweapon in choice.get('remove_weapons',[]):
                            validWeapon = False
                            for unitWeapon in unit.get('weapons', []):
                                if unitWeapon in rmweapon:
                                    validWeapon = True
                                    continue
                            if not validWeapon:
                                print(f"ERROR: {filename}: {unit_key}: Invalid Weapon Replacement: {rmweapon}")
                                print(f"Valid weapons: {unit.get("weapons")}")
                                valid = False
                    if 'add_weapons' in choice.keys():
                        for addweapon in choice.get('add_weapons', []):
                            if addweapon not in choice['name']:
                                print(f"WARNING: {filename}: {unit_key}: Add weapon is suspicious: {addweapon}")
            #Check weapon replace upgrades replace real waepon
            pass
    except Exception as e:
        print(f"ERROR: {filename} failed validation for unknown reason!")
        print(e)
        valid = False
    finally:
        if valid:
            print(f"{filename} PASSED Validation")
        else:
            print(f"{filename} FAILED Validation")

ArmyBookChecker('../private/ArmyBooks/Chivalrous_Kingdoms_V3.4.4_BETA.json')
displayArmyBook('../private/ArmyBooks/Chivalrous_Kingdoms_V3.4.4_BETA.json')