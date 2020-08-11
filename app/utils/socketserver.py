import socket
import threading


class SocketServer(object):
    # Here will be the instance stored.
    __instance = None
    __conn = None
    __address = None

    __PORT = 19245

    def __init__(self):
        """ Virtually private constructor. """
        if self.__instance is None:
            self.__instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__instance.bind(('', self.__PORT))
            self.__instance.listen(5)
            print('建立 Socket 連線 ...')
            while True:
                self.__conn, self.__address = self.__instance.accept()
                threading._start_new_thread(handle, (self.__conn, self.__address))        #5、多執行緒處理客戶端訊息
                print(f"有新的連線來自: {self.__address}")

        def handle(client, addr):
            while True:
                print(f"有新的連線來自: {self.__address}")
                try:
                    text = client.recv(1024)
                    if not text:
                        client.close()
                    client.send(text)
                    print(addr[0],addr[1],'>>',text.decode())
                except:
                    print(addr[0],addr[1],'>>say goodby')
                    break

    @staticmethod
    def getInstance():
        """ Static access method. """
        if SocketServer.__instance is None:
            SocketServer()
            print('Socket 不存在，重新呼叫 ...')
        return SocketServer.__instance

if __name__ == '__main__':
    pass