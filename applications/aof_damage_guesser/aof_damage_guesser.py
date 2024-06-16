import json
import os
from modules.simulator import simulate_damage

datadir = './dataFiles/'

dataFilesRaw = os.listdir(datadir)
dataFiles = []

for myfile in dataFilesRaw:
    if myfile.endswith('.json'):
        dataFiles.append(myfile)

validSelection = False
while not validSelection:
    print("\nChoose attacker stat file:")
    fileCounter = 1
    for dataFile in dataFiles:
        print('{0}: {1}'.format(fileCounter, dataFile))
        fileCounter += 1
    try:
        userinput_a = int(input("Attacker Stat File: "))
        userinput_d = int(input("Defender Stat File: "))
        if userinput_a > 0 and userinput_a <= len(dataFiles):
            if userinput_d > 0 and userinput_d <= len(dataFiles):
                validSelection = True
    except:
        pass

attacker_data = {}
defender_data = {}
with open(datadir+dataFiles[userinput_a-1]) as json_file:
        attacker_data = json.load(json_file)
with open(datadir+dataFiles[userinput_d-1]) as json_file:
        defender_data = json.load(json_file)


print('Attacker Stats:')
print(json.dumps(attacker_data, indent=2))
print('Defender Stats:')
print(json.dumps(defender_data, indent=2))

stats = attacker_data
stats['defense'] = defender_data['defense']
stats['defenseBonus'] = defender_data['defenseBonus']
stats['regen'] = defender_data['regen']

print(simulate_damage(stats, 20))
