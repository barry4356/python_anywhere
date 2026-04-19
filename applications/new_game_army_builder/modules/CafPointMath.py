def CalculateUnitCost(CafUnit):
    base_cost = _calculateBaseCost(CafUnit)
    model_perk_cost = _calculateModelPerksCost(CafUnit, base_cost)
    weapons_cost = _calculateLoadoutCost(CafUnit)
    return base_cost + model_perk_cost + weapons_cost

def _calculateBaseCost(CafUnit):
    #Price of model Def/Qual x number of models
    qua_pts = 11 - (CafUnit["Quality"]) #Convert Qual to a simple scalar
    qua_pts = qua_pts / 10 # And then adjust it based on dice %
    def_pts = 11 - (CafUnit["Defense"])  #Convert Def to a simple scalar
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
    return int(pricePerModel * CafUnit["Model Qty"])



def _calculateModelPerksCost(CafUnit, base_cost):
    perk_cost = 0
    #Price of Perks associated with the models
    if 'Specs' in CafUnit.keys() and 'Fast' in CafUnit['Specs']:
        perk_cost += .333333 * base_cost
    if 'Specs' in CafUnit.keys() and 'Regen' in CafUnit['Specs']:
        perk_cost += 2.47 * CafUnit["Model Qty"]
    return perk_cost

def _calculateLoadoutCost(CafUnit):
    #Price of all weapons in unit
    loadoutCost = 0
    for weapon in CafUnit['Weapons']:
        #Currently; all models in a unit must share the same weapon(s)
        loadoutCost += (__caclulateWeaponCost(weapon, CafUnit["Quality"]) * CafUnit["Model Qty"])
    return loadoutCost

def __caclulateWeaponCost(CafWeapon, quality):
    qua_pts = 11 - quality #Convert Qual to a simple scalar
    qua_pts = qua_pts / 10 # And then adjust it based on dice %
    #OPR Uses linear scaling for cost until >66.6(repeating, of course)%, and then switches to exponential scaling
    if qua_pts <= .666:
        price_per_attack = qua_pts * 7.8 #Derived from OPR Army Stats/Cost
    else:
        #Quadratic formula derived from OPR Armies (https://www.omnicalculator.com/statistics/quadratic-regression)
        price_per_attack = 7.8-(19.5 * qua_pts)+(23.4*qua_pts*qua_pts)
        price_per_attack_base = price_per_attack
    rending = False
    if 'Rending' in CafWeapon.keys() and CafWeapon['Rending']:
        rending = True
    if 'AP' in CafWeapon.keys():
        #AP/Rending math is.... weird. Simplified by breaking into the 4 possible cases based on AP level
        #AP Adjusts at a consistent ratio (regardless of quality); Rending follows the 'linear until 66% quality, and then exponential' paradigm
        try:
            ap_val = int(CafWeapon["AP"])
            if ap_val == 1:
                price_per_attack *= 1.5
                if rending:
                    if qua_pts <= .666:
                        price_per_attack += 0.65 + (1.812 * qua_pts)
                    else:
                        2.861 - (4.551 * qua_pts) + (5.454 * qua_pts * qua_pts)
            elif ap_val == 2:
                price_per_attack *= 2
                if rending:
                    if qua_pts <= .666:
                        price_per_attack += 0.6495 + (1.1664 * qua_pts)
                    else:
                        1.815 - (2.91 * qua_pts) + (3.492 * qua_pts * qua_pts)
            elif ap_val == 3:
                price_per_attack *= 2.4
                if rending:
                    if qua_pts <= .666:
                        price_per_attack += 0.65 + (0.648 * qua_pts)
                    else:
                        1.292 - (1.599 * qua_pts) + (1.926 * qua_pts * qua_pts)
            elif ap_val == 4:
                price_per_attack *= 2.7
                if rending:
                    if qua_pts <= .666:
                        price_per_attack += 0.6495 + (0.2598 * qua_pts)
                    else:
                        0.899 - (0.618 * qua_pts) + (0.756 * qua_pts * qua_pts)
        except:
            print("ERROR: WTF?")
    else:
        #Rending base case (NO AP present)
        if qua_pts <= .666:
            price_per_attack += 0.6505 + (2.2002 * qua_pts)
        else:
            2.861 - (5.532 * qua_pts) + (6.624 * qua_pts * qua_pts)
    #Price of a single weapon for a single model in unit
    weapon_price = price_per_attack * CafWeapon["Weapon qty per model"]
    return weapon_price

