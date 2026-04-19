from OprPointMath import _calculateBaseCost as Opr__calculateBaseCost
from CafPointMath import _calculateBaseCost as Caf__calculateBaseCost
from OprPointMath import __caclulateWeaponCost as Opr__calculateWeaponCost
import json
from UnitTestCases import Test_Cases

def Opr_TestBaseCase(OprUnit):
    print("==========")
    print("OPR MATH")
    print(OprUnit)
    print("Cost: "+str(Opr__calculateBaseCost(OprUnit)))
    print("==========")
    print()

def Opr_TestBaseCases():
    print()
    print("TESTING OPR BASE CASES")
    for defense in range(2, 7):
        for quality in range(2, 7):
            OprUnit = {'Def': defense, 'Qual': quality, 'ModelCount': 100}
            print("==========")
            print("OPR MATH")
            print(OprUnit)
            print("Cost: "+str(Opr__calculateBaseCost(OprUnit)))
            print("==========")
            print()
    print()
    print("==========")

def Caf_TestBaseCases():
    print()
    print("TESTING CAF BASE CASES")
    for defense in range(2, 11):
        for quality in range(2, 11):
            CafUnit = {'Defense': defense, 'Quality': quality, 'ModelCount': 100}
            print("==========")
            print("CAF MATH")
            print(CafUnit)
            print("Cost: "+str(Caf__calculateBaseCost(CafUnit)))
            print("==========")
            print()
    print()
    print("==========")

def Caf_Opr_Base_compare():
    CafUnit = {'Defense': 6, 'Quality': 6, 'ModelCount': 100}
    OprUnit = {'Def': 4, 'Qual': 4, 'ModelCount': 100}
    print("COMPARING BASE CASES")
    print("CAF MATH")
    print(CafUnit)
    print("Cost: "+str(Caf__calculateBaseCost(CafUnit)))
    print("OPR MATH")
    print(OprUnit)
    print("Cost: "+str(Opr__calculateBaseCost(OprUnit)))
    print()
    print("==========")


def Caf_TestBaseCase(OprUnit):
    print("==========")
    print("CAF MATH")
    print(OprUnit)
    print("Cost: "+str(Caf__calculateBaseCost(OprUnit)))
    print("==========")
    print()

def Opr_TestWeaponCase(oprWeapon):
    print("==========")
    print("OPR WEAPON MATH")
    print(oprWeapon)
    print("Cost: "+str(Opr__calculateWeaponCost(oprWeapon)))
    print("==========")
    print()

def Opr_TestWeaponCases():
    print("TESTING OPR WEAPON CASES")
    for attacks in range(1,20):
        for quality in range(2, 7):
            oprWeapon = {"Attacks": attacks, "AP": 0}
            print("==========")
            print("OPR WEAPON MATH")
            print(oprWeapon)
            print('quality: '+str(quality))
            print("Cost: "+str(Opr__calculateWeaponCost(oprWeapon, quality)))
            print("==========")
            print()
    print()
    print("==========")
    

## __MAIN__ ##
Opr_TestWeaponCases()
#Caf_Opr_Base_compare()
#Opr_TestBaseCases()
#Caf_TestBaseCases()
#print("TESTING OPR BASE CASES")
#for index in range(0,5):
#    Opr_TestBaseCase(Test_Cases[index])

#print("\nTESTING CAF BASE CASES")
#for index in range(5,14):
#    Caf_TestBaseCase(Test_Cases[index])

#print("TESTING OPR WEAPON CASES")
#for index in range(14,15):
#    Opr_TestWeaponCase(Test_Cases[index])

#For each test; compare OPR and CAF Math against each other.
#Add new test cases for any supported features

#for mycase in Test_Cases:
#    print(_calculateBaseCost(mycase))
