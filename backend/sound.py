#!/usr/bin/env python3

'''
Objects & Standards
----------------------------------------------------------------
GENERATORS [Object]
A generator is a signal-generating function with frequency as 
first argument. 

            timeline
                |
                v
    generator ---bake---> signal
                ^
                |
        arguments/parameters

SIGNALS [Standard]
A signal is a persistent 1-D numpy array. Signals can be loaded
in baked form (from audio file) or can originate from a 
generator. 

    
Unit System
----------------------------------------------------------------
Quantity        Unit
________________________
frequency       Hz (1/s)
time            s (1/Hz)
phase angle     radiants (2π/360°)
'''

import matplotlib.pyplot as plt 
from argparse import ArgumentError
import numpy as np
from time import sleep
import sounddevice as sd


class units:

    toneScale = [32.7032, 34.6478, 36.7081, 38.8909, 41.2034, 43.6535, 46.2493, 48.9994, 51.9131, 55, 58.2705, 61.7354]
    resolution = 10
    radiant = 2*np.pi
    period = {
        "1": radiant,
        "1/2": radiant*.5,
        "1/4": radiant*.25,
        "1/8": radiant*.125,
        "1/16": radiant*.0625
    }



class time:

    sampleRate = 44100
    
    def line (seconds, start=0):

        return np.linspace(start, seconds, int(time.sampleRate * seconds))
    
    def lineFromSignal (signal, start=0):

        seconds = signal.shape[0]/time.sampleRate

        return time.line(seconds, start=start)
    
    def minimumSampleRate (frequency):

        '''
        Use the nyquist limit to determine a proper time step.
        '''

        return np.round( 2 * frequency + 1 )



class filter:

    def modulate(carrier_signal, modulation_signal, shift=None):

        # shift the modulation to avoid under modulation
        if shift is None:
            modulation_signal = scale.shiftToNonNegative(modulation_signal)
        else:
            modulation_signal = modulation_signal + shift
        
        return carrier_signal * modulation_signal



class scale:

    def amplitudeRange (signal, min, max):

        sig_max, sig_min = np.max(signal), np.min(signal)
        sig_normalized, scale = signal - sig_min, (max-min)/(sig_max-sig_min)
        return sig_normalized * scale + min
    
    def normalize (signal):

        return scale.amplitudeRange(signal, 0, 1)
    
    def shiftToNonNegative(signal):

        return signal - np.min(signal)

        

class generator:

    def custom(frequency, timeline, generator1, generator2=None, frequencyMultiplier=1, crossFade=0.5, amplitudeScale=1.0):
        
        if generator2:
            f = lambda f, t: (1 + crossFade) * generator1(f, t) + crossFade * generator2(frequencyMultiplier*f, t)  
        else:
            f = lambda f, t: (1 + crossFade) * generator1(f, t)  
        
        return amplitudeScale * f(frequency, timeline)

    def saw (frequency, t):
        
        return ( t*frequency % 1. )

    def sine (frequency, t):

        return np.sin( frequency * units.period["1"] * t )

    def sine_array (frequency, t=None):

        if t is None: t = units.period["1"]
        else: t = t * frequency * units.period["1"]
        return np.sin( np.linspace( 0, t, time.sampleRate * t ) )



class sound:
            
    def play (signal):

        sd.play(np.array(signal), time.sampleRate)

    def setDevice (id):

        if type(id) is not int or id < 0:
            ArgumentError("id must be a non-negative integer.")
        try:
            sd.default.device = int(id)
        except:
            print(f'device id {id} not usable.')
    
    def setRate (frequency=None):

        '''
        If None is provided the default sample rate is taken.
        Override the sample rate in sd object accordingly.
        '''

        if frequency != None:
            time.samplingRate = frequency
        sd.default.samplerate = time.sampleRate

    def showDevices ():

        sd.query_devices()

    def stop ():

        sd.stop()



class keyBoard ():

    '''
    A virtual instrument keyboard. 
    '''

    def __init__ (self):

        self.currentGenerator = None
        self.octave = ["C{}", "C{}#", "D{}", "D{}#", "E{}", "F{}", "F{}#", "G{}", "G{}#", "A{}", "A{}#", "B{}"]
        self.toneDuration = 5
        self.toneRate = {
            "A0": 27.5,
            "A0#": 29.1352,
            "B0": 30.8677,
        }
        self.keyTones = {
            "A0": None,
            "A0#": None,
            "B0": None,
        }
        self.amplification = 1
        self.loadKeyScale()

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

    def applyGenerator (self, generator):

        # override internal generator
        self.currentGenerator = generator

        for tone, rate in self.toneRate.items():

            self.keyTones[tone] = self.amplification * self.currentGenerator(rate, time.line(self.toneDuration))
    
    def bindToKeyboard (self, level):

        # determine by the provided level which octaves to bind
        level = str(level)
        firstOctaveKeys = self.keyTones.keys()
        keysToBind = []
        for iter in [1,2]:
            for key in firstOctaveKeys:
                if level in key:
                    keysToBind.append(key)
            if level < 7:
                level += 1
            else:
                break
    
    def play (self, *tones, strength=0.5, volume=None, duration=None):

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

        sound.play(signal)

        if duration:
            sleep(duration)
            sound.stop()

# ==== global methods ====
def combine (signal_1, signal_2, start=None, mode='add'):

    '''
    main:       main signal
    second:     secondary signal

    The secondary signal will be placed in main.
    '''

    if start and start < 0: 
        ValueError('provided start time at which to combine has to be positive.')

    # decide on main and second channel by length
    main, second = None, None
    if signal_1.shape[0] >= signal_2.shape[0]:
        main, second = signal_1, signal_2
    else:
        main, second = signal_2, signal_1

    # define start index
    if start:
        start = int(time.sampleRate * start) # convert from seconds start to index start
    else:
        start = 0

    # slice the main array in at most 3 parts
    main_slice_1, main_slice_3 = main[:start], None
    overflow = main.shape[0] - start - second.shape[0]
    if overflow < 0:
        main_slice_2 = np.concatenate((main[start:], np.zeros(shape=(-overflow,))))
    elif overflow > 0:
        main_slice_2 = main[start:-overflow]
        main_slice_3 = main[-overflow:]
    else:
        main_slice_2 = main[start:]
    
    # combine by the provided mode
    if mode == 'add':
        main_slice_2 = main_slice_2 + second
    elif mode == 'multiply':
        main_slice_2 = main_slice_2 * second
    elif mode == 'subtract':
        main_slice_2 = main_slice_2 - second
    
    # override main by concatenating accordingly
    if main_slice_1.shape[0] > 0:
        main = np.concatenate((main_slice_1, main_slice_2))
    else:
        main = main_slice_2
    if main_slice_3 and main_slice_3.shape[0] > 0:
        main = np.concatenate((main, main_slice_3))
    
    return main

def plot (signal, start=None, stop=None):

    plt.Figuure

def square (signal):

    return combine(signal, signal, mode='multiply')

# set the sound rate

if __name__ == '__main__':

    T = time.line(seconds=1)

    # # create source signal
    # sig_1 = signal.saw(432 , T)
    # sig_2 = signal.sine(864, T)

    # # construct final signal
    # amplitude = 1
    # #sig_new = sig_1 * amplitude
    # sig_new = amplitude * combine(sig_1, sig_2, mode='multiply', start=0)
    
    # # plot the signal
    # # plt.plot(sig_new)
    # # plt.show()

    # # play the sound
    # try:
    #     sound.setRate()
    #     #sound.showDevices()
    #     #sound.setDevice(10)
    #     sound.play(sig_new)
    #     print('check')
    #     sleep(3)
    # except Exception as e:
    #     print(e)
    #     exit()
    
    #plt.plot(sig_1)
    #plt.plot(sig_2)
    #plt.plot(T_new, sig_new)
    #plt.show()