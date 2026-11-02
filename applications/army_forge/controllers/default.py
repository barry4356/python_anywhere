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
    # ======== Initializations ========
    #session.army_book = ''
    #session.clear()
    #session.new_unit = {'weapons': []}
    #response.flash = ""
    if not session.unit_count:
        session.unit_count = 0
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

    #======== Form Submissions ========
    if request.vars.request_id == 'selectArmyBook':
        session.army_book_name = request.vars.bookSelection
        session.army_book_json = request.vars.bookSelection.replace(' ','_') + '.json'
        with open(os.path.join(request.folder, 'private', 'ArmyBooks', session.army_book_json), 'r') as file:
            session.army_book = json.load(file)
        session.army_list = {"Units": {}, "ArmyBook": session.army_book_json, "Price": 0, "campaign_filter": False}
        session.list_name = "None"
        session.unit_count = get_unit_count(session.army_list.get('Units',[]))
        session.forceOrgPass=True
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
        campaign_skills = session.army_book.get('CampaignSkills',[])
        unit_campaign_traits = {}
        for trait in campaign_skills['Traits']:
            unit_campaign_traits[trait] = False
        new_unit['campaign_xp'] = 0
        new_unit['campaign_traits'] = unit_campaign_traits
        if 'Hero' in new_unit['perks']:
            campaign_skillsets = {}
            unit_campaign_injuries = {}
            unit_campaign_talents = {}
            for skillset in campaign_skills['SkillSets']:
                campaign_skillset = {}
                for skill in campaign_skills['SkillSets'][skillset]:
                    campaign_skillset[skill] = False
                campaign_skillsets[skillset] = campaign_skillset
            new_unit['campaign_skillsets'] = campaign_skillsets
            for injury in campaign_skills['Injuries']:
                unit_campaign_injuries[injury] = False
            new_unit['campaign_injuries'] = unit_campaign_injuries
            for talent in campaign_skills['Talents']:
                unit_campaign_talents[talent] = False
            new_unit['campaign_talents'] = unit_campaign_talents
        session.army_list["Units"][unit_uuid] = new_unit
        updateListCost()
        session.unit_count = get_unit_count(session.army_list.get('Units',[]))
        session.forceOrgPass = force_org_check(session.army_list)
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
        session.unit_count = get_unit_count(session.army_list.get('Units',[]))
        session.forceOrgPass = force_org_check(session.army_list)
        redirect(URL('index'))
    elif request.vars.request_id == 'updateUnitName':
        unit = session.army_list["Units"][request.vars.unitKey]
        unit["name"] = request.vars.unitName
        session.editUnit = copy.deepcopy(unit)
        session.editUnit['unit_key'] = request.vars.unitKey
        session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')
        redirect(URL('index'))
    elif request.vars.request_id == 'uploadListFile':
        uploaded_file = request.vars.textFile.file
        filename = request.vars.textFile.filename
        session.army_list = json.load(uploaded_file)
        session.army_book_json = session.army_list['ArmyBook']
        session.army_book_name = session.army_book_json.replace('_', ' ').replace('.json','')
        with open(os.path.join(request.folder, 'private', 'ArmyBooks', session.army_book_json), 'r') as file:
            session.army_book = json.load(file)
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
        session.army_list['Units'] = reorder_units(session.army_list['Units'])
        session.unit_count = get_unit_count(session.army_list.get('Units',[]))
        session.editUnit = copy.deepcopy(hero)
        session.editUnit['unit_key'] = request.vars.heroKey
        session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')
        redirect(URL('index'))

    return dict()

# ======== APIs ========

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
                if 'remove_perks' in choice.keys():
                    for perk in choice['remove_perks']:
                        session.army_list_upgraded["Units"][unit_key]["perks"].remove(perk)
                if 'add_weapons' in choice.keys():
                    session.army_list_upgraded["Units"][unit_key]['weapons'].extend(choice["add_weapons"])
                if 'remove_weapons' in choice.keys():
                    old_weapons = session.army_list_upgraded["Units"][unit_key]['weapons']
                    new_weapons = [weapon for weapon in old_weapons if weapon not in choice['remove_weapons']]
                    session.army_list_upgraded["Units"][unit_key]['weapons'] = new_weapons
                if 'add_tough' in choice.keys():
                    tough = session.army_list_upgraded["Units"][unit_key].get('tough',0)
                    tough += int(choice['add_tough'])
                    session.army_list_upgraded["Units"][unit_key]['tough'] = tough
        if session.army_list.get('campaign_filter'):
            for trait in session.army_list_upgraded["Units"][unit_key].get("campaign_traits", []):
                if session.army_list_upgraded["Units"][unit_key]["campaign_traits"][trait]:
                    session.army_list_upgraded["Units"][unit_key]["perks"].append(trait)
            for talent in session.army_list_upgraded["Units"][unit_key].get("campaign_talents", []):
                if session.army_list_upgraded["Units"][unit_key]["campaign_talents"][talent]:
                    session.army_list_upgraded["Units"][unit_key]["perks"].append(talent)
            for injury in session.army_list_upgraded["Units"][unit_key].get("campaign_injuries", []):
                if session.army_list_upgraded["Units"][unit_key]["campaign_injuries"][injury]:
                    session.army_list_upgraded["Units"][unit_key]["perks"].append(injury)
            for skillset in session.army_list_upgraded["Units"][unit_key].get("campaign_skillsets", []):
                for subskill in session.army_list_upgraded["Units"][unit_key]['campaign_skillsets'][skillset]:
                    if session.army_list_upgraded["Units"][unit_key]['campaign_skillsets'][skillset][subskill]:
                        session.army_list_upgraded["Units"][unit_key]["perks"].append(subskill)
        session.army_list_upgraded["Units"][unit_key]["upgrades"] = []

def update_unit_xp():
    #response.flash = request.vars.unitKey
    session.army_list['Units'][request.vars.unitKey]['campaign_xp'] = request.vars.xp

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

def enable_campaign_trait():
    unit = session.army_list['Units'][request.vars.unitKey]
    trait = request.vars.trait
    unit['campaign_traits'][trait] = True
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

def disable_campaign_trait():
    unit = session.army_list['Units'][request.vars.unitKey]
    trait = request.vars.trait
    unit['campaign_traits'][trait] = False
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

def enable_campaign_skill():
    unit = session.army_list['Units'][request.vars.unitKey]
    skill = request.vars.skill
    for skillset in unit.get('campaign_skillsets', []):
        for subskill in unit['campaign_skillsets'][skillset]:
            if subskill == skill:
                unit['campaign_skillsets'][skillset][skill] = True
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

def disable_campaign_skill():
    unit = session.army_list['Units'][request.vars.unitKey]
    skill = request.vars.skill
    for skillset in unit.get('campaign_skillsets', []):
        for subskill in unit['campaign_skillsets'][skillset]:
            if subskill == skill:
                unit['campaign_skillsets'][skillset][skill] = False
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

def enable_campaign_injury():
    unit = session.army_list['Units'][request.vars.unitKey]
    injury = request.vars.injury
    unit['campaign_injuries'][injury] = True
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

def disable_campaign_injury():
    unit = session.army_list['Units'][request.vars.unitKey]
    injury = request.vars.injury
    unit['campaign_injuries'][injury] = False
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

def enable_campaign_injury():
    unit = session.army_list['Units'][request.vars.unitKey]
    injury = request.vars.injury
    unit['campaign_injuries'][injury] = True
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

def disable_campaign_injury():
    unit = session.army_list['Units'][request.vars.unitKey]
    injury = request.vars.injury
    unit['campaign_injuries'][injury] = False
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

def enable_campaign_talent():
    unit = session.army_list['Units'][request.vars.unitKey]
    talent = request.vars.talent
    unit['campaign_talents'][talent] = True
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

def disable_campaign_talent():
    unit = session.army_list['Units'][request.vars.unitKey]
    talent = request.vars.talent
    unit['campaign_talents'][talent] = False
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

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
    session.unit_count = get_unit_count(session.army_list.get('Units',[]))
    session.forceOrgPass = force_org_check(session.army_list)
    updateUpgradedViews()

def editUnit():
    session.current_tab = 6
    session.editUnit = copy.deepcopy(session.army_list["Units"][request.vars.myvar])
    session.editUnit['unit_key'] = request.vars.myvar
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')
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
    session.forceOrgPass = force_org_check(session.army_list)
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')
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
    session.forceOrgPass = force_org_check(session.army_list)
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')
    redirect(URL('index'))

def enable_campaign_filter():
    session.army_list['campaign_filter'] = True

def disable_campaign_filter():
    session.army_list['campaign_filter'] = False

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
    session.forceOrgPass = force_org_check(session.army_list)
    session.unit_count = get_unit_count(session.army_list.get('Units',[]))
    session.editUnit = copy.deepcopy(unit)
    session.editUnit['unit_key'] = request.vars.unitKey
    session.editUnit['campaign_filter'] = session.army_list.get('campaign_filter')

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

def force_org_message_api():
    response.flash = XML(build_force_org_message(session.army_list))

def display_keywords_api():
    response.flash = build_keyword_popup(request.vars.myvar.lower(), session.army_book['Keywords'])

# ======== Modules ========

'''
Order units in the list so that embedded heroes and their units are together,
and at the top of the list
'''
def reorder_units(unsortedUnits):
    sortedUnits = {}
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
    return sortedUnits

'''
Takes a full string and a keywords dictionary. Returns a string built for the popup
'''
def build_keyword_popup(fullString, keywords):
    response_message = ''
    nextline = '                                                      '
    separator = '--------'
    for keyword in keywords.keys():
        keyword_stripped = keyword.replace('X)','')
        if keyword_stripped.lower() in fullString:
            response_message += f"{keyword}: {keywords[keyword]} {nextline}{separator}{nextline}"
    return XML(response_message)

'''
Get a count of units in this army list (embedded models don't count)
'''
def get_unit_count(units):
    unit_count = 0
    for unit_key in units:
        if units[unit_key].get('embedded_in',False):
            continue
        unit_count += 1
    return unit_count

'''
Get price of full units (including embedded heroes), paired with unit names.
Meant to be displayed (force org), so names instead of keys
'''
def get_unit_cost_list(units):
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

'''
Get map of each type of unit and its current count in the
army list (used for force org)
'''
def get_unit_type_count_map(units):
    unit_type_count_map = {}
    for unit_key in units:
        unit = units[unit_key]
        unit_type = unit['unit_type']
        if unit_type in unit_type_count_map.keys():
            unit_type_count_map[unit_type] += 1
        else:
            unit_type_count_map[unit_type] = 1
    return unit_type_count_map

'''
Returns number of heroes in army list (used for force org)
'''
def get_hero_count(units):
    heroes = 0
    for unit_key in units.keys():
        if 'Hero' in units[unit_key]['perks']:
            heroes += 1
    return heroes

'''
Check Army List against force org and return pass/fail status
'''
def force_org_check(army_list):
    force_org_ok = True
    hero_count = get_hero_count(army_list["Units"])
    total_points = army_list['Price']
    maxHeroes = int(total_points/375)
    if hero_count > maxHeroes:
        force_org_ok = False
    total_points = army_list['Price']
    max_units = int(total_points / 150)
    if get_unit_count(army_list["Units"]) > max_units:
        force_org_ok = False
    unit_counts = get_unit_type_count_map(army_list["Units"])
    max_unit_copies = 1 + int(total_points / 750)
    for unit in unit_counts:
        if unit_counts[unit] > max_unit_copies:
            force_org_ok = False
            break
    max_unit_cost = int(total_points * 0.35)
    unit_costs = get_unit_cost_list(army_list["Units"])
    for unit in unit_costs:
        if int(unit["price"]) > max_unit_cost:
            force_org_ok = False
            break
    return force_org_ok

'''
Build Force Org message
'''
def build_force_org_message(army_list):
    '''
    Build and display force org message, describing status of list in terms of force-org
    '''
    hero_count = get_hero_count(army_list["Units"])
    total_points = session.army_list['Price']
    maxHeroes = int(total_points/375)
    max_units = int(total_points / 150)
    unit_counts = get_unit_type_count_map(army_list["Units"])
    max_unit_copies = 1 + int(total_points / 750)
    unit_over_copies = []
    max_unit_cost = int(total_points * 0.35)
    unit_over_costs = []
    unit_costs = get_unit_cost_list(army_list["Units"])
    for unit in unit_counts:
        if unit_counts[unit] > max_unit_copies:
            unit_over_copies.append(unit)
    for unit in unit_costs:
        if int(unit["price"]) > max_unit_cost:
            unit_over_costs.append(unit)
    nextline = '                                                      '
    tabspace = '-    '
    message = ''
    unitCount = get_unit_count(army_list.get('Units',[]))
    message += f"Force Organization:{nextline}"
    message += f"* One unit per 150pts {nextline}"
    message += f"{tabspace}{unitCount}/{max_units} units {nextline}"
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
    return XML(message)

