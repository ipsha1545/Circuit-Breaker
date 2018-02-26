import socket
import select
from itertools import islice, cycle
import time
import sys
import redis
from cb_ans import CircuitBreaker
import cb_demo


server_cb1 = CircuitBreaker()
server_cb2 = CircuitBreaker()
server_cb3 = CircuitBreaker()

server_cb1.close()
server_cb2.close()
server_cb3.close()

array = [1,2,3]
redarray=[]
servernotrunning= []
redarray.append(1)




def find_position(port):
    length  = len(servernotrunning)
    if (length == 1):
        return 0
    elif length ==2:
        if(servernotrunning[0]==port):
            return 0
        elif(servernotrunning[1]==port):
            return 1
    elif length == 3:
        if (servernotrunning[0] == port):
            return 0
        elif (servernotrunning[1] == port):
            return 1
        elif (servernotrunning[2] == port):
            return 2
        
        
def find_port():
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    value = int(r.get(redarray[0]))
    if redarray[0] == 1:
        del redarray[0]
        redarray.append(2)
    elif redarray[0]==2:
        del redarray[0]
        redarray.append(3)
    elif redarray[0] == 3:
        del redarray[0]
        redarray.append(1)
    newvalue = is_working(value)

    return newvalue

def is_working(port):
    if (port in servernotrunning):
        if (port == 5001):
            server_cb1.check_state()
            if (server_cb1.find_state() == 2):
                position = find_position(5001)

                del servernotrunning[position]
                new_port = port

            else:
                print "*****************", server_cb1.find_state()
                new_port = find_port()

        if(port == 5002):

            server_cb2.check_state()
            if (server_cb2.find_state() == 2):
                position = find_position(5002)
                del servernotrunning[position]
                new_port=port

            else:
                print "*****************",server_cb2.find_state()
                new_port = find_port()


        if(port == 5003):
            server_cb3.check_state()
            if (server_cb3.find_state() == 2):
                position = find_position(5003)
                del servernotrunning[position]
                new_port = port

            else:
                print "*****************", server_cb3.find_state()
                new_port = find_port()


    else:
        new_port = port
    return new_port






buffer_size = 4096
delay = 0.0001
host = '127.0.0.1'
forward_to = (host,find_port())


class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
            print e
            return False

class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    print "Connected for the first time"
                    self.on_accept()
                    break
                print "Connected for the second time"
                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):

        a=find_port()

        forward = Forward().start('', a)
        #forward =Forward().start(forward_to[0],forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock

        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr

            if(a == 5001):
                server_cb1.handle_failure()
                state1 = server_cb1.find_state()
                if (state1 == 0):
                    servernotrunning.append(a)
                    print "AAAAAAAAAAAAAAAAAAAAAAA***************###############",servernotrunning

            elif(a == 5002):
                server_cb2.handle_failure()
                state2 = server_cb2.find_state()
                if (state2 == 0):
                    servernotrunning.append(a)
                    print "AAAAAAAAAAAAAAAAAAAAAAA***************###############",servernotrunning

            elif(a==5003):
                server_cb3.handle_failure()
                state3 = server_cb3.find_state()
                if (state3 == 0):
                    servernotrunning.append(a)
                    print "AAAAAAAAAAAAAAAAAAAAAAA***************###############",servernotrunning




            clientsock.close()

    def on_close(self):
        print self.s.getpeername(), "has disconnected"
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        print data
        self.channel[self.s].send(data)

if __name__ == '__main__':
        server = TheServer('', 9091)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping server"
            sys.exit(1)