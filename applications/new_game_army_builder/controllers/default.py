# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
import os
import json

armyData = []
armyDataFiltered = []
QualityOptions = [2,3,4,5,6,7,8,9,10]
DefenseOptions = [2,3,4,5,6,7,8,9,10]
weapons = [{'weaponName': '', 'qtyPer': 1, 'AP': 0, 'range': 0}]
Weapon = {'weaponName': '', 'qtyPer': 1, 'AP': 0, 'range': 0}

def index():
    dataFilePath = os.path.join(request.folder, 'private', 'AllArmyData.json')
    with open(dataFilePath, 'r') as dataFile:
        armyData = json.load(dataFile)
        armyDataFiltered = armyData.copy()
    return dict(myWeapons=weapons, newWeapon=Weapon)


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












