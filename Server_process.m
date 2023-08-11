clear
close all

data = [3, 16, 29, 31, 40, 55, 0, 78, 97, 83];
TCPIPServer=tcpserver('127.0.1.1',6002);
while (1)
    if(TCPIPServer.Connected>0)
        x=read(TCPIPServer,TCPIPServer.NumBytesAvailable);
        msg = char(x);
        dataSplit = split(msg,[";","="]);
        str = msg;
        if(dataSplit(2)=="PUT")
            val = char(dataSplit(6));
            ind = char(dataSplit(4));            
            a = str2double(ind);
            a = a + 1;
            data(a) = str2double(val);
        end
        if(dataSplit(2)=="GET")
            ind = char(dataSplit(4));
            a = str2double(ind);
            a = a + 1;
            answer = data(a);
            string(answer);
            msg = msg(1:end-1);
            str = append(msg,string(answer));
            str = append(str, ';');
        end
        if(dataSplit(2)=="CLR")
            data = [0 0 0 0 0 0 0 0 0 0];
        end
        data;
        write(TCPIPServer,str,"uint8")
    end
end