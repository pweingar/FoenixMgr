from abc import ABC, abstractmethod
import serial
import socket
import constants

class FoenixDebugPort:
    """Provide the connection to a C256 Foenix debug port."""
    connection = None
    status0 = 0
    status1 = 0

    def open(self, port):
        """Open a connection to the C256 Foenix."""
        if ':' in port:
            # A pretty weak test, looking for something like '192.168.1.114:2560'
            self.connection = SocketFoenixConnection()
        else:
            # Otherwise assume it's a serial connection
            self.connection = SerialFoenixConnection()

        self.connection.open(port=port)

    def is_open(self):
        return self.connection.is_open()

    def close(self):
        """Close the connection to the C256 Foenix."""
        self.connection.close()

    def enter_debug(self):
        """Send the command to make the C256 Foenix enter its debug mode."""
        self.transfer(constants.CMD_ENTER_DEBUG, 0, 0, 0)

    def exit_debug(self):
        """Send the command to make the C256 Foenix leave its debug mode.
        This will make the C256 reset.
        """
        self.transfer(constants.CMD_EXIT_DEBUG, 0, 0, 0)

    def erase_flash(self):
        """Send the command to have the C256 Foenix erase its flash memory."""
        self.transfer(constants.CMD_ERASE_FLASH, 0, 0, 0)

    def get_revision(self):
        """Gets the revision code for the debug interface.
        RevB2's revision code is 0, RevC4A is 1."""
        self.transfer(constants.CMD_REVISION, 0, 0, 0)
        return self.status1

    def program_flash(self, address):
        """Send the command to have the C256 Foenix reprogram its flash memory.
        Data to be written should already be in the C256's RAM at address."""
        self.transfer(constants.CMD_PROGRAM_FLASH, address, 0, 0)

    def write_block(self, address, data):
        """Write a block of data to the specified starting address in the C256's memory."""
        self.transfer(constants.CMD_WRITE_MEM, address, data, 0)

    def read_block(self, address, length):
        """Read a block of data of the specified length from the specified starting address of the C256's memory."""
        return self.transfer(constants.CMD_READ_MEM, address, 0, length)

    def readbyte(self):
        b = self.connection.read(1)
        return b[0]

    def transfer(self, command, address, data, read_length):
        """Send a command to the C256 Foenix"""

        self.status0 = 0
        self.status1 = 0
        lrc = 0
        length = 0
        if data == 0:
            length = read_length
        else:
            length = len(data)

        # if command == 0x80:
        #     print('Switching to debug mode')
        # elif command == 0x81:
        #     print('Resetting')
        # else:
        #     print('Writing data of length {:X} to {:X}'.format(length, address))        

        command_bytes = command.to_bytes(1, byteorder='big')
        address_bytes = address.to_bytes(3, byteorder='big')
        length_bytes = length.to_bytes(2, byteorder='big')

        header = bytearray(7)
        header[0] = constants.REQUEST_SYNC_BYTE
        header[1] = command_bytes[0]
        header[2] = address_bytes[0]
        header[3] = address_bytes[1]
        header[4] = address_bytes[2]
        header[5] = length_bytes[0]
        header[6] = length_bytes[1]

        for i in range(0, 6):
            lrc = lrc ^ header[i]

        if data:
            for i in range(0, length):
                lrc = lrc ^ data[i]

        lrc_bytes = lrc.to_bytes(1, byteorder='big')

        if data:
            packet = header + data + lrc_bytes
            written = self.connection.write(packet)
            if written != len(packet):
                raise Exception("Could not write packet correctly.")
        else:
            packet = header + lrc_bytes
            written = self.connection.write(packet)
            if written != len(packet):
                raise Exception("Could not write packet correctly.")            
        # print('Sent [{}]'.format(packet.hex()))

        c = 0
        while c != constants.RESPONSE_SYNC_BYTE:
            c = self.readbyte()

        # print('Got 0xAA')

        read_bytes = 0

        if c == constants.RESPONSE_SYNC_BYTE:

            self.status0 = self.readbyte()
            self.status1 = self.readbyte()

            if read_length > 0:
                read_bytes = self.connection.read(read_length)

            read_lrc = self.readbyte()

        # print("Status: {:X}, {:X}".format(self.status0, self.status1))
        
        return read_bytes


class FoenixConnection(ABC):
    @abstractmethod
    def open(self, port):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def is_open(self):
        pass

    @abstractmethod
    def read(self, num_bytes):
        pass

    @abstractmethod
    def write(self, data):
        pass


class SerialFoenixConnection(FoenixConnection):
    """ Connects to Foenix via local serial port """
    serial_port = None

    def open(self, port):
        self.serial_port = serial.Serial(port=port,
            baudrate=6000000,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=60,
            write_timeout=60)
        try:
            self.serial_port.open()
        except:
            self.serial_port.close()
            self.serial_port.open()

    def close(self):
        self.serial_port.close()

    def is_open(self):
        return self.serial_port.is_open()

    def read(self, num_bytes):
        return self.serial_port.read(num_bytes)

    def write(self, data):
        return self.serial_port.write(data)


class SocketFoenixConnection(FoenixConnection):
    """ Connects to Foenix via TCP-serial bridge """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPv4, SOCK_STREAM = TCP socket
    _is_open = False

    def open(self, port):
        parsed_host_port = port.split(":")
        tcp_host = parsed_host_port[0]
        tcp_port = int(parsed_host_port[1]) if len(parsed_host_port) > 0 else 2560

        print("Connecting to {}:{}".format(tcp_host, tcp_port))
        self.tcp_socket.connect(tuple([tcp_host, tcp_port]))
        print("Connected")
        self._is_open = True

    def close(self):
        self.tcp_socket.close()
        self._is_open = False

    def is_open(self):
        return self._is_open

    def read(self, num_bytes):
        print("Reading {} bytes".format(num_bytes))
        bytes_read = self.tcp_socket.recv(num_bytes)
        print("Got bytes: {}".format(bytes_read))
        return bytes_read

    def write(self, data):
        print("Writing bytes: {}".format(data))
        self.tcp_socket.sendall(data)
        print("Bytes written")
        return len(data)


class FoenixTcpBridge():
    """ Listens on a TCP socket and relays communications to the Foenix serial debug port """
    def __init__(self, tcp_host, tcp_port, serial_port):
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.serial_port = serial_port

    def recv_bytes(self, num_bytes):
        print("Reading until we receive {} bytes from TCP client".format(num_bytes))
        total_bytes_received = self.tcp_connection.recv(num_bytes)
        if not total_bytes_received:
            # Client hung up
            return total_bytes_received
        total_bytes_received = bytearray(total_bytes_received)
        print("Read {} bytes".format(len(total_bytes_received)))
        while len(total_bytes_received) < num_bytes:
            bytes_received = self.tcp_connection.recv(num_bytes - len(total_bytes_received))
            print("Read {} bytes".format(len(bytes_received)))
            total_bytes_received.extend(bytes_received)

        print("Limit of {} bytes reached for this read".format(len(total_bytes_received)))
        return bytes(total_bytes_received)


    def listen(self):
        """ Listen for TCP socket connections and relay messages to Foenix via serial port """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # AF_INET=IPv4, SOCK_STREAM=TCP
            while True:
                s.bind((self.tcp_host, self.tcp_port))
                s.listen()
                print("Listening for connections to {} on port {}".format(self.tcp_host, self.tcp_port))

                self.tcp_connection, tcp_address = s.accept()
                print("Received TCP socket connection from {}".format(tcp_address))
                with self.tcp_connection:
                    print("Initiating connection to Foenix debug port on {}".format(self.serial_port))
                    with serial.Serial(port=self.serial_port, baudrate=6000000, timeout=60,
                                       write_timeout=60) as serial_connection:
                        print("Connected to Foenix debug port")
                        while True:
                            # First get the 7-byte request header
                            print("Waiting for request from TCP client")

                            header = self.recv_bytes(7)
                            if not header:
                                print("Connection from {} closed".format(tcp_address))
                                break
                            print("Got 7-byte header from TCP client: {}".format(header))
                            print("  Sync byte: 0x{:02x}".format(header[0]))
                            print("  Command: 0x{:02x}".format(header[1]))
                            print("  Address: 0x{:02x} 0x{:02x} 0x{:02x}".format(header[2], header[3], header[4]))
                            print("  Data length: 0x{:02x} 0x{:02x}".format(header[5], header[6]))

                            command = header[1]

                            # The data size comes from bytes 5 and 6 in the header
                            data_length = int.from_bytes(header[5:7], byteorder="big")
                            print("    - Data length converted to int is {}".format(data_length))

                            # The data payload only comes along with a write command
                            data = None
                            if command == constants.CMD_WRITE_MEM:
                                print("Reading data payload from TCP client since we received a write memory command")
                                data = self.recv_bytes(data_length)

                            # The LRC byte is required and denotes the end of the request
                            print("Reading LRC checksum byte from TCP client")
                            request_lrc_byte = self.recv_bytes(1)
                            print("  LRC checksum: 0x{:02x}".format(request_lrc_byte[0]))
                            print("Request from TCP client is complete")

                            # TCP request is now complete, time to pass along to Foenix
                            bytes_to_write = bytearray(header)
                            if data is not None:
                                bytes_to_write.extend(data)
                            bytes_to_write.extend(request_lrc_byte)
                            print("Sending request to Foenix serial port: {}".format(bytes_to_write))
                            num_bytes_written = serial_connection.write(bytes_to_write)
                            print("Sent {} bytes".format(num_bytes_written))

                            # Probably should handle this situation a bit more elegantly
                            if num_bytes_written != len(bytes_to_write):
                                raise Exception("Serial port error - tried writing {} bytes, was only able to write {}"
                                    .format(len(bytes_to_write), num_bytes_written))

                            # Read until we get the start of the response
                            # TODO: do we really need to read more than 1 byte here?
                            print("Waiting for response from Foenix debug port")
                            response_sync_byte = serial_connection.read(1)
                            print("  Got response sync byte: {}".format(response_sync_byte))

                            # Next two bytes are the status bytes
                            response_status_bytes = serial_connection.read(2)
                            print("  Got status bytes: {}".format(response_status_bytes))

                            # Read the data payload if requested
                            response_data = None
                            if command == constants.CMD_READ_MEM and data_length > 0:
                                response_data = self.connection.read(data_length)
                                print("  Got response data payload: {}".format(response_data))

                            response_lrc_byte = serial_connection.read(1)
                            print("  Got response LRC checksum byte: {}".format(response_lrc_byte))

                            # Construct the response
                            print("Building the TCP client response from Foenix reponse")
                            response = bytearray(response_sync_byte)
                            print("Added response sync byte: {}".format(response))
                            response.extend(response_status_bytes)
                            print("Added status bytes: {}".format(response))
                            if response_data is not None:
                                response.extend(response_data)
                                print("Added data payload: {}".format(response))
                            response.extend(response_lrc_byte)
                            print("Added LRC checksum byte: {}".format(response))

                            # Return the response back to the TCP client
                            print("Sending response back to TCP client")
                            self.tcp_connection.sendall(response)
                            print("Response sent")
