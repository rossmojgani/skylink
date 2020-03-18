import socket

PORT = 4803

if __name__ == '__main__':
    # connect socket object and connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('', PORT))

    while True:
        try:
            from_server = client.recv(PORT)
            print("SERVER GOT: {}".format(from_server))
        except Exception as err:
            print(err)
