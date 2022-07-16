#!/usr/bin/env python3

'''
Signal Module
'''

import matplotlib.pyplot as plt 
from argparse import ArgumentError
import numpy as np
from time import sleep
import sounddevice as sd
from pathlib import Path


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

    def clock (frequency, t, t0=0, width=0.1):
        T = 1/frequency
        phase = t + (T-t%T)
        if phase > width:
            return 0
        return 1

    def custom (frequency, timeline, generator1, generator2=None, frequencyMultiplier=1, crossFade=0.5, amplitudeScale=1.0):
        
        if generator2:
            f = lambda f, t: (1 + crossFade) * generator1(f, t) + crossFade * generator2(frequencyMultiplier*f, t)  
        else:
            f = lambda f, t: (1 + crossFade) * generator1(f, t)  
        
        return amplitudeScale * f(frequency, timeline)
    
    def parabola (frequency, t, periodStart=0, periodEnd=1):

        return ( ( ( t * frequency % 1 ) * ( periodEnd - periodStart ) - periodStart )  ) ** 2.

    def saw (frequency, t):
        
        return ( t*frequency % 1. )

    def sine (frequency, t):

        return np.sin( frequency * units.period["1"] * t )

    def sine_array (frequency, t=None):

        if t is None: t = units.period["1"]
        else: t = t * frequency * units.period["1"]
        return np.sin( np.linspace( 0, t, time.sampleRate * t ) )



class sound:
            
    def play (signal, blocking=False):

        sd.play(np.array(signal), time.sampleRate, blocking=blocking)

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

def equal (signal_1, signal_2):

    '''
    Returns a boolean based on the question if the signals equal.
    '''

    return np.array_equal(signal_1, signal_2)

def extrapolate (signal, t):

    # draw period
    T = signal.shape[0]
    x = int( t / T )
    y = T - x

    # extrapolate the signal
    if x > 0:
        for i in range(x):
            signal = np.concatenate(signal, signal)
    if y > 0:
        signal = np.concatenate(signal, signal)
    
    return signal

def plot (signal, start=None, stop=None, savepath=None, label='Signal', show=False, color='#ffd900',  facecolor='black', edgecolor='white'):

    timeline = time.lineFromSignal(signal)
    
    # cut to range
    if start and stop:
        timeline = timeline[int(start*time.sampleRate):int(stop*time.sampleRate)]
        signal = signal[int(start*time.sampleRate):int(stop*time.sampleRate)]

    # build the figure
    dt = np.round(10**6/time.sampleRate,2)
    fig = plt.figure(dpi=150, facecolor=facecolor, edgecolor=edgecolor)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(timeline, signal, color=color, label=label)
    ax.set_facecolor(facecolor)
    ax.set_xlabel(f'time in s in interval {dt}μs')
    ax.yaxis.tick_right()
    ax.spines['right'].set_color(edgecolor)
    ax.xaxis.label.set_color(color)
    ax.tick_params(axis='x', colors=edgecolor)
    ax.tick_params(axis='y', colors=edgecolor)
    plt.legend(facecolor='#383838', edgecolor=edgecolor, labelcolor='linecolor' )
    
    if savepath:
        fig.savefig(Path(savepath))
    
    if show:
        plt.show()

    plt.close(fig)

def square (signal):

    '''
    Returns the squared signal array.
    '''

    return combine(signal, signal, mode='multiply')