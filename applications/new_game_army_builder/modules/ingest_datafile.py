import json
import traceback
from constants import NEW_CAF_UNIT, NEW_CAF_WEAPON

#This file take an output from the Army Book Parser Scripts (RPG Helpers Project) and converts it into the Army builder format for the Web2py project

dataFile = 'ArmyData__3_5_2.json'

CafUnitData = []

def validate_caf_unit(cafUnit):
    return True

def check_for_duplicate_and_update(NewUnit):
    return True
    ## Check if this unit is redundant. If so; check if we need to drop cost; if so... do that
    #for existingUnit in CafUnitData:
    #    for field in NEW_CAF_UNIT.keys():
    #        if existingUnit[field] != NewUnit[field]:
    #            return True #Unique
    #    for weapon in existingUnit['Weapons']:
    #        for weapon in NewUnit['Weapon']:
    #            pass
    #return False #Not Unique

def convert_opr_to_caf(OprUnit):
    cafUnit = NEW_CAF_UNIT.copy()
    cafUnit['Model Qty'] = OprUnit['ModelCount']
    cafUnit['Quality'] = 10-(2*(6-int(OprUnit["Qual"])))
    if cafUnit['Quality'] < 2:
        cafUnit['Quality'] = 2
    if cafUnit['Quality'] > 10:
        cafUnit['Quality'] = 10
    cafUnit['Defense'] = 10-(2*(6-int(OprUnit['Def'])))
    if cafUnit['Defense'] < 2:
        cafUnit['Defense'] = 2
    if cafUnit['Defense'] > 10:
        cafUnit['Defense'] = 10
    cafUnit['Special Perks'] = OprUnit['Specs']
    if 'Tough' in OprUnit.keys():
        if OprUnit['Tough'] > 1:
            cafUnit['Special Perks'].append('Tough('+str(OprUnit['Tough'])+')')
    #Remove dulicates and empty perks
    cafUnit['Special Perks'] = list(set(cafUnit['Special Perks']))
    cafUnit['Special Perks'] = [s for s in cafUnit['Special Perks'] if s]
    cafUnit['Cost'] = OprUnit['Cost']
    cafUnit['Weapons'] = []
    for weapon in OprUnit['Weapons']:
        cafWeapon = NEW_CAF_WEAPON.copy()
        cafWeapon['Weapon Perks'] = weapon['Specs']
        #TODO: LIMIT TO ONLY SUPPORTED PERKS?
        if 'range' in weapon.keys():
            cafWeapon['Weapon Range'] = weapon['range']
        if 'Count' in weapon.keys():
            cafWeapon['Quantity'] = weapon['Count']
        else:
            #if not specified; one weapon per model
            cafWeapon['Quantity'] = cafUnit['Model Qty']
        cafWeapon['Weapon qty per model'] = weapon['Attacks']
        cafUnit['Weapons'].append(cafWeapon)
    #TODO: Attacks per weapon??
    return cafUnit

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
        NewUnit = convert_opr_to_caf(OprUnit)
        #Check if duplicate; If duplicate check if we're updating the existing entry or not
        uniqueUnit = check_for_duplicate_and_update(NewUnit)
        if not uniqueUnit:
            continue
        CafUnitData.append(NewUnit)
            
        
    except Exception as e:
        print(e)
        traceback.print_exc()
CafUnitData = sorted(CafUnitData, key=lambda d: d['Cost'])
with open('../private/AllArmyData.json', 'w') as f:
    json.dump(CafUnitData, f, indent=2)
print(json.dumps(CafUnitData, indent=2))