# ServoCape
This is some Servo Cape additions made for the BBB and BBAI-64.

# If you break it, you buy it!
1. Get an image from beagleboard.org for a Debian Bullseye Distro w/ all the fixings.
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
10. That should get you started...

Please use caution while attempting to handle the ServoCape and BeagleBone Black.
` There is no excuse for not using safety! `

License: GPL v3 which can be found here: ` https://www.gnu.org/licenses/gpl-3.0.en.html `

Also, I take no responsibility for your endeavors, actions, or your lack of thought out processes. 

# AGAIN
` be careful and stay cautious `

# Update
If you have not noticed, there is a server, a Flask Server, in the src file to run called pwmsOne.py. 
That file needs a /templates directory and an HTML file in it to handle such an instance...

Please review flask and HTML to handle the file!
