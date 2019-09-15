import intelhex
import foenix
import configparser
import re
import sys
from optparse import OptionParser

label_file = ""
to_send = ""
port = ""
start_address = ""
count = ""
label=""

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

parser = OptionParser()
parser.add_option("-s", "--send", dest="to_send", help="Intel HEX file to send.")
parser.add_option("-p", "--port", dest="port", default=config['DEFAULT'].get('port', 'COM9'), help="communication port for the C256")
parser.add_option("-a", "--address", dest="start_address", type="string", help="starting address for memory to fetch (in hex)")
parser.add_option("-v", "--variable", dest="label", type="string", help="label to look up for the starting address")
parser.add_option("-d", "--reference", dest="pointer", type="string", help="label for a pointer to lookup for the starting address")
parser.add_option("-c", "--count", dest="count", default="10", type="string", help="number of bytes to read (in hex)")
parser.add_option("-l", "--label-file", dest="label_file", default=config['DEFAULT'].get('labels', 'basic816.lbl'), type="string", help="the name of the file containing the address labels")

(options, args) = parser.parse_args()

try:
    if options.port != "":
        if options.to_send:
            send(options.port, options.to_send)
        elif options.pointer and options.label_file:
            address = dereference(options.port, options.label_file, options.pointer)
            get(options.port, address, options.count)
        elif options.label and options.label_file:
            address = lookup(options.label_file, options.label)
            get(options.port, address, options.count)
        elif options.start_address:
            get(options.port, options.start_address, options.count)
        else:
            parser.print_help()
    else:
        parser.print_help()
finally:
    print
# except Exception as e:
#     sys.stderr.write("\nCaught an exception: {}".format(e))
#     sys.exit(2)
