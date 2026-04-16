def CalculateUnitCost(CafUnit):
    base_cost = _calculateBaseCost(CafUnit)
    model_perk_cost = _calculateModelPerkCost(CafUnit, base_cost)
    weapons_cost = _calculateLoadoutCost(CafUnit)
    return 0

def _calculateBaseCost(CafUnit):
    #Price of model Def/Qual x number of models
    return 0

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
