import intelhex
import foenix
import configparser
import re
import sys
import argparse
import os

FLASH_SIZE = 524288     # Required size of flash file: 512 KB
CHUNK_SIZE = 4096       # Size of block of binary data to transfer

label_file = ""
to_send = ""
port = ""
start_address = ""
count = ""
label=""

def confirm(question):
    return input(question).lower().strip()[:1] == "y"

def revision(port):
    """Get the version code for the debug port."""
    c256 = foenix.FoenixDebugPort()
    try:
        c256.open(port)
        c256.enter_debug()
        try:
            data = c256.get_revision()
            return "%X" % data
        finally:
            c256.exit_debug()
    finally:
        c256.close()

def upload_binary(port, filename, address):
    """Upload a binary file into the C256 memory."""
    with open(filename, "rb") as f:
        c256 = foenix.FoenixDebugPort()
        try:
            c256.open(port)
            c256.enter_debug()
            try:
                current_addr = int(address, 16)
                block = f.read(CHUNK_SIZE)
                while block:
                    c256.write_block(current_addr, block)
                    current_addr += len(block)
                    block = f.read(CHUNK_SIZE)
            finally:
                c256.exit_debug()
        finally:
            c256.close()

def program_flash(port, filename, hex_address):
    """Program the flash memory using the contents of the C256's RAM."""

    base_address = int(hex_address, 16)
    address = base_address
    print("About to upload image to address 0x{:X}".format(address), flush=True)

    if os.path.getsize(filename) == FLASH_SIZE:
        if confirm("Are you sure you want to reprogram the flash memory? (y/n): "):
            with open(filename, "rb") as f:
                c256 = foenix.FoenixDebugPort()
                try:
                    c256.open(port)
                    c256.enter_debug()
                    try:
                        block = f.read(CHUNK_SIZE)
                        while block:
                            c256.write_block(address, block)
                            address += len(block)
                            block = f.read(CHUNK_SIZE)

                        print("Binary file uploaded...", flush=True)
                        c256.erase_flash()
                        print("Flash memory erased...", flush=True)
                        c256.program_flash(base_address)
                        print("Flash memory programmed...")
                    finally:
                        c256.exit_debug()
                finally:
                    c256.close()
    else:
        print("The provided flash file is not the right size.")

def dereference(port, file, label):
    """Get the address contained in the pointer with the label in the label file."""
    c256 = foenix.FoenixDebugPort()
    try:
        address = lookup(file, label)
        c256.open(port)
        c256.enter_debug()
        try:
            data = c256.read_block(int(address, 16), 3)
            deref = data[2] << 16 | data[1] << 8 | data[0]
            return "%X" % deref
        finally:
            c256.exit_debug()
    finally:
        c256.close()

def lookup(file, label):
    """Return the hex address linked to the passed label in the label file."""
    with open(file) as f:
        for line in f:
            match = re.match('^(\S+)\s*\=\s*\$(\S+)', line)
            if match:
                if match.group(1) == label:
                    return match.group(2)
        sys.stderr.write("Could not find a definition for that label.\n")
        sys.exit(2)

def display(base_address, data):
    """Write a block of data to the console in a nice, hexadecimal format."""

    text_buff = ""
    for i in range(0, len(data)):
        if (i % 16) == 0:
            if text_buff != "":
                sys.stdout.write(" {}\n".format(text_buff))
            text_buff = ""
            sys.stdout.write("{:06X}: ".format(base_address + i))
        elif (i % 8) == 0:
            sys.stdout.write(" ")
        sys.stdout.write("{:02X}".format(data[i]))

        b = bytearray(1)
        b[0] = data[i]
        if (b[0] & 0x80 == 0):
            c = b.decode('ascii')
            if c.isprintable():
                text_buff = text_buff + c
            else:
                text_buff = text_buff + "."
        else:
            text_buff = text_buff + "."
        
    sys.stdout.write(' {}\n'.format(text_buff))

def send(port, filename):
    """Send the data in the hex file 'filename' to the C256 on the given serial port."""
    infile = intelhex.HexFile()
    c256 = foenix.FoenixDebugPort()
    try:
        c256.open(port)
        infile.open(filename)
        try:
            infile.set_handler(lambda address, data: c256.write_block(address, bytes.fromhex(data)))
            c256.enter_debug()
            try:
                # Process the lines in the hex file
                infile.read_lines()
            finally:
                c256.exit_debug()
        finally:
            infile.close()
    finally:
        c256.close()

def get(port, address, length):
    """Read a block of data from the C256."""
    c256 = foenix.FoenixDebugPort()
    try:
        c256.open(port)
        c256.enter_debug()
        try:
            data = c256.read_block(int(address, 16), int(length, 16))

            display(int(address, 16), data)
        finally:
            c256.exit_debug()
    finally:
        c256.close()

config = configparser.ConfigParser()
config.read('c256.ini')

parser = argparse.ArgumentParser(description='Manage the C256 Foenix through its debug port.')
parser.add_argument("--port", dest="port", default=config['DEFAULT'].get('port', 'COM3'),
                    help="Specify the serial port to use to access the C256 debug port.")

parser.add_argument("--label-file", dest="label_file", default=config['DEFAULT'].get('labels', 'basic8'),
                    help="Specify the label file to use for dereference and lookup")

parser.add_argument("--count", dest="count", default="10", help="the number of bytes to read")

parser.add_argument("--dump", metavar="ADDRESS", dest="dump_address",
                    help="Read memory from the C256's memory and display it.")

parser.add_argument("--deref", metavar="LABEL", dest="deref_name",
                    help="Lookup the address stored at LABEL and display the memory there.")

parser.add_argument("--lookup", metavar="LABEL", dest="lookup_name",
                    help="Display the memory starting at the address indicated by the label.")

parser.add_argument("--revision", action="store_true", dest="revision",
                    help="Display the revision code of the debug interface.")  

parser.add_argument("--flash", metavar="BINARY FILE", dest="flash_file",
                    help="Attempt to reprogram the flash using the binary file provided.")

parser.add_argument("--binary", metavar="BINARY FILE", dest="binary_file",
                    help="Upload a binary file to the C256's RAM.")

parser.add_argument("--address", metavar="ADDRESS", dest="address",
                    default=config['DEFAULT'].get('flash_address', '380000'),
                    help="Provide the starting address of the memory block to use in flashing memory.")

parser.add_argument("--upload", metavar="HEX FILE", dest="hex_file",
                    help="Attempt to reprogram the flash using the binary file provided.")                    

options = parser.parse_args()

try:
    if options.port != "":
        if options.hex_file:
            send(options.port, options.upload_file)

        elif options.deref_name and options.label_file:
            address = dereference(options.port, options.label_file, options.deref_name)
            get(options.port, address, options.count)

        elif options.deref_name and options.label_file:
            address = lookup(options.label_file, options.deref_name)
            get(options.port, address, options.count)

        elif options.dump_address:
            get(options.port, options.dump_address, options.count)

        elif options.revision:
            rev = revision(options.port)
            print(rev)

        elif options.address and options.binary_file:
            upload_binary(options.port, options.binary_file, options.address)

        elif options.address and options.flash_file:
            program_flash(options.port, options.flash_file, options.address)

        else:
            parser.print_help()
    else:
        parser.print_help()
finally:
    print

