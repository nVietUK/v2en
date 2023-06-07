import os

def convert(x):
    x=x.replace(".", " . ").replace(",", " , ").replace("(", " ( ")
    x=x.replace(")", " ) ").replace("\"", " \" ").replace(":", " : ")
    return x

def cleanScreen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

target='vi-en'
input_path='./data/{}.txt'.format(target[:2])
output_path='./data/{}.txt'.format(target[-2:])

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
        inptf = open(input_path, "a"); ouptf = open(output_path, "a")
        inptf.write("\n{}".format(convert(inpt))); ouptf.write("\n{}".format(convert(oupt)))
        inptf.close(); ouptf.close()
if choice == "2":
    file = open('./data/input.txt', "r")
    while 1:
        cleanScreen()
        inpt = file.readline(); oupt = file.readline()
        if (not inpt or not oupt):
            break
        inptf = open(input_path, "a"); ouptf = open(output_path, "a")
        inptf.write("\n{}".format(convert(inpt.replace('\n','')))); ouptf.write("\n{}".format(convert(oupt.replace('\n',''))))
        inptf.close(); ouptf.close()
    file.close()
if choice == "3":
    dataINp = "./data/train.{}".format(target[:2]); dataOUp = "./data/train.{}".format(target[-2:])
    while 1:
        cleanScreen()
        isError = False; isagree = '!'
        dataINf = open(dataINp, "r"); dataOUf = open(dataOUp, "r")
        dataIN = dataINf.readline(); dataOU = dataOUf.readline() 
        if not dataIN or not dataOU: 
            break
        if (dataIN.find('&') != -1 or dataOU.find('&') != -1):
            isError = True
        else:
            isagree=input("\t{} input\n\t\t- {}\n\n\t{} input\n\t\t- {}\n\n\tAdd to database? (Y/n)".format(target[:2], dataIN, target[-2:], dataOU))
        if (isagree.lower() == 'y' or isagree=='') and not isError:
            inptf = open(input_path, "a"); ouptf = open(output_path, "a")
            inptf.write("\n{}".format(convert(dataIN.replace('\n','')))); ouptf.write("\n{}".format(convert(dataOU.replace('\n', ''))))
            inptf.close(); ouptf.close()
        elif (isagree == 'exit'):
            break
        else:
            inptf = open('./data/dump.{}'.format(target[:2]), "a"); ouptf = open('./data/dump.{}'.format(target[-2:]), "a")
            inptf.write("\n{}".format(convert(dataIN.replace('\n','')))); ouptf.write("\n{}".format(convert(dataOU.replace('\n', ''))))
            inptf.close(); ouptf.close()
        saveIN = dataINf.read().splitlines(True); saveOU = dataOUf.read().splitlines(True); dataINf.close(); dataOUf.close()
        with open(dataINp, "w") as file:
            file.writelines(saveIN[1:])
        with open(dataOUp, "w") as file:
            file.writelines(saveOU[1:])