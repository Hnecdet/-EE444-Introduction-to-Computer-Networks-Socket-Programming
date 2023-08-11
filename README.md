# -EE444-Introduction-to-Computer-Networks-Socket-Programming

1. socket.socket(family=AF INET, type=SOCK STREAM, proto=0, fileno=None)
Creates a socket object, default parameters are correct for this homework.
2. socket.bind(address)
Binds the socket to an address that is (IP, PORT) pair.
3. socket.close()
Closes the socket and all its connections
4. socket.listen([backlog])
Enable a server to accept connections. Listens to the number of connections specified by backlog.
5. socket.connect(address)
Connect to a remote socket at the address, the address is (IP, PORT) pair.
6. socket.accept()
Accepts an incoming connection. The return value is a pair (conn, address) where
conn is a new socket object usable to send and receive data on the connection, and
address is the address bound to the socket on the other end of the connection.
7. socket.recv(bufsize[, flags])
Receives a specified number of bytes from the TCP buffer. Returns a byte object
representing the received data.
8. socket.send(bytes[, flags])
Sends a specified number of bytes through the socket. Returns the number of bytes
sent.
9. socket.sendall(bytes[, flags])
Similar to send but this method continues to send data from bytes until either all
data has been sent or an error occurs.


The Server will hold a list of 10 elements. Each entry will consist
of an index value ranging from 0 to 9 and data of a single integer. The Proxy should be
consistent with the server, that is any update made to the Proxy’s table should also be
made to Server’s table.

Nodes will exchange proxy messages between them using the format below.
OP=XXX;IND=Ind1,Ind2,..;DATA=Dat1,Dat2,...;
Notice that fields are separated with semicolons(;). OP field describes which operation
to do on the table, for more detail check Table 3. IND field tells which of the indexes are
required for the operation. The DATA field is for integer data either from the server for
operations like ”ADD” or as an update value from the client. Not all messages require
every field. You can choose to omit the unused fields for certain operations. Details of
the implementation are up to you
Response messages have the same form as request messages. For example response
to the ”ADD” messa

The Proxy server will hold half of the table in its process,
think of it as a cached version of the Server’s table. The Client will only communicate
with the proxy server, if an element that is not present in the Proxy’s table is required
proxy server will communicate with the Server to get that element and add it to its table
by overwriting the oldest table entry.
