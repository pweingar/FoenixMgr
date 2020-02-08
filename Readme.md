# C256MGR: A command line tool for connecting to the C256 Foenix Debug Port

C256MGR can be used to send binary and Intel HEX files to the C256 or to read memory
from the board.
It is a python script that uses the debug port protocol to control the C256 remotely.
Currently, the debug port supports seven actions: stop the processor, restart the processor,
read memory, write memory,
erase the flash memory, program the flash memory,
and retrieve a version code.

## C256mgr.py Script

The core of the tool is the c256mgr Python script. It takes an `c256.ini` file with three initialization tags:

* `port`, which is the name of the serial port to use for connecting to the debug port
* `labels`, which is the path to the 64TASS LBL file for this project.
* `address`, which is the default address (in hex) for any binary transfers.

All three settings can be over-ridden by command line options.

## Command Line Arguments

To list the available serial ports on your computer:
`c256mgr --list-ports`

To get the revision code of the C256's debug port:
`c256mgr --port <port> --revision`

To send a hex file:
`c256mgr --port <port> --upload <hexfile>`

To send a binary file to a location in C256 RAM:
`c256mgr --port <port> --binary <binary file> --address <address in hex>`

To reflash the C256 flash memory (NOTE: the binary file must be 512KB in size, and the address
is used as a temporary location in C256 RAM to store the data to be flashed):
`c256mgr --port <port> --flash <binary file> --address <address in hex>`

To display memory:
`c256mgr --port <port> --dump <address in hex> --count <count of bytes in hex>`

If you have a 64TASS label file (*.lbl), you can provide that as an option
and display the contents of a memory location by its label:
`c256mgr --port <port> --label-file <label file> --lookup <label> --count <count of bytes in hex>`

If you have a 64TASS label file (*.lbl), you can provide that as an option
and display the contents of a memory location by deferencing the pointer
at a location in the label file:
`c256mgr --port <port> --label-file <label file> --deref <label> --count <count of bytes in hex>`

The count of bytes is optional and defaults to 16 ("10" in hex).


```
usage: c256mgr.py [-h] [--port PORT] [--label-file LABEL_FILE] [--count COUNT]
                  [--dump ADDRESS] [--deref LABEL] [--lookup LABEL]
                  [--revision] [--flash BINARY FILE] [--binary BINARY FILE]   
                  [--address ADDRESS] [--upload HEX_FILE]

Manage the C256 Foenix through its debug port.

optional arguments:
  -h, --help            show this help message and exit
  --port PORT           Specify the serial port to use to access the C256     
                        debug port.
  --list-ports          List available serial ports.
  --label-file LABEL_FILE
                        Specify the label file to use for dereference and
                        lookup
  --count COUNT         the number of bytes to read
  --dump ADDRESS        Read memory from the C256's memory and display it.
  --deref LABEL         Lookup the address stored at LABEL and display the
                        memory there.
  --lookup LABEL        Display the memory starting at the address indicated
                        by the label.
  --revision            Display the revision code of the debug interface.
  --flash BINARY FILE   Attempt to reprogram the flash using the binary file
                        provided.
  --binary BINARY FILE  Upload a binary file to the C256's RAM.
  --address ADDRESS     Provide the starting address of the memory block to
                        use in flashing memory.
  --upload HEX_FILE     Attempt to reprogram the flash using the binary file
                        provided.
```

## Batch Files

This package includes four DOS batch files to help automate using the tool:

* `dump`: takes an address (in hex) and an optional byte count (also in hex)
  and dumps memory at that address to the screen: `dump 010000 20`.

* `run`: take an Intel HEX file and downloads it into the C256's memory.
  If the HEX file includes a block of memory covering the processor's RESET
  hardware vector, this will also cause the program in the HEX file to run
  starting with the RESET handler provided: `run basic816.hex`.

* `lookup`: takes a label and an optional byte count (in hex). The label
  is used to search the LBL file of the project for an address. If the
  address is found, the memory starting at that address will be dumped
  to the screen: `lookup COUNTER`.

* `deref`: takes a label and an optional byte count (in hex). The label
  is used to search the LBL file of the project for an address. If the
  address is found, the three bytes starting at that address will be read
  from the C256 memory and used as the starting address to dump memory to
  the screen: `deref INDEX 30`.

* `flash`: takes a binary file containing a flash image and an optional
  address. The binary image must be exactly 512KB and is copied raw to
  the address provided (or the default address from the INI file). The
  existing flash data is erased and replaced by the data in the BIN file. 
  The script will ask for confirmation before begining the process.
