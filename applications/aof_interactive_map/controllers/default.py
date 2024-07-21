# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
import random
from simulator import simulate_damage

townStats={
        'jamesonTown': 
            {
                'Owner': 'Marnier',
                'Tier': 3,
                'Bonus': 'Tournament Grounds'
            }
        }

# ---- example index page ----
def index():
    # Initialize input vars
    myshowZones = False
    myshowBattles = False
    if request.vars.showZones:
        myshowZones = True
    if request.vars.showBattles:
        myshowBattles = True
    myTownPrints = getStats(townStats)
    return dict(showZones=myshowZones, townPrints=myTownPrints, showBattles=myshowBattles)

def getStats(myStats):
    townPrints = {}
    for townname in townStats.keys():
        printlines = ''
        for statline in townStats[townname].keys():
            printlines += str(statline) + ': ' + str(townStats[townname][statline]) + '\n'
        townPrints[townname] = printlines
    return townPrints

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

