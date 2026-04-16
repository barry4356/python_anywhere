def CalculateUnitCost(OprUnit):
    base_cost = _calculateBaseCost(OprUnit)
    model_perk_cost = _calculateModelPerkCost(OprUnit, base_cost)
    weapon_cost = _calculateLoadoutCost(OprUnit)
    return 0

def _calculateBaseCost(OprUnit):
    #Price of model Def/Qual x number of models
    return 0

def _calculateModelPerkCost(OprUnit, base_cost):
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
