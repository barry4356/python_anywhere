# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
import os
import json
from CafConstants import NEW_CAF_UNIT
from CafPointMath import CalculateUnitCost

armyData = []
armyDataFiltered = []

def index():
    #session.clear()
    #session.new_unit = {'weapons': []}
    dataFilePath = os.path.join(request.folder, 'private', 'AllArmyData.json')
    if not session.new_unit:
        #TODO: Pull in the constants to auto-build new-unit struct
        session.new_unit = NEW_CAF_UNIT.copy()
        session.fastChecked = ''
        session.regenChecked = ''

    elif request.vars.request_id and request.vars.request_id == 'weaponBuild':
        session.new_unit['Weapons'].append({'Weapon Name': str(request.vars.wepName), 'Weapon qty per model': int(request.vars.qty), 'AP': int(request.vars.ap), 'Weapon Range': int(request.vars.range), 'Rending': bool(request.vars.rending)})
        #session.weapons = []
    elif request.vars.request_id == 'removeWeapon' and 'Weapons' in session.new_unit.keys() and session.new_unit['Weapons']:
        session.new_unit['Weapons'].pop()
    elif request.vars.request_id == 'unitBuild':
        pass

    session.new_unit['Cost'] = CalculateUnitCost(session.new_unit)
    #TODO add Finalization and point math
    #TODO add ajax hooks to update point math any time a value changes
    #TODO update point math when weapon is added to loadout
    #TODO run point math live on a new weapon being constructed
    return dict()


def add_weapon():
    weapons = request.vars.myWeapons
    new_weapon = Weapon.copy()
    weapons.append(new_weapon)
    #return 'HIYA'
    return weapons_to_html(weapons)

def select_handler():
    # Get the selected value from request.vars
    #selected_value = request.vars.value
    # Perform backend logic
    #result = "You selected: " + selected_value
    DefenseOptions = [3,4]
    return request.vars.qual # Or return a component/json


def weapons_to_html(weapons):
    html_string = ''
    for weapon in weapons:
        html_string += '<tr>\n'
        html_string += '<td><input type="text" name="weaponame" size=10></td>\n'
        html_string += '<td><input type="number" name="qtyPer" min="1" max="20" step="1" value="1"/></td>\n'
        html_string += '<td><input type="number" name="AP" min="0" max="8" step="1" value="0"/></td>\n'
        html_string += '<td><input type="number" name="Range" min="0" max="48" step="1" value="0"/></td>\n'
        html_string += '</tr>\n'
    return html_string


def remove_weapon():
    if session.new_unit['Weapons']:
        session.new_unit['Weapons'].pop()
    return "I TRIED"

def update_quality():
    if request.vars.quality:
        session.new_unit['Quality'] = int(request.vars.quality)
        session.new_unit['Cost'] = CalculateUnitCost(session.new_unit)
    return CalculateUnitCost(session.new_unit)

def update_defense():
    if request.vars.defense:
        session.new_unit['Defense'] = int(request.vars.defense)
        session.new_unit['Cost'] = CalculateUnitCost(session.new_unit)
    return CalculateUnitCost(session.new_unit)

def update_numOfModels():
    if request.vars.numOfModels:
        session.new_unit['Model Qty'] = int(request.vars.numOfModels)
        session.new_unit['Cost'] = CalculateUnitCost(session.new_unit)
    return CalculateUnitCost(session.new_unit)

def update_modelLength():
    if request.vars.modelLength:
        session.new_unit['modelLength'] = int(request.vars.modelLength)
    return session.new_unit['modelLength']

def update_modelWidth():
    if request.vars.modelWidth:
        session.new_unit['modelWidth'] = int(request.vars.modelWidth)
    return session.new_unit['modelWidth']

def update_modelHeight():
    if request.vars.modelHeight:
        session.new_unit['modelHeight'] = int(request.vars.modelHeight)
    return session.new_unit['modelHeight']

def update_Fast():
    session.new_unit['Fast'] = bool(request.vars.Fast)
    if session.new_unit['Fast']:
        session.fastChecked = 'checked'
    else:
        session.fastChecked = ''
    session.new_unit['Cost'] = CalculateUnitCost(session.new_unit)
    return CalculateUnitCost(session.new_unit)

def update_Regen():
    session.new_unit['Regeneration'] = bool(request.vars.Regen)
    if session.new_unit['Regeneration']:
        session.regenChecked = 'checked'
    else:
        session.regenChecked = ''
    session.new_unit['Cost'] = CalculateUnitCost(session.new_unit)
    return CalculateUnitCost(session.new_unit)


