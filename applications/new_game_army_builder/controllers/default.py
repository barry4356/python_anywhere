# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
import os
import json
# ---- example index page ----
armyData = []
armyDataFiltered = []
QualityOptions = [2,3,4,5,6,7,8,9,10]
DefenseOptions = [2,3,4,5,6,7,8,9,10]

def index():
    dataFilePath = os.path.join(request.folder, 'private', 'AllArmyData.json')
    with open(dataFilePath, 'r') as dataFile:
        armyData = json.load(dataFile)
        armyDataFiltered = armyData.copy()
    return dict(loaded=True, myQualityOptions=QualityOptions, myDefenseOptions=DefenseOptions)


def select_handler():
    # Get the selected value from request.vars
    #selected_value = request.vars.value
    # Perform backend logic
    #result = "You selected: " + selected_value
    DefenseOptions = [3,4]
    return request.vars.qual # Or return a component/json












