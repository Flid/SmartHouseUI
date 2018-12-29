# What's that?

A face of my Smart}{ouse project. That's an GUI application, based on python-kivy 
(really awesome framework, I love it!), that provides some visual interface to 
control other devices and display sensors readings.

It uses [sensor communicator](https://github.com/Flid/sensor_communicator) 
to access real world devices and services.

The design sucks, I know, but it's not bad for back-end developer I think :)

After a a minute of inactivity, idle screen appears. It shows the current time, 
temperature, and has a "Game of Life" live background.
It's very dark intentionally to dim the display to stay dark at night.

That's how it looks:

![Main screen](https://github.com/Flid/SmartHouseUI/raw/master/.docs/main_screen.png "Main Screen")

![Idle screen](https://github.com/Flid/SmartHouseUI/raw/master/.docs/idle_screen.png "Idle Screen")


# Currently supported functionality

* Show the current weather (temperature, humidity, pressure weather forecast) inside 
and outdoors.
* Music player.
* Add weight measurements, render them on graph. This graph also has information about 
  every workout from Endomondo, calculates the total distance you've run since 
  the beginning of the year.


# Terms and conditions.

Really? Ok, I have to write something about that. I wrote this code just for fun, so if 
you accidentally find something interesting - just use it. It would be nice to notify 
me in this case, I will be happy to help with deployment and updates.

# Installing Kivy with SDL2
KIVY_WINDOW=sdl2 KIVY_GL_BACKEND=sdl2 USE_SDL2=1 pip install --no-binary :all: kivy

# Use original RPi 7" touchscreen
https://kivy.org/doc/stable/installation/installation-rpi.html#using-official-rpi-touch-display
