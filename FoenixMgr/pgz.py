#
# Loader for PGZ files
#

import foenix_config
from pathlib import Path

class PGZBinFile:
    """Reads information from PGZ formated file"""
    address_size = 0
    data = 0
    handler = 0
    cpu = ""

    def __init__(self):
        config = foenix_config.FoenixConfig()
        self.cpu = config.cpu()
        pass

    def open(self, filename):
        self.data = Path(filename).read_bytes()

    def close(self):
        self.data = []

    def set_handler(self, proc):
        self.handler = proc

    def read_blocks(self):
        # Header is lower case z: address and size fields are four bytes long
        print("Initial {:x}".format(self.data[0]))

        if self.data[0] == 0x7a:
            self.address_size = 4
        elif self.data[0] == 0x5a:
            # Header is upper case Z: address and size fields are three bytes long
            self.address_size = 3
            print("Header Size 3")
        else:
            print("Error: bad PGZ file: {}.".format(self.data.hex()))
            exit(1)

        offset = 1
        while offset < len(self.data):
            (addr, block, offset) = self.__read_block(self.data, offset)
            if (len(block) == 0) and (addr > 0):
                # We have a start address block... register it with the Foenix so it gets called at reset
                if self.cpu == "65816":
                    print("CPU 65816")
                    if addr & 0xff0000 != 0:
                        # Startup code is not in bank 0, so we need a stub...
                        #   clc
                        #   xce
                        #   jml <address>
                        self.handler(0xff80, bytes([0x18, 0xfb, 0x5c, addr & 0xff, (addr >> 8) & 0xff, (addr >> 16) & 0xff]))
                        # Point the reset vector to our reset routine
                        self.handler(0xfffc, bytes([0x80, 0xff]))
                    else:
                        # Startup code is in bank 0, so we can just jump to it directly
                        # Point the reset vector to the start address
                        self.handler(0xfffc, bytes([addr & 0xff, (addr >> 8) & 0xff]))

                elif (self.cpu == "65c02") or (self.cpu == "65C02"):
                    print("CPU 65c02")
                    # Point the reset vector to our reset routine
                    # if using microkernel, this won't do anything
                    # but if we're not, it's nice
                    self.handler(0xfffc, bytes([addr & 0xff, (addr >> 8) & 0xff]))
                    # "CROSSDEV" springboard if we're using the microkernel
                    # and you have the crossdev tools installed
                    self.handler(0x0080, bytes([0x43,0x52,0x4f,0x53,0x53,0x44,0x45,0x56]))
                    self.handler(0x0088, bytes([addr & 0xff, (addr >> 8) & 0xff]))
                    # Pass 0 to the kernel args extlen, at least until someone implements argument passing
                    self.handler(0x00FA, bytes([0x00, 0x00]))
              
                elif self.cpu == "m68k":
                    print("CPU m68k")
                    # Point the reset vector to our reset routine
                    print("Starting address {:x}".format(addr))
                    self.handler(4, bytes([(addr>>24) & 0xff, (addr>>16) & 0xff, (addr>>8) & 0xff, addr & 0xff]))

            elif addr > 0:
                # JGA Support for large blocks
                block_size = 1024
                if len(block) > block_size:
                    #print("do block sizes =",block_size)
                    total_length = len(block)
                    chunk_offset = 0
                    while total_length > 0:
                        #print(chunk_offset, block_size)
                        self.handler(addr+chunk_offset, block[chunk_offset:chunk_offset+block_size])
                        total_length -= block_size
                        chunk_offset += block_size
                        if total_length < block_size:
                            block_size = total_length
                else:
                    self.handler(addr, block)

            else:
                return

    def __read_block(self, data, offset):
        # PGZ blocks have the format (each character is a byte):
        # A..AS..Sd...d, or
        # Where A..A is the destination address in little endian format
        #       S..S is the size of the block in bytes in little endian format
        #       d..d is the data block
        # The number of bytes in the address and size fields is determined by address_size
        addr = int.from_bytes(data[offset:offset+self.address_size], byteorder='little', signed=False)
        offset += self.address_size

        size = int.from_bytes(data[offset:offset+self.address_size], byteorder='little', signed=False)
        offset += self.address_size

        print(addr, size)

        if addr == 0:
            return (0, [], offset)

        block = data[offset:offset+size]
        return (addr, block, offset+size)
