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
    def_pts = def_pts / 10 # And then adjust it based on dice % (allows us to match 1:1 with OPR math)
    combined_pts = (qua_pts+def_pts)/2 # Combined Defense and Quality to make math easier
    #OPR Uses linear scaling for cost until >66.6(repeating, of course)%, and then switches to exponential scaling
    if combined_pts <= .666:
        pricePerModel = (11.1 * combined_pts) #Linear scale derived from OPR Armies (https://www.graphpad.com/quickcalcs/linear1/)
    else:
        pricePerModel = ((11.1 - (27.75*combined_pts) + (33.3*combined_pts*combined_pts))) #Quadratic formula derived from OPR Armies (https://www.omnicalculator.com/statistics/quadratic-regression)
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
