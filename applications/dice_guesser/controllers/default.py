# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
import random

# ---- example index page ----
def index():
    roll_count = 30000
    myoddslist = []
    myselections = []
    mydisplayodds = 0
    calculated_chances = 0

    if request.vars.d4 or request.vars.d6 or request.vars.d8 or request.vars.d10 or request.vars.d12 or request.vars.d20:
        d4 = sanitize_int(request.vars.d4)
        d6 = sanitize_int(request.vars.d6)
        d8 = sanitize_int(request.vars.d8)
        d10 = sanitize_int(request.vars.d10)
        d12 = sanitize_int(request.vars.d12)
        d20 = sanitize_int(request.vars.d20)
        bonus = sanitize_int(request.vars.bonus)
        goal = sanitize_int(request.vars.goal)
        myselections = [d4,d6,d8,d10,d12,d20,bonus,goal]
        #myoddslist = (d4, d6, d8, d10, d12, d20, bonus)
        rolls = simulate_rolls(d4, d6, d8, d10, d12, d20, bonus, roll_count)
        myoddslist = calculate_odds(rolls, roll_count)
        calculated_chances = calculate_chances(myoddslist, goal)
        mydisplayodds = 1
    return dict(selection_list=myselections, displayodds=mydisplayodds, oddslist=myoddslist, mychances=calculated_chances)

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

def roll_1d4():
    return (random.randrange(4) + 1)

def roll_1d6():
    return (random.randrange(6) + 1)

def roll_1d8():
    return (random.randrange(8) + 1)

def roll_1d10():
    return (random.randrange(10) + 1)

def roll_1d12():
    return (random.randrange(12) + 1)

def roll_1d20():
    return (random.randrange(20) + 1)

def simulate_rolls(d4, d6, d8, d10, d12, d20, bonus, count):
    results = []

    for j in range(count):
        total = 0
        for i in range(d4):
            total = total + (roll_1d4())
        for i in range(d6):
            total = total + (roll_1d6())
        for i in range(d8):
            total = total + (roll_1d8())
        for i in range(d10):
            total = total + (roll_1d10())
        for i in range(d12):
            total = total + (roll_1d12())
        for i in range(d20):
            total = total + (roll_1d20())
        total = total + bonus
        results.append(total)

    return(results)

def sanitize_int(myinput):
    val = 0
    try:
        val = int(myinput)
    except:
        val = 0
    return val

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

def calculate_chances(odds, goal):
    val = 0
    if goal > len(odds):
        return 0
    for i in range(goal, len(odds)):
        val = val + odds[i]
    if val > 100:
        val = 100
    return round(val)
