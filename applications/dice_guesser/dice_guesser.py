#dice_guesser.py
import numpy as np
import random

def get_dinput(prompt):
    val = 0
    try:
        val = int(input(prompt))
    except ValueError:
        val = 0
    print()
    return val

def roll_1d4():
    return (random.randrange(4) + 1)
    
def roll_1d6():
    return (random.randrange(6) + 1)

def roll_1d8():
    return (random.randrange(8) + 1)

def roll_1d10():
    return (random.randrange(10) + 1)

def roll_1d12():
    return (random.randrange(12) + 1)

def roll_1d20():
    return (random.randrange(20) + 1)

def print_dice(d4, d6, d8, d10, d12, d20, bonus):
    print(f'{d4}d4')
    print(f'{d6}d6')
    print(f'{d8}d8')
    print(f'{d10}d10')
    print(f'{d12}d12')
    print(f'{d20}d20')
    print(f'+{bonus}')

def simulate_rolls(d4, d6, d8, d10, d12, d20, bonus, count):
    results = []
    
    for j in range(count):
        total = 0
        for i in range(d4):
            total = total + (roll_1d4())
        for i in range(d6):
            total = total + (roll_1d6())
        for i in range(d8):
            total = total + (roll_1d8())
        for i in range(d10):
            total = total + (roll_1d10())
        for i in range(d12):
            total = total + (roll_1d12())
        for i in range(d20):
            total = total + (roll_1d20())
        total = total + bonus
        results.append(total)
    
    return(results)
    
def calculate_odds(results, count):
    odds = [0] * (max(results)+1)
    for value in results:
        odds[value] = odds[value] + 1
    for index, value in enumerate(odds):
        odds[index] = (value/count)*100
    return odds

def print_odds(odds):
    counter = 0
    print()
    print("Odds:")
    for i in odds:
        if i > 0:
            print(f' {counter}:\t{round(i)}%')
        counter=counter+1

exit = False;
while exit != True:
    print ("\n===== DICE GUESSER =====\n")
    print("")
    roll_count = 1000000

    d4 = get_dinput("How many d4? ")
    d6 = get_dinput("How many d6? ")
    d8 = get_dinput("How many d8? ")
    d10 = get_dinput("How many d10? ")
    d12 = get_dinput("How many d12? ")
    d20 = get_dinput("How many d20? ")
    bonus = get_dinput("Base amount? ")
    mymin = get_dinput("Minimum Goal?")
    print("\n")
    #print_dice(d4, d6, d8, d10, d12, d20, bonus)
    rolls = simulate_rolls(d4, d6, d8, d10, d12, d20, bonus, roll_count)
    odds = calculate_odds(rolls, roll_count)
    print_odds(odds)

