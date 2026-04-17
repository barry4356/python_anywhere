def CalculateUnitCost(OprUnit):
    base_cost = _calculateBaseCost(OprUnit)
    model_perk_cost = _calculateModelPerkCost(OprUnit, base_cost)
    weapons_cost = _calculateLoadoutCost(OprUnit)
    return 0

def _calculateBaseCost(OprUnit):
    #Price of model Def/Qual x number of models
    qua_pts = 7 - (OprUnit["Qual"]) #Convert Qual to a simple scalar
    qua_pts = qua_pts / 6 # And then adjust it based on dice %
    def_pts = 7 - (OprUnit["Def"])  #Convert Def to a simple scalar
    def_pts = def_pts / 6 # And then adjust it based on dice %
    combined_pts = (qua_pts+def_pts)/2 # Combined Defense and Quality to make math easier
    #OPR Uses linear scaling for cost until >66.6(repeating, of course)%, and then switches to exponential scaling
    if combined_pts <= .666:
        pricePerModel = (11.1 * combined_pts) #Linear scale derived from OPR Armies (https://www.graphpad.com/quickcalcs/linear1/)
    else:
        pricePerModel = ((11.1 - (27.75*combined_pts) + (33.3*combined_pts*combined_pts))) #Quadratic formula derived from OPR Armies (https://www.omnicalculator.com/statistics/quadratic-regression)
    return int(pricePerModel * OprUnit["ModelCount"])

    
    

def _calculateModelPerksCost(OprUnit, base_cost):
    #Price of Perks associated with the models
    return 0

def _calculateLoadoutCost(OprUnit):
    #Price of all weapons in unit
    loadoutCost = 0
    #for weapon in OprUnit['weapons']:
    #    loadoutCost += __caclulateWeaponCost(OprWeapon)
    return loadoutCost

def __caclulateWeaponCost(OprWeapon):
    #Price of a single weapon for a single model in unit
    return 0
