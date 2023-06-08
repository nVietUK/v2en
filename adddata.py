import os
from googletrans import Translator
from difflib import SequenceMatcher

target = 'vi-en'
input_path = './data/{}.txt'.format(target[:2])
output_path = './data/{}.txt'.format(target[-2:])

def convert(x):
    x = x.replace(".", " . ").replace(",", " , ").replace("(", " ( ")
    x = x.replace(")", " ) ").replace("\"", " \" ").replace(":", " : ")
    return x


def cleanScreen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def gtrans(x, target):
    trans = Translator().translate(x, target).text
    return trans

def diffratio(x, y):
    return SequenceMatcher(None, x, y).ratio()

choice = input("Select input type:\n\t(1): keyboard input\n\t(2): file input\n\t(3): database input\n >> ")
if choice == "1":
    while (1):
        cleanScreen()
        oupt = input("Output sentence\n>> ")
        inpt = input("Input sentence\n>> ")
        if (inpt == "exit" or oupt == "exit"):
            break
        if inpt == "" or oupt == "":
            continue
        inptf = open(input_path, "a")
        ouptf = open(output_path, "a")
        inptf.write("\n{}".format(convert(inpt)))
        ouptf.write("\n{}".format(convert(oupt)))
        inptf.close()
        ouptf.close()
if choice == "2":
    file = open('./data/input.txt', "r")
    while 1:
        cleanScreen()
        inpt = file.readline()
        oupt = file.readline()
        if (not inpt or not oupt):
            break
        inptf = open(input_path, "a")
        ouptf = open(output_path, "a")
        inptf.write("\n{}".format(convert(inpt.replace('\n', ''))))
        ouptf.write("\n{}".format(convert(oupt.replace('\n', ''))))
        inptf.close()
        ouptf.close()
    file.close()
if choice == "3":
    dataINp = "./data/train.{}".format(target[:2])
    dataOUp = "./data/train.{}".format(target[-2:])
    inptf = open(input_path, "a"); ouptf = open(output_path, "a")
    dinptf = open('./data/dump.{}'.format(target[:2]), "a"); douptf = open('./data/dump.{}'.format(target[-2:]), "a")
    while 1:
        cleanScreen()
        iserror = False
        isagree = '!'
        dataINf = open(dataINp, "r")
        dataOUf = open(dataOUp, "r")
        dataIN = dataINf.readline().replace('\n', '')
        dataOU = dataOUf.readline().replace('\n', '')
        transIN = gtrans(dataOU, target[:2]); transOU = gtrans(dataIN, target[-2:])
        otoiratio = diffratio(dataIN, transIN); itooratio = diffratio(dataOU, transOU)
        if not dataIN or not dataOU:
            break
        if (dataIN.find('&') != -1 or dataOU.find('&') != -1): iserror = True
        elif otoiratio > 0.73 or itooratio > 0.73: isagree = ''
        else:
            print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n".format(target[:2], diffratio(dataIN, transIN), dataIN, transIN))
            print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n".format(target[-2:], diffratio(dataOU, transOU), dataOU, transOU))
            isagree = input("\tAdd to database? (Y/n)")
        if (isagree.lower() == 'y' or isagree == '') and not iserror:
            inptf.write("\n{}".format(convert(dataIN)))
            ouptf.write("\n{}".format(convert(dataOU)))
        elif (isagree == 'exit'): break
        else:
            dinptf.write("\n{}".format(convert(dataIN)))
            douptf.write("\n{}".format(convert(dataOU)))
        saveIN = dataINf.read().splitlines(True)
        saveOU = dataOUf.read().splitlines(True)
        dataINf.close(); dataOUf.close()
        with open(dataINp, "w") as file: file.writelines(saveIN[1:])
        with open(dataOUp, "w") as file: file.writelines(saveOU[1:])
    inptf.close(); ouptf.close()
    dinptf.close(); douptf.close()