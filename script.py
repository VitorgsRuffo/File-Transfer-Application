import socket
import tqdm
import os
import time

separator = "<SEP>"

class FileTransferer:
    def __init__(self, ip: str, port: int):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(100)
        self.client_socket = None

    def __menu(self):
        print("---------------------------")
        print("    VW File Transferer\n")
        print("1 - Send.")
        print("2 - Receive.")
        print("3 - Exit.")
        print("---------------------------")

    def send_file(self):

        ip = input("Enter the IP you want to send a file to:")
        port = int(input("Enter the ip's port:"))

        file_path = input("Enter the file path:")
        file_size = os.path.getsize(file_path)
        packet_size = int(input("Enter the packet size (100, 500, 1000 or 1500): "))

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"Establishing connection with {ip}:{port}...\n")
        self.client_socket.connect((ip, port))

        message = self.client_socket.recv(1024).decode('utf-8')
        if message:
            print(message)
        else:
            self.client_socket.close()
            print("Failed to connect.\nExiting...\n")
            return

        # Sending meta-data
        self.client_socket.send(f"{file_path}{separator}{file_size}{separator}{packet_size}".encode())
        msg = self.client_socket.recv(1024).decode()


        # time at which upload started.
        trasmission_start = time.time()
        
        progress = tqdm.tqdm(range(file_size), f"Sending {file_path}", unit="B", unit_scale=True, unit_divisor=packet_size)

        packets_sent = 0

        with open(file_path, "rb") as file:
            while True:
                
                bytes_read = file.read(packet_size)
                if not bytes_read:
                    break
                
                self.client_socket.sendall(bytes_read)
                msg = self.client_socket.recv(1024).decode()
                packets_sent+=1
                progress.update(bytes_read)

        
        transmission_time = time.time() - trasmission_start
        time.sleep(1)
        print("File sent successfully.")
        
        up_speed = (file_size * 8) / transmission_time
        report = "File transfer report\n--------------------\n" + \
                 f"File size: {file_size} bytes;\nPackets: {packets_sent};" + \
                 f"\nUpload speed: {up_speed} bps.\n--------------------\n"
        print(report)

        self.client_socket.close()
        self.client_socket = None
    

    def receive_file(self):

        print("Waiting for a connection...")
        while True:
            connection, addr = self.server_socket.accept()

            print("{}:{} wants to connect.".format(addr[0], addr[1]))
            print("Do you accept ? (y/n)")
            allow = input()

            if (allow == "n") | (allow == "N"):
                connection.shutdown(socket.SHUT_RD)
                connection.close()
            else:
                break

        print("{}:{} just to connected!".format(addr[0], addr[1]))

        ip = self.server_socket.getsockname()[0]
        connection.send(str("You connected to {}.\n".format(ip)).encode('utf-8'))


        # receiving file to be received meta-data...
        meta_data = connection.recv(1024).decode()
        file_path, file_size, packet_size = meta_data.split(separator)
        file_name = os.path.basename(file_path) #removing file path
        file_size = int(file_size)
        packet_size = int(packet_size)
        packets_received = 0
        connection.send("Metadata received successfully.".encode())

        # time at which dowload started.
        trasmission_start = time.time()

        progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=packet_size)

        with open(file_name, "wb") as file:
            while True:

                bytes_read = connection.recv(packet_size)
                if not bytes_read:    
                    break
                packets_received+=1
                file.write(bytes_read)
                connection.send("Packet received successfully.".encode())
                progress.update(bytes_read)

        transmission_time = time.time() - trasmission_start

        print("File received successfully.")
        
        dw_speed = (file_size * 8) / transmission_time
        report = "File transfer report\n--------------------\n" + \
                 f"File size: {file_size} bytes;\nPackets: {packets_received};" + \
                 f"\nDownload speed: {dw_speed} bps.\n--------------------\n"
        print(report)

        connection.close()


    def run(self):
        while True:
            self.__menu()
            option = int(input())

            if option == 1:
                self.send_file()
            elif option == 2:
                self.receive_file()
            elif option == 3:
                print("Exiting...")
                return
            else:
                print("Invalid option. Please try again.")


print("\n\nWelcome to VW file transfering app!\n")
ip = input("Enter you computer's IP address:")
port = int(input("Enter the port in which the application will run:"))
chat = FileTransferer(ip, port)
chat.run()
