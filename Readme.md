# C256MGR: A command line tool for connecting to the C256 Foenix Debug Port

C256MGR can be used to send Intel HEX files to the C256 or to read memory from the board.
It is a python script that uses the debug port protocol to control the C256 remotely.
Currently, the debug port only supports four actions: stop the processor, restart the processor,
read memory, and write memory.

## C256mgr.py Script

The core of the tool is the c256mgr Python script. It takes an `c256.ini` file, that provides
two initialization tags: port, which is the name of the serial port to use for connecting
to the debug port, and labels, which is the path to the 64TASS LBL file for this project.
Both settings can be over-ridden by command line options.

To send a hex file:
`c256mgr -p <port> -s <hexfile>`

To display memory:
`c256mgr -p <port> -a <address in hex> -c <count of bytes in hex>`

If you have a 64TASS label file (*.lbl), you can provide that as an option
and display the contents of a memory location by its label:
`c256mgr -p <port> -l <label file> -v <label> -c <count of bytes in hex>`

If you have a 64TASS label file (*.lbl), you can provide that as an option
and display the contents of a memory location by deferencing the pointer
at a location in the label file:
`c256mgr -p <port> -l <label file> -d <label> -c <count of bytes in hex>`

The count of bytes is optional and defaults to 16.

## Batch Files

This package includes four DOS batch files to help automate using the tool:

DUMP: takes an address (in hex) and an optional byte count (also in hex) and dumps
memory at that address to the screen: `dump 010000 20`.

RUN: take an Intel HEX file and downloads it into the C256's memory. If the HEX file
includes a block of memory covering the processor's RESET hardware vector, this will
also cause the program in the HEX file to run starting with the RESET handler provided: `run basic816.hex`.

LOOKUP: takes a label and an optional byte count (in hex). The label is used to search
the LBL file of the project for an address. If the address is found, the memory starting
at that address will be dumped to the screen: `lookup COUNTER`.

DEREF: takes a label and an optional byte count (in hex). The label is used to search
the LBL file of the project for an address. If the address is found, the three bytes starting
at that address will be read from the C256 memory and used as the starting address to dump
memory to the screen: `deref INDEX 30`.

```
Usage: c256mgr.py [options]

Options:
  -h, --help            show this help message and exit
  -s TO_SEND, --send=TO_SEND
                        Intel HEX file to send.
  -p PORT, --port=PORT  communication port for the C256
  -a START_ADDRESS, --address=START_ADDRESS
                        starting address for memory to fetch (in hex)
  -v LABEL, --variable=LABEL
                        label to look up for the starting address
  -d LABEL, --reference=LABEL
                        label of a pointer to look up and dereference for the starting address
  -c COUNT, --count=COUNT
                        number of bytes to read (in hex)
  -l LABEL_FILE, --label-file=LABEL_FILE
                        the name of the file containing the address labels
```