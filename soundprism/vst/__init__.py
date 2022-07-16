#!/usr/bin/env python3

'''
Virtual Instruments Module
'''

import numpy as np
from soundprism.signal import *
from pynput import keyboard as kb

class keyBoard ():

    '''
    A base virtual instrument keyboard. 
    '''

    def __init__ (self):

        self.currentGenerator = None
        self.keyBoardKeys = 'yxcvbnmasdfghjklqwertzuiop'
        self.keyTones = {
            "A0": None,
            "A0#": None,
            "B0": None,
        }
        self.level = 4
        self.octave = ["C{}", "C{}#", "D{}", "D{}#", "E{}", "F{}", "F{}#", "G{}", "G{}#", "A{}", "A{}#", "B{}"]
        self.pianoKeyMap = {}
        self.toneDuration = 5
        self.toneRate = {
            "A0": 27.5,
            "A0#": 29.1352,
            "B0": 30.8677,
        }
        self.amplification = 1
        self.volume = 1
        
        # load the tone scale for all keys
        self.loadKeyScale()

    def applyGenerator (self, generator=None):

        # use the recent generator
        if generator is None:
            if self.currentGenerator is None:
                ArgumentError('No generator loaded yet, please initialize by providing a generator.')
            generator = self.currentGenerator
        else:
            # override internal generator
            self.currentGenerator = generator

        for tone, rate in self.toneRate.items():

            self.keyTones[tone] = self.amplification * self.currentGenerator(rate, time.line(self.toneDuration))
    
    def bindTonesToKeyboard (self, level=None, live=False):

        # determine by the provided level which octaves to bind
        if level is None: level = self.level
        level = level
        firstOctaveKeys = self.keyTones.keys()
        keysToBind = []
        for iter in [1,2]:
            for key in firstOctaveKeys:
                if str(level) in key:
                    keysToBind.append(key)
            if level < 7:
                level += 1
            else:
                break
        
        # build a map from keyboard keys to piano keys
        for i in range(len(keysToBind)):
            self.pianoKeyMap[self.keyBoardKeys[i]] = keysToBind[i]

        if live:

            listener = kb.Listener(on_press=self.keyDown)
            listener.start()
            listener.join()
    
    def keyDown (self, key):

        '''
        Simulate a piano key press event by pressing a keyboard char.
        '''
                
        if key == kb.Key.esc:
            return False
        if key == kb.Key.space:
            sound.stop()
            return
        try:
            k = key.char # single character
        except:
            k = key.name

        if k in self.keyBoardKeys:

            # synthizise    
            self.synth(self.pianoKeyMap[k])
            print(self.pianoKeyMap[k])

    def loadKeyScale (self):

        '''
        Loads rohling keys and corresponding tones with frequencies.
        '''

        for level in range(1, 7):
            for i in range(len(self.octave)):
                tone = str(self.octave[i]).format(level)
                self.toneRate[tone] = units.toneScale[i] * level
                self.keyTones[tone] = None
        self.keyTones["C8"] = 4186.01

    def refresh (self):

        "Call this method when major changes occured."

        try:
            self.applyGenerator()
            return True
        except Exception as e:
            print(e)
            return False
        
    def synth (self, *tones, strength=0.5, volume=None, duration=None, playSound=True, blocking=True):

        if volume is not None:
            self.volume = volume

        # bake signal and play
        signal = None
        if len(tones) == 1:
            signal = self.keyTones[tones[0]] * strength * self.volume
        else:
            for tone in tones:
                layer = self.keyTones[tone] * strength * self.volume
                if signal is None:
                    signal = layer
                else:
                    signal = signal + layer
        
        if duration is not None:
            signal = signal[:int(duration * time.sampleRate)]

        if playSound:
            sound.play(signal, blocking=blocking)

        return signal