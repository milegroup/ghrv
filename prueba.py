from DataModel import *
dm=DM(Verbose)
dm.LoadFileAscii("/home/leandro/Documentos/Programacion/gHRV/Tmp/RHRV/beat_ascii.txt",factorySettings)
dm.FilterNIHR()
dm.InterpolateNIHR()
dm.CalculateFrameBasedParams()