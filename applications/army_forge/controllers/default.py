# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
import os
import json
import uuid
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
        session.army_list = {"Units": {}, "ArmyBook": session.army_book_json}
        session.list_name = None
        redirect(URL('index'))
    if request.vars.request_id == 'AddUnitToList':
        unit_uuid = str(uuid.uuid4())
        new_unit = session.army_book['Units'][request.vars.unitName]
        new_unit['unit_type'] = request.vars.unitName
        new_unit['name'] = ''
        session.army_list["Units"][unit_uuid] = new_unit
        redirect(URL('index'))
    if request.vars.request_id == 'updateListName':
        session.list_name = request.vars.listName
        redirect(URL('index'))
    if request.vars.request_id == 'loadArmyList':
        session.list_name = request.vars.armyFileSelection
        session.army_list_json = request.vars.armyFileSelection.replace(' ','_') + '.json'
        with open(os.path.join(request.folder, 'private', 'ArmyLists', session.username, session.army_list_json), 'r') as file:
            session.army_list = json.load(file)
        session.army_book_json = session.army_list['ArmyBook']
        session.army_book_name = session.army_book_json.replace('_',' ').replace('.json','')
        with open(os.path.join(request.folder, 'private', 'ArmyBooks', session.army_book_json), 'r') as file:
            session.army_book = json.load(file)
        session.current_tab = 1
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



def switchTab():
    session.current_tab = int(request.vars.myvar)
    if session.current_tab == 5:
        #Get all available Army List Files
        updateAvailableLists()
    return session.current_tab

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
