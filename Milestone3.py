#
# Milestone3.py - This is the Python code template used to 
# setup the structure for Milestone 3. In this milestone, you need
# to demonstrate the capability to productively display a message
# in Morse code utilizing the Red and Blue LEDs. The message should
# change between SOS and OK when the button is pressed using a state
# machine.
#
# This code works with the test circuit that was built for module 5.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------

##
## Imports required to handle our Button, and our LED devices
##
from gpiozero import Button, LED

##
## Imports required to allow us to build a fully functional state machine
##
from statemachine import StateMachine, State

##
## Import required to allow us to pause for a specified length of time
##
from time import sleep

##
## These are the packages that we need to pull in so that we can work
## with the GPIO interface on the Raspberry Pi board and work with
## the 16x2 LCD display
##
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

from threading import Thread

##
## DEBUG flag - boolean value to indicate whether or not to print 
## status messages on the console of the program
## 
DEBUG = True

##
## ManagedDisplay - Class intended to manage the 16x2 
## Display
##
class ManagedDisplay():
    ##
    ## Class Initialization method to setup the display
    ##
    def __init__(self):
        ##
        ## Setup the six GPIO lines to communicate with the display.
        ## This leverages the digitalio class to handle digital 
        ## outputs on the GPIO lines. There is also an analagous
        ## class for analog IO.
        ##
        ## You need to make sure that the port mappings match the
        ## physical wiring of the display interface to the 
        ## GPIO interface.
        ##
        ## compatible with all versions of RPI as of Jan. 2019
        ##
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        # Modify this if you have a different sized character LCD
        self.lcd_columns = 16
        self.lcd_rows = 2 

        # Initialise the lcd class
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, 
                    self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7, 
                    self.lcd_columns, self.lcd_rows)

        # wipe LCD screen before we start
        self.lcd.clear()

    ##
    ## cleanupDisplay - Method used to cleanup the digitalIO lines that
    ## are used to run the display.
    ##
    def cleanupDisplay(self):
        # Clear the LCD first - otherwise we won't be abe to update it.
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()
        
    ##
    ## clear - Convenience method used to clear the display
    ##
    def clear(self):
        self.lcd.clear()

    ##
    ## updateScreen - Convenience method used to update the message.
    ##
    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

    ## End class ManagedDisplay definition  
    

##
## CWMachine - This is our StateMachine implementation class.
## The purpose of this state machine is to send a message in 
## morse code, blinking the red light for a dot, and the blue light
## for a dash.
##
## A dot should be displayed for 500ms. 
## A dash should be displayed for 1500ms.
## There should be a pause of 250ms between dots/dashes.
## There should be a pause of 750ms between letters.
## There should be a pause of 3000ms between words.
##
class CWMachine(StateMachine):
    "A state machine designed to display morse code messages"

    ##
    ## Our two LEDs, utilizing GPIO 18, and GPIO 23
    ##
    redLight = LED(18)
    blueLight = LED(23)

    ##
    ## Set the contents of our messages
    ##
    message1 = 'SOS'
    message2 = 'OK'

    ##
    ## keep track of the active message
    ##
    activeMessage = message1

    ##
    ## endTransmission - flag used to determine whether or not
    ## we are shutting down
    ##
    endTransmission = False

    ##
    ## Define these states for our machine.
    ##
    ##  off - nothing lit up
    ##  dot - red lit for 500ms
    ##  dash - blue lit for 1500ms
    ##  dotDashPause - dark for 250ms
    ##  letterPause - dark for 750ms
    ##  wordPause - dark for 3000ms
    ##
    off = State(initial = True)
    dot = State()
    dash = State()
    dotDashPause = State()
    letterPause = State()
    wordPause = State()

    ##
    ## Initialize our display
    ##
    screen = ManagedDisplay()

    ##
    ## A dictionary of Morse Code - this is a utility that will allow us
    ## to convert any common string into Morse code.
    ##
    morseDict = {
        "A" : ".-", "B" : "-...", "C" : "-.-.", "D" : "-..",
        "E" : ".", "F" : "..-.", "G" : "--.", "H" : "....",
        "I" : "..", "J" : ".---", "K" : "-.-", "L" : ".-..",
        "M" : "--", "N" : "-.", "O" : "---", "P" : ".--.",
        "Q" : "--.-", "R" : ".-.", "S" : "...", "T" : "-",
        "U" : "..-", "V" : "...-", "W" : ".--", "X" : "-..-",
        "Y" : "-.--", "Z" : "--..", "0" : "-----", "1" : ".----",
        "2" : "..---", "3" : "...--", "4" : "....-", "5" : ".....",
        "6" : "-....", "7" : "--...", "8" : "---..", "9" : "----.",
        "+" : ".-.-.", "-" : "-....-", "/" : "-..-.", "=" : "-...-",
        ":" : "---...", "." : ".-.-.-", "$" : "...-..-", "?" : "..--..",
        "@" : ".--.-.", "&" : ".-...", "\"" : ".-..-.", "_" : "..--.-",
        "|" : "--...-", "(" : "-.--.-", ")" : "-.--.-"
    }

    ##
    ## doDot - Event that moves between the off-state (all-lights-off)
    ## and a 'dot'
    ##
    doDot = (
        off.to(dot) | dot.to(off)
    )

    ##
    ## doDash - Event that moves between the off-state (all-lights-off)
    ## and a 'dash'
    ##
    doDash = (
        off.to(dash) | dash.to(off)
    )

    ##
    ## doDDP - Event that moves between the off-state (all-lights-off)
    ## and a pause between dots and dashes
    ##
    doDDP = (
        off.to(dotDashPause) | dotDashPause.to(off)
    )

    ##
    ## doLP - Event that moves between the off-state (all-lights-off)
    ## and a pause between letters
    ##
    doLP = (
        off.to(letterPause) | letterPause.to(off)
    )

    ##
    ## doWP - Event that moves between the off-state (all-lights-off)
    ## and a pause between words
    ##
    doWP = (
        off.to(wordPause) | wordPause.to(off)
    )

    ##
    ## on_enter_dot - Action performed when the state machine transitions
    ## into the dot state
    ##
    def on_enter_dot(self):
        # Red light comes on for 500ms
        self.redLight.on()
        sleep(0.5)

        if(DEBUG):
            print("* Changing state to red - dot")

    def on_exit_dot(self):
        # Red light forced off
        self.redLight.off()

    def on_enter_dash(self):
        # Blue light comes on for 1500ms
        self.blueLight.on()
        sleep(1.5)

        if(DEBUG):
            print("* Changing state to blue - dash")

    def on_exit_dash(self):
        # Blue light forced off
        self.blueLight.off()

    def on_enter_dotDashPause(self):
        # wait for 250ms
        sleep(0.25)

        if(DEBUG):
            print("* Pausing Between Dots/Dashes - 250ms")

    def on_exit_dotDashPause(self):
        pass

    def on_enter_letterPause(self):
        # wait for 750ms
        sleep(0.75)

        if(DEBUG):
            print("* Pausing Between Letters - 750ms")

    def on_exit_letterPause(self):
        pass

    def on_enter_wordPause(self):
        # wait for 3000ms
        sleep(3.0)

        if(DEBUG):
            print("* Pausing Between Words - 3000ms")

    def on_exit_wordPause(self):
        pass

    def toggleMessage(self):
        # Safely toggle between the two messages referencing the instance variable (self)
        if self.activeMessage == self.message1:
            self.activeMessage = self.message2
        else:
            self.activeMessage = self.message1

        if(DEBUG):
            print(f"* Toggling active message to: {self.activeMessage} ")

    def processButton(self):
        print('*** processButton')
        self.toggleMessage()

    def run(self):
        myThread = Thread(target=self.transmit)
        myThread.start()
        
    def transmit(self):
        while not self.endTransmission:
            self.screen.updateScreen(f"Sending:\n{self.activeMessage}")
            wordList = self.activeMessage.split()
            lenWords = len(wordList)
            wordsCounter = 1

            for word in wordList:
                lenWord = len(word)
                wordCounter = 1

                for char in word:
                    morse = self.morseDict.get(char)
                    lenMorse = len(morse)
                    morseCounter = 1

                    for x in morse:
                        # Determine if the next symbol is a dot or a dash
                        if x == '.':
                            self.doDot() # Transition to dot (Turns on & sleeps)
                            self.doDot() # Transition back to off
                        elif x == '-':
                            self.doDash() # Transition to dash (Turns on & sleeps)
                            self.doDash() # Transition back to off

                        # Process dotDashPause event if there are more symbols
                        if morseCounter < lenMorse:
                            self.doDDP()
                            self.doDDP()
                            morseCounter += 1

                    # Process letterPause event if there are more letters
                    if wordCounter < lenWord:
                        self.doLP()
                        self.doLP()
                        wordCounter += 1

                # Process wordPause event if there are more words
                if wordsCounter < lenWords:
                    self.doWP()
                    self.doWP()
                    wordsCounter += 1

        self.screen.cleanupDisplay()

## Initialize our State Machine, and begin transmission
cwMachine = CWMachine()
cwMachine.run()


greenButton = Button(24)
greenButton .when_pressed = cwMachine.processButton
repeat = True

##
## Repeat until the user creates a keyboard interrupt (CTRL-C)
##
while repeat:
    try:
        ## Only display if the DEBUG flag is set
        if(DEBUG):
            print("Killing time in a loop...")

        ## sleep for 20 seconds at a time. This value is not crucial, 
        ## all of the work for this application is handled by the 
        ## Button.when_pressed event process
        sleep(20)
    except KeyboardInterrupt:
        ## Catch the keyboard interrupt (CTRL-C) and exit cleanly
        ## we do not need to manually clean up the GPIO pins, the 
        ## gpiozero library handles that process.
        print("Cleaning up. Exiting...")

        ## Stop the loop
        repeat = False
        
        ## Cleanly exit the state machine after completing the last message
        cwMachine.endTransmission = True
        sleep(1)
