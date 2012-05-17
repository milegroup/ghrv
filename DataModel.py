# -*- coding:utf-8 -*-


#   ----------------------------------------------------------------------
#   gHRV: a graphical application for Heart Rate Variability analysis
#   Copyright (C) 2012  Milegroup - Dpt. Informatics
#      University of Vigo - Spain
#      www.milegroup.net
#
#   Authors:
#     - Leandro Rodríguez-Liñares
#     - Arturo Méndez
#     - María José Lado
#     - Xosé Antón Vila
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#   ----------------------------------------------------------------------


import os, random
import numpy as np
from sys import platform
from configvalues import *
import matplotlib

listofsettings=['interpfreq','windowsize','windowshift','ulfmin','ulfmax','vlfmin','vlfmax','lfmin','lfmax','hfmin','hfmax','name']

class DM:
        
    data={}
    labelColors=['Orange','cyan','red','blue','green','yellow','grey','pink','purple','maroon','lightgreen']

    def __init__(self,Verbose):
        """Initialization of the data model"""
        self.ClearAll()
            
    def ClearAll(self):
        self.data={}
        self.data["Verbose"]=Verbose
        
        self.data["name"]=""
        #self.data["version"]=Version
        self.ClearColors()
        self.ClearBands()
        if (self.data["Verbose"]==True):
            print("** Clearing all data")
            
                
    def ClearColors(self):
        """Resets colors for episodes"""
        self.data["ColorIndex"]=0
        self.data["DictColors"]={}
        
    def ClearBands(self):
        self.data["Bands"]=["LF/HF","ULF","VLF","LF","HF","Power","Mean HR","HR STD","pNN50","rmssd","Heart rate"]
        self.data["VisibleBands"]=["LF/HF","ULF","VLF","LF","HF","Heart rate"]
        self.data["FixedBands"]=["Heart rate"]
        
         
    def AssignEpisodeColor(self,Tag):
        """Assigns color to episodes tags"""
        if self.data["ColorIndex"] == len(self.labelColors)-1:
            self.data["DictColors"][Tag]=(random.random(),random.random(),random.random())
        else:
            self.data["DictColors"][Tag]=self.labelColors[self.data["ColorIndex"]]
            self.data["ColorIndex"] += 1
                    
    def GetEpisodeColor(self,Tag):
        """Returns color assigned to an episode Tag"""
        return self.data["DictColors"][Tag]
                
    def LoadBeatAscii(self,beatsFile,settings):
        """Loads beats from ascii file
        Beats instants must be in seconds, and one per line"""
        
        if (self.data["Verbose"]==True):
            print("** Loading beats file "+beatsFile)
            print("   Calculating non-interpolated heart rate")
                
        self.data["BeatTime"]=np.loadtxt(beatsFile)
        
        self.data["niHR"] = 60.0/(self.data["BeatTime"][1:]-self.data["BeatTime"][0:-1])
        self.data["niHR"] = np.insert(self.data["niHR"],[0],self.data["niHR"][0])

        self.data["RR"] = 1000.0*(self.data["BeatTime"][1:]-self.data["BeatTime"][0:-1])
        self.data["RR"] = np.insert(self.data["RR"],[0],self.data["RR"][0])
        
        if (self.data["Verbose"]):
            print("   BeatTime: "+str(len(self.data["BeatTime"]))+" points (max: "+str(self.data["BeatTime"][-1])+")")
            print("   niHR: "+str(len(self.data["niHR"]))+" points")
            print("   RR: "+str(len(self.data["RR"]))+" points")
                
        for k in settings.keys():
            self.data[k]=float(settings[k])
        if (self.data["Verbose"]):
            print("   Parameters set to default values")
            
        self.data["name"]=os.path.splitext(os.path.basename(beatsFile))[0]
        
        if (self.data["Verbose"]):
            print("   Project created: "+self.data["name"])
            
        self.data["version"]=Version
    
    def LoadBeatPolar(self,polarFile,settings):
        """Loads beats from polar file
        Polar files contain rr series, expresed in milliseconds"""
        
        if (self.data["Verbose"]==True):
            print("** Loading polar file "+polarFile)
        
        self.data["RR"]=[]
        dataFound=False
        File = open(polarFile,'r')
        for line in File:
            if dataFound:
                data=line.strip()
                if data:
                    self.data["RR"].append(float(data))
            if line.strip() == "[HRData]":
                dataFound=True
        File.close()
        
        self.data["RR"]=np.array(self.data["RR"])
        self.data["BeatTime"]=np.cumsum(self.data["RR"])/1000.0
        self.data["niHR"]=60.0/(self.data["RR"]/1000.0)
        
        if (self.data["Verbose"]==True):
            print("   BeatTime: "+str(len(self.data["BeatTime"]))+" points (max: "+str(self.data["BeatTime"][-1])+")")
            print("   RR: "+str(len(self.data["RR"]))+" points")
            print("   niHR: "+str(len(self.data["niHR"]))+" points")
        
        for k in settings.keys():
            self.data[k]=float(settings[k])
        if (self.data["Verbose"]):
            print("   Parameters set to default values")
            
        self.data["name"]=os.path.splitext(os.path.basename(polarFile))[0]
        
        if (self.data["Verbose"]):
            print("   Project created: "+self.data["name"])
            
        self.data["version"]=Version
        
    def LoadBeatSuunto(self,suuntoFile,settings):
        """Loads beats from suunto file
        suunto files contain rr series, expresed in milliseconds"""
        
        if (self.data["Verbose"]==True):
            print("** Loading suunto file "+suuntoFile)
        
        self.data["RR"]=[]
        dataFound=False
        File = open(suuntoFile,'r')
        for line in File:
            if dataFound:
                data=line.strip()
                if data:
                    self.data["RR"].append(float(data))
            if line.strip() == "[CUSTOM1]":
                dataFound=True
        File.close()
        
        self.data["RR"]=np.array(self.data["RR"])
        self.data["BeatTime"]=np.cumsum(self.data["RR"])/1000.0
        self.data["niHR"]=60.0/(self.data["RR"]/1000.0)
        
        if (self.data["Verbose"]==True):
            print("   BeatTime: "+str(len(self.data["BeatTime"]))+" points (max: "+str(self.data["BeatTime"][-1])+")")
            print("   RR: "+str(len(self.data["RR"]))+" points")
            print("   niHR: "+str(len(self.data["niHR"]))+" points")
        
        for k in settings.keys():
            self.data[k]=float(settings[k])
        if (self.data["Verbose"]):
            print("   Parameters set to default values")
            
        self.data["name"]=os.path.splitext(os.path.basename(suuntoFile))[0]
        
        if (self.data["Verbose"]):
            print("   Project created: "+self.data["name"])
            
        self.data["version"]=Version
                     
            
                     
            
    def LoadEpisodesAscii(self,episodesFile):
        """Reads espisodes from ascii file
            episodesFile -> file containing episodes. Must be in the following format:
                Init_Time       Resp_Events     Durat   SaO2
                00:33:00        GEN_HYPO        120.0   82.9
                01:30:00        OBS_APNEA       60.0    81.0
                ...
                
            First line of file is discarded
            Duration in seconds"""
                
        if (self.data["Verbose"]):
            print("** Opening episodes file: "+episodesFile)
                
        epFile = open(episodesFile,'r')
        index=0
        for line in epFile:
            if index!=0:
                linedata=line.strip().split()
                if not self.data.has_key("EpisodesType"):
                    self.__CreatesEpisodesInfo()
                self.data["EpisodesType"].append(linedata[1])
                self.data["EpisodesDuration"].append(float(linedata[2]))
                HMS=linedata[0].split(":")
                self.data["EpisodesInitTime"].append(float(HMS[0])*3600.0+float(HMS[1])*60.0+float(HMS[2]))
            index += 1
        epFile.close()
                
        self.data["EpisodesVisible"]=list(set(self.data["EpisodesType"]))
                
        if (self.data["Verbose"]):
            print("   Read "+str(len(self.data["EpisodesType"]))+" episodes from file")
            print("   Read "+str(len(self.data["EpisodesVisible"]))+" types of episodes")
                    
    def LoadDataModel(self,datamodelFile):
        """Loads the data model from a zip file"""
        import zipfile, tempfile, shutil
        tempDir = tempfile.mkdtemp(prefix="gHRV")
        if self.data["Verbose"]:
            print("** Loading project: "+datamodelFile)
            print("   Temporal directory: "+tempDir)
                
        zf = zipfile.ZipFile(datamodelFile, mode='r')
    
        for zfitem in zf.namelist():
            zf.extract(zfitem,tempDir)
            fileName=tempDir+os.sep+zfitem
            dataName=zfitem[1:]
            #print("--- Reading file: "+fileName)
            if zfitem[0]=="#":
                self.data[dataName]=np.loadtxt(fileName)
                #print("   Length: "+str(len(self.data[dataName])))
            else:
                tempF = open(fileName,'r')
                if dataName=="name":
                    self.data[dataName]=tempF.read()
                else:
                    self.data[dataName]=eval(tempF.read())
                tempF.close()
                #print("   Data: "+str(self.data[dataName]))
        zf.close()
        
        #print ("Keys: "+str(self.data.keys()))
        
        #print self.data["name"]
        
        if "interpfreq" not in self.data.keys(): # Project generated with gHRV 0.17
            if self.data['Verbose']:
                print("   Importing project from gHRV 0.17")
            if 'FreqHR' in self.data.keys():
                del self.data['FreqHR']
            for k in factorySettings.keys():
                self.data[k]=float(factorySettings[k])
            self.data['name']='mygHRVproject'
            
        if "version" not in self.data.keys(): # Project generated with gHRV 0.18 or older
            if self.data['Verbose']:
                print("   Importing project from gHRV 0.18 or older")
                self.ClearBands()
                if self.HasFrameBasedParams():
                    self.ClearFrameBasedParams()
                    self.CalculateFrameBasedParams()
              
        shutil.rmtree(tempDir)
        self.data["version"]=Version
        
            
    def GetSettings(self):
        """Returns parameters of the project"""
        settings={}
        for k in listofsettings:
            settings[k]=str(self.data[k])
        return settings
    
    def SetSettings(self,settings):
        """Sets parameters of the project"""
        for k in listofsettings:
            if k != 'name':
                self.data[k]=float(settings[k])
            else:
                self.data[k]=settings[k]
   
                        
    def SaveDataModel(self,datamodelFile):
        """Saves the data model into a zip file"""
        
        import zipfile,shutil,tempfile
        
        tempDir = tempfile.mkdtemp(prefix="gHRV")
        
        
        if self.data["Verbose"]:
            print("** Saving project: "+datamodelFile)
            #print("   Temporal directory: "+tempDir)
                            
        for kData in self.data.keys():
            if type(self.data[kData])==np.ndarray:
                tempFName=tempDir+os.sep+"#"+str(kData)
                np.savetxt(tempFName,self.data[kData])
            else:
                tempFName=tempDir+os.sep+"%"+str(kData)
                tempF = open(tempFName,'w')
                tempF.write(str(self.data[kData]))
                tempF.close()
                        
        zf = zipfile.ZipFile(datamodelFile, mode='w',compression=zipfile.ZIP_DEFLATED)          
        list = os.listdir(tempDir)
        for file in list:
            #print("File: "+str(file))
            zf.write(tempDir+os.sep+file,str(file))
        zf.close()
        
        shutil.rmtree(tempDir)
        
    def SaveFrameBasedData(self,dataFile,listOfBands,SepChar,RHeader,CHeader):
            
        if self.data["Verbose"]:
            print("** Saving frame-based data: "+dataFile)
            print("   List of bands: "+str(listOfBands))
            print("   Separator: '"+SepChar+"'")
            print("   Row header: "+str(RHeader))
            print("   Column header: "+str(CHeader))
        
        NumFrames=len(self.data["ULF"])
        File = open(dataFile,'w')
        
        if RHeader:
            FirstColumn = True
            if CHeader:
                File.write("Frame")
                FirstColumn=False
            for Band in listOfBands:
                if FirstColumn:
                    FirstColumn=False
                else:
                    File.write(SepChar)
                File.write(Band)
            File.write("\n")
        
        for x in range(NumFrames):
            FirstColumn = True
            if CHeader:
                File.write(str(x))
                FirstColumn=False
            for Band in listOfBands:
                if FirstColumn:
                    FirstColumn = False
                else:
                    File.write(SepChar)
                if Band == "LF/HF":
                    File.write(str(self.data["LFHF"][x]))
                else:
                    File.write(str(self.data[Band][x]))
            File.write("\n")
            
        File.close()
        
        if self.data["Verbose"]:
            print("   No. of lines: "+str(NumFrames))
        
                                        
    def ClearEpisodes(self):
        """Purges episodes from data model"""
        del self.data["EpisodesType"]
        del self.data["EpisodesInitTime"]
        del self.data["EpisodesDuration"]
        del self.data["EpisodesVisible"]
        if (self.data["Verbose"]):
            print("** Episodes removed from data model")
            
    def ClearHR(self):
        """Purges interpolated HR from data model"""
        del self.data["HR"]
        del self.data["PlotHRXMin"]
        del self.data["PlotHRXMax"]
        if (self.data["Verbose"]):
            print("** Interpolated HR removed from data model")
            
    def ClearFrameBasedParams(self):
        """Purges power bands information from data model"""
        del self.data["ULF"]
        del self.data["VLF"]
        del self.data["LF"]
        del self.data["HF"]
        del self.data["LFHF"]
        if (self.data["Verbose"]):
            print("** Power bands removed from data model")
                        
    def __CreatesEpisodesInfo(self):
        """Creates blank episodes structure"""
        self.data["EpisodesType"]=[]
        self.data["EpisodesInitTime"]=[]
        self.data["EpisodesDuration"]=[]
        self.data["EpisodesVisible"]=[]
                        
    def AddEpisode(self,init,end,tag):
        """Adds information of one episode"""
        if (self.data["Verbose"]):
            print("** Adding an episode ({0:.2f},{1:.2f}) with label {2:s}".format(init,end,tag))
                
        if not self.data.has_key("EpisodesType"):
            self.__CreatesEpisodesInfo()
        
        self.data["EpisodesType"].append(tag)
        self.data["EpisodesInitTime"].append(init)
        self.data["EpisodesDuration"].append(float(end)-float(init))
        if tag not in self.data["EpisodesVisible"]:
            self.data["EpisodesVisible"].append(tag)
                        
    def ReplaceHRVectors(self,xvector,yvector,rrvector):
        """After EditNIHR the beats (Time, niHR and RR) are replaced"""
        
        self.data["BeatTime"]=xvector
        self.data["niHR"]=yvector
        self.data["RR"]=rrvector
        if (self.data["Verbose"]):
            print("** HR vectors replaced")
            print("   BeatTime: "+str(len(self.data["BeatTime"]))+" points (max: "+str(self.data["BeatTime"][-1])+")")
            print("   niHR: "+str(len(self.data["niHR"]))+" points")
            print("   RR: "+str(len(self.data["RR"]))+" points")

                                
    def FilterNIHR(self,winlength=50,last=13,minbpm=24,maxbpm=198):
        """Removes outliers from non interpolated heart rate"""
        if (self.data["Verbose"]):
           print ("** Filtering non-interpolated heart rate")
           print ("   Number of original beats: "+str(len(self.data["niHR"])))

        # threshold initialization
        ulast=last
        umean=1.5*ulast

        index=1
        while index<len(self.data["niHR"])-1:
            v=self.data["niHR"][max(index-winlength,0):index]
            M=np.mean(v)
            if ( ( (100*abs((self.data["niHR"][index]-self.data["niHR"][index-1])/self.data["niHR"][index-1]) < ulast) |
            (100*abs((self.data["niHR"][index]-self.data["niHR"][index+1])/self.data["niHR"][index+1]) < ulast) |
            (100*abs((self.data["niHR"][index]-M)/M) < umean) )
            & (self.data["niHR"][index] > minbpm) & (self.data["niHR"][index] < maxbpm)):
                index += 1
            else:
                self.data["BeatTime"]=np.delete(self.data["BeatTime"],index)
                self.data["niHR"]=np.delete(self.data["niHR"],index)
                self.data["RR"]=np.delete(self.data["RR"],index)

        if (self.data["Verbose"]):
            print ("   Number of filtered beats: "+str(len(self.data["BeatTime"])))

                            
    def InterpolateNIHR(self):
        "Interpolates instantaneous heart rate (linear method)"   

        from scipy import interpolate

        if self.data["Verbose"]:
            print ("** Interpolating instantaneous heart rate (method: linear interpolation)")
            print ("   Frequency: "+str(self.data["interpfreq"])+" Hz.")


        
        xmin=int(self.data["BeatTime"][0])
        xmax=int(self.data["BeatTime"][-1])+1
        step=1.0/self.data["interpfreq"]
        
        BeatTmp = np.insert(self.data["BeatTime"],0,self.data["BeatTime"][0]-1)
        BeatTmp = np.append(BeatTmp,BeatTmp[-1]+1)
        niHRTmp = np.insert(self.data["niHR"],0,self.data["niHR"][0])
        niHRTmp = np.append(niHRTmp,niHRTmp[-1])
        
        
        tck = interpolate.interp1d(BeatTmp,niHRTmp)
        xnew = np.arange(xmin,xmax,step)

        if self.data["Verbose"]:
            print ("   Original signal from: "+str(self.data["BeatTime"][0])+" to "+str(self.data["BeatTime"][-1]))
            print ("   Interpolating from "+str(xmin)+" to "+str(xmax)+" seconds")
           
        self.data["HR"] = tck(xnew)

        if self.data["Verbose"]:
            print ("   Obtained "+str(len(self.data["HR"]))+" points")
            
                
    def CalculateFrameBasedParams(self):
        """Calculates power per band
            size -> size of window (seconds)
            shift -> displacement of window (seconds)"""
                
        def Freq2Sample(f,numfsamples):
            """Obtain spectrum sample from frequency"""
            return (2*f*numfsamples/self.data["interpfreq"])
                
        if self.data["Verbose"]:
            print("** Calculating power per band")
            
                
        signal=self.data["HR"]/60.0
        shiftsamp=self.data['windowshift']*self.data["interpfreq"]
        sizesamp=self.data['windowsize']*self.data["interpfreq"]
        
        numframes=int(((len(signal)-sizesamp)/shiftsamp)+1.0)
        
        
        if self.data["Verbose"]:
            print("   Signal length: "+str(len(signal))+" samples")
            print("   Frame length: "+str(sizesamp)+" samples")
            print("   Frame shift: "+str(shiftsamp)+" samples")
            print("   Number of frames: "+str(numframes))
            
        self.data["ULF"]=[]
        self.data["VLF"]=[]
        self.data["LF"]=[]
        self.data["HF"]=[]
        self.data["LFHF"]=[]
        self.data["Power"]=[]
        self.data["Mean HR"]=[]
        self.data["HR STD"]=[]
        self.data["pNN50"]=[]
        self.data["rmssd"]=[]
                
        for indexframe in range(numframes):
            begframe=int(indexframe*shiftsamp)
            endframe=int(begframe+sizesamp) # samples
            frame=signal[begframe:endframe]
            
            begtime=indexframe*self.data['windowshift']
            endtime=begtime+self.data['windowsize'] # seconds
            
            h=np.hamming(len(frame))
            frame=frame-np.mean(frame)
            frame=frame*h
            #print("-----------------------")
            #print("Frame "+str(indexframe))
            spec=abs(np.fft.rfft(frame)) # Sólo la mitad positiva del espectro
            #print("Frame power (time): "+str(np.sum(frame*frame)))
            #print("Frame power (frequency): "+str(2*np.sum(spec*spec)/len(frame)))
            
            ulfspec=spec[Freq2Sample(self.data['ulfmin'],len(spec)):Freq2Sample(self.data['ulfmax'],len(spec))]
            ulfpower=2*np.sum(ulfspec*ulfspec)/len(frame) # Hz^2
            self.data["ULF"].append(ulfpower)
            #print("ULF power: "+str(ulfpower))
            
            vlfspec=spec[Freq2Sample(self.data['vlfmin'],len(spec)):Freq2Sample(self.data['vlfmax'],len(spec))]
            vlfpower=2*np.sum(vlfspec*vlfspec)/len(frame) # Hz^2
            self.data["VLF"].append(vlfpower)
            #print("VLF power: "+str(vlfpower))
            
            lfspec=spec[Freq2Sample(self.data['lfmin'],len(spec)):Freq2Sample(self.data['lfmax'],len(spec))]
            lfpower=2*np.sum(lfspec*lfspec)/len(frame) # Hz^2
            self.data["LF"].append(lfpower)
            #print("LF power: "+str(lfpower))
            
            hfspec=spec[Freq2Sample(self.data['hfmin'],len(spec)):Freq2Sample(self.data['hfmax'],len(spec))]
            hfpower=2*np.sum(hfspec*hfspec)/len(frame)  # Hz^2
            self.data["HF"].append(hfpower)
            #print("HF: "+str(hfpower))
            
            totalpower=2*np.sum(spec*spec)/len(frame)  # Hz^2
            self.data["Power"].append(totalpower)
            
            #print("ULF+VLF+LF+HF power: "+str(ulfpower+vlfpower+lfpower+hfpower))
            
            self.data["LFHF"].append(lfpower/hfpower)
            #print("LF/HF: "+str(lfpower/hfpower))
            
            frameHR = self.data["HR"][begframe:endframe]
            self.data["Mean HR"].append(np.mean(frameHR))
            self.data["HR STD"].append(np.std(frameHR))            
            
            BeatsFrame = [x for x in self.data["BeatTime"] if x>=begtime and x<=endtime]
            frameRR = 1000.0*np.diff(BeatsFrame)
            #print "Window has ",len(BeatsFrame), " beats"
            #print "frameHR - ",len(frameHR)
            #print "frameRR - ",len(frameRR)
            RRDiffs=np.diff(frameRR)
            RRDiffs50 = [x for x in np.abs(RRDiffs) if x>50]
            self.data["pNN50"].append(100.0*len(RRDiffs50)/len(RRDiffs))
            self.data["rmssd"].append(np.sqrt(np.mean(RRDiffs**2)))
                
        self.data["ULF"]=np.array(self.data["ULF"])
        self.data["VLF"]=np.array(self.data["VLF"])
        self.data["LF"]=np.array(self.data["LF"])
        self.data["HF"]=np.array(self.data["HF"])
        self.data["LFHF"]=np.array(self.data["LFHF"])
        self.data["Power"]=np.array(self.data["Power"])
        self.data["Mean HR"]=np.array(self.data["Mean HR"])
        self.data["HR STD"]=np.array(self.data["HR STD"])
        self.data["pNN50"]=np.array(self.data["pNN50"])
        self.data["rmssd"]=np.array(self.data["rmssd"])
                
                    
        
    def GetHRDataPlot(self):
        if self.HasInterpolatedHR():
            xvector = np.linspace(self.data["BeatTime"][0], self.data["BeatTime"][-1], len(self.data["HR"]))
            yvector = self.data["HR"]
        else: 
            xvector = self.data["BeatTime"]
            yvector = self.data["niHR"]
        return (xvector,yvector)
        
    def GetName(self):
        return self.data["name"]
        
        
    def CreateReport(self,DirName,ReportName):
        
        def WriteTitleLine(fileHandler):
            fileHandler.write('<table cellspacing="5" border="0" width="'+str(HTMLPageWidth)+'" bgcolor="'+ReportWindowTitleColor+'">\n<tr><td align="left" ><b><font color="white" size="+1">gHRV analysis report</font></b></td></tr></table>\n')
            
        # -----------------
            
        def WriteSubtitleLine(fileHandler,text):
            fileHandler.write('<table cellspacing="5" border="0" width="'+str(HTMLPageWidth)+'">\n<tr><td align="left" ><font color='+ReportWindowTitleColor+'><b>'+text+'</b></font></td></tr></table>\n')
            
        # -----------------
        
        
        reportSubDir='report_files'
        os.mkdir(DirName+os.sep+reportSubDir)
        
        if (self.data["Verbose"]==True):
            print("** Creating report in directory "+DirName)
            
        FileName = DirName + os.sep + ReportName
        File = open(FileName,'w')
        File.write(HTMLHead)
        
        # Line header   
        WriteTitleLine(File)
        File.write("<hr>\n")
        
        # HR Plot
        WriteSubtitleLine(File,'File details')        
        info=self.GetInfoFile()
        self.CreatePlotFile("HR",DirName+os.sep+reportSubDir+os.sep+"HR.png",plotHRWidth,plotHRHeight)
        
        File.write('<table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'"><tr align="center"> <td width="50%"><b>Name: </b><i>'+info["name"]+'</i></td><td width="50%"><b>Signal length: </b><i>'+info["length"]+'</i></td></tr></table>\n')

        File.write('<table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'"><tr align="center"><td><img src="./'+reportSubDir+'/HR.png"/></td></tr></table>\n')
        
        File.write("<hr>\n")
        
        
        # Histogram and time-based parameters
        WriteSubtitleLine(File,'Time-domain analysis')          
        info=self.GetInfoTime()
        self.CreatePlotFile("HRHistogram",DirName+os.sep+reportSubDir+os.sep+"HRHistogram.png",plotHRHistogramWidth,plotHRHistogramHeight)
        File.write('<table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'">\n')
        File.write('<tr align="center"><td><img src="./'+reportSubDir+'/HRHistogram.png"/></td><td align="left">\n')
        File.write('<font size="-1">\n<table align="left">')
        File.write('<tr><td><b>No. of beats: </b><i>'+info["beats"]+'</i></td></tr>')
        File.write('<tr><td><b>Mean HR: </b><i>'+info["meanhr"]+' bps</i></td></tr>')
        File.write('<tr><td><b>STD HR: </b><i>'+info["stdhr"]+' bps</i></td></tr>')
        File.write('<tr><td><b>Mean RR (AVNN): </b><i>'+info["meanrr"]+' msec.</i></td></tr>')
        File.write('<tr><td><b>STD RR (SDNN): </b><i>'+info["stdrr"]+' msec.</i></td></tr>')
        File.write('<tr><td><b>SDANN: </b><i>'+info["sdann"]+' msec.</i></td></tr>')
        File.write('<tr><td><b>SDNNIDX: </b><i>'+info["sdnnidx"]+' msec.</i></td></tr>')
        File.write('</table>\n</font></td>\n')
        File.write('<td align="left"><font size="-1"><table>\n')
        File.write('<tr><td><b>pNN50: </b><i>'+info["pnn50"]+'%</i></td></tr>')
        File.write('<tr><td><b>rMSSD: </b><i>'+info["rmssd"]+' msec.</i></td></tr>')
        File.write('<tr><td><b>IRRR: </b><i>'+info["irrr"]+' msec.</i></td></tr>')
        File.write('<tr><td><b>MADRR: </b><i>'+info["madrr"]+' msec.</i></td></tr>')
        File.write('<tr><td><b>TINN: </b><i>'+info["tinn"]+' msec.</i></td></tr>')
        File.write('<tr><td><b>HRV index: </b><i>'+info["hrvi"]+'</i></td></tr>')
        File.write('</table>\n</font>\n')
        File.write('</td></tr>\n')
        File.write('</table>\n')
        File.write("<hr>\n")
        
        # Frame-based parameters
        if self.HasInterpolatedHR():
            if self.HasFrameBasedParams()==False:
                self.CalculateFrameBasedParams()
            WriteSubtitleLine(File,'Frequency-domain analysis')
            self.CreatePlotFile("FB",DirName+os.sep+reportSubDir+os.sep+"FB.png",plotFBWidth,plotFBHeight)
            File.write('<table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'">\n')
    
            File.write('<tr align="center"><td><img src="./'+reportSubDir+'/FB.png"/></td></tr>\n')
            File.write('</table>\n')
            File.write("<hr>\n")
            
        
        
        File.write(HTMLTail)
        File.close()
        
        
        
        

    def GetInfoFile(self):
        info={}
        if self.data["name"]=="":
            info["name"]="NoName"
        else:
            info["name"]=self.data["name"]
        
        info["length"]="{0:.2f}".format((self.data["BeatTime"][-1]-self.data["BeatTime"][0]))+" seconds"
            
        return info
    
    def GetInfoTime(self, winsize=300.0, interval=7.8125):
        from scipy.stats.mstats import mquantiles
        
        info={}
        info["beats"]="{0:.2f}".format((len(self.data["BeatTime"])))
        info["minhr"]="{0:.2f}".format(min(self.data["niHR"]))
        info["maxhr"]="{0:.2f}".format(max(self.data["niHR"]))
        info["meanhr"]="{0:.2f}".format(np.mean(self.data["niHR"]))
        info["meanrr"]="{0:.2f}".format(np.mean(self.data["RR"]))
        info["stdhr"]="{0:.2f}".format(np.std(self.data["niHR"],ddof=1))
        info["stdrr"]="{0:.2f}".format(np.std(self.data["RR"],ddof=1))
        
        RRWindowMean=[]
        RRWindowSD=[]
        winmin=0.0
        winmax=winsize
        while winmax < self.data["BeatTime"][-1]:
            winrr=[self.data["RR"][i] for i in range(len(self.data["RR"])) if self.data["BeatTime"][i]>winmin and self.data["BeatTime"][i]<winmax]
            RRWindowMean.append(np.mean(winrr))
            RRWindowSD.append(np.std(winrr,ddof=1))
            winmin=winmin+winsize
            winmax=winmax+winsize
                
        info["sdann"]="{0:.2f}".format(np.std(RRWindowMean,ddof=1))
        info["sdnnidx"]="{0:.2f}".format(np.mean(RRWindowSD))
        
        RRDiffs=np.diff(self.data["RR"])
        RRDiffs50 = [x for x in np.abs(RRDiffs) if x>50]
        info["pnn50"]="{0:.2f}".format(100.0*len(RRDiffs50)/len(RRDiffs))
        info["rmssd"]="{0:.2f}".format(np.sqrt(np.mean(RRDiffs**2)))
        
        RRQuant=mquantiles(RRDiffs)
        info["irrr"]="{0:.2f}".format(RRQuant[-1]-RRQuant[0])
        
        info["madrr"]="{0:.2f}".format(np.median(np.abs(RRDiffs)))
        
        minRR = min(self.data["RR"])
        maxRR = max(self.data["RR"])
        medRR = (minRR+maxRR)/2
        lowhist = medRR - interval * np.ceil((medRR - minRR)/interval)
        longhist = int(np.ceil((maxRR - lowhist)/interval) + 1)
        vecthist=np.array([lowhist+interval*i for i in range(longhist)])
        h=np.histogram(self.data["RR"],vecthist)
        area = float(len(self.data["RR"])) * interval
        maxhist = max(h[0])
        info["tinn"] = "{0:.2f}".format(area/maxhist)
        info["hrvi"] = "{0:.2f}".format(float(len(self.data["RR"]))/maxhist)
   
        return info
        
        
    def DataEditHR(self):
        """Data for edit non interpolated Heart Rate"""
        return (self.data["BeatTime"], self.data["niHR"], self.data["RR"])
    
    def DataPlotHasVisibleEpisodes(self):
        """Checks if there are visible episodes in the data model"""
        if not self.data.has_key("EpisodesType"):
            return(False)
        else:
            if (len(self.data["EpisodesVisible"])>0):
                return(True)
            else:
                return(False)
            
    def HasEpisodes(self):
        """Checks if there are episodes in the data model"""
        if self.data.has_key("EpisodesType"):
            return(True)
        else:
            return(False)
                        
    def HasHR(self):
        """Checks if there are data for plotting HR (interpolated or not)"""
        if self.data.has_key("niHR") or self.data.has_key("HR"):
            return True
        else:
            return False
            
    def HasInterpolatedHR(self):
        """Checks if there are data of interpolated HR"""
        if self.data.has_key("HR"):
            return True
        else:
            return False
                        
    def HasFrameBasedParams(self):
        """Checks if there is information of power bands"""
        if self.data.has_key("ULF"):
            return(True)
        else:
            return(False)
            
    def GetEpisodes(self):
        """Gets all the information of the episodes for time plotting"""
        return(self.data["EpisodesType"],self.data["EpisodesInitTime"],self.data["EpisodesDuration"],self.data["EpisodesVisible"])
    
    def GetVisibleEpisodes(self):
        """Gives the tags of the episodes (all and visible) in the data model"""
        if self.HasEpisodes():
            return (list(set(self.data["EpisodesType"])),self.data["EpisodesVisible"])
        else:
            return ([],set([]))
    
    def SetVisibleEpisodes(self,ListOfEp):
        """Updates the list of visible episodes"""
        self.data["EpisodesVisible"]=ListOfEp
                
    def GetEpisodesTags(self):
        """Gets the list of tags of all the episodes (both visible and hidden)"""
        if self.HasEpisodes():
            return(list(set(self.data["EpisodesType"])))
        else:
            return([])

    def GetVisibleBands(self):
        """Gets information of bands to plot"""
        return (self.data["Bands"],self.data["VisibleBands"])
    
    def GetFixedBands(self):
        """Gets informations of bands always in plot"""
        return self.data["FixedBands"]
    
    def GetHeartRatePlotTitle(self):
        """Gets title of Heart Rate Plot"""
        if self.data.has_key("HR"):
            return (self.data["name"] + " - Interpolated HR")
        else:
            return(self.data["name"] + " - Non interpolated HR")
        
    def SetVisibleBands(self,ListOfBands):
        """Changes the list of bands visible in plot"""
        self.data["VisibleBands"]=ListOfBands
            
    def GetFrameBasedDataPlot(self):
        """Returns data necessary for frame-based plot"""
        return(self.data["LFHF"], self.data["ULF"], self.data["VLF"], self.data["LF"], self.data["HF"], self.data["Power"],self.data["Mean HR"], self.data["HR STD"], self.data["pNN50"], self.data["rmssd"], self.data["HR"])
        
    
    def CreatePlot(self,plotType):
        
        """Creates and opens a new plot with HR"""
        fig = matplotlib.pyplot.figure()
        axes = fig.add_subplot(1,1,1)
        if plotType=="HR":
            self.CreatePlotHREmbedded(axes)
        if plotType=="HRHistogram":
            self.CreatePlotHRHistogramEmbedded(axes)
        if plotType=="RRHistogram":
            self.CreatePlotRRHistogramEmbedded(axes)
        matplotlib.pyplot.grid(True)
        matplotlib.pyplot.show()
        
       
        
    def CreatePlotFile(self,plotType,filename,width,height):
        """Creates and saves a new plot with HR"""
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        fig = Figure()
        fig.set_size_inches((width/plotDPI,height/plotDPI))
        
        if plotType=="HR":
            self.CreatePlotHREmbedded(fig)
        if plotType=="HRHistogram":
            self.CreatePlotHRHistogramEmbedded(fig)
        if plotType=="RRHistogram":
            self.CreatePlotRRHistogramEmbedded(fig)
        if plotType=="FB":
            self.CreatePlotFBEmbedded(fig)
        canvas = FigureCanvasAgg(fig)
        canvas.print_figure(filename, dpi=plotDPI)
        
        
    def CreatePlotHRHistogramEmbedded(self,fig):
        axes = fig.add_subplot(1,1,1)
        xvector, yvector = self.GetHRDataPlot()
        axes.hist(yvector, 30, normed=1, facecolor="blue")
        axes.set_xlabel("HR (beats/min.)")
        axes.set_ylabel("Probability")
        axes.set_title("HR histogram")
        axes.grid(True)
        matplotlib.pyplot.show()
        
    def CreatePlotRRHistogramEmbedded(self,fig):
        axes = fig.add_subplot(1,1,1)
        axes.hist(self.data["RR"], 30, normed=1, facecolor="red")
        axes.set_xlabel("RR (msec.)")
        axes.set_ylabel("Probability")
        axes.set_title("RR histogram")
        axes.grid(True)
        matplotlib.pyplot.show()
        
    
    def CreatePlotHREmbedded(self,fig):
        """Creates an HR Plot embedded in axes
        Valid for windows and stand-alone plots"""
        
        
        self.HRaxes = fig.add_subplot(1,1,1)
        
        xvector, yvector = self.GetHRDataPlot()
        if "PlotHRXMin" not in self.data:
            self.data["PlotHRXMin"]=xvector[0]
            self.data["PlotHRXMax"]=xvector[-1]
        
        self.HRaxes.plot(xvector,yvector,'k-')
        self.HRaxes.set_xlabel("Time (sec.)")
        self.HRaxes.set_ylabel("HR (beats/min.)")
        
        
        self.HRaxes.set_title(self.GetHeartRatePlotTitle())
            
        
        if self.DataPlotHasVisibleEpisodes():
            tags,starts,durations,tagsVisible = self.GetEpisodes()
            numEpisodes=len(starts)
            i=0
            for tag in tagsVisible:
                startsvector=[starts[w] for w in range(numEpisodes) if tags[w]==tag]
                durationsvector=[durations[w] for w in range(numEpisodes) if tags[w]==tag]
                endsvector=[starts[w]+durations[w] for w in range(numEpisodes) if tags[w]==tag]
                for j in range(len(startsvector)):
                    if j==0:
                        self.HRaxes.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=self.GetEpisodeColor(tag), alpha=alphaMatplotlibTags, label=tag)
                    else:
                        self.HRaxes.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=self.GetEpisodeColor(tag), alpha=alphaMatplotlibTags)
                i=i+1
            leg=self.HRaxes.legend(fancybox=True,shadow=True)
            for t in leg.get_texts():
                t.set_fontsize('small')
               
        self.HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
        self.HRaxes.grid()
        
        
        
    
        
    def CreatePlotFBEmbedded(self, fig):
        """ Redraws the frame-based evolution figure"""
        
        def CreateBandSupblot(axes,x,y,ylabel):
            axes.plot(x,y,'-k')        
            axes.set_ylabel(ylabel)
            if ylabel not in ["Mean HR","HR STD","Heart rate"]:
                axes.set_ylim(bottom=0)
            axes.tick_params(axis='x',labelbottom='off')
            axes.set_xlim(xvectortimemin,xvectortimemax)
            axes.yaxis.set_major_locator(matplotlib.pyplot.MaxNLocator(4))
            axes.grid()
        
        
        def AddEpisodesToBandSubplot(axes,legend=False):
            
            i=0
            for tag in tagsVisible:
                startsvector=[self.data["EpisodesInitTime"][w] for w in range(numEpisodes) if tags[w]==tag]
                endsvector=[self.data["EpisodesInitTime"][w]+self.data["EpisodesDuration"][w] for w in range(numEpisodes) if tags[w]==tag]
                for j in range(len(startsvector)):
                    if not legend:
                        axes.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=self.GetEpisodeColor(tag), alpha=alphaMatplotlibTags)
                    else:
                        if j==0:
                            axes.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=self.GetEpisodeColor(tag), alpha=alphaMatplotlibTags, label=tag)
                        else:
                           axes.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=self.GetEpisodeColor(tag), alpha=alphaMatplotlibTags)
                i=i+1

        
        
        
        fig.clear()
        xvectortimemin=0
        xvectortimemax=1.0/self.data["interpfreq"]*(len(self.data["HR"])-1)
        xvectortime=np.linspace(start=0, stop=xvectortimemax, num=len(self.data["HR"]))
        
       

        lfhfvector,ulfvector,vlfvector, lfvector, hfvector, powervector,meanhrvector, hrstdvector, pnn50vector, rmssdvector, hrvector = self.GetFrameBasedDataPlot()
        xvectorframe=np.array([x*self.data["windowshift"]+self.data["windowsize"]/2.0 for x in range(len(ulfvector))])
        
        self.AllBands, self.VisibleBands=self.GetVisibleBands()
        
        hasEpisodes=self.DataPlotHasVisibleEpisodes()
        if hasEpisodes:
            tags,starts,durations,tagsVisible = self.GetEpisodes()
            starts=np.array(starts)
            durations=np.array(durations)
            ends=starts+durations
            numEpisodes=len(tags)
                              
        matplotlib.rc('xtick', labelsize=10) 
        matplotlib.rc('ytick', labelsize=10) 
        matplotlib.rc('legend', fontsize=10) 
        
        
        if hasEpisodes:
            fig.subplots_adjust(left=0.10, right=0.83, bottom=0.08, top=0.90)
        else:
            fig.subplots_adjust(left=0.10, right=0.96, bottom=0.08, top=0.90)
            
        # Heart rate plot
        axBottom = fig.add_subplot(len(self.VisibleBands),1,len(self.VisibleBands))
        CreateBandSupblot(axBottom, xvectortime, hrvector, 'Heart rate')
        axBottom.tick_params(axis='x',labelbottom='on')
        axBottom.set_xlabel('Time [sec.]',fontsize=10)
        
        if hasEpisodes:
            AddEpisodesToBandSubplot(axBottom,legend=True)
            #i=0
            #for tag in tagsVisible:
            #    startsvector=[starts[w] for w in range(numEpisodes) if tags[w]==tag]
            #    endsvector=[ends[w] for w in range(numEpisodes) if tags[w]==tag]
            #    for j in range(len(startsvector)):
            #        if j==0:
            #            axBottom.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=self.GetEpisodeColor(tag), alpha=alphaMatplotlibTags, label=tag)
            #        else:
            #            axBottom.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=self.GetEpisodeColor(tag), alpha=alphaMatplotlibTags)
            #    i=i+1       

            leg=axBottom.legend(bbox_to_anchor=(1.02, 0.0), loc=3, ncol=1, borderaxespad=0.)
            for t in leg.get_texts():
                t.set_fontsize('small')

    
           
        BandsToPlot = [ x for x in self.VisibleBands if x not in self.GetFixedBands()]
        
        for Band in BandsToPlot:
            BandIndex = BandsToPlot.index(Band)
            
            axBand=fig.add_subplot(len(self.VisibleBands),1,BandIndex+1)
            if Band == "LF/HF":
                CreateBandSupblot(axBand, xvectorframe, lfhfvector, 'LF/HF')
            if Band == "ULF":
                CreateBandSupblot(axBand, xvectorframe, ulfvector, 'ULF')
            if Band == "VLF":
                CreateBandSupblot(axBand, xvectorframe, vlfvector, 'VLF')
            if Band == "LF":
                CreateBandSupblot(axBand, xvectorframe, lfvector, 'LF')
            if Band == "HF":
                CreateBandSupblot(axBand, xvectorframe, hfvector, 'HF')
            if Band == "Power":
                CreateBandSupblot(axBand, xvectorframe, powervector, 'Power')
            if Band == "Mean HR":
                CreateBandSupblot(axBand, xvectorframe, meanhrvector, 'Mean HR')
            if Band == "HR STD":
                CreateBandSupblot(axBand, xvectorframe, hrstdvector, 'HR STD')
            if Band == "pNN50":
                CreateBandSupblot(axBand, xvectorframe, pnn50vector, 'pNN50')
            if Band == "rmssd":
                CreateBandSupblot(axBand, xvectorframe, rmssdvector, 'rmssd')
                
            #axBand.set_xlabel('Frame number',size=10)
            #axBand.tick_params(axis='x',labeltop='on')
            #axBand.xaxis.set_label_position("top")        
    
            if hasEpisodes :
                AddEpisodesToBandSubplot(axBand)
                
          
        
        fig.suptitle(self.GetName() + " - frame-based evolution", fontsize=16) 
        
    def PlotHRZoomIn(self):
        delta=(self.data["PlotHRXMax"]-self.data["PlotHRXMin"])*0.25
        self.data["PlotHRXMin"]+=delta
        self.data["PlotHRXMax"]-=delta
        self.HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
        if self.data["Verbose"]:
            print("*** HR Zoom in")
        
    def PlotHRZoomReset(self):
        xvector = self.GetHRDataPlot()[0]
        self.data["PlotHRXMin"] = xvector[0]
        self.data["PlotHRXMax"] = xvector[-1]
        self.HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
        if self.data["Verbose"]:
            print("*** HR Zoom reset")
        
    def PlotHRZoomOut(self):
        delta=(self.data["PlotHRXMax"]-self.data["PlotHRXMin"])*0.5
        self.data["PlotHRXMin"]-=delta
        self.data["PlotHRXMax"]+=delta
        xvector = self.GetHRDataPlot()[0]
        self.data["PlotHRXMin"]=max(xvector[0],self.data["PlotHRXMin"])
        self.data["PlotHRXMax"]=min(xvector[-1],self.data["PlotHRXMax"])
        self.HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
        if self.data["Verbose"]:
            print("*** HR Zoom out")
            
    def PlotHRPanRight(self):
        delta=(self.data["PlotHRXMax"]-self.data["PlotHRXMin"])*0.25
        xvector = self.GetHRDataPlot()[0]
        delta=min(delta,xvector[-1]-self.data["PlotHRXMax"])
        self.data["PlotHRXMin"] += delta
        self.data["PlotHRXMax"] += delta
        self.HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
        if self.data["Verbose"]:
            print("*** HR Pan right")
            
    def PlotHRPanLeft(self):
        delta=(self.data["PlotHRXMax"]-self.data["PlotHRXMin"])*0.25
        xvector = self.GetHRDataPlot()[0]
        delta=min(delta,self.data["PlotHRXMin"]-xvector[0])
        self.data["PlotHRXMin"] -= delta
        self.data["PlotHRXMax"] -= delta
        self.HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
        if self.data["Verbose"]:
            print("*** HR Pan left")
        
        
   
        
        
                
