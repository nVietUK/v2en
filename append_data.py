def convert(x):
    x=x.replace(".", " . ").replace(",", " , ").replace("(", " ( ")
    x=x.replace(")", " ) ").replace("\"", " \" ").replace(":", " : ")
    return x.lower()

while (1):
    inpt = input("Input sentence\n>> ")
    if (inpt == "exit"):
        break
    oupt = input("Output sentence\n>> ")
    inptf = open("./data/inpt.txt", "a"); ouptf = open("./data/oupt.txt", "a")
    inptf.write("\n{}".format(convert(inpt))); ouptf.write("\n{}".format(convert(oupt)))
    inptf.close(); ouptf.close()