# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
import random

# ---- example index page ----
def index():
    # Initialize input vars
    roll_count = 30000
    myoddslist = []
    myselections = []
    mydisplayodds = 0
    calculated_chances = 0
    stats = {
        'quality': 0,
        'attacks': 0,
        'armorPiercing': 0,
        'poison': False,
        'rending': False,
        'furious': False,
        'furiouser': False,
        'defense': 0,
        'defenseBonus': 0,
        'regen': False
    }
    # Get input vars from form
    if request.vars.quality and request.vars.attacks and request.vars.defense:
        stats["quality"] = sanitize_int(request.vars.quality)
        stats["attacks"] = sanitize_int(request.vars.attacks)
        stats["defense"] = sanitize_int(request.vars.defense)
        stats["defenseBonus"] = sanitize_int(request.vars.defenseBonus)
        stats["armorPiercing"] = sanitize_int(request.vars.armorPiercing)
        if request.vars.furiouser:
            stats["furiouser"] = True
        elif request.vars.furious:
            stats["furious"] = True
        if request.vars.poison:
            stats["poison"] = True
        if request.vars.rending:
            stats["rending"] = True
        if request.vars.regen:
            stats["regen"] = True

        # Run the simulation and calculate odds
        damage = simulate_damage(stats, roll_count)
        myoddslist = calculate_odds(damage, roll_count)
        mydisplayodds = 1
    return dict(displayodds=mydisplayodds, oddslist=myoddslist)


# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

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

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def roll_1d6():
    return (random.randrange(6) + 1)

def sanitize_int(myinput):
    val = 0
    try:
        val = int(myinput)
    except:
        val = 0
    return val

def simulate_damage(stats, count):
    results = []
    # Run one simulation for each 'count'
    for j in range(count):
        damage = 0
        # Roll each attack, and immediately roll defense
        for i in range(stats["attacks"]):
            dieroll_a = roll_1d6()
            damage += handle_furious(dieroll_a, stats)
            applied_ap = stats["armorPiercing"]
            # If 'rending'; 6 results in extra AP
            if stats["rending"] and dieroll_a == 6:
                applied_ap = 4
            # Check if the initial attack roll meets the quality value
            if dieroll_a >= stats["quality"]:
                dieroll_d = roll_1d6()
                # If 'poison'; re-roll on a defense roll of 6
                if stats["poison"] and dieroll_d == 6:
                    dieroll_d = roll_1d6()
                # Defense rolls of 1 always fail
                if dieroll_d <= 1:
                    damage += defender_takes_damage(stats)
                # Defense rolls of 6 always succeed
                elif dieroll_d < 6:
                    # Apply any AP or defense bonus
                    if dieroll_d < (stats["defense"] + applied_ap - stats['defenseBonus']):
                        damage += defender_takes_damage(stats)
        results.append(damage)
    return results

# Handle Furiousness
def handle_furious(dieroll_a, stats):
    damage = 0
    # If 'furiouser'; 5 & 6 result in an extra hit w/o AP
    if stats["furiouser"] and dieroll_a >= 5:
        dieroll_d = roll_1d6()
        if dieroll_d <= 1:
            damage += defender_takes_damage(stats["regen"])
        elif dieroll_d < 6:
            if dieroll_d < (stats["defense"] - stats['defenseBonus']):
                damage += defender_takes_damage(stats["regen"])
    # If 'furious'; 6 results in an extra hit w/o AP
    elif stats["furious"] and dieroll_a == 6:
        dieroll_d = roll_1d6()
        if dieroll_d <= 1:
            damage += defender_takes_damage(stats["regen"])
        elif dieroll_d < 6:
            if dieroll_d < (stats["defense"] - stats['defenseBonus']):
                damage += defender_takes_damage(stats["regen"])
    return damage

# Handle regen check
def defender_takes_damage(stats):
    damage = 1
    if stats["regen"]:
        dieroll_d = roll_1d6()
        if dieroll_d >= 5:
            damage = 0
    return damage

# Take all results and calculate odds of each
def calculate_odds(results, count):
    odds = [0] * (max(results)+1)
    for value in results:
        odds[value] = odds[value] + 1
    for index, value in enumerate(odds):
        odds[index] = (value/count) * 100
        if odds[index] < 1:
            odds[index] = round(odds[index],1)
        else:
            odds[index] = round(odds[index])
    return odds

