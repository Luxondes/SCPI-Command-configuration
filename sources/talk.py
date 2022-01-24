import vxi11
import socket
class Talk:
    def write(self, textMessage):
        pass
    def ask(self, textMessage):
        pass
    def close(self):
        pass
    def connect(self):
        pass
class GPIB_Talk(Talk):

    def __init__(self, host, timeout=1,port=1234,gpibaddr=18):
        self.host = host
        self.timeout = timeout
        self.port=port
        self.gpibaddr=gpibaddr

        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM,
                                    socket.IPPROTO_TCP)
        self.socket.settimeout(self.timeout)

    def connect(self):
        self.socket.connect((self.host, self.port))
        self._send('++mode 1')
        self._send('++auto 1')
        self._send('++addr %i' % int(self.gpibaddr))

    def close(self):
        self.socket.close()

    def write(self, textMessage):
        self._send(textMessage)
        
    def ask(self, textMessage):
        self.write(textMessage)
        return self.read(1024*1024)
    
    def read(self, num_bytes=1024):
        self._send('++read eoi')
        return self._recv(num_bytes)
    def _send(self, value):
        encoded_value = ('%s\n' % value).encode('ascii')
        self.socket.send(encoded_value)

    def _recv(self, byte_num):
        value = self.socket.recv(byte_num)
        return value
##        try:
##            return value.decode('ascii')
##        except Exception as err:
##            return str(value)
class Raw_Talk(Talk):

    def __init__(self, host, timeout=1,port=9001):
        self.host = host
        self.timeout = timeout
        self.port=port
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM,
                                    socket.IPPROTO_TCP)
        self.socket.settimeout(self.timeout)

    def connect(self):
        self.socket.connect((self.host, self.port))

    def close(self):
        self.socket.close()

    def write(self, textMessage):
        self._send(textMessage)
        
    def ask(self, textMessage):
        self.write(textMessage)
        return self.read(1024*1024)
    def read(self, num_bytes=1024):
        return self._recv(num_bytes)
    def _send(self, value):
        encoded_value = ('%s\n' % value).encode('ascii')
        self.socket.send(encoded_value)
    def _recv(self, byte_num):
        value = self.socket.recv(byte_num)
        return value
##        try:
##            return value.decode('ascii')
##        except Exception as err:
##            return str(value)
class VXi11_Talk(Talk):

    def __init__(self, host, timeout=1,port=9001):
        self.host=host
        self.instr=None

    def connect(self):
        self.instr=vxi11.Instrument(self.host)

    def close(self):
        self.instr.close()

    def write(self, textMessage):
        self.instr.write(textMessage)
        
    def ask(self, textMessage):
        self.instr.write(textMessage)
        bytesarr=self.instr.read_raw(-1)
        return bytesarr
##        try:
##            return bytesarr.decode('utf-8').rstrip('\r\n')
##        except Exception as err:
##            return str(bytesarr)
        
##        return self.instr.ask(textMessage)

