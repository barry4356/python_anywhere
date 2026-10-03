# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
import os
import json
import uuid
import copy


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
        session.list_name = None
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
        unit_key = session.embeddable_unitLookup[request.vars.embedSelection]
        unit = session.army_list["Units"][unit_key]
        #if hero was previously embedded, break the connection first
        if hero.get('embedded_in', None):
            previous_unitkey = hero['embedded_in']
            previous_unit = session.army_list['Units'][previous_unitkey]
            previous_unit['embedded_by'] = None
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
    pass

def force_org_message():
    '''
    Build and display force org message, describing status of list in terms of force-org
    '''
    pass

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
