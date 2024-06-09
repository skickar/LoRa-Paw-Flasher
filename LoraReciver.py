# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

## RECIEVER

# Simple demo of sending and recieving data with the RFM95 LoRa radio.
# Author: Tony DiCola
import board
import busio
import digitalio
import neopixel
import adafruit_rfm9x
import displayio
import terminalio
from adafruit_display_text import label
import busio
from adafruit_displayio_sh1106 import SH1106
import neopixel
import time


time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems

# Release any resources currently in use for the displays
displayio.release_displays()

i2c = busio.I2C(scl=board.SCL, sda=board.SDA)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

# Define the width and height of the display
WIDTH = 130
HEIGHT = 64
display = SH1106(display_bus, width=WIDTH, height=HEIGHT, rotation=180)



pixel = neopixel.NeoPixel(board.IO10, 2, brightness=0.2)
pixel[0] = (0,0,255)  # equivalent
pixel[1] = (0,0,255)  # equivalent

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.IO9)
RESET = digitalio.DigitalInOut(board.IO4)
# Or uncomment and instead use these if using a Feather M0 RFM9x board and the appropriate
# CircuitPython build:
# CS = digitalio.DigitalInOut(board.RFM9X_CS)
# RESET = digitalio.DigitalInOut(board.RFM9X_RST)


# Initialize SPI bus.
spi = busio.SPI(board.IO6, MOSI=board.IO8, MISO=board.IO7)

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
# Common settings for both transmitter and receiver
rfm9x.tx_power = 23
#rfm9x.spreading_factor = 12
rfm9x.coding_rate = 5
rfm9x.signal_bandwidth = 125000
rfm9x.enable_crc = True
rfm9x.auto_agc = True
rfm9x.preamble_length = 12

# Ensure low data rate optimization is enabled
rfm9x.low_data_rate_optimize = True

flash = digitalio.DigitalInOut(board.IO37)
flash.direction = digitalio.Direction.OUTPUT


while True:
    packet = rfm9x.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        pixel[0] = (255,0,0)  # equivalent
        pixel[1] = (255,0,0)  # equivalent
        #print("Received nothing! Listening again...")
    else:
        # Received a packet!
        pixel[0] = (0,255,0)  # equivalent
        # Print out the raw bytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        packet_text = str(packet, "ascii")
        print("Received (ASCII): {0}".format(packet_text))
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
        if "flash" in packet_text:
            flash.value = True
            time.sleep(1)
            flash.value = False
        else:
            flash.value = False
