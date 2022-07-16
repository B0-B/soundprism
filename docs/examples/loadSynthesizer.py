from soundprism.signal import *
from soundprism.vst import keyBoard


gen = lambda f,t: combine(generator.sine(f, t), generator.saw(1.5*f, t), mode="multiply")

synth = keyBoard()
synth.applyGenerator(gen)
synth.bindTonesToKeyboard(live=True)