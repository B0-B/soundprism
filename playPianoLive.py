from soundprism.signal import *
from soundprism.vst import keyBoard

gen = lambda f, t: generator.sine(f, t) * generator.saw(f, t) + 0.5*generator.saw(.5*f, t)
piano = keyBoard()
piano.applyGenerator(gen)
print('Press ESC key to exit the piano ...')
piano.bindTonesToKeyboard(live=True)