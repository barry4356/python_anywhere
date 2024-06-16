import random

def roll_1d6():
    return (random.randrange(6) + 1)

def simulate_damage(stats, count):
    results = []
    # Run one simulation for each 'count'
    for j in range(count):
        damage = 0
        # Roll each attack, and immediately roll defense
        for i in range(stats["attacks"]):
            dieroll_a = roll_1d6()
            damage += handle_furious(dieroll_a, stats)
            applied_ap = stats["armorPiercing"]
            # If 'rending'; 6 results in extra AP
            if stats["rending"] and dieroll_a == 6:
                applied_ap = 4
            # Check if the initial attack roll meets the quality value
            if dieroll_a >= stats["quality"]:
                dieroll_d = roll_1d6()
                # If 'poison'; re-roll on a defense roll of 6
                if stats["poison"] and dieroll_d == 6:
                    dieroll_d = roll_1d6()
                # Defense rolls of 1 always fail
                if dieroll_d <= 1:
                    damage += defender_takes_damage(stats)
                # Defense rolls of 6 always succeed
                elif dieroll_d < 6:
                    # Apply any AP or defense bonus
                    if dieroll_d < (stats["defense"] + applied_ap - stats['defenseBonus']):
                        damage += defender_takes_damage(stats)
        results.append(damage)
    return results

# Handle Furiousness
def handle_furious(dieroll_a, stats):
    damage = 0
    # If 'furiouser'; 5 & 6 result in an extra hit w/o AP
    if stats["furiouser"] and dieroll_a >= 5:
        dieroll_d = roll_1d6()
        if dieroll_d <= 1:
            damage += defender_takes_damage(stats)
        elif dieroll_d < 6:
            if dieroll_d < (stats["defense"] - stats['defenseBonus']):
                damage += defender_takes_damage(stats)
    # If 'furious'; 6 results in an extra hit w/o AP
    elif stats["furious"] and dieroll_a == 6:
        dieroll_d = roll_1d6()
        if dieroll_d <= 1:
            damage += defender_takes_damage(stats)
        elif dieroll_d < 6:
            if dieroll_d < (stats["defense"] - stats['defenseBonus']):
                damage += defender_takes_damage(stats)
    return damage

# Handle regen check
def defender_takes_damage(stats):
    damage = 1
    if stats["regen"]:
        dieroll_d = roll_1d6()
        if dieroll_d >= 5:
            damage = 0
    return damage
