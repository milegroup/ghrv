from DataModel import *
from matplotlib.mlab import psd,window_none

dm=DM(Verbose=False)
dm.LoadFileSuunto("/Users/leandro/Tmp/Luis.sdf",factorySettings)
dm.FilterNIHR()
dm.InterpolateNIHR()
# dm.CalculateFrameBasedParams()
print "Complete signal has",len(dm.data["HR"]),"samples"
data = dm.data["HR"][2000:3000]
signal=data/60.0  # First frame in Hz
# print (str(signal))
print "----------------"
print "HR in Hz has",len(signal),"samples"
signal=signal-np.mean(signal)
h=np.hamming(len(signal))
hwp = sum(h*h)/len(h)
signal=h*signal
print "Removing mean and windowing"
powerintime = np.mean(signal*signal)
print "Power (time dimension): ",powerintime," Hz^2"
spec=abs(np.fft.rfft(signal,n=4096*2))
powerinfreq=np.mean(spec*spec)/len(signal)
print "Power (freq dimension): ",powerinfreq," Hz^2"
periodogram = psd(signal,NFFT=len(signal),window=window_none)
print "Power (periodogram): ",2*sum(periodogram[0])[0]/len(signal)," Hz^2"

signal=1000.0/(data/60.0)  # First frame in msec.
# print (str(signal))
print "----------------"
print "HR in msec. has",len(signal),"samples"
signal=signal-np.mean(signal)
h=np.hamming(len(signal))
signal=h*signal
print "Removing mean and windowing"
powerintime = np.mean(signal*signal)
print "Power (time dimension): ",powerintime," msec.^2"
spec=abs(np.fft.rfft(signal,n=4096*4))
powerinfreq=np.mean(spec*spec)/len(signal)
print "Power (freq dimension): ",powerinfreq," msec.^2"
periodogram = psd(signal,NFFT=len(signal),window=window_none)
print "Power (periodogram): ",2*sum(periodogram[0])[0]/len(signal)," msec.^2"