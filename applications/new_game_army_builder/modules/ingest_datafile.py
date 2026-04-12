import json
import traceback

#This file take an output from the Army Book Parser Scripts (RPG Helpers Project) and converts it into the Army builder format for the Web2py project

dataFile = 'ArmyData__3_5_2.json'

CafUnitData = {}
CafWeaponData = {}
CafLinkValData = {}

def check_for_duplicate_and_update(OprUnit, CafUnitData, CafWeaponData, CafLinkValData):
    # Check if this unit is redundant. If so; check if we need to drop cost; if so... do that
    return False

def convert_opr_to_caf(OprUnit):
    return {}

# ----- MAIN -----

OprData = []
with open(dataFile, 'r') as jsonfile:
    OprData = json.load(jsonfile)
#print(json.dumps(OprData, indent=2))
#Break OprData into models; weaponLoads; and Links (Validating the full chain and logging errors)
for OprUnit in OprData:
    try:
        #Check OprUnit for required fields
        requiredInts = ['Qual', 'Def', 'ModelCount', 'Cost']
        requiredFields = ['Weapons']
        for requiredField in requiredFields:
            if requiredField not in OprUnit.keys():
                print(f'Skipping OprUnit [{OprUnit["Name"]}]: Missing key [{requiredField}]')
        for requiredInt in requiredInts:
            test = int(OprUnit[requiredInt])
        #Check if duplicate; If duplicate check if we're updating the existing entry or not
        uniqueUnit = check_for_duplicate_and_update(OprUnit, CafUnitData, CafWeaponData, CafLinkValData)
        if not uniqueUnit:
            continue
        NewUnit = convert_opr_to_caf(OprUnit)
        append_new_caf_unit(NewUnit, CafUnitData, CafWeaponData, CafLinkValData)
            
        
    except Exception as e:
        print(e)
        traceback.print_exc()