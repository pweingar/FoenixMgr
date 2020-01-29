import serial

class FoenixDebugPort:
    """Provide the conneciton to a C256 Foenix debug port."""
    connection = 0
    status0 = 0
    status1 = 0

    def open(self, port):
        """Open a connection to the C256 Foenix."""
        self.connection = serial.Serial(port=port,
            baudrate=6000000,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=60,
            write_timeout=60)
        try:
            self.connection.open()
        except:
            self.connection.close()
            self.connection.open()

    def is_open(self):
        return self.connection.is_open()

    def close(self):
        """Close the connection to the C256 Foenix."""
        self.connection.close()

    def enter_debug(self):
        """Send the command to make the C256 Foenix enter its debug mode."""
        self.transfer(0x80, 0, 0, 0)

    def exit_debug(self):
        """Send the command to make the C256 Foenix leave its debug mode.
        This will make the C256 reset.
        """
        self.transfer(0x81, 0, 0, 0)

    def erase_flash(self):
        """Send the command to have the C256 Foenix erase its flash memory."""
        self.transfer(0x11, 0, 0, 0)

    def get_revision(self):
        """Gets the revision code for the debug interface.
        RevB2's revision code is 0, RevC4A is 1."""
        self.transfer(0xFE, 0, 0, 0)
        return self.status1

    def program_flash(self, address):
        """Send the command to have the C256 Foenix reprogram its flash memory.
        Data to be written should already be in the C256's RAM at address."""
        self.transfer(0x10, address, 0, 0)

    def write_block(self, address, data):
        """Write a block of data to the specified starting address in the C256's memory."""
        self.transfer(0x01, address, data, 0)

    def read_block(self, address, length):
        """Read a block of data of the specified length from the specified starting address of the C256's memory."""
        return self.transfer(0x00, address, 0, length)

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

        command_bytes = command.to_bytes(1, 'big')
        address_bytes = address.to_bytes(3, 'big')
        length_bytes = length.to_bytes(2, 'big')

        header = bytearray(7)
        header[0] = 0x55
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

        lrc_bytes = lrc.to_bytes(1, 'big')

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
        while c != 0xAA:
            c = self.readbyte()

        # print('Got 0xAA')

        read_bytes = 0

        if c == 0xAA:
            self.status0 = self.readbyte()
            self.status1 = self.readbyte()

            if read_length > 0:
                read_bytes = self.connection.read(read_length)

            read_lrc = self.readbyte()

        # print("Status: {:X}, {:X}".format(self.status0, self.status1))
        
        return read_bytes
