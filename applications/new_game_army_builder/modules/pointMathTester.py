from OprPointMath import _calculateBaseCost as Opr__calculateBaseCost
from CafPointMath import _calculateBaseCost as Caf__calculateBaseCost
import json
from UnitTestCases import Test_Cases

def Opr_TestBaseCase(OprUnit):
    print("==========")
    print("OPR MATH")
    print(OprUnit)
    print("Cost: "+str(Opr__calculateBaseCost(OprUnit)))
    print("==========")
    print()

def Caf_TestBaseCase(OprUnit):
    print("==========")
    print("CAF MATH")
    print(OprUnit)
    print("Cost: "+str(Caf__calculateBaseCost(OprUnit)))
    print("==========")
    print()

print("TESTING OPR BASE CASES")
for index in range(5):
    Opr_TestBaseCase(Test_Cases[index])
print("\nTESTING CAF BASE CASES")
for index in range(5,14):
    Caf_TestBaseCase(Test_Cases[index])

#For each test; compare OPR and CAF Math against each other.
#Add new test cases for any supported features

#for mycase in Test_Cases:
#    print(_calculateBaseCost(mycase))
