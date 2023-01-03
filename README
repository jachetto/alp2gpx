A simple AlpineQuest Trk2GPX converter

Alpine Quest is a very nice GPS app for outdoor activities
https://www.alpinequest.net/

Based on flifplip's apq2gpx (https://github.com/phkehl/apq2gpx).
Many thanks!

This job is an attempt to port flipflip's original code
in Perl to Python.

Special thanks to @dhicks (https://github.com/dhicks) for the TRK 4 parser and the I/O arguments
Special thanks to @ydespond (https://github.com/ydespond) for the suggestions about to better calculate the elevation and the timestamp

A special thanks to my friends 'Amici Alpinisti'. 
The friends with whom i share my hiking adventures

*** CHANGELOG ***
03 Jan 2023 Added support for OM 3.8b / AQ 2.2.9b specification
03 Jan 2023 Added support for pyproj (better elevation calc, see https://github.com/jachetto/alp2gpx/issues/2)
25 May 2021 Added support for TRK version 4,  dhicks (https://github.com/dhicks)
25 May 2021 Added Arguments for I/O, dhicks (https://github.com/dhicks)
18 April 2020 1st beta release.  Only TRK supported


**TIPS**
###### Install pyproj if you want a better calculation of elevation ######

```
pip install pyproj
```


###### Mass trk conversion  ######

Use something like:

```
find . -type f -name '*.trk' -exec python3 alp2gpx.py "{}" \;
```
