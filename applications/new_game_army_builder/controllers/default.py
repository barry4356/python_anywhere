# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
import os
import json
# ---- example index page ----
armyData = []
def index():
    dataFilePath = os.path.join(request.folder, 'private', 'AllArmyData.json')
    with open(dataFilePath, 'r') as dataFile:
        armyData = json.load(dataFile)
    return dict(loaded=True)
