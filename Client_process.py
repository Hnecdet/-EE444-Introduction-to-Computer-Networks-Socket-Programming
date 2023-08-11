import socket
from time import sleep

PROXY_PORT = 6001
specified_Indices = list()
specified_Data = list()
msg = ""
responsemsg = ""
resp_Indices = list()
resp_Data = list()
HOST = "127.0.0.1"


try:
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0, fileno=None)
    print("Client socket created\n")
except Exception as error:
    print(str(error))
    print("Error when creating the client-server socket")
    exit(1)
try:
    clientSocket.connect((HOST, PROXY_PORT))
    print("Connected to the proxy server at {0}:{1}\n".format(HOST, PROXY_PORT))
except Exception as error:
    print(str(error))
    print("Error when connecting to the proxy-server socket")
    exit(1)


def get_add_op(OPCode):

    if OPCode == 1 or OPCode == 4:
        pass
    else:
        raise Exception("Invalid OPCode mode ({0}) supplied to get_add_op.".format(OPCode))
    global specified_Indices
    enter_Indices = input("Enter the indices you want to {0}:\n(format required is: 0,1,2,3,4,5,6,7,8,9".format("get" if OPCode == 1 else "add"))
    valid_Indices = list()
    try:
        enter_Indices = enter_Indices.strip(" ").replace(" ", "").split(",")
        for index in enter_Indices:
            if int(index) > 0 or int(index) < 9:
                valid_Indices.append(int(index))
            else:
                raise ValueError("Invalid index: {0}.".format(index))
        if OPCode == 4 and (len(valid_Indices) < 2 or len(valid_Indices) > 5):
            raise ValueError(
            )

        specified_Indices = valid_Indices
    except ValueError as error:
        raise error
    except:
        raise ValueError("Invalid input.")


def put_op():
    global specified_Indices
    global specified_Data
    enter_Indices = input(
        "Enter the indices you want to put:\n(format required is: 0,1,2,3,4,5,6,7,8,9"
    )
    enteredData = input(
        "Enter the data whatever you want as integer"
    )
    valid_Indices = list()
    valid_Data = list()
    try:
        enter_Indices = enter_Indices.strip(" ").replace(" ", "").split(",")
        enteredData = enteredData.strip(" ").replace(" ", "").split(",")
        for index in enter_Indices:
            if int(index) < 0 or int(index) > 9:
                raise ValueError("Invalid index: {0}. Try again\n".format(index))
            valid_Indices.append(int(index))
        for datum in enteredData:
            valid_Data.append(int(datum))
        specified_Data = valid_Data
        specified_Indices = valid_Indices
    except ValueError as error:
        raise error
    except:
        raise ValueError("Invalid input. Try again\n")

def prepare_msg(OPCode):
    global msg
    if OPCode == 1:
        msg = "OP=GET;IND={0}".format(",".join(str(i) for i in specified_Indices))
    elif OPCode == 2:
        msg = "OP=PUT;IND={0};DATA={1}".format(
            ",".join(str(i) for i in specified_Indices), ",".join(str(i) for i in specified_Data)
        )
    elif OPCode == 3:
        msg = "OP=CLR"
    elif OPCode == 4:
        msg = "OP=ADD;IND={0}".format(",".join(str(i) for i in specified_Indices))

def send_proxy():
    global msg
    global clientSocket
    clientSocket.send(msg.encode())
    print("msg sent to proxy server: {0}\n".format(msg))

def decompose_msg():
    global responsemsg
    global resp_Indices
    global resp_Data

    OPCode = ""
    msgParts = responsemsg.split(";")
    try:
        for mPart in msgParts:
            key, value = mPart.split("=")

            if key == "OP":
                OPCode = value

            elif key == "IND":
                resp_Indices = [int(i) for i in value.split(",")]

            elif key == "DATA":
                resp_Data = [int(i) for i in value.split(",")]
            elif key == "CODE":
                if int(value) == 404:
                    raise Exception("Indices not found")
                elif int(value) == 500:
                    raise Exception("Server error.")
                elif int(value) == 200:
                    pass
    except Exception as error:
        raise error
    return OPCode

def print_response(OPCode):
    global resp_Indices
    global resp_Data
    if OPCode == "GET":
        print("Retrieved data\nIndex\tData")
        for i in range(len(resp_Indices)):
            print("{0}\t{1}".format(resp_Indices[i], resp_Data[i]))
    elif OPCode == "PUT":
        print("Updated data\nIndex\tData")
        for i in range(len(resp_Indices)):
            print("{0}\t{1}".format(resp_Indices[i], resp_Data[i]))
    elif OPCode == "CLR":
        print("Cleared!")
    elif OPCode == "ADD":
        print("Added: {0}".format(",".join(str(i) for i in resp_Indices)))
        print("Result: {0}".format(resp_Data[0]))

def clear_variables():
    global specified_Indices
    global specified_Data
    global resp_Indices
    global resp_Data
    global msg
    global responsemsg
    responsemsg = ""
    msg = ""
    specified_Indices = []
    specified_Data = []
    resp_Indices = []
    resp_Data = []


def main():
    global msg
    global specified_Data
    global specified_Indices
    global responsemsg
    global clientSocket
    while (1):
        print("OPCodes:")
        print("1. GET: (1)")
        print("2. PUT: (2)")
        print("3. CLR: (3)")
        print("4. ADD: (4)")
        print("5. Exit: (5)")
        chosen_OPCode = input("Enter the OPCode:\n")
        try:
            chosen_OPCode = int(chosen_OPCode)
        except:
            print("Invalid OPCode\n")
            sleep(1)
            continue
        if chosen_OPCode > 1 or chosen_OPCode < 5:
            try:
                if chosen_OPCode == 5:
                    break
                elif chosen_OPCode == 1:
                    get_add_op(1)
                elif chosen_OPCode == 2:
                    put_op()
                elif chosen_OPCode == 4:
                    get_add_op(4)
                else:
                    pass
                prepare_msg(chosen_OPCode)
                send_proxy()
                try:
                    dataReceived = clientSocket.recv(1024)
                except:
                    print("Error occurred when receiving data from the proxy server.\n")
                    exit(1)
                if dataReceived:
                    try:
                        responsemsg = dataReceived.decode("utf-8")
                    except:
                        print("Error occured when decoding")
                        continue
                    print("Received from the proxy server: {0}".format(responsemsg))
                    try:
                        OPCode = decompose_msg()
                        print_response(OPCode)
                    except Exception as error:
                        print(str(error))
                    clear_variables()
                    print("\n")
                    sleep(1)
            except Exception as error:
                print(error)
                sleep(1)
                continue
        else:
            print("Invalid OPCode.\n")
            sleep(1)
            continue

if __name__ == "__main__":
    main()