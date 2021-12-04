import socket
import os
import time

separator = "<SEP>"

class FileTransferer:
    def __init__(self, ip: str, port: int):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((ip, port))
        self.client_socket = None

    def __menu(self):
        print("---------------------------")
        print("    VW File Transferer\n")
        print("1 - Send.")
        print("2 - Receive.")
        print("3 - Exit.")
        print("---------------------------")

    def secure_sendto(self, bytes, bytesAmount, address):
        while True:
            self.client_socket.sendto(bytes, address)
            try:
                msg, _ = self.client_socket.recvfrom(1024)
            except:
                continue 
            msg = msg.decode()
            #print("certo")
            if msg == "ok":
                break

    def secure_recvfrom(self, bytesAmount, packets_received, expected_packets):
        while True:
            #if packets_received > 90:
            #    input()
            try:
                bytes_read, _ = self.server_socket.recvfrom(bytesAmount)
            except:
                continue            
            if (len(bytes_read) < bytesAmount) & ((packets_received+1) < expected_packets):
                #print("notok")
                self.server_socket.sendto("notok".encode(), _)
            else:
                #print("ok")
                self.server_socket.sendto("ok".encode(), _)
                break
        return bytes_read
    
    def send_file(self):

        ip = input("Enter the IP you want to send a file to:")
        port = int(input("Enter the ip's port:"))

        file_path = input("Enter the file path:")
        file_size = os.path.getsize(file_path)
        packet_size = int(input("Enter the packet size (500, 1000 or 1500): "))

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Sending meta-data
        self.client_socket.sendto(
            f"{file_path}{separator}{file_size}{separator}{packet_size}".encode(), 
            (ip, port))

        # receiving confirmation message...
        self.client_socket.recvfrom(1024)

        with open(file_path, "rb") as file:
            buffer = file.read()

        self.client_socket.settimeout(0.2)

        packets_sent = 0
        start = 0
        end = packet_size
        
        bytes_read = buffer[start:end]
        print("Sending...")
        trasmission_start = time.time() # time at which upload started.
        while bytes_read:
            self.secure_sendto(bytes_read, packet_size, (ip, port))
            packets_sent+=1
            #print(packets_sent)
            start = end
            end += packet_size
            bytes_read = buffer[start:end]

        transmission_time = time.time() - trasmission_start
        print("File sent successfully.")

        self.client_socket.close()
        self.client_socket = None

        # Tratamento de envio muito rápido de arquivo
        if transmission_time == 0:
            transmission_time = 1
        
        up_speed = round((file_size * 8) / transmission_time, 2)
        report = "\nFile transfer report\n--------------------\n" + \
                 f"File size: {file_size} bytes;\nPackets: {packets_sent};" + \
                 f"\nUpload speed: {up_speed} bps.\n--------------------\n"
        print(report)

        
    

    def receive_file(self):
    
        print("Waiting for a connection...")

        # receiving file to be received meta-data...
        while True:
            try:
                meta_data, address = self.server_socket.recvfrom(1024)
                meta_data = meta_data.decode()
                break
            except:
                pass
        file_path, file_size, packet_size = meta_data.split(separator)
        file_name = os.path.basename(file_path) #removing file path
        file_size = int(file_size)
        packet_size = int(packet_size)
        packets_received = 0
        expected_packets = file_size // packet_size
        if file_size % packet_size > 0:
            expected_packets+=1
        self.server_socket.sendto("Ok".encode(), address)

        buffer = b""
        
        self.server_socket.settimeout(0.2)

        print("Receiving...")        
        trasmission_start = time.time() # time at which dowload started.
        
        bytes_read = b""
        
        #self.secure_recvfrom(packet_size, packets_received, expected_packets)
        #while (packet_size*packets_received) < file_size:
        #    packets_received+=1
        #    print(packets_received)
        #    buffer += bytes_read
        #    if (packet_size*packets_received) < file_size:
        #        self.secure_recvfrom(packet_size, packets_received, expected_packets)
        
        #print(expected_packets)
        while (packet_size*packets_received) < file_size:
            bytes_read = self.secure_recvfrom(packet_size, packets_received, expected_packets)
            packets_received+=1
            #print(packets_received)
            #print(f"1:{packet_size*packets_received} 2:{file_size}")
            #time.sleep(0.000999) 1000
            #time.sleep(0.01) 1500
            buffer += bytes_read
            

        transmission_time = time.time() - trasmission_start
        print("File received successfully.")

        with open(file_name, "wb") as file:
            file.write(buffer)

        # Tratamento de envio muito rápido de arquivo
        if transmission_time == 0:
            transmission_time = 1
        
        dw_speed = round((file_size * 8) / transmission_time, 2)
        report = "File transfer report\n--------------------\n" + \
                 f"File size: {file_size} bytes;\nPackets: {packets_received};" + \
                 f"\nDownload speed: {dw_speed} bps.\n--------------------\n"
        print(report)
            
        self.server_socket.settimeout(None)


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