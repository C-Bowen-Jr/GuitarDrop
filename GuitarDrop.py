# Guitar Drop (WIP)
# 08/2/22

# This is a project similar to chordfinder's scale -> note. The main difference
# is the added feature of alternate tuning adjustments and mabe improved readability

Version = "0.1.9"

import pygame
from pygame.locals import *
import sys
import configparser
from ast import literal_eval
from dataclasses import dataclass
from enum import IntEnum

# Global Variables
NOTES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
DISPLAYSURF = pygame.Surface((1080,640))
SCREEN = pygame.display.set_mode((2160,1280))
FRETTINGSPOTS = pygame.Surface((1080,640))
BLACK = (30,30,30)
BROWN = (200,90,50)
GREY  = (190,190,190)
RED   = (240,0,0)
GREEN = (0,240,0)
BLUE  = (0,0,240)
WHITE = (255,255,255)
FRETWIDTH = 40
FRETHEIGHT = 70
Frets = []
GStrings = []
Standard = ["E","B","G","D","A","E"]
Tuning = ["E","B","G","D","A","E"]
CurrentScale = "Major"
CurrentKey = "E"
CurrentScaleNotes = []

class Tune(IntEnum):
    UP = 1
    DOWN = -1

@dataclass
class GuitarString:
    TunedTo: str   # What note the open string plays
    Position: int  # 0-5, low E to high e
    Line: tuple    # not sure if this is the best implementation, but gfx location
    Visible: bool  # Filter option, 50%/100% alpha and hide/show notes for the string
    
@dataclass
class Fret:
    Number: int
    Rectangle: tuple
    Visible: bool

pygame.init()

Font = pygame.font.SysFont(None, 20)

def line_intersect(LineAStart, LineAEnd, LineBStart, LineBEnd):
    Ax1, Ay1 = LineAStart
    Ax2, Ay2 = LineAEnd
    Bx1, By1 = LineBStart
    Bx2, By2 = LineBEnd
    
    delta = (By2 - By1) * (Ax2 - Ax1) - (Bx2 - Bx1) * (Ay2 -Ay1)
    if delta:
        uA = ((Bx2 - Bx1) * (Ay1 - By1) - (By2 - By1) * (Ax1 - Bx1)) / delta
        uB = ((Ax2 - Ax1) * (Ay1 - By1) - (Ay2 - Ay1) * (Ax1 - Bx1)) / delta
    else:
        return
    if not(0 <= uA <= 1 and 0 <= uB <=1):
        return
    x = Ax1 + uA * (Ax2 - Ax1)
    y = Ay1 + uA * (Ay2 - Ay1)
    
    return x, y

def textRender(text, color):
    background_color = BLACK
    if color == BLACK:
        background_color = WHITE
    return Font.render(text, True, color, background_color)

def getNote(StrOff, TunOff, Fretted):
    global NOTES
    
    # PlayedNote is from NOTES the sum looped by offsets of the
    # actual string offset, any tuning offset, and the fretted
    # note. the loop is handled by % 12 (12 being total note steps
    if isinstance(StrOff, int):
        PlayedNote = (StrOff + TunOff + Fretted) % 12
    else:
        PlayedNote = (NOTES.index(StrOff) + TunOff + Fretted) % 12
    return NOTES[PlayedNote]

def getScale(keyNote, scaleName):
    global NOTES
    availableScales = ["Major", "Natural Minor", "Melodic Minor"]
    ScaleOffsets = []
    Scale = []
    if scaleName not in availableScales:
        return "Not a valid scale"
    if scaleName == "Major":
        ScaleOffsets = [2,2,1,2,2,2,1] # whole whole half whole whole whole half
    elif scaleName == "Natural Minor": 
        ScaleOffsets = [2,1,2,2,1,2,2]
    elif scaleName == "Melodic Minor": 
        ScaleOffsets = [2,1,2,2,2,2,1]
        
    Scale.append(keyNote) # Add the root note
    for degree in ScaleOffsets:
        # Next note in scale by checking the last added note, and then offsetting it
        # by the scale degree. Root starts the set at keynote
        Scale.append(getNote(Scale[-1],0,degree))
        
    return Scale

def TuneString(thisString, TuneDirection):
    global Tuning, GStrings, CurrentKey

    Tuning[thisString] = getNote(Tuning[thisString],0,TuneDirection)

def drawFretboard():
    global Frets
    DISPLAYSURF.fill(BLACK)
    for fretNumber in Frets:
        if fretNumber.Number > 0:
            pygame.draw.rect(DISPLAYSURF, BROWN, fretNumber.Rectangle)
            pygame.draw.rect(DISPLAYSURF, BLACK, fretNumber.Rectangle, 1)
        if fretNumber.Number in [3,5,7,9,15,17,19]: # one dot marked spots
            dot = (fretNumber.Rectangle[0][0]+(FRETWIDTH/2)-3,fretNumber.Rectangle[0][1]+(FRETHEIGHT/2)-3)
            pygame.draw.circle(DISPLAYSURF, WHITE, dot, 6)
        elif fretNumber.Number == 12:
            dot = (fretNumber.Rectangle[0][0]+(FRETWIDTH/2)-3, fretNumber.Rectangle[0][1]+(FRETHEIGHT/3)-3)
            pygame.draw.circle(DISPLAYSURF, WHITE, dot, 6)
            dot2 = (fretNumber.Rectangle[0][0]+(FRETWIDTH/2)-3, fretNumber.Rectangle[0][1]+(FRETHEIGHT/3)+30)
            pygame.draw.circle(DISPLAYSURF, WHITE, dot2, 6)
    
def drawStrings():
    global Tuning, GStrings
    strIter = 0
    GStrings = []
    for eachString in Tuning:
        lineX = 70
        lineY = 107 + (strIter*(int(FRETHEIGHT/6)))
        # PROBLEM FOUND: tuning.index(e) always returns first e and duplicates low e string
        GStrings.append(GuitarString(eachString, strIter,((lineX,lineY),(lineX+(FRETWIDTH*22),lineY)), True))
        strIter += 1 # Because Tuning.index(eachString) is get hung up on same note strings like E and e
        
    for eachString in GStrings:
        Text = Font.render(eachString.TunedTo, True, WHITE, BLACK)
        TuningLabelOffset = tuple(map(lambda i, j: i - j, eachString.Line[0], (12,6)))
        DISPLAYSURF.blit(Text, TuningLabelOffset)
        pygame.draw.line(DISPLAYSURF, GREY, eachString.Line[0],eachString.Line[1], 2)
        
def drawScaleMarkers():
    global Frets, Gstrings, CurrentScaleNotes
    for eachFret in Frets:
        # for each fret, check that string 6 (low e) in getNote(GStr.tuned,0,Fret.number) to be in currentscalenotes
        for eachString in GStrings:
            if getNote(eachString.TunedTo,0,eachFret.Number) in CurrentScaleNotes:
                dotOffset = tuple(map(lambda i, j: i+j, eachString.Line[0], ((eachFret.Number*FRETWIDTH)+(FRETWIDTH/2),0)))
                if getNote(eachString.TunedTo,0,eachFret.Number) == CurrentScaleNotes[0]: # Root Note
                    pygame.draw.circle(DISPLAYSURF, GREEN, dotOffset, 5)
                else:
                    pygame.draw.circle(DISPLAYSURF, BLUE, dotOffset, 4)
        
def main():
    # Personal Init features
    # Defines
    global CurrentKey, CurrentScale, CurrentScaleNotes, Frets, DISPLAYSURF
    FramePerSec = pygame.time.Clock()
    Redraw = True
    DisplayScaleMarkers = True
    
    # Sets
    pygame.display.set_caption("Guitar Drop")
    DISPLAYSURF.fill(BLACK)
    for fretNumber in range(22):
        rectX = 70 + (fretNumber*FRETWIDTH)
        rectY = 100
        Frets.append(Fret(fretNumber, ((rectX, rectY),(FRETWIDTH, FRETHEIGHT)), True)) # create a fret, and visible is true by default
        
    drawFretboard()
    drawStrings()
    CurrentScaleNotes = getScale(CurrentKey, CurrentScale)
    
    while True:
        # Logic code
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            mods_pressed = pygame.key.get_mods()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_a:
                    CurrentKey = "A"
                if event.key == pygame.K_b:
                    CurrentKey = "B"
                if event.key == pygame.K_c:
                    CurrentKey = "C"
                if event.key == pygame.K_d:
                    CurrentKey = "D"
                if event.key == pygame.K_e:
                    CurrentKey = "E"
                if event.key == pygame.K_f:
                    CurrentKey = "F"
                if event.key == pygame.K_g:
                    CurrentKey = "G"
                if event.key == pygame.K_0:
                    Tuning = Standard
                if event.key == pygame.K_1:
                    if mods_pressed & pygame.KMOD_SHIFT:
                        TuneString(0, Tune.UP)
                    else:
                        TuneString(0, Tune.DOWN)
                if event.key == pygame.K_2:
                    if mods_pressed & pygame.KMOD_SHIFT:
                        TuneString(1, Tune.UP)
                    else:
                        TuneString(1, Tune.DOWN)
                if event.key == pygame.K_3 and not mods_pressed & pygame.KMOD_ALT:
                    if mods_pressed & pygame.KMOD_SHIFT:
                        TuneString(2, Tune.UP)
                    else:
                        TuneString(2, Tune.DOWN)
                if event.key == pygame.K_4:
                    if mods_pressed & pygame.KMOD_SHIFT:
                        TuneString(3, Tune.UP)
                    else:
                        TuneString(3, Tune.DOWN)
                if event.key == pygame.K_5:
                    if mods_pressed & pygame.KMOD_SHIFT:
                        TuneString(4, Tune.UP)
                    else:
                        TuneString(4, Tune.DOWN)
                if event.key == pygame.K_6:
                    if mods_pressed & pygame.KMOD_SHIFT:
                        TuneString(5, Tune.UP)
                    else:
                        TuneString(5, Tune.DOWN)
                if event.key == pygame.K_m:
                    if mods_pressed & pygame.KMOD_ALT:
                        CurrentScale = "Melodic Minor"
                    elif mods_pressed & pygame.KMOD_SHIFT:
                        CurrentScale = "Major"
                    else:
                        CurrentScale = "Natural Minor"
                if event.key == pygame.K_LSHIFT:
                    CurrentScale = "Major"
                if event.key == pygame.K_3 and mods_pressed & pygame.KMOD_ALT: # 3 is where sharp/pound/hash is
                    if "#" in getNote(CurrentKey,0,1): # If the next note is can be sharped
                        CurrentKey = getNote(CurrentKey,0,1)
                        
                if event.key == pygame.K_SPACE:
                    DisplayScaleMarkers = not DisplayScaleMarkers
                    
                CurrentScaleNotes = getScale(CurrentKey, CurrentScale)
                Redraw = True
                        
            
        
        # Render code
        if Redraw:
            drawFretboard()
            drawStrings()
            if DisplayScaleMarkers:
                drawScaleMarkers()
            Redraw = not Redraw # we did it, don't waste cpu reprocessing no changes
            

        DISPLAYSURF.blit(textRender(f"The {CurrentScale} in the key of {CurrentKey} is {CurrentScaleNotes}", WHITE), (70, 200))
        DISPLAYSURF.blit(textRender("Press A-G to change keys",WHITE), (70,220))
        DISPLAYSURF.blit(textRender("Press 3 to change to sharp", WHITE), (70,240))
        DISPLAYSURF.blit(textRender("Press space to toggle position dots",WHITE), (70,260))
        DISPLAYSURF.blit(textRender("Press M for Natural Minor, +Shift for Major, +Alt for Melodic Minor", WHITE), (70,280))
        DISPLAYSURF.blit(textRender("Press 1-6 to drop a string's tuning, +Shift to raise instead", WHITE), (70, 300))
        SCREEN.blit(pygame.transform.scale(DISPLAYSURF, (2160,1280)), (0,0))
        pygame.display.flip()
        FramePerSec.tick(30)
    
if __name__ == '__main__':
    main()
