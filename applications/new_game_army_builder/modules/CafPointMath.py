def CalculateUnitCost(CafUnit):
    base_cost = _calculateBaseCost(CafUnit)
    model_perk_cost = _calculateModelPerkCost(CafUnit, base_cost)
    weapons_cost = _calculateLoadoutCost(CafUnit)
    return 0

def _calculateBaseCost(CafUnit):
    #Price of model Def/Qual x number of models
    qua_pts = 11 - (CafUnit["Qual"]) #Convert Qual to a simple scalar
    qua_pts = qua_pts / 10 # And then adjust it based on dice %
    def_pts = 11 - (CafUnit["Def"])  #Convert Def to a simple scalar
    def_pts = def_pts / 10 # And then adjust it based on dice %
    pricePerModel = 0
    #OPR Uses linear scaling for cost until >66.6(repeating, of course)%, and then switches to exponential scaling
    #Defense is weighter higher than Quality. Cost was found for every combination, and the equations reverse engineered.
    #Linear scale derived from OPR Armies (https://www.graphpad.com/quickcalcs/linear1/)
    if def_pts <= .666:
        pricePerModel += (7.38 * def_pts) 
    if qua_pts <= .666:
        pricePerModel += (3.72 * qua_pts)
    #Quadratic formula derived from OPR Armies (https://www.omnicalculator.com/statistics/quadratic-regression)
    if def_pts > .666:
        pricePerModel += ((7.38 - (18.45*def_pts) + (22.14*def_pts*def_pts))) 
    if qua_pts > .666:
        pricePerModel += ((3.72 - (9.3*qua_pts) + (11.16*qua_pts*qua_pts))) 
    return int(pricePerModel * CafUnit["ModelCount"])



def _calculateModelPerksCost(CafUnit, base_cost):
    #Price of Perks associated with the models
    return 0

def _calculateLoadoutCost(CafUnit):
    #Price of all weapons in unit
    loadoutCost = 0
    #for weapon in CafUnit['weapons']:
    #    loadoutCost += __caclulateWeaponCost(CafWeapon)
    return loadoutCost

def __caclulateWeaponCost(CafWeapon):
    #Price of a single weapon for a single model in unit
    return 0
