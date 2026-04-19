def CalculateUnitCost(OprUnit):
    base_cost = _calculateBaseCost(OprUnit)
    model_perk_cost = _calculateModelPerkCost(OprUnit, base_cost)
    weapons_cost = _calculateLoadoutCost(OprUnit)
    return base_cost + weapons_cost

def _calculateBaseCost(OprUnit):
    #Price of model Def/Qual x number of models
    qua_pts = 7 - (OprUnit["Qual"]) #Convert Qual to a simple scalar
    qua_pts = qua_pts / 6 # And then adjust it based on dice %
    def_pts = 7 - (OprUnit["Def"])  #Convert Def to a simple scalar
    def_pts = def_pts / 6 # And then adjust it based on dice %
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
    return int(pricePerModel * OprUnit["ModelCount"])

def _calculateModelPerksCost(OprUnit, base_cost):
    #Price of Perks associated with the models
    return 0

def _calculateLoadoutCost(OprUnit):
    #Price of all weapons in unit
    loadoutCost = 0
    for weapon in OprUnit['Weapons']:
        loadoutCost += (__caclulateWeaponCost(weapon) * OprUnit["ModelCount"])
    return loadoutCost

def __caclulateWeaponCost(OprWeapon, quality):
    qua_pts = 7 - quality #Convert Qual to a simple scalar
    qua_pts = qua_pts / 6 # And then adjust it based on dice %
    #OPR Uses linear scaling for cost until >66.6(repeating, of course)%, and then switches to exponential scaling
    if qua_pts <= .666:
        price_per_attack = qua_pts * 7.8 #Derived from OPR Army Stats/Cost
    else:
        #Quadratic formula derived from OPR Armies (https://www.omnicalculator.com/statistics/quadratic-regression)
        price_per_attack = 7.8-(19.5 * qua_pts)+(23.4*qua_pts*qua_pts)
        price_per_attack_base = price_per_attack
    rending = False
    if 'Rending' in OprWeapon.keys() and OprWeapon['Rending']:
        rending = True
    if 'AP' in OprWeapon.keys():
        #AP math is.... weird. Simplified by breaking into the 4 possible values
        try:
            ap_val = int(OprWeapon["AP"])
            if ap_val == 1:
                price_per_attack *= 1.5
            elif ap_val == 2:
                price_per_attack *= 2
            elif ap_val == 3:
                price_per_attack *= 2.4
            elif ap_val == 4:
                price_per_attack *= 2.7
            elif rending:
                pass
        except:
            pass

    #Price of a single weapon for a single model in unit
    weapon_price = price_per_attack * OprWeapon["Attacks"]
    return weapon_price
