# This Servo Cape for the BBAI-64 and the BBB from beagleboard.org

### I have recently, 01/2024, tried to make it work and have failed

### Something changed that is not known to me...I am sorry

# ServoCape
This is some Servo Cape additions made for the BBB and BBAI-64.

### Ideas about Bullseye because Bookworm will need a Virtual Environment for python3 -m pip install smbus2

1. Get an image from beagleboard.org for a Debian Bullseye Distro or another one.
2. Make sure it is the minimal flasher image...
3. Here is a location where you can grab the image...
   a. https://forum.beagleboard.org/t/arm64-debian-11-x-bullseye-monthly-snapshots-2023-10-07/32318
4. Look to your smbus2 file called smbus2.py and change line 302.
5. The smbus2.py file is located, after installing w/ `python3 -m pip install smbus2`, at:
   a. `~/.local/lib/python3/site-packages/smbus2/smbus2.py`
6. Then, on line 302 in smbus2.py, make sure it is a fd of `/dev/bone/i2c/2`.
7. If that is not working, try `/dev/i2c-5`.
8. Add your favorite server and a `/templates/` dir. w/ a file called whatever you wish...
9. Make sure that pwmsOne.py has the same .html file listed as what you will call the .html file in `/ServoCape/templates/Your_File.html`.

Also...Bookworm has some ideas relating to the OS itself that plays a bit differently compared to Bullseye.

Use a virtual env instead of trying to use outside package managers like pip3 or pip when attempting installs.
This means...

1. apt install python3-venv
2. python3 -m venv Your_FILE
3. source Your_FILE/bin/activate
4. cd Your_FILE && python3 -m pip install smbus2
5. Or...you can use smbus via: apt install python3-smbus
6. There are arm64 and armhf ports of python3-smbus for utilization
7. Then, try-try-try to make things work via the already acquired docs. here

License: GPL v3 which can be found here: ` https://www.gnu.org/licenses/gpl-3.0.en.html `

# Update
If you have not noticed, there is a server, a Flask Server, in the src file to run called pwmsOne.py. 
That file needs a /templates directory and an HTML file in it to handle such an instance...

# Flask
Please review flask and HTML to handle the file!
