from essentia.standard import *
import numpy
import numpy as np
from scipy.io import wavfile
import os
import librosa
import sys

def do_goat(inname, outname, double = False, ins=None):
    rate=44100

    goats = [librosa.core.load("goat1.wav", sr=rate)[0]]
    
    # ampLoader = AudioLoader(filename=inname)
    # ampAud = ampLoader()

    # Load audio file; it is recommended to apply equal-loudness filter for PredominantPitchMelodia
    loader = EqloudLoader(filename=inname, sampleRate=44100)
    audio = loader()
    # print(len(audio))
    # Extract the pitch curve
    # PitchMelodia takes the entire audio signal as input (no frame-wise processing is required)

    #nsamps=int(30.*rate/(137)/2)
    nsamps=int(4000)
    print(nsamps)
    pitch_extractor = PredominantPitchMelodia(frameSize=2048, hopSize=nsamps)
    pitch_values, pitch_confidence = pitch_extractor(audio)
    # volume = average_loudness(ampAud)
    # print(volume)
    # Pitch is estimated on frames. Compute frame time positions
    pitch_times = numpy.linspace(0.0,len(audio)/44100.0,len(pitch_values) )

    print(len(pitch_values))
    print(len(pitch_times))
    delta = pitch_times[1]-pitch_times[0]
    print(delta)

    import math
    pitches = [16.35, 17.32, 18.35, 19.45, 20.6, 21.83, 23.12, 24.5, 25.96, 27.5, 29.14, 30.87, 32.7, 34.65, 36.71, 38.89, 41.2, 43.65, 46.25, 49.0, 51.91, 55.0, 58.27, 61.74, 65.41, 69.3, 73.42, 77.78, 82.41, 87.31, 92.5, 98.0, 103.83, 110.0, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.0, 196.0, 207.65, 220.0, 233.08, 246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.0, 415.3, 440.0, 466.16, 493.88, 523.25, 554.37, 587.33, 622.25, 659.25, 698.46, 739.99, 783.99, 830.61, 880.0, 932.33, 987.77, 1046.5, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98, 1567.98, 1661.22, 1760.0, 1864.66, 1975.53, 2093.0, 2217.46, 2349.32, 2489.02, 2637.02, 2793.83, 2959.96, 3135.96, 3322.44, 3520.0, 3729.31, 3951.07, 4186.01, 4434.92, 4698.63, 4978.03, 5274.04, 5587.65, 5919.91, 6271.93, 6644.88, 7040.0, 7458.62, 7902.13]
    logpitches = list(map(math.log10, pitches))

    def find_pitch(freq):
        if not freq: return -2
        f=math.log10(freq)
        i=min(range(len(pitches)), key=lambda a:abs(f-logpitches[a]))
        return i

    shift_goats = {}
    def get_goat(steps):
        if steps in shift_goats:
            return shift_goats[steps]
        shift_goats[steps] = librosa.effects.pitch_shift(goats[0], rate, steps)
        return shift_goats[steps]

    segs=[]
    print(pitch_values[:100])
    num_samps = 0
    last_freq = -1
    for most_freq in pitch_values:
        #most_freq=f[max(range(len(amps)), key=amps.__getitem__)]
        most_freq=find_pitch(most_freq)
        #if most_freq>=0 and last_freq>=0 and abs(most_freq-last_freq)>13: most_freq=last_freq
        if most_freq!=last_freq:
            if last_freq==-2:
                segs.append(np.zeros(nsamps*num_samps))
                num_samps=0
                last_freq=most_freq
                continue
            if last_freq!=-1:
                #cur_wave = np.sin(np.arange(nsamps*num_samps)/rate*last_freq*2*3.14159265)
                #segs.append(cur_wave)
                #cur_wave*=32766/2

                if double: last_freq=min(last_freq+12, len(pitches)-1)
                goat_note = get_goat(last_freq-72)[:nsamps*num_samps]
                #goat_note = get_goat(math.log(last_freq/1046.5*2, 2**(1./12)))[:nsamps*num_samps]
                segs.append(goat_note)
                #if nsamps*num_samps>len(goats[0]):
                #    segs.append(np.zeros(nsamps*num_samps-len(goats[0])))

            num_samps=0
            last_freq=most_freq
        
        num_samps+=1
            
    outWav = np.concatenate(segs)

    if ins:
        kar = librosa.core.load(ins, rate)
        kar = np.pad(kar, outWav.shape)
        outWav = (outWav+kar)/2

    print(len(segs))
    print(len(outWav))
    librosa.output.write_wav(outname, outWav, rate, True)

if __name__=='__main__':
    do_goat(sys.argv[1], "out.wav")
    os.system("rm out.mp3")
    os.system("ffmpeg -i out.wav out.mp3")
