
def convert(x):
    x=x.replace(".", " . ").replace(",", " , ").replace("(", " ( ")
    x=x.replace(")", " ) ").replace("\"", " \" ").replace(":", " : ")
    return x

target='en-vi'
input_path='./data/{}.txt'.format(target[:2])
output_path='./data/{}.txt'.format(target[-2:])

while (1):
    oupt = input("Output sentence\n>> ")
    inpt = input("Input sentence\n>> ")
    if (inpt == "exit" or oupt == "exit"):
        break
    if inpt == "" or oupt == "":
        continue
    inptf = open(input_path, "a"); ouptf = open(output_path, "a")
    inptf.write("\n{}".format(convert(inpt))); ouptf.write("\n{}".format(convert(oupt)))
    inptf.close(); ouptf.close()