# Guitar Drop

This is simple scale/tuning display program to aid in guitar practice.

## Description

Guitar Drop is used to display root and regular notes in a scale displayed 
on a fretboard. You can change a few things to get what you're in need of. 
Pressing 

## Getting Started

### Dependencies

* Python 3^
* pip
* PyGame

If you don't already have PyGame, you can use ```pip install pygame```


### Executing program

* Run using python3
```
python3 GuitarDrop.py
```

## Usage

### Reading

The fretboard is layed out in the standard way of low E (when in standard 
tuning) at the bottom and higher notes going up from there. Fret markers 
are in standard positions with the double dots at the 12th fret marking the 
octave.

The dots are colored to denote that they are in the scale by being blue. 
The green dots then are also in the scale, but are the root notes.

Notes that are next to the string markers and appear to be off the 
fretboard itself are the open string notes.

### Changing Keys

To change keys:
* a - Key of A
* b - Key of B
...
* g - Key of G
Additionally, for sharps or flats, approach by the sharp (ie to get D♭, 
press C and make it C♯) and press 3 and Alt at the same time. Note: If 
you press this and the tuning on the 3rd string changes, then try 
pressing Alt first and holding it while pressing 3.

To change scales:
* m - Natural minor
* m + Shift - Major
* m + Alt - Melodic minor

To tune strings:
* 1 - Tune high E down half step
* 1 + Shift - Tune high E up half step
...
* 6 - Tune low E down half step
* 6 + Shift - Tune low E up half step

