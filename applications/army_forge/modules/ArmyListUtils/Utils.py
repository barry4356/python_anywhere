import copy
import uuid

'''
Calculate the actual cost of a unit (including selected upgrades)
'''
def calculate_unit_price(unit):
    total_price = unit["base_points"]
    if unit['combined']:
        total_price += unit['base_points']
    for upgrade in unit['upgrades']:
        for choice in upgrade['choices']:
            if choice['selected']:
                total_price += choice['price']
                if unit['combined'] and upgrade['unit_level']:
                    #Double the price for combined units with unit-wide upgrades
                    total_price += choice['price']
    return total_price

'''
Add an empty/fresh unit to an army list 
(optinally add name/uuid if this unit is based off an existing unit eg. unit list migration)
'''
def add_unit_to_list(armyList, armyBook, unittype, unitname='', unit_uuid=None):
    if not unit_uuid:
        unit_uuid = str(uuid.uuid4())
    new_unit = copy.deepcopy(armyBook['Units'][unittype])
    new_unit['unit_type'] = unittype
    new_unit['name'] = unitname
    new_unit['price'] = armyBook['Units'][unittype]["base_points"]
    new_unit['combined'] = False
    for upgrade in new_unit['upgrades']:
        for choice in upgrade['choices']:
            choice['selected'] = False
    campaign_skills = armyBook.get('CampaignSkills',[])
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
    armyList["Units"][unit_uuid] = new_unit
    armyList['Price'] += new_unit['price']
    return armyList