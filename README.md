# PCars_Matrix_Portal
Telemetry display of Project Cars data on a 32x64 LED Display using Adafruit Matrix Portal board

This decodes and displays Project Cars 1 UDP Packets  
Project Cars 2 users just need to, in SYSTEM settings  
set "UDP Protocol Version" to "Project Cars 1"  
For help on this see: <https://www.projectcarsgame.com/two/02-options-and-settings>  
Search for "SYSTEM" settings  
Set the UDP Frequency setting in PCars to value 8  
9 is too slow and anything lower is too fast and there is too much lag  
Original API was found here...  
<http://forum.projectcarsgame.com/showthread.php?40113-HowTo-Companion-App-UDP-Streaming>  
Thanks to James Muscat and his project  
<https://github.com/jamesremuscat/pcars>  
For helping me figure out how to decode the UDP packets  

### What you need to run this project  
Hardware Requirements:  
32x64 LED Matrix Display  
Get one from Adafruit <https://www.adafruit.com/category/327> but almost any HUB-75 compatible display will work

Adafruit Matrix Portal  
<https://www.adafruit.com/product/4745>  
This is the board that drives the display  
Needs to be configured to run CircuitPython  
<https://learn.adafruit.com/adafruit-matrixportal-m4/install-circuitpython>

Copy code.py and fonts directory into the "CIRCUITPY" drive.
But you'll also need to create a "lib" folder to hold the CircuitPython libraries you'll need  
You'll need...
* adafruit_bitmap_font
* adafruit_bitmap_font
* adafruit_display_text
* adafruit_esp32spi
* adafruit_matrixportal

Last you'll need a "secrets.py" file that hold your local WiFi SSID and password.  
<https://learn.adafruit.com/adafruit-pyportal/internet-connect#whats-a-secrets-file-15-1>

That should do it, just configure Project Cars or Project Cars 2 to transmit UDP packets.  
Level 8 is the best setting for that.

This project is a narrow use case but it does demonstate how to grab UDP packets from your local network, parse them and display some data.

[![Project Cars Picture]("Project Cars Picture")](https://github.com/DeanDavis/PCars_Matrix_Portal/blob/master/Project%20Cars%20Matrix.png)

