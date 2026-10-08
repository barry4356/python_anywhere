# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
import os
import json
import uuid
import copy
import html
import json


armyData = []
armyDataFiltered = []

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

def index():
    #### Initializations ###
    #session.army_book = ''
    #session.clear()
    #session.new_unit = {'weapons': []}
    #response.flash = ""
    if not session.army_list:
        session.army_list = {}
    if not session.current_tab:
        session.current_tab = 1
    if not session.armyLists:
        session.armyLists = []
    if session.forceOrgPass == None:
        session.forceOrgPass = True
    if not session.armyBooks:
        ArmyBookRepo = os.path.join(request.folder, 'private', 'ArmyBooks')
        armyBookFiles = [f for f in os.listdir(ArmyBookRepo) if f.endswith('.json')]
        armyBookFiles.sort()
        session.armyBooks = [armyBook.replace("_", " ").replace('.json','') for armyBook in armyBookFiles]

    ### Form Submissions ###
    if request.vars.request_id == 'selectArmyBook':
        session.army_book_name = request.vars.bookSelection
        session.army_book_json = request.vars.bookSelection.replace(' ','_') + '.json'
        with open(os.path.join(request.folder, 'private', 'ArmyBooks', session.army_book_json), 'r') as file:
            session.army_book = json.load(file)
        session.army_list = {"Units": {}, "ArmyBook": session.army_book_json, "Price": 0}
        session.list_name = "None"
        redirect(URL('index'))
    elif request.vars.request_id == 'AddUnitToList':
        unit_uuid = str(uuid.uuid4())
        new_unit = copy.deepcopy(session.army_book['Units'][request.vars.unitName])
        new_unit['unit_type'] = request.vars.unitName
        new_unit['name'] = ''
        new_unit['price'] = session.army_book['Units'][request.vars.unitName]["base_points"]
        new_unit['combined'] = False
        for upgrade in new_unit['upgrades']:
            for choice in upgrade['choices']:
                choice['selected'] = False
        session.army_list["Units"][unit_uuid] = new_unit
        updateListCost()
        force_org_check()
        redirect(URL('index'))
    elif request.vars.request_id == 'updateListName':
        session.list_name = request.vars.listName
        redirect(URL('index'))
    elif request.vars.request_id == 'loadArmyList':
        session.list_name = request.vars.armyFileSelection
        session.army_list_json = request.vars.armyFileSelection.replace(' ','_') + '.json'
        with open(os.path.join(request.folder, 'private', 'ArmyLists', session.username, session.army_list_json), 'r') as file:
            session.army_list = json.load(file)
        session.army_book_json = session.army_list['ArmyBook']
        session.army_book_name = session.army_book_json.replace('_',' ').replace('.json','')
        with open(os.path.join(request.folder, 'private', 'ArmyBooks', session.army_book_json), 'r') as file:
            session.army_book = json.load(file)
        session.current_tab = 1
        updateListCost()
        force_org_check()
        redirect(URL('index'))
    elif request.vars.request_id == 'updateUnitName':
        unit = session.army_list["Units"][request.vars.unitKey]
        unit["name"] = request.vars.unitName
        session.editUnit = copy.deepcopy(unit)
        session.editUnit['unit_key'] = request.vars.unitKey
        redirect(URL('index'))
    elif request.vars.request_id == 'uploadListFile':
        uploaded_file = request.vars.textFile.file
        filename = request.vars.textFile.filename
        session.army_list = json.load(uploaded_file)
        session.list_name = filename.replace('_',' ').replace('.json','')
        redirect(URL('index'))
    elif request.vars.request_id == 'embedHero':
        hero = session.army_list["Units"][request.vars.heroKey]
        #if hero was previously embedded, break the connection first
        if hero.get('embedded_in', None):
            previous_unitkey = hero['embedded_in']
            previous_unit = session.army_list['Units'][previous_unitkey]
            previous_unit['embedded_by'] = None
        if request.vars.embedSelection == "None":
            hero['embedded_in'] = None
        else:
            unit_key = session.embeddable_unitLookup[request.vars.embedSelection]
            unit = session.army_list["Units"][unit_key]
            #Embed hero in unit
            hero['embedded_in'] = unit_key
            unit['embedded_by'] = request.vars.heroKey
        update_embeddable_unit_names()
        reorder_units()
        session.editUnit = copy.deepcopy(hero)
        session.editUnit['unit_key'] = request.vars.heroKey
        redirect(URL('index'))

    return dict()

def updateAvailableLists():
    if not session.username:
        username = auth.user.email
        username = username.replace('.','_').replace('@','__')
        session.username = username
    ArmyListRepo = os.path.join(request.folder, 'private', 'ArmyLists', session.username)
    armyListFiles = [f for f in os.listdir(ArmyListRepo) if f.endswith('.json')]
    session.armyLists = [armyList.replace("_", " ").replace('.json','') for armyList in armyListFiles]

def updateUpgradedViews():
    #Creates a view of our army list that only accounts for selected upgrades
    session.army_list_upgraded = copy.deepcopy(session.army_list)
    for unit_key in session.army_list_upgraded["Units"]:
        if session.army_list_upgraded["Units"][unit_key]["combined"]:
            session.army_list_upgraded["Units"][unit_key]['models'] += session.army_list_upgraded["Units"][unit_key]['models']
        for upgrade in session.army_list_upgraded["Units"][unit_key]["upgrades"]:
            for choice in upgrade['choices']:
                if not choice['selected']:
                    continue
                if 'add_perks' in choice.keys():
                    session.army_list_upgraded["Units"][unit_key]["perks"].extend(choice["add_perks"])
                if 'add_weapons' in choice.keys():
                    session.army_list_upgraded["Units"][unit_key]['weapons'].extend(choice["add_weapons"])
                if 'remove_weapons' in choice.keys():
                    old_weapons = session.army_list_upgraded["Units"][unit_key]['weapons']
                    new_weapons = [weapon for weapon in old_weapons if weapon not in choice['remove_weapons']]
                    session.army_list_upgraded["Units"][unit_key]['weapons'] = new_weapons
        session.army_list_upgraded["Units"][unit_key]["upgrades"] = []



def switchTab():
    session.current_tab = int(request.vars.myvar)
    if session.current_tab == 5:
        #Get all available Army List Files if opening the "Load List from File" tab
        updateAvailableLists()
    if session.current_tab == 3 or session.current_tab == 4 or session.current_tab == 6:
        #Update our army list view if we're opening the edit/view army list tabs
        #(Reads the upgrades and displays the current state of upgraded units)
        updateUpgradedViews()
    return session.current_tab

def removeUnit():
    unit_key = request.vars.myvar
    del_unit = session.army_list['Units'].pop(unit_key, None)
    #If unit had an embedded hero; break connection
    if del_unit.get('embedded_by', None):
        embedded_hero_key = del_unit['embedded_by']
        if session.army_list['Units'].get(embedded_hero_key, None):
            session.army_list['Units'][embedded_hero_key]['embedded_in'] = None
    #If unit was an embedded hero; break connection
    if del_unit.get('embedded_in', None):
        embedded_unit_key = del_unit['embedded_in']
        if session.army_list['Units'].get(embedded_unit_key, None):
            session.army_list['Units'][embedded_unit_key]['embedded_by'] = None
    updateListCost()
    force_org_check()
    updateUpgradedViews()

def editUnit():
    session.current_tab = 6
    session.editUnit = copy.deepcopy(session.army_list["Units"][request.vars.myvar])
    session.editUnit['unit_key'] = request.vars.myvar
    if 'Hero' in session.editUnit['perks']:
        update_embeddable_unit_names()
    redirect(URL('index'))

def updateUnitCost(unit_key):
    unit = session.army_list['Units'][unit_key]
    unit['price'] = unit["base_points"]
    if unit['combined']:
        unit['price'] += unit['base_points']
    for upgrade in unit['upgrades']:
        for choice in upgrade['choices']:
            if choice['selected']:
                unit['price'] += choice['price']
                if unit['combined'] and upgrade['unit_level']:
                    #Double the price for combined units with unit-wide upgrades
                    unit['price'] += choice['price']

def updateListCost():
    session.army_list['Price'] = 0
    for unit_key in session.army_list["Units"]:
        updateUnitCost(unit_key)
        session.army_list['Price'] += session.army_list["Units"][unit_key]["price"]


def saveList():
    if not session.username:
        username = auth.user.email
        username = username.replace('.','_').replace('@','__')
        session.username = username
    armyListRepo = os.path.join(request.folder, 'private', 'ArmyLists')
    armyListRepo = os.path.join(armyListRepo, session.username)
    session.army_list['ArmyBook'] = session.army_book_json
    os.makedirs(armyListRepo, exist_ok=True)
    list_file_name = session.list_name.replace(' ','_') + '.json'
    list_file = os.path.join(armyListRepo, list_file_name)
    with open(list_file, "w") as file:
        json.dump(session.army_list, file, indent=2)

def update_unit_chooseone():
    unit = session.army_list['Units'][request.vars.unitKey]
    upgrade_section = {}
    for upgrade in unit['upgrades']:
        if upgrade['section'] in request.vars.upgradeSection:
            upgrade_section = upgrade
    if upgrade_section:
        for option in upgrade_section['choices']:
            if option['name'] == request.vars.optionName:
                option['selected'] = True
            else:
                option['selected'] = False
        #session.flash = str(upgrade_section['choices'])
    updateListCost()
    force_org_check()
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    redirect(URL('index'))

def update_unit_choosemult():
    unit = session.army_list['Units'][request.vars.unitKey]
    upgrade_section = {}
    for upgrade in unit['upgrades']:
        if upgrade['section'] in request.vars.upgradeSection:
            upgrade_section = upgrade
    if upgrade_section:
        for option in upgrade_section['choices']:
            if option['name'] == request.vars.optionName:
                if request.vars.Selected.strip().lower() == "true":
                    option['selected'] = True
                else:
                    option['selected'] = False
        #session.flash = str(upgrade_section['choices'])
    updateListCost()
    force_org_check()
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    redirect(URL('index'))

def update_embeddable_unit_names():
    '''
    Create a list of unique-ified unit names for our list, and
    a map tying each unique name to the unit's Key.
    Used
    '''
    unitNames = []
    unitLookup = {}
    units = session.army_list["Units"]
    for unit_key in units.keys():
        if units[unit_key]['models'] < 2:
            continue
        if units[unit_key].get('embedded_by', None):
            continue
        unitName = ''
        if units[unit_key]['name']:
            unitName = units[unit_key]['name']
        else:
            unitName = units[unit_key]['unit_type']
        if unitName not in unitNames:
            unitNames.append(unitName)
            unitLookup[unitName] = unit_key
            continue
        originalUnitName = unitName
        index = 1
        while True:
            index += 1
            unitName = originalUnitName + ' (' + str(index) + ')'
            if unitName not in unitNames:
                unitNames.append(unitName)
                unitLookup[unitName] = unit_key
                break
    #if any embeddable units; add a "None" option as well
    unitNames.append("None")
    session.embeddable_unit_names = unitNames
    session.embeddable_unitLookup = unitLookup

def combine_unit():
    '''
    Function called from Edit Unit tab. Either combines a unit(doubles models)
    or un-combines a unit that was previously combined
    '''
    unit = session.army_list['Units'][request.vars.unitKey]
    if request.vars.combine.lower().strip() == 'true':
        unit['combined'] = True
    else:
        unit['combined'] = False
    # Need to update our unit's cost, and then copy unit to active editting space
    updateListCost()
    force_org_check()
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey

def download_list():
    '''
    Download List as a file. Called from Configure List Tab
    '''
    content = json.dumps(session.army_list, indent=2)
    session.army_list_json = str(session.list_name).replace(' ','_') + '.json'
    # Set headers to force download
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = f'attachment; filename={session.army_list_json}'
    return content

def force_org_check():
    '''
    Check Army List against force org and update its status
    '''
    force_org_ok = True
    hero_count = get_hero_count()
    total_points = session.army_list['Price']
    maxHeroes = int(total_points/375)
    if hero_count > maxHeroes:
        force_org_ok = False
    total_points = session.army_list['Price']
    unit_count = len(session.army_list["Units"])
    max_units = int(total_points / 150)
    if unit_count > max_units:
        force_org_ok = False
    unit_counts = get_unit_type_count_map()
    max_unit_copies = 1 + int(total_points / 750)
    for unit in unit_counts:
        if unit_counts[unit] > max_unit_copies:
            force_org_ok = False
            break
    max_unit_cost = int(total_points * 0.35)
    unit_costs = get_unit_cost_list()
    for unit in unit_costs:
        if int(unit["price"]) > max_unit_cost:
            force_org_ok = False
            break
    session.forceOrgPass = force_org_ok

def force_org_message():
    '''
    Build and display force org message, describing status of list in terms of force-org
    '''
    hero_count = get_hero_count()
    total_points = session.army_list['Price']
    maxHeroes = int(total_points/375)
    unit_count = len(session.army_list["Units"])
    max_units = int(total_points / 150)
    unit_counts = get_unit_type_count_map()
    max_unit_copies = 1 + int(total_points / 750)
    unit_over_copies = []
    max_unit_cost = int(total_points * 0.35)
    unit_over_costs = []
    unit_costs = get_unit_cost_list()
    for unit in unit_counts:
        if unit_counts[unit] > max_unit_copies:
            unit_over_copies.append(unit)
    for unit in unit_costs:
        if int(unit["price"]) > max_unit_cost:
            unit_over_costs.append(unit)
    nextline = '                                                      '
    tabspace = '-    '
    message = ''
    message += f"Force Organization:{nextline}"
    message += f"* 1 unit per 150pts {nextline}"
    message += f"{tabspace}{unit_count}/{max_units} units {nextline}"
    message += f"* One Hero Per 375pts {nextline}"
    message += f"{tabspace}{hero_count}/{maxHeroes} heroes {nextline}"
    message += f"* One unit copy per 750pts {nextline}"
    if unit_over_copies:
        for unit in unit_over_copies:
            message += f"{tabspace}{unit}: {unit_counts[unit]}/{max_unit_copies} {nextline}"
    else:
        message += f"{tabspace}({max_unit_copies} copies) {nextline}"
    message += f"* No unit worth > 35% of pts {nextline}"
    if unit_over_costs:
        for unit in unit_over_costs:
            message += f'{tabspace}{unit["name"]}: {unit["price"]}/{max_unit_cost} {nextline}'
    else:
        message += f"{tabspace}({max_unit_cost}pts) {nextline}"
    response.flash = XML(message)

def get_hero_count():
    heroes = 0
    units = session.army_list["Units"]
    for unit_key in units.keys():
        if 'Hero' in units[unit_key]['perks']:
            heroes += 1
    return heroes

def get_copy_count():
    copies = {}
    units = session.army_list["Units"]
    for unit_key in units.keys():
        unit_type = units[unit_key]['unit_type']
        if unit_type in copies.keys():
            copies[unit_type] += 1
        else:
            copies[unit_type] = 0
    return copies

def get_unit_type_count_map():
    units = session.army_list["Units"]
    unit_type_count_map = {}
    for unit_key in units:
        unit = units[unit_key]
        unit_type = unit['unit_type']
        if unit_type in unit_type_count_map.keys():
            unit_type_count_map[unit_type] += 1
        else:
            unit_type_count_map[unit_type] = 1
    return unit_type_count_map

def get_unit_cost_list():
    units = session.army_list["Units"]
    unit_cost_list = []
    for unit_key in units:
        unit = units[unit_key]
        unit_cost = {}
        if unit.get('embedded_in'):
            continue
        unit_cost["name"] = unit.get('name')
        if not unit_cost['name']:
            unit_cost['name'] = unit.get('unit_type', "UNKNOWN")
        unit_cost["price"] = unit['price']
        embedded_hero_key = unit.get('embedded_by')
        if embedded_hero_key:
            hero = units.get(embedded_hero_key)
            if hero:
                unit_cost["price"] += int(hero['price'])
        unit_cost_list.append(unit_cost)
    return unit_cost_list



def reorder_units():
    sortedUnits = {}
    unsortedUnits = session.army_list['Units']
    #Pull in heros and their embedded units first
    for unit_key in unsortedUnits.keys():
        if unsortedUnits[unit_key].get('embedded_in'):
            sortedUnits[unit_key] = unsortedUnits[unit_key]
            embeddedUnitKey = unsortedUnits[unit_key].get('embedded_in')
            sortedUnits[embeddedUnitKey] = unsortedUnits[embeddedUnitKey]
    #Now pull in everything else
    for unit_key in unsortedUnits.keys():
        if not unit_key in sortedUnits.keys():
            sortedUnits[unit_key] = unsortedUnits[unit_key]
    session.army_list['Units'] = sortedUnits
