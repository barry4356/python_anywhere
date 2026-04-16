# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
import os
import json


armyData = []
armyDataFiltered = []
QualityOptions = [2,3,4,5,6,7,8,9,10]
DefenseOptions = [2,3,4,5,6,7,8,9,10]
Weapon = {'weaponName': '', 'qtyPer': 1, 'AP': 0, 'range': 0}

def index():
    #session.new_unit = {'weapons': []}
    dataFilePath = os.path.join(request.folder, 'private', 'AllArmyData.json')
    if not session.new_unit:
        #TODO: Pull in the constants to auto-build new-unit struct
        session.new_unit = {'weapons': []}
    elif request.vars.request_id and request.vars.request_id == 'weaponBuild':
        session.new_unit['weapons'].append({'weaponName': request.vars.wepName, 'qtyPer': request.vars.qty, 'AP': request.vars.ap, 'range': request.vars.range, 'rending': request.vars.rending})
        #session.weapons = []
    elif request.vars.request_id == 'removeWeapon' and 'weapons' in session.new_unit.keys() and session.new_unit['weapons']:
        session.new_unit['weapons'].pop()
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
    if session.new_unit['weapons']:
        session.new_unit['weapons'].pop()
    return "I TRIED"









