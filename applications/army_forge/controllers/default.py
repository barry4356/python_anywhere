# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
import os
import json
import uuid
import copy
from CafConstants import NEW_CAF_UNIT
from CafPointMath import CalculateUnitCost

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
    elif request.vars.request_id == 'updateUnit':
        unit = session.army_list['Units'][request.vars.unitKey]
        upgrade_section = {}
        for upgrade in unit['upgrades']:
            if upgrade['section'] in request.vars.upgradeSection:
                upgrade_section = upgrade
        if upgrade_section:
            for option in upgrade_section['choices']:
                if request.vars[upgrade_section['section']] and option['name'] in request.vars[upgrade_section['section']]:
                    option['selected'] = True
                else:
                    option['selected'] = False
            #session.flash = str(upgrade_section['choices'])
        updateListCost()
        session.editUnit = copy.deepcopy(unit)
        session.editUnit['unit_key'] = request.vars.unitKey
        redirect(URL('index'))
    elif request.vars.request_id == 'updateUnitName':
        unit = session.army_list["Units"][request.vars.unitKey]
        unit["name"] = request.vars.unitName
        session.editUnit = copy.deepcopy(unit)
        session.editUnit['unit_key'] = request.vars.unitKey
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
        for upgrade in session.army_list_upgraded["Units"][unit_key]["upgrades"]:
            for choice in upgrade['choices']:
                if not choice['selected']:
                    continue
                if upgrade['type'] == "CHOOSE_MULTIPLE":
                    session.army_list_upgraded["Units"][unit_key]["perks"].append(choice["name"])
                if upgrade['type'] == "CHOOSE_ONE_WEAPON_REPLACE":
                    session.army_list_upgraded["Units"][unit_key]['weapons'][upgrade['weapon_index']] = choice['name']
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
    del_unit = session.army_list_upgraded["Units"].pop(unit_key, None)
    updateListCost()
    redirect(URL('index'))

def editUnit():
    session.current_tab = 6
    session.editUnit = copy.deepcopy(session.army_list["Units"][request.vars.myvar])
    session.editUnit['unit_key'] = request.vars.myvar
    redirect(URL('index'))

def updateUnitCost(unit_key):
    unit = session.army_list['Units'][unit_key]
    unit['price'] = unit["base_points"]
    for upgrade in unit['upgrades']:
        for choice in upgrade['choices']:
            if choice['selected']:
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

def download_list():
    content = json.dumps(session.army_list, indent=2)
    session.army_list_json = str(session.list_name).replace(' ','_') + '.json'
    # Set headers to force download
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = f'attachment; filename={session.army_list_json}'
    return content
