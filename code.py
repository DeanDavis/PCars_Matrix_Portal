# Project Cars Telemetry Display
# Author: Dean Davis
# Date: November 18, 2020
#
# Note this decodes Project Cars 1 UDP Packets
# Project Cars 2 users just need to, in SYSTEM settings
# set "UDP Protocol Version" to "Project Cars 1"
# For help on this see: https://www.projectcarsgame.com/two/02-options-and-settings/
# Search for "SYSTEM" settings
# Set the UDP Frequency setting in PCars to value 8
# 9 is too slow and anything lower is too fast and there is too much lag
# Original API was found here...
# http://forum.projectcarsgame.com/showthread.php?40113-HowTo-Companion-App-UDP-Streaming
# Thanks to James Muscat and his project
# https://github.com/jamesremuscat/pcars
# For helping me figure out how to decode the UDP packets
#
#
import board  # Access Matrix Portal
import busio  # Access SPI
from digitalio import DigitalInOut  # Used to set up the ESP32 Chip for connecting to WiFi
from adafruit_esp32spi import adafruit_esp32spi  # Also Used to set up the ESP32 Chip for connecting to WiFi

import displayio  # Base class for dislaying text and graphics on the LED Matrix
from adafruit_matrixportal.matrix import Matrix  # Used in initializing the display
from adafruit_bitmap_font import bitmap_font  # Used to import fonts for display in Labels
from adafruit_display_text import label  # Used to create labels for display
import struct  # Needed to unpack data from UDP data packets coming from Project Cars

# We will use this function to set multiple attributes on a Label object at one time
# This prevents screen flicker when needing to change two things like
# label text and position
def setattrs(_self, **kwargs):
    for k, v in kwargs.items():
        setattr(_self, k, v)

BIG_FONT = bitmap_font.load_font('/fonts/helvB12.bdf')

# Initialize the display
MATRIX = Matrix(bit_depth=6)
display = MATRIX.display

# This is the group we will display.
projectCarsGroup = displayio.Group(max_size=5, x=0, y=0)

# Static label for the "MPH" text
projectCarsGroup.append(label.Label(BIG_FONT, x=36, y=6, text="MPH", max_glyphs=3, color=0xFFFFFF))

# Label that displays the speed in MPH - THis is always your personal car in the race.
# I don't see how you get the speed of other racers
speedLabel = label.Label(BIG_FONT, x=15, y=6, text="0.0", max_glyphs=5, color=0xFFFFFF)
projectCarsGroup.append(speedLabel)

# Label for Position of the car you are viewing - usually you
positionLabel = label.Label(BIG_FONT, x=0, y=16, text="Pos: 0/0", max_glyphs=9, color=0x0000FF)
projectCarsGroup.append(positionLabel)

# Label for the current lap of the car you are viewing - usually you
lapLabel = label.Label(BIG_FONT, x=0, y=26, text="Lap: 0/0", max_glyphs=9, color=0xFFFF00)
projectCarsGroup.append(lapLabel)

# Show current connection status.
# RED - Not connected to WiFi
# Yellow - Connected but no Project Cars UDP packets detected
# Green - Connected and packets are flowing
connectLabel = label.Label(BIG_FONT, x=60, y=27, text=".", max_glyphs=1, color=0xFF0000)
projectCarsGroup.append(connectLabel)

# looking at the screen this rotation is having the Matrix Portal on the right side.
# if you prefer the Matrix Portal on the left change the rotation to 180
display.rotation = 0
# Display the group. All the text will now appear
display.show(projectCarsGroup)

# Add a secrets.py to your filesystem that has a dictionary called secrets with "ssid" and
# "password" keys with your WiFi credentials. DO NOT share that file or commit it into Git or other
# source control.
# pylint: disable=no-name-in-module,wrong-import-order
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Set up the ESP32 for connection to WiFi
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except RuntimeError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
# We have a connection so change the color of the connection indicator
connectLabel.color = 0xFFFF00

# To see the UDP packets we'll use a low level socket from the esp
# We need to use the espSocketNum as the reference to all the socket commands
espSocketNum = esp.get_socket()
# Bind the socket to port 5606 - this is the port Project Cars broadcasts UDP data on
# conn_mode = 1 is specifing UDP connection
esp.socket_connect(espSocketNum, dest="", port=5606, conn_mode=1)

# We'll use this to track the number of times we try to read a USP packet and don't see one
# Could probably use a time differential but I was just lazy
packetLossCounter = 0

# Loop forever to prevent code from exiting
while True:
    # Read a packet
    fullPacket = esp.socket_read(espSocketNum, 1500)  # 1500 is more than what is expected in a packet
    # Check to see if we got some data
    if len(fullPacket) > 0:
        packetLossCounter = 0
        # Good connection - change indicator to green
        connectLabel.color = 0x00FF00
        # Start unpacking the data
        byteTuple = struct.unpack_from('<HB', fullPacket, 0)
        seqNumber = (byteTuple[1] & 0xFC) >> 2
        packetType = byteTuple[1] & 0x03
        # print("{}-{}".format(seqNumber,packetType))
        # Packet type 0 is what we want. Other kinds of packets could be sent
        if packetType == 0:
            # get Viewed Paticipant Index
            byteTuple = struct.unpack_from('<bbBBbBbb', fullPacket, 4)
            VPI = byteTuple[0]
            numParticipants = byteTuple[1]
            lapsInEvent = byteTuple[7]
            if numParticipants < 0:
                numParticipants = 0
            carSpeed = round(struct.unpack_from('<f', fullPacket, 120)[0] * 2.237, 1)  # Speed from API is in Meters/Second so * by 2.237 to get MPH
            # print("Speed: {}".format(carSpeed))
            # Need to adjust exactly where speed is displayed depending on number of digits
            if carSpeed < 10.0:
                setattrs(speedLabel, x=15, text="{}".format(carSpeed))
            elif carSpeed < 100.0:
                setattrs(speedLabel, x=8, text="{}".format(carSpeed))
            else:
                setattrs(speedLabel, x=1, text="{}".format(carSpeed))
            # The packet contains a data structure (16 bytes) repeated for
            # every possible participant which is 56
            # So, decode Loop of 56 potential player information
            participants = []
            for currentPlayerIndex in range(0, 56):
                player = {}
                # the player info starts at byte 464 and the packet is 16 bytes in total
                # so 464 + (currentPlayerIndex * 16) gets us to the right starting byte
                byteTuple = struct.unpack_from('<hhhHBBBB', fullPacket, 464 + (currentPlayerIndex * 16))
                player["racePosition"] = byteTuple[4] & 0x7F
                player["lapsCompleted"] = byteTuple[5] & 0x7F
                player["currentLap"] = byteTuple[6]
                participants.append(player)
            positionLabel.text = "Pos: {}/{}".format(participants[VPI]["racePosition"], numParticipants)
            lapLabel.text = "Lap: {}/{}".format(participants[VPI]["currentLap"], lapsInEvent)
    else:
        # We didn't detect a packet in this loop
        packetLossCounter += 1
        # if we get to 400 loops without a packet assume we are in some state
        # where they aren't being sent or just can't detect them
        # change the indicator to yellow
        if packetLossCounter >= 400:
            packetLossCounter = 400
            connectLabel.color = 0xFFFF00