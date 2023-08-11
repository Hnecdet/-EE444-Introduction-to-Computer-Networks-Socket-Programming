import socket

server_connection = False
server_established = False
req_Indices = list()
req_Data = list()
resp_Indices = list()
serverresp_Indices = list()
serverresp_Data = list()
responseData = list()
serverreq_Indices = list()
serverreq_Data = list()
sum_result = 0
client_msg = ""
server_msg = ""
server_resp_msg = ""
HOST = "127.0.0.1"
SELF_PORT = 6001
SERVER_PORT = 6002

try:
    proxy_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Proxy - server socket created")
except Exception as error:
    print(str(error))
    print("Error when creating the proxy - server socket")
    #exit(1)
try:
    proxy_server_socket.connect((HOST, SERVER_PORT))
    print("Connected to the backend server at {0}:{1}\n".format(HOST, SERVER_PORT))
except Exception as error:
    print(str(error))
    print("Error when connecting to the backend server")
    #exit(1)

try:
    proxyClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxyClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxyClientSocket.bind((HOST, SELF_PORT))
except Exception as error:
    print(str(error))
    print("Error when creating the client - proxy socket")
    #exit(1)
print("Proxy server is running on {0}:{1}\n".format(HOST, SELF_PORT))
try:
    proxyClientSocket.listen(1)
    print("Listening...")
except Exception as error:
    print(str(error))
    print("Error when listening")
    #exit(1)
try:
    clientConnection, clientAddress = proxyClientSocket.accept()
    print("Connected by", clientAddress)
except Exception as error:
    print(str(error))
    print("Error when accepting")
    #exit(1)

storage_Indices = []
storage_Data = []

def decompose_msg(msg, isServerResponse=False):
    global req_Indices
    global req_Data
    global serverresp_Indices
    global serverresp_Data

    OPCode = ""
    msgParts = msg.split(";")
    try:
        for mPart in msgParts:
            key, value = mPart.split("=")

            if key == "OP":
                OPCode = value

            elif key == "IND":
                if isServerResponse:
                    serverresp_Indices = [int(i) for i in value.split(",")]
                else:
                    req_Indices = [int(i) for i in value.split(",")]

            elif key == "DATA":
                if isServerResponse:
                    serverresp_Data = [int(i) for i in value.split(",")]
                else:
                    req_Data = [int(i) for i in value.split(",")]
            elif key == "CODE":
                if int(value) == 404:
                    raise Exception("404-Indices not found.")
                elif int(value) == 500:
                    raise Exception("505-Server error.")
                elif int(value) == 200:
                    pass
    except Exception as error:
        raise error
    return OPCode


def send_client():
    global client_msg
    global clientConnection
    try:
        clientConnection.send(client_msg.encode("utf-8"))
        print("Sent msg to client: {0}".format(client_msg))
    except:
        print("Error when sending msg to client")
        raise Exception("500-Error when sending msg to client")


def send_server():
    global server_msg
    global proxy_server_socket
    try:
        proxy_server_socket.send(server_msg.encode("utf-8"))
        print("Sent msg to server: {0}".format(server_msg))
    except:
        print("Error when sending msg to backend server")
        raise Exception("500-Error when sending msg to backend server")


def prepare_server(OPCode):
    global server_msg
    global serverreq_Indices
    global serverreq_Data
    if OPCode == "GET":
        server_msg = "OP=GET;IND={0}".format(",".join(str(i) for i in serverreq_Indices))
    elif OPCode == "PUT":
        server_msg = "OP=PUT;IND={0};DATA={1}".format(
            ",".join(str(i) for i in serverreq_Indices), ",".join(str(i) for i in serverreq_Data)
        )
    elif OPCode == "CLR":
        server_msg = "OP=CLR"
    elif OPCode == "ADD":
        server_msg = "OP=ADD;IND={0}".format(",".join(str(i) for i in serverreq_Indices))


def prepare_client(OPCode):
    global client_msg
    global resp_Indices
    global responseData
    global sum_result
    if OPCode == "GET":
        client_msg = "OP=GET;IND={0};DATA={1};CODE=200".format(",".join(str(i) for i in resp_Indices), ",".join(str(i) for i in responseData))
    elif OPCode == "PUT":
        client_msg = "OP=PUT;IND={0};DATA={1};CODE=200".format(",".join(str(i) for i in serverresp_Indices), ",".join(str(i) for i in serverresp_Data))
    elif OPCode == "CLR":
        client_msg = "OP=CLR;CODE=200"
    elif OPCode == "ADD":
        client_msg = "OP=ADD;IND={0};DATA={1};CODE=200".format(",".join(str(i) for i in resp_Indices), sum_result)

def perform_OPCode(OPCode):
    global storage_Indices
    global storage_Data
    global lastUpdated
    global req_Indices
    global req_Data
    global resp_Indices
    global responseData
    global server_connection
    global sum_result
    if OPCode == "GET":
        for index in req_Indices:
            if index in storage_Indices:
                resp_Indices.append(index)
                responseData.append(storage_Data[storage_Indices.index(index)])
            else:
                server_connection = True
                serverreq_Indices.append(index)
    elif OPCode == "CLR":
        server_connection = True

        storage_Data = []
        storage_Indices = []
        lastUpdated = []
        print("Proxy table cleared\n")
        
    elif OPCode == "ADD":
        sum = 0
        for index in req_Indices:
            if index in storage_Indices:
                sum += storage_Data[storage_Indices.index(index)]
            else:
                server_connection = True
                break
        if server_connection:
            for index in req_Indices:
                serverreq_Indices.append(index)
        else:
            sum_result = sum
            resp_Indices = req_Indices

    elif OPCode == "PUT":
        server_connection = True
        proxyTableUpdated = False

        for index in req_Indices:
            if index in storage_Indices:
                storage_Data[storage_Indices.index(index)] = req_Data[req_Indices.index(index)]
                proxyTableUpdated = True
            serverreq_Indices.append(index)
            serverreq_Data.append(req_Data[req_Indices.index(index)])
        if proxyTableUpdated:
            print_proxy_table()


def perform_server_OPCode(OPCode):
    global storage_Indices
    global storage_Data
    global lastUpdated
    global serverresp_Indices
    global serverresp_Data
    global sum_result
    global resp_Indices
    global responseData
    if OPCode == "GET":
        for index in serverresp_Indices:
            resp_Indices.append(index)
            responseData.append(serverresp_Data[serverresp_Indices.index(index)])
            if len(storage_Data) == 5:
                storage_Indices.pop(0)
                storage_Data.pop(0)
            storage_Indices.append(index)
            storage_Data.append(serverresp_Data[serverresp_Indices.index(index)])
        print_proxy_table()
    elif OPCode == "ADD":
        sum_result = serverresp_Data[0]
        resp_Indices = serverresp_Indices

def print_proxy_table():
    print("\nChanges made to the proxy table:")
    print("Index\tData")
    for i in range(len(storage_Indices)):
        print("{0}\t{1}".format(storage_Indices[i], storage_Data[i]))
    print("\n")

def clear_variables():
    global req_Indices
    global req_Data
    global resp_Indices
    global responseData
    global serverreq_Indices
    global serverreq_Data
    global serverresp_Indices
    global serverresp_Data
    global client_msg
    global server_msg
    global server_resp_msg
    global server_connection
    global server_established
    req_Indices = []
    req_Data = []
    resp_Indices = []
    responseData = []
    serverreq_Indices = []
    serverreq_Data = []
    serverresp_Indices = []
    serverresp_Data = []
    client_msg = ""
    server_msg = ""
    server_resp_msg = ""
    server_connection = False
    server_established = False


def main():
    global proxyClientSocket
    global clientConnection
    global clientAddress
    global server_connection
    global client_msg
    while True:
        try:
            dataReceived = clientConnection.recv(1024)
        except:
            print(clientAddress, "disconnected")
            proxyClientSocket.listen(1)
            clientConnection, clientAddress = proxyClientSocket.accept()
            print("Connected by", clientAddress)
            continue
        if dataReceived:
            try:
                dataReceived = dataReceived.decode("utf-8")
            except:
                print("Error when decoding")
                client_msg = "500"
                try:
                    send_client()
                except:
                    pass
                clear_variables()
                continue
            print("Received msg from client: {0}".format(dataReceived))
            try:
                OPCode = decompose_msg(dataReceived)
                perform_OPCode(OPCode)
                if server_connection:
                    prepare_server(OPCode)
                    send_server()
                    try:
                        serverDataReceived = proxy_server_socket.recv(1024)
                    except:
                        print("Error when receiving data")
                        #exit(1)
                    if serverDataReceived:
                        try:
                            server_resp_msg = serverDataReceived.decode("utf-8")
                        except:
                            print("Error when decoding")
                            continue
                        print("Received msg from the backend server: {0}".format(server_resp_msg))
                        OPCode = decompose_msg(server_resp_msg, True)
                        perform_server_OPCode(OPCode)
                prepare_client(OPCode)
                send_client()
                print("\n")
            except Exception as error:
                print(str(error))
                print("\n")
                if "404" in str(error):
                    client_msg = "404"
                if "500" in str(error):
                    client_msg = "500"
                try:
                    send_client()
                except:
                    pass
            clear_variables()


if __name__ == "__main__":
    main()