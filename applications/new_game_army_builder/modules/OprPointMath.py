def CalculateUnitCost(OprUnit):
    base_cost = _calculateBaseCost(OprUnit)
    model_perk_cost = _calculateModelPerksCost(OprUnit, base_cost)
    weapons_cost = _calculateLoadoutCost(OprUnit)
    return base_cost + weapons_cost + model_perk_cost

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
    perk_cost = 0
    #Price of Perks associated with the models
    if 'Specs' in OprUnit.keys() and 'Fast' in OprUnit['Specs']:
        perk_cost += .333333 * base_cost
    if 'Specs' in OprUnit.keys() and 'Regen' in OprUnit['Specs']:
        hp_count = CafUnit["Model Qty"]
        if 'Tough' in OprUnit.keys() and int(OprUnit['Tough']) > 1:
            hp_count *= OprUnit['Tough']
        perk_cost += 2.47 * hp_count
    if 'Tough' in OprUnit.keys() and int(OprUnit['Tough']) > 1:
        if OprUnit['Tough'] == 2:
            perk_cost += (.75 * base_cost) #Just to keep things rational... Tough2 is a joke
        else:
            perk_cost += (1.522 * int(OprUnit['Tough']) - 3.647) * base_cost
    if 'Caster' in OprUnit.keys() and int(OprUnit['Caster']) > 0:
        #Direct cost based on Caster Level
        perk_cost += (16.03 * OprUnit['Caster'] - 1.325) * OprUnit["Model Qty"]
    return perk_cost

def _calculateLoadoutCost(OprUnit):
    #Price of all weapons in unit
    loadoutCost = 0
    for weapon in OprUnit['Weapons']:
        #Currently; all models in a unit must share the same weapon(s)
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
        #AP/Rending math is.... weird. Simplified by breaking into the 4 possible cases based on AP level
        #AP Adjusts at a consistent ratio (regardless of quality); Rending follows the 'linear until 66% quality, and then exponential' paradigm
        try:
            ap_val = int(OprWeapon["AP"])
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
    if 'Weapon Range' in OprWeapon.keys() and OprWeapon['Weapon_Range'] > 0:
        price_per_attack = price_per_attack * (OprWeapon['Weapon_Range'] / 12)
    #Price of a single weapon for a single model in unit
    weapon_price = price_per_attack * OprWeapon["Attacks"]
    return weapon_price
