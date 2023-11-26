# FoenixMgr: A command line tool for connecting to the Foenix debug port

FoenixMgr can be used to send binary and Intel HEX files to the Foenix or to read memory from the board. It is a python script that uses the debug port protocol to control the Foenix remotely. Currently, the debug port supports seven actions: stop the processor, restart the processor, read memory, write memory, erase the flash memory, program the flash memory, and retrieve a version code.

## Installation

NOTE: To run FoenixMgr, you will need Python3 installed on your system. There are a couple of required libraries listed in `requirements.txt`. You can use Python's `pip` utility to install the required packages automatically using the command line:

`pip install -r requirements.txt`

FoenixMgr has been recoded from the C256Mgr original to be more flexible. One of the new features is that only one copy of the scripts are necessary on the system, where the old C256Mgr really needed to be included with every project. To get this to work, once you have copied the FoenixMgr project to your system, you will need to define an environment variable `FOENIXMGR`, which is the directory that contains this repository. The batch file tools will look for the Python scripts using that variable, and the Python scripts will look for the configuration file in that folder as well (although it can look for the configuration file in other folders as well... see below).

## Configuration File

The core of the tool is the FoenixMgr Python script. It takes an `foenixmgr.ini` file with three initialization tags:

* `port`, which is the name of the serial port to use for connecting to the debug port
* `labels`, which is the path to the 64TASS LBL file for this project.
* `address`, which is the default address (in hex) for any binary transfers.
* `flash_size`, which is the required size of a flash binary file
* `chunk_size`, which is the size of the data packet to send over the debug port
* `data_rate`, which is the bit rate to use in communicating over the debug port
* `timeout`, which is the amount of time (in seconds) to allow before timing out the serial connection
* `cpu`, which is the name of the CPU on the target Foenix (currently: 65c02, 65816, m68k). This setting is used by the `run-pgz` option to determine what kind of bootstrap loader needs to be inserted to actually start the executable.

The setting `port`, `labels`, and `address` can be over-ridden by command line options.

FoenixMgr will look for the configuration file in your current directory, in your user home directory, or in the directory indicated by the environment variable `FOENIXMGR`.

## Target Machine Names

As the range of Foenix machines increases, this script is becoming more and more unwieldy. To try to help manage this, a new target option has been added. This option will be used to specify machine-specific configurations in such a way that a user can use the script with multiple machines without having to edit the configuration file every time. Currently, it is only being used for the flash sector option, and the only machine names supported are `f256jr`, `f256jr`, and `fnx1591`... the only machines that support this capability. As an example of its use, the following command will send the file `dos1581.bin` to the FNX1591 drive on COM6, and upload it to flash sector 1 (strictly speaking, that is not flash sector 6, but the 6th 32 KB slot in the FNX1591's flash memory).

```
python FoenixMgr\fnxmgr.py --port COM6 --target fnx1591 --flash-sector 1 --flash dos1581.bin
```

## Command Line Arguments

To list the available serial ports on your computer:
`FoenixMgr/fnxmgr --list-ports`

To get the revision code of the Foenix's debug port:
`FoenixMgr/fnxmgr --port <port> --revision`

To send a hex file:
`FoenixMgr/fnxmgr --port <port> --upload <hexfile>`

To send a binary file to a location in Foenix RAM:
`FoenixMgr/fnxmgr --port <port> --binary <binary file> --address <address in hex>`

To reflash the Foenix flash memory (NOTE: the binary file must be exactly `flash_size` long, and the address is used as a temporary location in Foenix RAM to store the data to be flashed):
`FoenixMgr/fnxmgr --port <port> --flash <binary file> --address <address in hex>`

To reflash a particular 8KB sector of flash memory (currently F256jr, F256k, and FNX1591 only):
`FoenixMgr/fnxmgr --target <machine name> --port <port> --flash-sector=01 --flash <binary file>`

To set a boot source (F256jr RevA boards and F256k):
`FoenixMgr/fnxmgr --port <port> --boot=RAM|FLASH`

To display memory:
`FoenixMgr/fnxmgr --port <port> --dump <address in hex> --count <count of bytes in hex>`

For the F256jr and F256k only, if you would like to stop the CPU from processing instructions, you can use the `stop` command:
`FoenixMgr/fnxmgr --port <port> --stop`
Once that is issued, the machine will halt, a special indicator file called `f256.stp` will be created in your current directory, and the other FoenixMgr commands can be executed without resetting the CPU. To restart the CPU, you can issue the `start` command, which will start the machine back up but without resetting the processor: `FoenixMgr/fnxmgr --port <port> --start` The indicator file created by `stop` will be removed by `start`.

If you have a 64TASS label file (`*.lbl`), you can provide that as an option and display the contents of a memory location by its label:
`FoenixMgr/fnxmgr --port <port> --label-file <label file> --lookup <label> --count <count of bytes in hex>`

If you have a 64TASS label file (`*.lbl`), you can provide that as an option and display the contents of a memory location by deferencing the pointer at a location in the label file:
`FoenixMgr/fnxmgr --port <port> --label-file <label file> --deref <label> --count <count of bytes in hex>`

The count of bytes is optional and defaults to 16 ("10" in hex).

```
usage: FoenixMgr.zip [-h] [--port PORT] [--list-ports] [--label-file LABEL_FILE] [--count COUNT] [--dump ADDRESS]
                     [--deref LABEL] [--lookup LABEL] [--revision] [--flash BINARY FILE] [--flash-sector NUMBER]
                     [--flash-bulk CSV FILE] [--binary BINARY FILE] [--copy COPY FILE] [--address ADDRESS]
                     [--upload HEX FILE] [--upload-wdc BINARY FILE] [--run-pgz PGZ FILE] [--run-pgx PGX FILE]
                     [--upload-srec SREC FILE] [--boot STRING] [--target STRING] [--tcp-bridge HOST:PORT] [--stop]
                     [--start]

Manage the C256 Foenix through its debug port.

options:
  -h, --help            show this help message and exit
  --port PORT           Specify the serial port to use to access the C256 debug port.
  --list-ports          List available serial ports.
  --label-file LABEL_FILE
                        Specify the label file to use for dereference and lookup
  --count COUNT         the number of bytes to read
  --dump ADDRESS        Read memory from the C256's memory and display it.
  --deref LABEL         Lookup the address stored at LABEL and display the memory there.
  --lookup LABEL        Display the memory starting at the address indicated by the label.
  --revision            Display the revision code of the debug interface.
  --flash BINARY FILE   Attempt to reprogram the flash using the binary file provided.
  --flash-sector NUMBER
                        Sector number of the 8KB sector of flash to program.
  --flash-bulk CSV FILE
                        Program multiple flash sectors based on a CSV file
  --binary BINARY FILE  Upload a binary file to the C256's RAM.
  --copy COPY FILE      Copy a file to F256jr SDCARD.
  --address ADDRESS     Provide the starting address of the memory block to use in flashing memory.
  --upload HEX FILE     Upload an Intel HEX file.
  --upload-wdc BINARY FILE
                        Upload a WDCTools binary hex file. (WDCLN.EXE -HZ)
  --run-pgz PGZ FILE    Upload and run a PGZ binary file.
  --run-pgx PGX FILE    Upload and run a PGX binary file.
  --upload-srec SREC FILE
                        Upload a Motorola SREC hex file.
  --boot STRING         For F256k: set boot source: RAM or FLASH
  --target STRING       Set the target machine
  --tcp-bridge HOST:PORT
                        Setup a TCP-serial bridge, listening on HOST:PORT and relaying messages to the Foenix via the
                        configured serial port
  --stop                Stop the CPU from processing instructions (F256 only).
  --start               Restart the CPU after a STOP (F256 only).
  --quiet               Suppress some printed messages.
```

## Batch Files

This package includes four DOS batch files and Unix/Linux shell scripts to help automate using the tool:

* `dump`: takes an address (in hex) and an optional byte count (also in hex) and dumps memory at that address to the screen: `dump 010000 20`.

* `run`: take an Intel HEX file and downloads it into the Foenix's memory. If the HEX file includes a block of memory covering the processor's RESET hardware vector, this will also cause the program in the HEX file to run starting with the RESET handler provided: `run basic816.hex`.

* `runpgx`: take a Foenix PGX binary file, download it into the Foenix's memory, and attempt to run it.

* `runpgz`: take a Foenix PGZ binary file, download it into the Foenix's memory, and attempt to run it.

* `lookup`: takes a label and an optional byte count (in hex). The label is used to search the LBL file of the project for an address. If the address is found, the memory starting at that address will be dumped to the screen: `lookup COUNTER`.

* `deref`: takes a label and an optional byte count (in hex). The label is used to search the LBL file of the project for an address. If the address is found, the three bytes starting at that address will be read from the Foenix memory and used as the starting address to dump memory to the screen: `deref INDEX 30`.

* `flash`: takes a binary file containing a flash image and an optional address. The binary image must be exactly 512KB and is copied raw to the address provided (or the default address from the INI file). The existing flash data is erased and replaced by the data in the BIN file. The script will ask for confirmation before beginning the process.

* `flash_sector`: takes a target machine name, a sector number (in hex from 0x00 to 0x3F), and an 8KB binary file containing the image to load into that sector of flash memory. The binary file is loaded into the F256's RAM (from 0x00000 to 0x01FFF) and then copied into the correct sector of flash memory. Machine names supported include `f256jr`, `f256k`, `fnx1591`.

* `flash_bulk`: takes a CSV file specifying the mapping between sector numbers and binary files and loads all the binary files into their respective flash sectors. Each file must be an 8KB binary file. The first column of the CSV file must contain the sector numbers in hex with no prefix (from 00 to 3F). The second column must contain the path to the file to load for that sector number. There must not be a column header row.

## Copy to a F256 SD Card

A command `pcopy` has been added that allows the user to upload a file to an SD card on an F256 (not supported on other Foenix devices). The command makes use of a PGX file that is uploaded to run on the F256 along with the file to copy. The source for this PGX file can be found at: https://github.com/dwsJason/f256/tree/develop/merlin32/pcopy. The `pcopy` feature is a contribution from dwsJason. Thanks!

## TCP Bridge Mode
FoenixMgr can also be configured to act as a TCP-to-serial bridge, allowing remote clients on your network to use the debug port without being physically connected to the Foenix. This can be useful if you want to undock your laptop. It's also the only solution available for Mac users, since the driver for the MaxLinear/Exar I/O chip has not been updated for more recent versions of macOS.

To run the FoenixMgr in TCP bridge mode, use these two options:

* `--tcp-bridge`: Set this to the host and port you want to listen on, for example, `192.168.1.114:2650`. Note that you should not listen on the loopback interface (`127.0.0.1`), as that would not work for remote client connections.

* `--port`: Set this to the serial port of the Foenix, like you would when communicating directly.

### Running on a Raspberry Pi
It can be handy to use a Raspberry Pi as the TCP bridge. However, getting one setup for this function requires a bit of work. Here are some notes that might help you in this situation:

1. Remove the existing CDC-ACM serial driver
   ```
   sudo rmmod cdc-acm
   modprobe -r usbserial
   sudo modprobe usbserial
   ```

2. Block the CDC-ACM driver from loading again
   ```
   sudo bash -c "echo blacklist cdc-acm > /etc/modprobe.d/blacklist-cdc-acm.conf"
   sudo update-initramfs -u
   ```

3. Install kernel headers so the driver can be compiled:
   ```
   sudo apt install raspberrypi-kernel-headers
   ````

4. Install the Dynamic Kernel Module Support to build and install the Exar driver:
   ```
   sudo apt-get install dkms
   ```

5. Download the driver code - official driver releases from MaxLinear (owners of Exar) are [here](https://www.maxlinear.com/support/design-tools/software-drivers). You'll want the USB UART driver for XR21B1411 for Linux. The current version is 1D.

6. Unzip the driver zip file and add a file inside that directory named `dkms.conf` with the following contents (note the version of the driver is `1d` to reflect the most recent version from Exar):
   ```
   MAKE="make -C ./ KERNELDIR=/lib/modules/${kernelver}/build"
   CLEAN="make -C ./ clean"
   BUILT_MODULE_NAME=xr_usb_serial_common
   BUILT_MODULE_LOCATION=./
   DEST_MODULE_LOCATION=/kernel/drivers/usb/serial
   PACKAGE_NAME=xr_usb_serial_common
   PACKAGE_VERSION=1d
   REMAKE_INITRD=yes
   ```

7. Create a directory for the driver source and config where DKMS will look for it (`1d` appears here again):
   ```
   sudo mkdir /usr/src/xr_usb_serial_common-1d
   sudo cp * /usr/src/xr_usb_serial_common-1d/
   ```

8. Finally, use DKMS to build and install the driver:
   ```
   sudo dkms add -m xr_usb_serial_common -v 1d
   sudo dkms build -m xr_usb_serial_common -v 1d
   sudo dkms install -m xr_usb_serial_common -v 1d
   ```
