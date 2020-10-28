#   ----------------------------------------------------------------------
#   gHRV: a graphical application for Heart Rate Variability analysis
#   Copyright (C) 2020 LIA2 Research Group - Dpt. Informatics
#      University of Vigo - Spain
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
import Utils
from matplotlib.widgets import Button
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


listofsettings=['interpfreq','windowsize','windowshift','ulfmin','ulfmax','vlfmin','vlfmax','lfmin','lfmax','hfmin','hfmax','name']

class DM:
        
    data={}
    labelColors=['Orange','cyan','red','blue','green','yellow','grey','pink','purple','maroon','lightgreen']

    def __init__(self,Verbose):
        """Initialization of the data model"""
        self.ClearAll()
        
        self.data["Verbose"]=Verbose

        if (self.data["Verbose"]==True):
            print("** Creating data model")

    def SetVerbose(self,verboseValue):
        self.data["Verbose"] = verboseValue
        
            
    def ClearAll(self):
        self.data={}
        self.data["Verbose"]=Verbose
        
        self.data["name"]=""
        #self.data["version"]=Version
        self.ClearColors()
        self.ClearBands()
        self.ClearPP()
        if (self.data["Verbose"]==True):
            print("** Clearing all data")

                
    def ClearColors(self):
        """Resets colors for episodes"""
        self.data["ColorIndex"]=0
        self.data["DictColors"]={}
        
    def ClearBands(self):
        self.data["Bands"]=["LF/HF","ULF","VLF","LF","HF","Power","Mean HR","HR STD","pNN50","rMSSD","ApEn","FracDim","Heart rate"]
        self.data["VisibleBands"]=["LF/HF","ULF","VLF","LF","HF","Heart rate"]
        self.data["FixedBands"]=["Heart rate"]

    def ClearPP(self):
        self.data["PPActiveTagLeft"]="Global"
        self.data["PPActiveTagRight"]="None"
        
         
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
                
    def LoadFileAscii(self,asciiFile,settings):
        """Loads from ascii file
        One data (beats instants in seconds, rr in msec. or rr in sec.) per line"""
        
        
        if (self.data["Verbose"]==True):
            print(("** Loading ascii file "+asciiFile))
                
                
        asciiData = np.loadtxt(asciiFile)
        asciiDataDiffs=np.diff(asciiData)
        asciiDataNeg = [ x for x in asciiDataDiffs if x<0]
        
        if len(asciiDataNeg)>0:  # The file contains an RR series
            asciiDataBig = [x for x in asciiData if x>100]
            if len(asciiDataBig)>0:
                if (self.data["Verbose"]==True):
                    print("   File contains RR data in milliseconds")
                self.LoadRRMillisec(asciiData,settings)
            else:
                if (self.data["Verbose"]==True):
                    print("   File contains RR data in seconds")
                self.LoadRRMillisec(asciiData*1000.0,settings)
        else:
            if (self.data["Verbose"]==True):
                print("   File contains beats instants in seconds")
                
            self.LoadBeatSec(asciiData,settings)
            
        
            
        self.data["name"]=os.path.splitext(os.path.basename(asciiFile))[0]
        
        if (self.data["Verbose"]):
            print(("   Project created: "+self.data["name"]))
            
        self.data["version"]=Version
        
    def LoadBeatSec(self,dataSec,settings):
        """Loads a vector containing beats positions in seconds"""
        
        self.data["BeatTime"]=dataSec
         
        
        self.data["niHR"] = 60.0/(self.data["BeatTime"][1:]-self.data["BeatTime"][0:-1])
        self.data["niHR"] = np.insert(self.data["niHR"],[0],self.data["niHR"][0])

        self.data["RR"] = 1000.0*(self.data["BeatTime"][1:]-self.data["BeatTime"][0:-1])
        self.data["RR"] = np.insert(self.data["RR"],[0],self.data["RR"][0])
        
        if (self.data["Verbose"]):
            print(("   BeatTime: "+str(len(self.data["BeatTime"]))+" points (max: "+str(self.data["BeatTime"][-1])+")"))
            print(("   niHR: "+str(len(self.data["niHR"]))+" points"))
            print(("   RR: "+str(len(self.data["RR"]))+" points"))
                
        for k in list(settings.keys()):
            self.data[k]=float(settings[k])
        if (self.data["Verbose"]):
            print("   Parameters set to default values")
            
        
    def LoadRRMillisec(self,dataMSec,settings):
        """Loads a vector containing milliseconds"""
        
        self.data["RR"]=np.array(dataMSec)
        self.data["BeatTime"]=np.cumsum(self.data["RR"])/1000.0
        self.data["niHR"]=60.0/(self.data["RR"]/1000.0)
        
        if (self.data["Verbose"]==True):
            print(("   BeatTime: "+str(len(self.data["BeatTime"]))+" points (max: "+str(self.data["BeatTime"][-1])+")"))
            print(("   RR: "+str(len(self.data["RR"]))+" points"))
            print(("   niHR: "+str(len(self.data["niHR"]))+" points"))
        
        for k in list(settings.keys()):
            self.data[k]=float(settings[k])
        if (self.data["Verbose"]):
            print("   Parameters set to default values")
                    
    
    def LoadFilePolar(self,polarFile,settings):
        """Loads polar file
        Polar files contain rr series, expresed in milliseconds"""
        
        if (self.data["Verbose"]==True):
            print(("** Loading polar file "+polarFile))
        
        dataMillisec=[]
        dataFound=False
        File = open(polarFile,'r')
        for line in File:
            if dataFound:
                data=line.strip()
                if data:
                    dataMillisec.append(float(data))
            if line.strip() == "[HRData]":
                dataFound=True
        File.close()
        
        self.LoadRRMillisec(dataMillisec,settings)
            
        self.data["name"]=os.path.splitext(os.path.basename(polarFile))[0]
        
        if (self.data["Verbose"]):
            print(("   Project created: "+self.data["name"]))
            
        self.data["version"]=Version
        
    def LoadFileSuunto(self,suuntoFile,settings):
        """Loads suunto file
        suunto files contain rr series, expresed in milliseconds"""
        
        if (self.data["Verbose"]==True):
            print(("** Loading suunto file "+suuntoFile))
        
        dataMillisec=[]
        dataFound=False
        File = open(suuntoFile,'r')
        for line in File:
            if dataFound:
                data=line.strip()
                if data:
                    dataMillisec.append(float(data))
            if line.strip() == "[CUSTOM1]":
                dataFound=True
        File.close()
        
        self.LoadRRMillisec(dataMillisec,settings)
        
        self.data["name"]=os.path.splitext(os.path.basename(suuntoFile))[0]
        
        if (self.data["Verbose"]):
            print(("   Project created: "+self.data["name"]))
            
        self.data["version"]=Version

    def LoadBeatWFDB(self,wfdbheaderfile,settings):
        """Loads wfdb file"""

        import glob
        
        if (self.data["Verbose"]==True):
            print(("** Loading WFDB file "+wfdbheaderfile))

        heaFile = open(wfdbheaderfile,'r')
        line=heaFile.readline()
        heaFile.close()

        lineFields = line.split(" ")
        if len(lineFields)>2:
            try:
                samplingFrequency = float(lineFields[2])
            except:
                samplingFrequency = 250.0
        else:
            samplingFrequency = 250.0

        if (self.data["Verbose"]==True):
            print(("   Sampling frequency: "+str(samplingFrequency)))

        filesfound = glob.glob(wfdbheaderfile[:-4]+".*")
        extensionsfound=[]
        for filefound in filesfound:
            extension = os.path.splitext(filefound)[1][1:]
            extensionsfound.append(extension)
        extensionsfound.remove('hea')

        if len(extensionsfound)==0:
            Utils.ErrorWindow(messageStr="No data file found with: "+wfdbheaderfile,captionStr="Error loading beats    ")
            return

        if 'dat' in extensionsfound:
            extensionsfound.remove('dat')

        if 'atr' in extensionsfound:
            extensionsfound.remove('atr')
            extensionsfound.insert(0,'atr')
        if 'qrs' in extensionsfound:
            extensionsfound.remove('qrs')
            extensionsfound.insert(0,'qrs')

        if len(extensionsfound)>1:
            AnnotatorSelection=Utils.SelectAnnotator(extensionsfound)
            extensionSelected = AnnotatorSelection.GetValue()
            if extensionSelected == '':
                return
        else:
            extensionSelected=extensionsfound[0]

        
            # 'qrs' in first place, then 'atr'


        wfdbdatafile=wfdbheaderfile[:-4]+"."+extensionSelected

        if (self.data["Verbose"]==True):
            print(("   Trying data file: "+wfdbdatafile))

        try:

            datafile = open(wfdbdatafile,'rb')
            accumulator=0.0
            beats=[]

            while True:
                value = ord(datafile.read(1))+ord(datafile.read(1))*256
                code = value >> 10
                time = value % 1024
                
                # print ("Value: "+str(int(value)))
                # print ("Code: "+str(code))
                # print ("Time: "+str(time))

                if code==0 and time==0:
                    break

                # Original code:
                # if code==1: # Only normal beats

                # Modified code:
                if code<50: 
                    accumulator = accumulator+time
                    # print "Sec: ",accumulator/samplingFrequency
                    beats.append(accumulator/samplingFrequency)
                else:
                    if code==63:
                        # Modified code:
                        jump = int(time) + int(time)%2
                        x = datafile.read(jump)
                        value = ord(datafile.read(1))+ord(datafile.read(1))*256
                        # Original code:    
                        # jump = int(time)/2 + int(time)%2
                        # for i in range(jump):
                        #     value = ord(datafile.read(1))+ord(datafile.read(1))*256
                    else:
                        if code==59 and time==0:
                            for i in range(2):
                                value = ord(datafile.read(1))+ord(datafile.read(1))*256
                        else:
                            if code!=60 and code!=61 and code!=62 and code!=22 and code!=0:
                                accumulator = accumulator+time
        except:
            if (self.data["Verbose"]==True):
                print(("   File "+wfdbdatafile+" didn't work"))
            Utils.ErrorWindow(messageStr="Error loading file: "+wfdbdatafile,captionStr="Error loading beats    ")
            return
        else:
            if (self.data["Verbose"]==True):
                print(("   File "+wfdbdatafile+" has been loaded"))

        self.LoadBeatSec(np.array(beats),settings)
        
        self.data["name"]=os.path.splitext(os.path.basename(wfdbheaderfile))[0]
        
        if (self.data["Verbose"]):
            print(("   Project created: "+self.data["name"]))
            
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
            print(("** Opening episodes file: "+episodesFile))
                
        epFile = open(episodesFile,'r')
        index=0
        for line in epFile:
            if index!=0:
                linedata=line.strip().split()
                if "EpisodesType" not in self.data:
                    self.__CreatesEpisodesInfo()
                self.data["EpisodesType"].append(linedata[1])
                self.data["EpisodesDuration"].append(float(linedata[2]))
                HMS=linedata[0].split(":")
                self.data["EpisodesInitTime"].append(float(HMS[0])*3600.0+float(HMS[1])*60.0+float(HMS[2]))
            index += 1
        epFile.close()
                
        self.data["EpisodesVisible"]=list(set(self.data["EpisodesType"]))
                
        if (self.data["Verbose"]):
            print(("   Read "+str(len(self.data["EpisodesType"]))+" episodes from file"))
            print(("   Read "+str(len(self.data["EpisodesVisible"]))+" types of episodes"))


    def LoadEpisodesWFDB(self,wfdbheaderfile):
        """Loads episodes from physionet files"""
        import glob

        if (self.data["Verbose"]==True):
            print(("** Loading episodes from WFDB file "+wfdbheaderfile))

        heaFile = open(wfdbheaderfile,'r')
        line=heaFile.readline()
        heaFile.close()

        lineFields = line.split(" ")
        if len(lineFields)>2:
            try:
                samplingFrequency = float(lineFields[2])
            except:
                samplingFrequency = 250.0
        else:
            samplingFrequency = 250.0

        if (self.data["Verbose"]==True):
            print(("   Sampling frequency: "+str(samplingFrequency)))

        filesfound = glob.glob(wfdbheaderfile[:-4]+".*")
        extensionsfound=[]
        for filefound in filesfound:
            extension = os.path.splitext(filefound)[1][1:]
            extensionsfound.append(extension)
        extensionsfound.remove('hea')

        if len(extensionsfound)==0:
            Utils.ErrorWindow(messageStr="No data file found with: "+wfdbheaderfile,captionStr="Error loading episodes    ")
            return

        if 'dat' in extensionsfound:
            extensionsfound.remove('dat')

        if 'atr' in extensionsfound:
            extensionsfound.remove('atr')
            extensionsfound.append('atr')
        if 'qrs' in extensionsfound:
            extensionsfound.remove('qrs')
            extensionsfound.append('qrs')

        if len(extensionsfound)>1:
            AnnotatorSelection=Utils.SelectAnnotator(extensionsfound)
            extensionSelected = AnnotatorSelection.GetValue()
            if extensionSelected == '':
                return
        else:
            extensionSelected=extensionsfound[0]

        wfdbdatafile=wfdbheaderfile[:-4]+"."+extensionSelected

        if (self.data["Verbose"]==True):
            print(("   Trying data file: "+wfdbdatafile))

        try:
            ApneaTag="Apnea"

            datafile = open(wfdbdatafile,'rb')

            accumulator=0.0
            ActiveTags=[]
            ActiveTagsOnsets=[]
            EpisodesTypes=[]
            EpisodesInits=[]
            EpisodesEnds=[]

            if extensionSelected=="apn":
                while True:
                    value = ord(datafile.read(1))+ord(datafile.read(1))*256
                    code = value >> 10
                    time = value % 1024

                    if code==0 and time==0:
                        break

                    if code==8 and ApneaTag not in ActiveTags:
                        ActiveTags.append(ApneaTag)
                        ActiveTagsOnsets.append(accumulator)

                    if code==1 and ApneaTag in ActiveTags:
                        EpisodesTypes.append(ApneaTag)
                        EpisodesInits.append(ActiveTagsOnsets[0])
                        EpisodesEnds.append(accumulator)
                        del ActiveTags[0]
                        del ActiveTagsOnsets[0]

                    if code == 59:
                        interval = (ord(datafile.read(1))+ord(datafile.read(1))*256)*65536+(ord(datafile.read(1))+ord(datafile.read(1))*256)
                        accumulator=accumulator+interval/samplingFrequency
                        next

            else:
                while True:
                    value = ord(datafile.read(1))+ord(datafile.read(1))*256
                    code = value >> 10
                    time = value % 1024
                    
                    if code==0 and time==0:
                        break

                    if code <= 49:
                        next

                    if code == 59:
                        interval = (ord(datafile.read(1))+ord(datafile.read(1))*256)*65536+(ord(datafile.read(1))+ord(datafile.read(1))*256)
                        accumulator=accumulator+interval/samplingFrequency
                        next

                    if code==22:
                        ll = ord(datafile.read(1))
                        datafile.read(1)  # value 252
                        comment = datafile.read(ll)
                        # print "  String: ",comment
                        Tags=comment.split()

                        if (ll%2):
                            datafile.read(1)

                        for ActiveTag in ActiveTags:
                            if ActiveTag not in Tags:
                                ii=ActiveTags.index(ActiveTag)
                                EpisodesTypes.append(ActiveTag)
                                EpisodesInits.append(ActiveTagsOnsets[ii])
                                EpisodesEnds.append(accumulator)
                                del ActiveTags[ii]
                                del ActiveTagsOnsets[ii]

                        for Tag in Tags:
                            if Tag not in ActiveTags:
                                ActiveTags.append(Tag)
                                ActiveTagsOnsets.append(accumulator)


            for ActiveTag in ActiveTags:
                ii=ActiveTags.index(ActiveTag)
                EpisodesTypes.append(ActiveTag)
                EpisodesInits.append(ActiveTagsOnsets[ii])
                EpisodesEnds.append(self.GetHRDataPlot()[0][-1]) # Last beat

        except:
            if (self.data["Verbose"]==True):
                print(("   File "+wfdbdatafile+" didn't work"))
            Utils.ErrorWindow(messageStr="Error loading file: "+wfdbdatafile,captionStr="Error loading episodes    ")
            return
        else:
            if (self.data["Verbose"]==True):
                print(("   File "+wfdbdatafile+" has been loaded"))
        # print EpisodesTypes
        # print EpisodesInits
        # print EpisodesEnds

        if len(EpisodesTypes)==0:
            Utils.ErrorWindow(messageStr="No valid episodes found in: "+wfdbdatafile,captionStr="Error loading episodes    ")
            return

        if extensionSelected=="apn":
            TagsSelected=[ApneaTag]
        else:
            TagsDetected=sorted(list(set(EpisodesTypes)))
            TagsSelection=Utils.SelectEpisodesTags(TagsDetected)
            IndexTagsSelected = TagsSelection.GetValues()
            if len(IndexTagsSelected) == 0:
                return
            TagsSelected=[]
            for indexTag in IndexTagsSelected:
                TagsSelected.append(TagsDetected[indexTag])

        numAddedEpisodes=0
        for indexEpisode in range(len(EpisodesTypes)):
            if EpisodesTypes[indexEpisode] in TagsSelected:
                self.AddEpisode(EpisodesInits[indexEpisode],EpisodesEnds[indexEpisode],EpisodesTypes[indexEpisode])
                numAddedEpisodes += 1

        Utils.InformEpisodesFile(wfdbdatafile,numAddedEpisodes)

                    
    def LoadProject(self,datamodelFile):
        """Loads the data model from a zip file"""
        import zipfile, tempfile, shutil
        tempDir = tempfile.mkdtemp(prefix="gHRV")
        if self.data["Verbose"]:
            print(("** Loading project: "+datamodelFile))
            print(("   Temporal directory: "+tempDir))
                
        zf = zipfile.ZipFile(datamodelFile, mode='r')
    
        for zfitem in zf.namelist():
            zf.extract(zfitem,tempDir)
            fileName=tempDir+os.sep+zfitem
            dataName=zfitem[1:]
            # print("--- Reading file: "+fileName)
            if zfitem[0]=="#":
                self.data[dataName]=np.loadtxt(fileName)
                # print("   Length: "+str(len(self.data[dataName])))
            else:
                tempF = open(fileName,'r')
                if dataName=="name" or dataName=='PPActiveTagLeft' or dataName=='PPActiveTagRight':
                    self.data[dataName]=tempF.read()
                else:
                    self.data[dataName]=eval(tempF.read())
                tempF.close()
                # print("   Data: "+str(self.data[dataName]))
        zf.close()

        if "version" in list(self.data.keys()):
            self.data["version"] = str(self.data["version"])
            # version needs to be a string for comparison purposes
        
        # print ("Keys: "+str(self.data.keys()))
        
        #print self.data["name"]
        
        if "interpfreq" not in list(self.data.keys()): # Project generated with gHRV 0.17
            if self.data['Verbose']:
                print("   Importing project from gHRV 0.17")
            if 'FreqHR' in list(self.data.keys()):
                del self.data['FreqHR']
            for k in list(factorySettings.keys()):
                self.data[k]=float(factorySettings[k])
            self.data['name']='mygHRVproject'
            
        if "version" not in list(self.data.keys()): # Project generated with gHRV 0.18 or older
            if self.data['Verbose']:
                print("   Importing project from gHRV 0.18 or older")
            self.ClearBands()
            if self.HasFrameBasedParams():
                self.ClearFrameBasedParams()
                self.CalculateFrameBasedParams(showProgress=True)
            self.data["version"]=Version

        if self.data["version"]<Version:
            if self.data['Verbose']:
                print(("   gHRV version: *"+Version+"*"))
                print(("   Project build with gHRV version: *"+self.data["version"]+"*"))
                print("   Importing project from an old version of gHRV")
            self.ClearBands()
            if self.HasFrameBasedParams():
                self.ClearFrameBasedParams()
                self.CalculateFrameBasedParams(showProgress=True)
            self.data["version"]=Version
              
        shutil.rmtree(tempDir)
        
            
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
   
                        
    def SaveProject(self,datamodelFile):
        """Saves the data model into a zip file"""
        
        import zipfile,shutil,tempfile
        
        tempDir = tempfile.mkdtemp(prefix="gHRV")
        
        
        if self.data["Verbose"]:
            print(("** Saving project: "+datamodelFile))
            #print("   Temporal directory: "+tempDir)
                            
        for kData in list(self.data.keys()):
            if type(self.data[kData])==np.ndarray:
                tempFName=tempDir+os.sep+"#"+str(kData)
                np.savetxt(tempFName,self.data[kData])
            else:
                # print kData, ": ", type(self.data[kData])
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
            print(("** Saving frame-based data: "+dataFile))
            print(("   List of bands: "+str(listOfBands)))
            print(("   Separator: '"+SepChar+"'"))
            print(("   Row header: "+str(RHeader)))
            print(("   Column header: "+str(CHeader)))
        
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
                File.write(Band.replace(" ","_"))
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
            print(("   No. of lines: "+str(NumFrames)))
        
                                        
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
            print(("** Adding an episode ({0:.2f},{1:.2f}) with label {2:s}".format(init,end,tag)))
                
        if "EpisodesType" not in self.data:
            self.__CreatesEpisodesInfo()
        
        self.data["EpisodesType"].append(tag)
        self.data["EpisodesInitTime"].append(init)
        self.data["EpisodesDuration"].append(float(end)-float(init))
        if tag not in self.data["EpisodesVisible"]:
            self.data["EpisodesVisible"].append(tag)

    def SetEpisodes(self,Episodes):
        if (self.data["Verbose"]):
            print ("** Changing episodes from manual edition")

        if len(Episodes)==0:
            self.ClearEpisodes()
            self.ClearColors()
            if (self.data["Verbose"]):
                print ("   Episodes information removed")
            return

        EpVis = list(self.data["EpisodesVisible"])
        self.__CreatesEpisodesInfo()
        for Ep in Episodes:
            self.data["EpisodesType"].append(Ep[0])
            self.data["EpisodesInitTime"].append(Ep[1])
            self.data["EpisodesDuration"].append(Ep[3])

        # Removes tags label if all episodes of this label were removed
        self.data["EpisodesVisible"]=[Tag for Tag in EpVis if Tag in self.data["EpisodesType"]]

        if (self.data["Verbose"]):
            print(("   Number of episodes: "+str(len(Episodes))))
                        
    def ReplaceHRVectors(self,xvector,yvector,rrvector):
        """After EditNIHR the beats (Time, niHR and RR) are replaced"""
        
        self.data["BeatTime"]=xvector
        self.data["niHR"]=yvector
        self.data["RR"]=rrvector
        if (self.data["Verbose"]):
            print("** HR vectors replaced")
            print(("   BeatTime: "+str(len(self.data["BeatTime"]))+" points (max: "+str(self.data["BeatTime"][-1])+")"))
            print(("   niHR: "+str(len(self.data["niHR"]))+" points"))
            print(("   RR: "+str(len(self.data["RR"]))+" points"))

                                
    def FilterNIHR(self,winlength=50,last=13,minbpm=24,maxbpm=198):
        """Removes outliers from non interpolated heart rate"""
        if (self.data["Verbose"]):
           print ("** Filtering non-interpolated heart rate")
           print(("   Number of original beats: "+str(len(self.data["niHR"]))))

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
            print(("   Number of filtered beats: "+str(len(self.data["BeatTime"]))))

                            
    def InterpolateNIHR(self):
        "Interpolates instantaneous heart rate (linear method)"   

        from scipy import interpolate

        if self.data["Verbose"]:
            print ("** Interpolating instantaneous heart rate (method: linear interpolation)")
            print(("   Frequency: "+str(self.data["interpfreq"])+" Hz"))

        xmin=self.data["BeatTime"][0]
        xmax=self.data["BeatTime"][-1]
        step=1.0/self.data["interpfreq"]
        
        tck = interpolate.interp1d(self.data["BeatTime"],self.data["niHR"])
        xnew = np.arange(xmin,xmax,step)

        if self.data["Verbose"]:
            print(("   Original signal from: "+str(self.data["BeatTime"][0])+" to "+str(self.data["BeatTime"][-1])))
            print(("   Interpolating from "+str(xmin)+" to "+str(xmax)+" seconds"))
           
        self.data["HR"] = tck(xnew)

        if self.data["Verbose"]:
            print(("   Obtained "+str(len(self.data["HR"]))+" points"))


    def GetNumFrames(self,interfreq,windowsize,windowshift):
        shiftsamp=windowshift*interfreq
        sizesamp=windowsize*interfreq     
        numframes=int(((len(self.data["HR"])-sizesamp)/shiftsamp)+1.0)
        return numframes
        
                
    def CalculateFrameBasedParams(self, showProgress=False):
        """Calculates power per band
            size -> size of window (seconds)
            shift -> displacement of window (seconds)"""

        hammingfactor=1.586



        def power(spec,freq,fmin,fmax):
            band = [spec[i] for i in range(len(spec)) if freq[i] >= fmin and freq[i]<fmax]
            powerinband = hammingfactor*np.sum(band)/(2*len(spec)**2)
            return powerinband
                                
        if self.data["Verbose"]:
            print("** Calculating power per band")
            
        signal=1000/(self.data["HR"]/60.0) # msec.

        shiftsamp=self.data['windowshift']*self.data["interpfreq"]
        sizesamp=self.data['windowsize']*self.data["interpfreq"]
        
        numframes=int(((len(signal)-sizesamp)/shiftsamp)+1.0)

        lenZeroPadding=2**int(np.ceil(np.log2(sizesamp)))-int(sizesamp)
        
        if (numframes < minNumFrames):
            raise Utils.FewFramesException(numframes)

        sizesamp2=sizesamp
        if (sizesamp2%2 != 0):
            sizesamp2=sizesamp2+1

        
        hw=np.hamming(sizesamp2)

        if numframes<=10:
            showProgress = False

        
        if showProgress:
            import wx
            dlg = wx.ProgressDialog("Calculating parameters","Preparing data...",maximum = (numframes-1)//10,
                style=wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME | wx.PD_ESTIMATED_TIME)
        
        
        if self.data["Verbose"]:
            print(("   Signal length: "+str(len(signal))+" samples"))
            print(("   Frame length: "+str(sizesamp)+" samples"))
            print(("   Frame shift: "+str(shiftsamp)+" samples"))
            print(("   Number of frames: "+str(numframes)))
            
        self.data["ULF"]=[]
        self.data["VLF"]=[]
        self.data["LF"]=[]
        self.data["HF"]=[]
        self.data["LFHF"]=[]
        self.data["Power"]=[]
        self.data["Mean HR"]=[]
        self.data["HR STD"]=[]
        self.data["pNN50"]=[]
        self.data["rMSSD"]=[]
        self.data["ApEn"]=[]
        self.data["FracDim"]=[]




        KeepGoing = True
             
        indexframe = 0   
        while indexframe<numframes and KeepGoing:
            if showProgress:
                if indexframe%10 == 0:
                    KeepGoing = dlg.Update(indexframe//10, "Frame number: %s/%s" % (indexframe,numframes))[0]
                    # print "Keep: "+str(KeepGoing)
            begframe=int(indexframe*shiftsamp)
            endframe=int(begframe+sizesamp) # samples
            frame=signal[begframe:endframe]
            if (len(frame)%2 != 0):
                frame=np.append(frame,[0])
            
            begtime=indexframe*self.data['windowshift']
            endtime=begtime+self.data['windowsize'] # seconds
            
            frame=frame-np.mean(frame)
            frame=frame*hw
            frame = np.append(frame,np.zeros(lenZeroPadding))
            
            # print("-----------------------")
            # print("Frame "+str(indexframe))
            # print("Frame power (time): "+str(hammingfactor*np.mean(frame*frame))+" ms^2")

            spec_tmp=np.absolute(np.fft.fft(frame))**2
            spec=spec_tmp[0:(len(spec_tmp)/2)] # Only positive half of spectrum

            freqs = np.linspace(start=0,stop=self.data["interpfreq"]/2,num=len(spec),endpoint=True)

            
            # print("Frame power (frequency): "+str(power(spec,freqs,0,self.data["interpfreq"]/2)))
            
            ulfpower=power(spec,freqs,self.data["ulfmin"],self.data["ulfmax"])
            self.data["ULF"].append(ulfpower)
            #print("ULF power: "+str(ulfpower))
            
            vlfpower=power(spec,freqs,self.data["vlfmin"],self.data["vlfmax"])
            self.data["VLF"].append(vlfpower)
            #print("VLF power: "+str(vlfpower))
            
            lfpower=power(spec,freqs,self.data["lfmin"],self.data["lfmax"])
            self.data["LF"].append(lfpower)
            #print("LF power: "+str(lfpower))
            
            hfpower=power(spec,freqs,self.data["hfmin"],self.data["hfmax"])
            self.data["HF"].append(hfpower)
            #print("HF: "+str(hfpower))
            
            totalpower=power(spec,freqs,0,self.data["interpfreq"]/2.0)
            self.data["Power"].append(totalpower)
            
            #print("ULF+VLF+LF+HF power: "+str(ulfpower+vlfpower+lfpower+hfpower))
            
            self.data["LFHF"].append(lfpower/hfpower)
            #print("LF/HF: "+str(lfpower/hfpower))
            
            frameHR = self.data["HR"][begframe:endframe]
            self.data["Mean HR"].append(np.mean(frameHR))
            self.data["HR STD"].append(np.std(frameHR,ddof=1))            
            
            BeatsFrame = [x for x in self.data["BeatTime"] if x>=begtime and x<=endtime]
            frameRR = 1000.0*np.diff(BeatsFrame)
            # print "Window has ",len(BeatsFrame), " beats"
            # print "frameHR - ",len(frameHR)
            # print "frameRR - ",len(frameRR)
            RRDiffs=np.diff(frameRR)
            RRDiffs50 = [x for x in np.abs(RRDiffs) if x>50]
            self.data["pNN50"].append(100.0*len(RRDiffs50)/len(RRDiffs))
            self.data["rMSSD"].append(np.sqrt(np.mean(RRDiffs**2)))

            ApEn,FracDim=self.CalculateNonLinearAnalysis(BeatsFrame)
            self.data["ApEn"].append(ApEn)
            self.data["FracDim"].append(FracDim)

            indexframe += 1
                
        if showProgress:
            dlg.Destroy()

        if not KeepGoing:
            self.ClearFrameBasedParams()
        else:
            self.data["ULF"]=np.array(self.data["ULF"])
            self.data["VLF"]=np.array(self.data["VLF"])
            self.data["LF"]=np.array(self.data["LF"])
            self.data["HF"]=np.array(self.data["HF"])
            self.data["LFHF"]=np.array(self.data["LFHF"])
            self.data["Power"]=np.array(self.data["Power"])
            self.data["Mean HR"]=np.array(self.data["Mean HR"])
            self.data["HR STD"]=np.array(self.data["HR STD"])
            self.data["pNN50"]=np.array(self.data["pNN50"])
            self.data["rMSSD"]=np.array(self.data["rMSSD"])
            self.data["ApEn"]=np.array(self.data["ApEn"])
            self.data["FracDim"]=np.array(self.data["FracDim"])


    def CalculateNonLinearAnalysis(self,Data=None, N=1000):

        def BuildTakensVector(Data,m,tau):
            # DataInt = range(1001)
            N = len(Data)
            jump = tau
            maxjump=(m-1)*jump
            jumpsvect=list(range(0,maxjump+1,jump))
            # print("jumpsvect: "+str(jumpsvect))
            numjumps=len(jumpsvect)
            numelem=N-maxjump
            # print("Building matrix "+str(numelem)+"x"+str(numjumps))
            DataExp = np.zeros(shape=(numelem,numjumps))
            for i in range(numelem):
                for j in range(numjumps):
                    DataExp[i,j]=Data[jumpsvect[j]+i]

            # print("DataExp first row: "+str(DataExp[0]))
            # print("DataExp last row: "+str(DataExp[-1]))

            return DataExp
            # --------------------


        def AvgIntegralCorrelation(Data,m,tau,r):

            from scipy.spatial.distance import cdist

            DataExp = BuildTakensVector(Data, m, tau)
            numelem=DataExp.shape[0]
            # print("Number of rows: "+str(numelem))
            mutualDistance=cdist(DataExp,DataExp,'chebyshev')

            Cmr=np.zeros(numelem)

            for i in range(numelem):
                vector=mutualDistance[i]
                Cmr[i]=float((vector <=r).sum())/numelem

            Phi=(np.log(Cmr)).sum()/len(Cmr)

            # if self.data["Verbose"]:
            #     print("      m="+str(m))
            #     print("      Integral correlation: "+str(Cmr.sum()))
            #     print("      Average integral correlation: "+str(Phi))

            return Phi
            # --------------------


        def CalculateApEn(Data,m=2,tau=1,r=0.2):

            r=r*np.std(Data,ddof=1)

            # print("r: "+str(r))

            Phi1 = AvgIntegralCorrelation(Data,m,tau,r)
            Phi2 = AvgIntegralCorrelation(Data,m+1,tau,r)

            return Phi1-Phi2
            # --------------------


        def CalculateFracDim(Data, m=10, tau=3, Cra=0.005, Crb=0.75):

            from scipy.spatial.distance import pdist
            from scipy.stats.mstats import mquantiles

            DataExp=BuildTakensVector(Data,m,tau)
            # print("Number of rows: "+str(DataExp.shape[0]))
            # print("Number of columns: "+str(DataExp.shape[1]))

            mutualDistance=pdist(DataExp,'chebyshev')

            numelem=len(mutualDistance)
            # print("numelem: "+str(numelem))
            
            rr=mquantiles(mutualDistance,prob=[Cra,Crb])
            ra=rr[0]
            rb=rr[1]

            Cmra= float(((mutualDistance <= ra).sum()))/numelem
            Cmrb= float(((mutualDistance <= rb).sum()))/numelem

            # if self.data["Verbose"]:
            #     print("      ra: "+str(ra))
            #     print("      rb: "+str(rb))
            #     print("      Cmra: "+str(100.0*Cmra)+"%")
            #     print("      Cmrb: "+str(100.0*Cmrb)+"%")

            FracDim = (np.log(Cmrb)-np.log(Cmra))/(np.log(rb)-np.log(ra))

            return FracDim
            # --------------------


        # if self.data["Verbose"]:
        #     print("** Calculating non-linear parameters")

        npoints=len(Data)

        # print ("Number of points: "+str(npoints))
        if npoints > N:
            DataInt=Data[(npoints/2-N/2)-1:(npoints/2+N/2)]
        else:
            DataInt=Data

        # dd=np.linspace(start=0, stop=100, num=1000)
        # DataInt=np.sin(dd)

        # if self.data["Verbose"]:
        #     print("   Calculating approximate entropy")
        ApEn = CalculateApEn(DataInt)
        # if self.data["Verbose"]:
        #     print("   Approximate entropy: "+str(ApEn))

        # if self.data["Verbose"]:
        #     print("   Calculating fractal dimension")
        FracDim = CalculateFracDim(DataInt)
        # if self.data["Verbose"]:
        #     print("  Fractal dimension: "+str(FracDim))

        return ApEn,FracDim
        
                        
            
    def GetHRDataPlot(self):
        if self.HasInterpolatedHR():
            xvector = np.linspace(self.data["BeatTime"][0], self.data["BeatTime"][-1], len(self.data["HR"]))
            yvector = self.data["HR"]
        else: 
            xvector = self.data["BeatTime"]
            yvector = self.data["niHR"]
        return (xvector,yvector)


    def GetHRBeatTimes(self):
        return self.data["BeatTime"]

    def GetHR_RR(self):
        return self.data["RR"]



    def GetPoincareDataPlot(self,tag):
        if tag=="Global":
            data=self.data["RR"]
            return (data[:-1],data[1:])

        outsideTag=False
        pointsInTag=np.zeros(len(self.data["RR"]))
        if tag[0:7] == "Outside":
            outsideTag=True
            tag = tag[8:]
        tags,starts,durations,tagsVisible = self.GetEpisodes()
        numEpisodes=len(starts)
        startsvector=[starts[w] for w in range(numEpisodes) if tags[w]==tag]
        durationsvector=[durations[w] for w in range(numEpisodes) if tags[w]==tag]
        endsvector=[starts[w]+durations[w] for w in range(numEpisodes) if tags[w]==tag]

        for indexEp in range(len(startsvector)):
            pointsInTag[[x for x in range(len(self.data["RR"])) if self.data["BeatTime"][x] > startsvector[indexEp] and self.data["BeatTime"][x] < endsvector[indexEp]]] = 1

        inside=self.data["RR"][[x for x in range(len(self.data["RR"])) if pointsInTag[x]==1]]
        outside=self.data["RR"][[x for x in range(len(self.data["RR"])) if pointsInTag[x]==0]]
        # print "Inside: ",len(inside)
        # print "Outside: ",len(outside)
        # print "Total: ",len(self.data["RR"])

        if outsideTag:
            data = outside
        else:
            data = inside

        return (data[:-1],data[1:])
        
        
    def GetName(self):
        return self.data["name"]
        
        
    def CreateReport(self,DirName, ReportName, ReportSubDir):
        
        def WriteTitleLine(fileHandler):
            fileHandler.write('<table cellspacing="5" border="0" width="'+str(HTMLPageWidth)+'" bgcolor="'+ReportWindowTitleColor+'">\n<tr><td align="left" ><b><font color="white" size="+1">gHRV analysis report</font></b></td></tr></table>\n')
            
        # -----------------
            
        def WriteSubtitleLine(fileHandler,text):
            fileHandler.write('<table cellspacing="5" border="0" width="'+str(HTMLPageWidth)+'">\n<tr><td align="left" ><font color='+ReportWindowTitleColor+'><b>'+text+'</b></font></td></tr></table>\n')
            
        # -----------------
        
        def WriteSubsubtitleLine(fileHandler,text):
            fileHandler.write('<table cellspacing="5" border="0" width="'+str(HTMLPageWidth)+'">\n<tr><td align="left" ><font size="-1" color='+ReportWindowSubTitleColor+'><b>&nbsp;'+text+'</b></font></td></tr></table>\n')
            
        # -----------------
        
        # print "Creating: ",DirName+os.sep+ReportSubDir

        os.mkdir(DirName+os.sep+ReportSubDir)
        
        if (self.data["Verbose"]==True):
            print(("** Creating report in directory "+DirName))

        if self.HasInterpolatedHR():
            if self.HasFrameBasedParams()==False:
                self.CalculateFrameBasedParams(showProgress=True)
            
        FileName = DirName + os.sep + ReportName
        File = open(FileName,'w')
        File.write(HTMLHead)
        
        # Line header   
        WriteTitleLine(File)
        File.write("<hr>\n")
        
        # HR Plot
        WriteSubtitleLine(File,'File details')        
        info=self.GetInfoFile()
        self.CreatePlotFile("HR",DirName+os.sep+ReportSubDir+os.sep+"HR.png",plotHRWidth,plotHRHeight,zoomReset=True)
        
        File.write('<table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'"><tr align="center"> <td width="50%"><b>Name: </b><i>'+info["name"]+'</i></td><td width="50%"><b>Signal length: </b><i>'+info["length"]+'</i></td></tr></table>\n')
        File.write('<table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'"><tr align="center"><td><img src="./'+ReportSubDir+'/HR.png"/></td></tr></table>\n')
        
        File.write("<hr>\n")
        
        
        # Histogram and time-based parameters
        WriteSubtitleLine(File,'Global analysis (time-domain parameters)')          
        info=self.GetInfoTime()
        self.CreatePlotFile("HRHistogram",DirName+os.sep+ReportSubDir+os.sep+"HRHistogram.png",plotHRHistogramWidth,plotHRHistogramHeight)
        File.write('<table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'">\n')
        File.write('<tr align="center"><td><img src="./'+ReportSubDir+'/HRHistogram.png"/></td><td align="left">\n')
        File.write('<font size="-1">\n<table align="left">')
        File.write('<tr><td><b>No. of beats: </b><i>'+info["beats"]+'</i></td></tr>')
        File.write('<tr><td><b>Mean HR: </b><i>'+info["meanhr"]+'</i></td></tr>')
        File.write('<tr><td><b>STD HR: </b><i>'+info["stdhr"]+'</i></td></tr>')
        File.write('<tr><td><b>Mean RR (AVNN): </b><i>'+info["meanrr"]+'</i></td></tr>')
        File.write('<tr><td><b>STD RR (SDNN): </b><i>'+info["stdrr"]+'</i></td></tr>')
        File.write('<tr><td><b>SDANN: </b><i>'+info["sdann"]+'</i></td></tr>')
        File.write('<tr><td><b>SDNNIDX: </b><i>'+info["sdnnidx"]+'</i></td></tr>')
        File.write('</table>\n</font></td>\n')
        File.write('<td align="left"><font size="-1"><table>\n')
        File.write('<tr><td><b>pNN50: </b><i>'+info["pnn50"]+'</i></td></tr>')
        File.write('<tr><td><b>rMSSD: </b><i>'+info["rMSSD"]+'</i></td></tr>')
        File.write('<tr><td><b>IRRR: </b><i>'+info["irrr"]+'</i></td></tr>')
        File.write('<tr><td><b>MADRR: </b><i>'+info["madrr"]+'</i></td></tr>')
        File.write('<tr><td><b>TINN: </b><i>'+info["tinn"]+'</i></td></tr>')
        File.write('<tr><td><b>HRV index: </b><i>'+info["hrvi"]+'</i></td></tr>')
        File.write('</table>\n</font>\n')
        File.write('</td></tr>\n')
        File.write('</table>\n')
        File.write("<hr>\n")

        # Non-linear analysis
        WriteSubtitleLine(File,'Non-linear analysis')
        info=self.GetInfoNonLinear()
        self.CreatePlotFile("Poincare",DirName+os.sep+ReportSubDir+os.sep+"Poincare.png",plotPoincareWidth,plotPoincareHeight)
        File.write('<table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'">\n')
        File.write('<tr align="center">')
        File.write('<td><img src="./'+ReportSubDir+'/Poincare.png"/></td>\n')
        File.write('<td align="left"><font size="-1"><table>\n')
        File.write('<tr><td><b>Poincar&eacute; Plot: </b></td></tr>')
        File.write('<tr><td><b>&nbsp;&nbsp;&nbsp;&nbsp;SD1: </b><i>'+info["SD1"]+'</i></td></tr>')
        File.write('<tr><td><b>&nbsp;&nbsp;&nbsp;&nbsp;SD2: </b><i>'+info["SD2"]+'</i></td></tr>')
        File.write('</table>\n</font>\n')
        File.write('</td>\n')

        if self.HasFrameBasedParams():
            File.write('<td align="left"><font size="-1"><table>\n')
            File.write('<tr><td><b>&nbsp;&nbsp;&nbsp;&nbsp;ApEn: </b><i>'+info["ApEn"]+'</i></td></tr>')
            File.write('<tr><td><b>&nbsp;&nbsp;&nbsp;&nbsp;FracDim: </b><i>'+info["FracDim"]+'</i></td></tr>')
            File.write('</table>\n</font>\n')
            File.write('</td>\n')
        
        File.write('</tr>\n')
        File.write('</table>\n')
        File.write("<hr>\n")
        
        # Frame-based parameters
        if self.HasInterpolatedHR():
            WriteSubtitleLine(File,'Frame-based analysis')
            self.CreatePlotFile("FB",DirName+os.sep+ReportSubDir+os.sep+"FB.png",plotFBWidth,plotFBHeight,zoomReset=True)
            File.write('<table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'">\n')
    
            File.write('<tr align="center"><td><img src="./'+ReportSubDir+'/FB.png"/></td></tr>\n')
            File.write('</table>\n')
            
            
            
            info = self.GetInfoFB()
            WriteSubsubtitleLine(File,'Window details')
            File.write('<font size="-1"><table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'">\n')
            File.write('<tr align="left"><td>&nbsp;&nbsp;&nbsp;</td>\n')
            File.write('<td><b>Interpolation freq.: </b><i>'+info["freqinterp"]+'</i></td>')
            File.write('<td><b>Frame length: </b><i>'+info["windowsize"]+'</i></td>')
            File.write('<td><b>Frame shift: </b><i>'+info["windowshift"]+'</i></td>')
            File.write('</tr>')
            File.write('<tr align="left"><td></td>')
            File.write('<td><b>No. of frames: </b><i>'+info["numframes"]+'</i></td>')
            File.write('<td><b>Window type: </b><i>'+info["windowtype"]+'</i></td>')
            File.write('<td><b>Mean removal: </b><i>'+info["meanremoval"]+'</i></td>')
            File.write('</tr>')
            File.write('</table></font>\n')
            File.write('<br><br>\n')
            
            WriteSubsubtitleLine(File,'Bands limits')
            File.write('<font size="-1"><table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'">\n')
            File.write('<tr align="left"><td>&nbsp;&nbsp;&nbsp;</td>\n')
            File.write('<td><b>ULF: </b><i>'+info["ulflim"]+'</i></td>')
            File.write('<td><b>VLF: </b><i>'+info["vlflim"]+'</i></td>')
            File.write('<td><b>LF: </b><i>'+info["lflim"]+'</i></td>')
            File.write('<td><b>HF: </b><i>'+info["hflim"]+'</i></td>')
            File.write('</tr>')
            File.write('</table></font>\n')
            File.write('<br><br>\n')
            
            WriteSubsubtitleLine(File,'Mean and STD of frame-based parameters')
            File.write('<font size="-1"><table cellspacing="0" border="0" width="'+str(HTMLPageWidth)+'">\n')
            File.write('<tr align="left"><td>&nbsp;&nbsp;&nbsp;</td>\n')
            File.write('<td><b>ULF power: </b><i>'+info["ulf"]+'</i></td>')
            File.write('<td><b>Total power: </b><i>'+info["Power"]+'</i></td>')
            File.write('<td><b>Mean HR: </b><i>'+info["Mean HR"]+'</i></td>')
            File.write('</tr>')
            
            File.write('<tr align="left"><td></td>')
            File.write('<td><b>VLF power: </b><i>'+info["vlf"]+'</i></td>')
            File.write('<td><b>LF/HF ratio: </b><i>'+info["LFHF"]+'</i></td>')
            File.write('<td><b>HR STD: </b><i>'+info["HR STD"]+'</i></td>')
            File.write('</tr>')
            
            File.write('<tr align="left"><td></td>')
            File.write('<td><b>LF power: </b><i>'+info["lf"]+'</i></td>')
            File.write('<td></td>')
            File.write('<td><b>pNN50: </b><i>'+info["pNN50"]+'</i></td>')
            File.write('</tr>')
            
            File.write('<tr align="left"><td></td>')
            File.write('<td><b>HF power: </b><i>'+info["hf"]+'</i></td>')
            File.write('<td></td>')
            File.write('<td><b>rMSSD: </b><i>'+info["rMSSD"]+'</i></td>')
            File.write('</tr>')
            
            File.write('</table></font>\n')
            File.write('<br><br>\n')
           
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
    
    def GetInfoFB(self):
        info={}
        info["freqinterp"]="{0:.2f} Hz".format(self.data["interpfreq"])
        info["windowsize"]="{0:.2f} sec.".format(self.data['windowsize'])
        info["windowshift"]="{0:.2f} sec.".format(self.data['windowshift'])
        
        shiftsamp=self.data['windowshift']*self.data["interpfreq"]
        sizesamp=self.data['windowsize']*self.data["interpfreq"]
        numframes=int(((len(self.data["HR"])-sizesamp)/shiftsamp)+1.0)
        info["numframes"]=str(numframes)
        
        info["windowtype"]="Hamming"
        info["meanremoval"]="yes"
        
        info["ulflim"]="{0:.3f} - {1:.3f} Hz".format(self.data['ulfmin'],self.data['ulfmax'])
        info["vlflim"]="{0:.3f} - {1:.3f} Hz".format(self.data['vlfmin'],self.data['vlfmax'])
        info["lflim"]="{0:.3f} - {1:.3f} Hz".format(self.data['lfmin'],self.data['lfmax'])
        info["hflim"]="{0:.3f} - {1:.3f} Hz".format(self.data['hfmin'],self.data['hfmax'])
        
        info["ulf"]="{0:.3f} &plusmn; {1:.3f} msec.&sup2;".format(np.mean(self.data['ULF']),np.std(self.data['ULF'],ddof=1))
        info["vlf"]="{0:.3f} &plusmn; {1:.3f} msec.&sup2;".format(np.mean(self.data['VLF']),np.std(self.data['VLF'],ddof=1))
        info["lf"]="{0:.3f} &plusmn; {1:.3f} msec.&sup2;".format(np.mean(self.data['LF']),np.std(self.data['LF'],ddof=1))
        info["hf"]="{0:.3f} &plusmn; {1:.3f} msec.&sup2;".format(np.mean(self.data['HF']),np.std(self.data['HF'],ddof=1))
        info["Power"]="{0:.3f} &plusmn; {1:.3f} msec.&sup2;".format(np.mean(self.data['Power']),np.std(self.data['Power'],ddof=1))
        info["LFHF"]="{0:.3f} &plusmn; {1:.3f}".format(np.mean(self.data['LFHF']),np.std(self.data['LFHF'],ddof=1))
        info["Mean HR"]="{0:.3f} &plusmn; {1:.3f} bps".format(np.mean(self.data['Mean HR']),np.std(self.data['Mean HR'],ddof=1))
        info["HR STD"]="{0:.3f} &plusmn; {1:.3f} bps".format(np.mean(self.data['HR STD']),np.std(self.data['HR STD'],ddof=1))
        info["pNN50"]="{0:.3f} &plusmn; {1:.3f} %".format(np.mean(self.data['pNN50']),np.std(self.data['pNN50'],ddof=1))
        info["rMSSD"]="{0:.3f} &plusmn; {1:.3f} msec.".format(np.mean(self.data['rMSSD']),np.std(self.data['rMSSD'],ddof=1))
                       
        
        return info
    
    
    def GetInfoTime(self, winsize=300.0, interval=7.8125):
        from scipy.stats.mstats import mquantiles
        
        info={}
        info["beats"]="{0:.2f}".format((len(self.data["BeatTime"])))
        info["minhr"]="{0:.2f}".format(min(self.data["niHR"]))
        info["maxhr"]="{0:.2f}".format(max(self.data["niHR"]))
        info["meanhr"]="{0:.2f} bps".format(np.mean(self.data["niHR"]))
        info["meanrr"]="{0:.2f} msec.".format(np.mean(self.data["RR"]))
        info["stdhr"]="{0:.2f} bps".format(np.std(self.data["niHR"],ddof=1))
        info["stdrr"]="{0:.2f} msec.".format(np.std(self.data["RR"],ddof=1))
        
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
                
        if len(RRWindowMean)>1:
            info["sdann"]="{0:.2f} msec.".format(np.std(RRWindowMean,ddof=1))
            info["sdnnidx"]="{0:.2f} msec.".format(np.mean(RRWindowSD))
        
        else:
            info["sdann"]="--"
            info["sdnnidx"]="--"
        
        RRDiffs=np.diff(self.data["RR"])
        RRDiffs50 = [x for x in np.abs(RRDiffs) if x>50]
        info["pnn50"]="{0:.2f}%".format(100.0*len(RRDiffs50)/len(RRDiffs))
        info["rMSSD"]="{0:.2f} msec.".format(np.sqrt(np.mean(RRDiffs**2)))
        
        RRQuant=mquantiles(RRDiffs)
        info["irrr"]="{0:.2f} msec.".format(RRQuant[-1]-RRQuant[0])
        
        info["madrr"]="{0:.2f} msec.".format(np.median(np.abs(RRDiffs)))
        
        minRR = min(self.data["RR"])
        maxRR = max(self.data["RR"])
        medRR = (minRR+maxRR)/2
        lowhist = medRR - interval * np.ceil((medRR - minRR)/interval)
        longhist = int(np.ceil((maxRR - lowhist)/interval) + 1)
        vecthist=np.array([lowhist+interval*i for i in range(longhist)])
        h=np.histogram(self.data["RR"],vecthist)
        area = float(len(self.data["RR"])) * interval
        maxhist = max(h[0])
        info["tinn"] = "{0:.2f} msec.".format(area/maxhist)
        info["hrvi"] = "{0:.2f}".format(float(len(self.data["RR"]))/maxhist)
   
        return info

    def GetInfoNonLinear(self):
        info={}
        xdata,ydata = self.GetPoincareDataPlot(tag="Global")
        sd1 = np.std((xdata-ydata)/np.sqrt(2.0),ddof=1)
        sd2 = np.std((xdata+ydata)/np.sqrt(2.0),ddof=1)
        info["SD1"] = "{0:.2G} msec.".format(sd1)
        info["SD2"] = "{0:.2G} msec.".format(sd2)
        if self.HasFrameBasedParams():
            info["ApEn"]= "{0:.2G} &plusmn; {1:.2G}".format(np.mean(self.data["ApEn"]),np.std(self.data['ApEn'],ddof=1))
            info["FracDim"]= "{0:.2G} &plusmn; {1:.2G}".format(np.mean(self.data["FracDim"]),np.std(self.data['FracDim'],ddof=1))
        return info
        
        
    def DataEditHR(self):
        """Data for edit non interpolated Heart Rate"""
        return (self.data["BeatTime"], self.data["niHR"], self.data["RR"])
    
    def HasVisibleEpisodes(self):
        """Checks if there are visible episodes in the data model"""
        if "EpisodesType" not in self.data:
            return(False)
        else:
            if (len(self.data["EpisodesVisible"])>0):
                return(True)
            else:
                return(False)
            
    def HasEpisodes(self):
        """Checks if there are episodes in the data model"""
        if "EpisodesType" in self.data:
            return(True)
        else:
            return(False)
                        
    def HasHR(self):
        """Checks if there are data for plotting HR (interpolated or not)"""
        if "niHR" in self.data or "HR" in self.data:
            return True
        else:
            return False
            
    def HasInterpolatedHR(self):
        """Checks if there are data of interpolated HR"""
        if "HR" in self.data:
            return True
        else:
            return False
                        
    def HasFrameBasedParams(self):
        """Checks if there is information of power bands"""
        if "ULF" in self.data:
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
            return ([],[])
    
    def SetVisibleEpisodes(self,ListOfEp):
        """Updates the list of visible episodes"""
        self.data["EpisodesVisible"]=ListOfEp

    def AddToVisibleEpisodes(self,tag):
        """Appends a tag to visible episodes list"""
        EpVis = self.GetVisibleEpisodes()[1]
        EpVis.append(tag)
        self.SetVisibleEpisodes(EpVis)

    def PurgeVisibleEpisodes(self):
        """Removes from visible episodes tags without episodes"""
        Eps = self.GetVisibleEpisodes()[0]
        Vis = self.GetVisibleEpisodes()[1]
        for tag in Vis:
            if tag not in Eps:
                Vis.remove(tag)
        self.SetVisibleEpisodes(Vis)
        # print "Eps: ",self.GetVisibleEpisodes()[0]
        # print "Vis: ",self.GetVisibleEpisodes()[1]

                
    def GetEpisodesTags(self):
        """Gets the list of tags of all the episodes (both visible and hidden)"""
        if self.HasEpisodes():
            return(list(set(self.data["EpisodesType"])))
        else:
            return([])

    def RenameEpisodes(self, OldTag, NewTag): 
        self.data["EpisodesType"] = [NewTag  if w == OldTag else w for w in self.data["EpisodesType"]]
        self.data["EpisodesVisible"] = [NewTag if w == OldTag else w for w in self.data["EpisodesVisible"] ]
        self.data["DictColors"][NewTag] = self.data["DictColors"].pop(OldTag)


    def GetVisibleBands(self):
        """Gets information of bands to plot"""
        return (self.data["Bands"],self.data["VisibleBands"])
    
    def GetFixedBands(self):
        """Gets informations of bands always in plot"""
        return self.data["FixedBands"]
    
    def GetHeartRatePlotTitle(self):
        """Gets title of Heart Rate Plot"""
        if "HR" in self.data:
            return (self.data["name"] + " - Interpolated HR")
        else:
            return(self.data["name"] + " - Non interpolated HR")

    def GetPoincarePlotTitle(self):
        return (self.data["name"] + " - Poincaré Plot")

    def GetPoincarePlotTags(self):
        return (self.data["PPActiveTagLeft"],self.data["PPActiveTagRight"])

    def GetPoincarePlotTagLeft(self):
        return (self.data["PPActiveTagLeft"])

    def GetPoincarePlotTagRight(self):
        return (self.data["PPActiveTagRight"])

    def SetPoincarePlotTagLeft(self,tag):
        self.data["PPActiveTagLeft"]=tag

    def SetPoincarePlotTagRight(self,tag):
        self.data["PPActiveTagRight"]=tag

    def SetVisibleBands(self,ListOfBands):
        """Changes the list of bands visible in plot"""
        self.data["VisibleBands"]=ListOfBands
            
    def GetFrameBasedDataPlot(self):
        """Returns data necessary for frame-based plot"""
        return(self.data["LFHF"], self.data["ULF"], self.data["VLF"], self.data["LF"], self.data["HF"],
            self.data["Power"],self.data["Mean HR"], self.data["HR STD"], self.data["pNN50"],
            self.data["rMSSD"], self.data["ApEn"], self.data["FracDim"], self.data["HR"])
        
    def SetSignifPlotParams(self,ActiveTagLeft,ActiveTagRight,ActiveParam):
        self.SignifPlotParam={}
        self.SignifPlotParam["ActiveTagLeft"]=ActiveTagLeft
        self.SignifPlotParam["ActiveTagRight"]=ActiveTagRight
        self.SignifPlotParam["ActiveParam"]=ActiveParam
        
    def GetSignifPlotParams(self):
        return (self.SignifPlotParam["ActiveTagLeft"],self.SignifPlotParam["ActiveTagRight"],self.SignifPlotParam["ActiveParam"])
    
        
    def GetFrameBasedData(self,param,tag):
        """Returns values of a parameter inside episodes, outside episodes and total"""
        total = self.data[param]
        framesCenters=np.array([x*self.data["windowshift"]+self.data["windowsize"]/2.0 for x in range(len(total))])

        tags,starts,durations,tagsVisible = self.GetEpisodes()
        numEpisodes=len(starts)

        startsvector=[starts[w] for w in range(numEpisodes) if tags[w]==tag]
        durationsvector=[durations[w] for w in range(numEpisodes) if tags[w]==tag]
        endsvector=[starts[w]+durations[w] for w in range(numEpisodes) if tags[w]==tag]

        inside=[]
        outside=[]
        for index in range(len(total)):
            isInside=False
            for indexEp in range(len(startsvector)):
                if (framesCenters[index] > startsvector[indexEp]) and (framesCenters[index] < endsvector[indexEp]):
                    isInside = True
            if isInside:
                inside.append(total[index])
            else:
                outside.append(total[index])

        return total,inside,outside
    
    # def CreatePlot(self,plotType):
        
    #     """Creates and opens a new plot with HR"""
    #     fig = matplotlib.pyplot.figure()
    #     axes = fig.add_subplot(1,1,1)
    #     if plotType=="HR":
    #         self.CreatePlotHREmbedded(axes)
    #     if plotType=="HRHistogram":
    #         self.CreatePlotHRHistogramEmbedded(axes)
    #     if plotType=="RRHistogram":
    #         self.CreatePlotRRHistogramEmbedded(axes)
    #     matplotlib.pyplot.grid(True)
    #     matplotlib.pyplot.show()
        
       
        
    def CreatePlotFile(self,plotType,filename,width=100,height=100,zoomReset=False,automatic=False):
        """Creates and saves a new plot"""
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        fig = Figure()
        if not automatic:
            fig.set_size_inches((width/plotDPI,height/plotDPI))
            
        if os.path.exists(filename) and platform!="darwin":
            confirm = Utils.OverwriteConfirm(filename)
            if not confirm:
                return
            
        
        if plotType=="HR":
            self.CreatePlotHREmbedded(fig,zoomReset,interactive=False)
        if plotType=="HRHistogram":
            self.CreatePlotHRHistogramEmbedded(fig)
        if plotType=="RRHistogram":
            self.CreatePlotRRHistogramEmbedded(fig)
        if plotType=="FB":
            self.CreatePlotFBEmbedded(fig,zoomReset,interactive=False)
        if plotType=="Poincare":
            self.CreatePlotPoincareEmbedded(fig,interactive=False)  
        if plotType=="Signif":
            self.CreatePlotSignifEmbedded(fig,interactive=False)
        canvas = FigureCanvasAgg(fig)

        if automatic:
            try:
                canvas.print_figure(filename)
                Utils.InformCorrectFile(filename)
            except:
#                print str(e)
                Utils.ErrorWindow(messageStr="Error saving figure to file: "+filename,captionStr="Error saving figure    ")
        else:
            try:
                canvas.print_figure(filename, dpi=plotDPI)
            except:
                Utils.ErrorWindow(messageStr="Error saving figure to file: "+filename,captionStr="Error saving figure    ")
                

    def CreatePlotPoincareEmbedded(self,fig,interactive=True,parentWindow=None):
    # def CreatePlotPoincareEmbedded(self,fig,interactive=True):

        from matplotlib.patches import Ellipse
        import wx
                
        def CreateSubplot(axes, xdata, ydata, titlestr=None, pos="left"):
            if pos=="left":
                color=".r"
            else:
                color=".c"
 
            meanx=np.mean(xdata)
            meany=np.mean(ydata)
 
            sd1 = np.std((xdata-ydata)/np.sqrt(2.0),ddof=1)
            sd2 = np.std((xdata+ydata)/np.sqrt(2.0),ddof=1)
 
            cad =""
 
            if self.GetPoincarePlotTagRight()!="None":
                cad += " "+titlestr+" - "
                cad += "SD1: %.2f ms. - SD2: %.2f ms." % (sd1,sd2)
                if pos=="left":
                    cad += "\n"
            else:
                cad += " SD1: %.2f ms. - SD2: %.2f ms." % (sd1,sd2)
              
            axes.plot(xdata,ydata,color)
 
            coordarrow1 =np.sqrt(sd2*sd2/2)
            coordarrow2 =np.sqrt(sd1*sd1/2)

            axes.arrow(meanx,meany,coordarrow1,coordarrow1,
                lw=1, length_includes_head=True, fc='k', zorder=3)

            axes.arrow(meanx, meany, -coordarrow2, coordarrow2,
                lw=1, length_includes_head=True, fc='k', zorder=4)
 
 
            axes.set_xlim(mincoord,maxcoord)
            axes.set_ylim(mincoord,maxcoord)
            axes.set_xlabel("$RR_i (msec.)$")
            if pos=="left":
                axes.set_ylabel("$RR_{i+1} (msec.)$")
 
            if self.GetPoincarePlotTagRight()=="None":
                if self.GetPoincarePlotTagLeft()=="Global":
                    axes.set_title(self.GetPoincarePlotTitle())
                else:
                    axes.set_title(self.GetPoincarePlotTagLeft())
 
            else:
                axes.set_title(titlestr)
                fig.suptitle(self.GetPoincarePlotTitle())
 
             
 
#             if self.data["Verbose"]==True:
#                 if titlestr:
#                     print ("** Creating Poincare Plot  -  " + titlestr)
#                 else:
#                     print ("** Creating Poincare Plot")
#                 print("   SD1: {0:.3f}".format(sd1))
#                 print("   SD2: {0:.3f}".format(sd2))
#          
            ell=Ellipse(xy=(meanx,meany),width=2*sd1,height=2*sd2,angle=-45,linewidth=1, color='k', fc="none")
            axes.add_artist(ell)
            # ell.set_alpha(0.7)
            ell.set(zorder=2)
 
            axes.grid(True)
            return cad
            # End of CreateSubplot
#         
        
        if interactive:
            def saveplot(event):
                fileName = Utils.SavePlotFileName(self.GetName()+"_PP")
                if fileName != None:
                    if self.data["Verbose"]:
                        print(("** Poincare Saving figure in file: "+fileName))
                    self.CreatePlotFile('Poincare',fileName,zoomReset=False,automatic=True)

            def configplot(event):
                if self.GetPoincarePlotTagRight()=="None":
                    minAxisPrev,maxAxisPrev = axes.get_xlim()
                else:
                    minAxisPrev,maxAxisPrev = axes1.get_xlim()
                dia = Utils.ConfigPoincarePlot(parentWindow, -1,
                    int(minAxisPrev),
                    int(maxAxisPrev))
                if dia.ShowModal() == wx.ID_OK :
                    error=False
                    try:
                        minAxisNew = float(dia.AxesMin.GetValue())
                        maxAxisNew = float(dia.AxesMax.GetValue())
                        assert minAxisNew<maxAxisNew
                    except:
                        error = True
                        Utils.ErrorWindow("Invalid limits for Poincaré plot")
                    if not error:
                        if self.GetPoincarePlotTagRight()=="None":
                            axes.set_xlim(float(minAxisNew),float(maxAxisNew))
                            axes.set_ylim(float(minAxisNew),float(maxAxisNew))
                        else:
                            axes1.set_xlim(float(minAxisNew),float(maxAxisNew))
                            axes1.set_ylim(float(minAxisNew),float(maxAxisNew))
                            axes2.set_xlim(float(minAxisNew),float(maxAxisNew))
                            axes2.set_ylim(float(minAxisNew),float(maxAxisNew))
                        self.data["PlotPPMin"] = float(minAxisNew)
                        self.data["PlotPPMax"] = float(maxAxisNew)
                        fig.canvas.draw()

                    dia.Destroy()
                        
        fig.clear()
        
                
        cad =""
 
        if self.GetPoincarePlotTagRight()=="None":
            axes = fig.add_subplot(111, aspect='equal')
            xvector,yvector = self.GetPoincareDataPlot(tag=self.GetPoincarePlotTagLeft())
            maxval=max(max(xvector),max(yvector))
            minval=min(min(xvector),min(yvector))
        else:
            axes1 = fig.add_subplot(121, aspect='equal')
            axes2 = fig.add_subplot(122, aspect='equal')
            xvector1,yvector1 = self.GetPoincareDataPlot(tag=self.GetPoincarePlotTagLeft())
            xvector2,yvector2 = self.GetPoincareDataPlot(tag=self.GetPoincarePlotTagRight())
            minval=min(min(xvector1),min(yvector1),min(xvector2),min(yvector2))
            maxval=max(max(xvector1),max(yvector1),max(xvector2),max(yvector2))


 
 
        mincoord=minval*0.9
        maxcoord=maxval*1.1
        
        if interactive:
            self.data["PlotPPMin"]=mincoord
            self.data["PlotPPMax"]=maxcoord
 
 
 
        if self.GetPoincarePlotTagRight()=="None":
            cad += CreateSubplot(axes, xvector, yvector)
        else:
            cad +=CreateSubplot(axes1, xvector1, yvector1, titlestr=self.GetPoincarePlotTagLeft())
            cad +=CreateSubplot(axes2, xvector2, yvector2, titlestr=self.GetPoincarePlotTagRight(), pos="right")
          
        
        if interactive:
            if self.GetPoincarePlotTagRight()=="None":
                newaxsaveplot = fig.add_axes(axes.get_position())
                newaxconfigplot = fig.add_axes(axes.get_position())
            else:
                newaxsaveplot = fig.add_axes(axes1.get_position())
                newaxconfigplot = fig.add_axes(axes1.get_position())
     
            newaxsaveplot.set_position([
                  2*plotFormat['buttonsmargin'],
                  1.0-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                  1.5*plotFormat['savebuttonwidth'],
                  1.5*plotFormat['littlebuttonsize']
              ])
            self.PPbtsaveplot=Button(newaxsaveplot,"Save")
            self.PPbtsaveplot.on_clicked(saveplot)

            newaxconfigplot.set_position([
                  2*plotFormat['buttonsmargin'],
                  1.0-4*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                  1.5*plotFormat['savebuttonwidth'],
                  1.5*plotFormat['littlebuttonsize']
              ])
            self.PPbtconfigplot=Button(newaxconfigplot,"Config")
            self.PPbtconfigplot.on_clicked(configplot)

        else:  # Exporting to file reads the axis limits to create the plot

            if self.GetPoincarePlotTagRight()=="None":
                if "PlotPPMin" not in list(self.data.keys()):
                    self.data["PlotPPMin"] = min(min(xvector), min(yvector))*0.9
                if "PlotPPMax" not in list(self.data.keys()):
                    self.data["PlotPPMax"] = max(max(xvector),max(yvector))*1.1
                axes.set_xlim(self.data["PlotPPMin"],self.data["PlotPPMax"])
                axes.set_ylim(self.data["PlotPPMin"],self.data["PlotPPMax"])
            else:
                axes1.set_xlim(self.data["PlotPPMin"],self.data["PlotPPMax"])
                axes1.set_ylim(self.data["PlotPPMin"],self.data["PlotPPMax"])
                axes2.set_xlim(self.data["PlotPPMin"],self.data["PlotPPMax"])
                axes2.set_ylim(self.data["PlotPPMin"],self.data["PlotPPMax"])


        matplotlib.pyplot.show()
        
        return cad
        
    def CreatePlotSignifEmbedded(self,fig,interactive=True):
        
        def CreateHistogram():
            fig.clear()
            SignifAxes = fig.add_subplot(1,1,1)    
            SignifAxes.hist([valuesleft,valuesright], self.signifNumBins, 
                            weights = [valuesleftweight,valuesrightweight],
                            normed=False, histtype='bar',
                            color=['red', 'cyan'],
                            label=labels)
            SignifAxes.set_title('Histogram: '+self.ActiveParamSignif)

            SignifAxes.legend(bbox_to_anchor=(1., -0.1), loc=1,
                            ncol=2, borderaxespad=0.)
            SignifAxes.grid()
           
        
            
                
        self.ActiveTagLeftSignif, self.ActiveTagRightSignif, self.ActiveParamSignif = self.GetSignifPlotParams()
        if interactive:
            self.signifNumBins=signifNumBins
        
        if interactive:
            def morebins(event):
                if self.data["Verbose"]:
                    print("  Significance plot: increasing number of bins")
                self.signifNumBins += 1
#                 self.CreatePlotSignifEmbedded(fig, interactive=True)
                CreateHistogram()
                CreateButtons()
                fig.canvas.draw()
                
            def lessbins(event):
                if self.signifNumBins <= 2:
                    return
                if self.data["Verbose"]:
                    print("  Significance plot: decreasing number of bins")
                self.signifNumBins -= 1
#                 self.CreatePlotSignifEmbedded(fig, interactive=True)
                CreateHistogram()
                CreateButtons()
                fig.canvas.draw()
            
            def resetbins(event):
                if self.data["Verbose"]:
                    print("  Significance plot: reseting number of bins")
                self.signifNumBins = signifNumBins
#                 self.CreatePlotSignifEmbedded(fig, interactive=True)
                CreateHistogram()
                CreateButtons()
                fig.canvas.draw()

            def saveplot(event):
                # from matplotlib.backends.backend_agg import FigureCanvasAgg
                fileName = Utils.SavePlotFileName(self.GetName()+"_Hist")
                if fileName != None:
                    if self.data["Verbose"]:
                        print(("** Significance histogram figure in file: "+fileName))
                    self.CreatePlotFile('Signif',fileName,zoomReset=False,automatic=True)
                    
        def CreateButtons():
            newaxmorebins = fig.add_axes(SignifAxes.get_position())
            newaxmorebins.set_position([
               1.0-1.5*plotFormat['savebuttonwidth']-2*plotFormat['buttonsmargin'],
               1.0-2*plotFormat['littlebuttonsize']-plotFormat['buttonsmargin'],
               1.5*plotFormat['savebuttonwidth'],
               1.5*plotFormat['littlebuttonsize']
            ])
            self.Signifbtmorebins=Button(newaxmorebins,"+ bins")
            self.Signifbtmorebins.on_clicked(morebins)

            newaxlessbins = fig.add_axes(SignifAxes.get_position())
            newaxlessbins.set_position([
               1.0-1.5*plotFormat['savebuttonwidth']-2*plotFormat['buttonsmargin'],
               1.0-3*plotFormat['littlebuttonsize']-6*plotFormat['buttonsmargin'],
               1.5*plotFormat['savebuttonwidth'],
               1.5*plotFormat['littlebuttonsize']
            ])
            self.Signifbtlessbins=Button(newaxlessbins,"- bins")
            self.Signifbtlessbins.on_clicked(lessbins)
            
            newaxresetbins = fig.add_axes(SignifAxes.get_position())
            newaxresetbins.set_position([
               1.0-1.5*plotFormat['savebuttonwidth']-2*plotFormat['buttonsmargin'],
               1.0-4*plotFormat['littlebuttonsize']-11*plotFormat['buttonsmargin'],
               1.5*plotFormat['savebuttonwidth'],
               1.5*plotFormat['littlebuttonsize']
            ])
            self.Signifbtresetbins=Button(newaxresetbins,"Reset")
            self.Signifbtresetbins.on_clicked(resetbins)
            
            newaxsaveplot = fig.add_axes(SignifAxes.get_position())
            newaxsaveplot.set_position([
                1.0-1.5*plotFormat['savebuttonwidth']-2*plotFormat['buttonsmargin'],
                1.0-5*plotFormat['littlebuttonsize']-16*plotFormat['buttonsmargin'],
                1.5*plotFormat['savebuttonwidth'],
                1.5*plotFormat['littlebuttonsize']
            ])
            self.Signifbtsaveplot=Button(newaxsaveplot,"Save")
            self.Signifbtsaveplot.on_clicked(saveplot)
            # End of CreateButtons
        
        ActiveParamTmp = self.ActiveParamSignif
        if ActiveParamTmp=="LF/HF":
            ActiveParamTmp="LFHF"
        valuesleft = self.GetFrameBasedData(ActiveParamTmp,self.ActiveTagLeftSignif)[1]
        if not self.ActiveTagRightSignif:
            valuesright = self.GetFrameBasedData(ActiveParamTmp,self.ActiveTagLeftSignif)[2]
        else:
            valuesright = self.GetFrameBasedData(ActiveParamTmp,self.ActiveTagRightSignif)[1]
            
        valuesleftweight=np.ones_like(valuesleft)/len(valuesleft)
        valuesrightweight=np.ones_like(valuesright)/len(valuesright)
        
        fig.clear()
        SignifAxes = fig.add_subplot(1,1,1)    
            
#        print "signifNumMinValues: ",signifNumMinValues
#        print "valuesleft:",len(valuesleft)
#        print "valuesright:",len(valuesright)
            
        if (len(valuesleft)>signifNumMinValues) and (len(valuesright)>signifNumMinValues):
            self.EnoughDataSignif=True
            
            if self.ActiveTagRightSignif:
                labels= [self.ActiveTagLeftSignif, self.ActiveTagRightSignif]
            else: 
                labels= ["Inside " +self.ActiveTagLeftSignif, "Outside " +self.ActiveTagLeftSignif]
            
            CreateHistogram()
            if interactive:
                CreateButtons()
                
            if not interactive:
                fig.subplots_adjust(bottom=0.15,left=0.07,right=0.97,top=0.94)
                    
        else:
            self.EnoughDataSignif=False
            
            SignifAxes.set_xlim(-1,1)
            SignifAxes.set_ylim(-1,1)
            SignifAxes.text(0.0, 0.0, "Not enough data", size=20,
                            horizontalalignment='center',
                            verticalalignment='center',
                            bbox=dict(boxstyle='round',facecolor='red', alpha=0.5))
#            
          
        return (valuesleft,valuesright)
        
        
        
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
        
    
    def CreatePlotHREmbedded(self,fig,zoomReset=False,interactive=True):
        """Creates an HR Plot embedded in axes
        Valid for windows and stand-alone plots"""
        
        # interactive = True when the plot is showed in the GUI

        if interactive: 
            self.HRPosLinePresent=False
    
            def drawPosLine():
                ymin,ymax = HRaxes.get_ylim()
                ypos = ymin+(ymax-ymin)*0.01
                
                xvector = self.GetHRDataPlot()[0]
                xminrel = (self.data["PlotHRXMin"]-xvector[0])/(xvector[-1]-xvector[0])
                xmaxrel = (self.data["PlotHRXMax"]-xvector[0])/(xvector[-1]-xvector[0])
                if self.HRPosLinePresent:
                    self.fgHRPosLine.remove()
                    self.bgHRPosLine.remove()
                self.bgHRPosLine = HRaxes.axhline(y=ypos,color='g',linewidth=1)
                self.fgHRPosLine = HRaxes.axhline(y=ypos,color='g',linewidth=5,xmin=xminrel,xmax=xmaxrel)
                self.HRPosLinePresent=True
    
    
            def zoomin(event):
                if self.data["Verbose"]:
                    print("** HR Zoom in")
                delta=(self.data["PlotHRXMax"]-self.data["PlotHRXMin"])*0.1
                self.data["PlotHRXMin"]+=delta
                self.data["PlotHRXMax"]-=delta
                HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
                drawPosLine()
                fig.canvas.draw()
    
    
            def zoomout(event):
                if self.data["Verbose"]:
                    print("** HR Zoom out")
                delta=(self.data["PlotHRXMax"]-self.data["PlotHRXMin"])*0.2
                self.data["PlotHRXMin"]-=delta
                self.data["PlotHRXMax"]+=delta
                xvector = self.GetHRDataPlot()[0]
                self.data["PlotHRXMin"]=max(xvector[0],self.data["PlotHRXMin"])
                self.data["PlotHRXMax"]=min(xvector[-1],self.data["PlotHRXMax"])
                HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
                drawPosLine()
                fig.canvas.draw()
                
    
            def zoomreset(event):
                if self.data["Verbose"]:
                    print("** HR Zoom reset")
                xvector = self.GetHRDataPlot()[0]
                self.data["PlotHRXMin"] = xvector[0]
                self.data["PlotHRXMax"] = xvector[-1]
                HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
                drawPosLine()
                fig.canvas.draw()
    
    
            def panright(event):
                if self.data["Verbose"]:
                    print("** HR Pan right")
                delta=(self.data["PlotHRXMax"]-self.data["PlotHRXMin"])*0.1
                xvector = self.GetHRDataPlot()[0]
                delta=min(delta,xvector[-1]-self.data["PlotHRXMax"])
                self.data["PlotHRXMin"] += delta
                self.data["PlotHRXMax"] += delta
                HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
                drawPosLine()
                fig.canvas.draw()
    
    
            def panleft(event):
                if self.data["Verbose"]:
                    print("** HR Pan left")
                delta=(self.data["PlotHRXMax"]-self.data["PlotHRXMin"])*0.1
                xvector = self.GetHRDataPlot()[0]
                delta=min(delta,self.data["PlotHRXMin"]-xvector[0])
                self.data["PlotHRXMin"] -= delta
                self.data["PlotHRXMax"] -= delta
                HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
                drawPosLine()
                fig.canvas.draw()
    
            def saveplot(event):
                # from matplotlib.backends.backend_agg import FigureCanvasAgg
                fileName = Utils.SavePlotFileName(self.GetName()+"_HR")
                if fileName != None:
                    if self.data["Verbose"]:
                        print(("** HR Saving figure in file: "+fileName))
                    self.CreatePlotFile('HR',fileName,zoomReset=False,automatic=True)
                

        
        
        HRaxes = fig.add_subplot(1,1,1)
        
        fig.subplots_adjust(
            left=plotFormat['left'],
            bottom=plotFormat['bottom'],
            right=plotFormat['right'],
            top=plotFormat['top'],
            wspace=plotFormat['wspace'],
            hspace=plotFormat['hspace']
        )


        
        xvector, yvector = self.GetHRDataPlot()
        if "PlotHRXMin" not in self.data:
            self.data["PlotHRXMin"]=xvector[0]
            self.data["PlotHRXMax"]=xvector[-1]
        
        HRaxes.plot(xvector,yvector,'k-')
        HRaxes.set_xlabel("Time (sec.)")
        HRaxes.set_ylabel("HR (beats/min.)")
        
        
        HRaxes.set_title(self.GetHeartRatePlotTitle())


        if interactive:
            newaxzoomin = fig.add_axes(HRaxes.get_position())
            newaxzoomin.set_position([
                plotFormat['left']+plotFormat['littlebuttonsize']+2*plotFormat['buttonsmargin'],
                plotFormat['top']-plotFormat['littlebuttonsize']-plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.HRbtzoomin=Button(newaxzoomin,"+")
            self.HRbtzoomin.on_clicked(zoomin)

            newaxzoomout = fig.add_axes(HRaxes.get_position())
            newaxzoomout.set_position([
                plotFormat['left']+plotFormat['littlebuttonsize']+2*plotFormat['buttonsmargin'],
                plotFormat['top']-3*plotFormat['littlebuttonsize']-3*plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.HRbtzoomout=Button(newaxzoomout,"-")
            self.HRbtzoomout.on_clicked(zoomout)

            newaxzoomreset = fig.add_axes(HRaxes.get_position())
            newaxzoomreset.set_position([
                plotFormat['left']+plotFormat['littlebuttonsize']+2*plotFormat['buttonsmargin'],
                plotFormat['top']-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.HRbtzoomreset=Button(newaxzoomreset,"0")
            self.HRbtzoomreset.on_clicked(zoomreset)

            newaxpanright = fig.add_axes(HRaxes.get_position())
            newaxpanright.set_position([
                plotFormat['left']+2*plotFormat['littlebuttonsize']+3*plotFormat['buttonsmargin'],
                plotFormat['top']-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.HRbtpanright=Button(newaxpanright,">")
            self.HRbtpanright.on_clicked(panright)

            newaxpanleft = fig.add_axes(HRaxes.get_position())
            newaxpanleft.set_position([
                plotFormat['left']+plotFormat['buttonsmargin'],
                plotFormat['top']-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.HRbtpanleft=Button(newaxpanleft,"<")
            self.HRbtpanleft.on_clicked(panleft)

            newaxsaveplot = fig.add_axes(HRaxes.get_position())
            newaxsaveplot.set_position([
                plotFormat['left']+2*plotFormat['buttonsmargin']+1.5*plotFormat['littlebuttonsize']-0.5*plotFormat['savebuttonwidth'],
                plotFormat['top']-4*plotFormat['littlebuttonsize']-4*plotFormat['buttonsmargin'],
                plotFormat['savebuttonwidth'],
                plotFormat['littlebuttonsize']
            ])
            self.HRbtsaveplot=Button(newaxsaveplot,"Save")
            self.HRbtsaveplot.on_clicked(saveplot)

            drawPosLine()

            # End program block if interactive = True
            
        
        if self.HasVisibleEpisodes():
            tags,starts,durations,tagsVisible = self.GetEpisodes()
            numEpisodes=len(starts)
            i=0
            for tag in tagsVisible:
                startsvector=[starts[w] for w in range(numEpisodes) if tags[w]==tag]
                durationsvector=[durations[w] for w in range(numEpisodes) if tags[w]==tag]
                endsvector=[starts[w]+durations[w] for w in range(numEpisodes) if tags[w]==tag]
                for j in range(len(startsvector)):
                    if j==0:
                        HRaxes.axvspan(startsvector[j], endsvector[j], ymin=plotFormat['ymintag'], ymax=plotFormat['ymaxtag'], facecolor=self.GetEpisodeColor(tag), alpha=alphaMatplotlibTags, label=tag)
                    else:
                        HRaxes.axvspan(startsvector[j], endsvector[j], ymin=plotFormat['ymintag'], ymax=plotFormat['ymaxtag'], facecolor=self.GetEpisodeColor(tag), alpha=alphaMatplotlibTags)
                i=i+1
            leg=HRaxes.legend(fancybox=True,shadow=True)
            for t in leg.get_texts():
                t.set_fontsize('small')
                
        if not zoomReset:       
            HRaxes.set_xlim(self.data["PlotHRXMin"],self.data["PlotHRXMax"])
            
        HRaxes.grid()
        
        # end of CreateHRPlotEmbedded
        
        
        
    
        
    def CreatePlotFBEmbedded(self, fig, zoomReset=False, interactive=True):

        """ Redraws the frame-based evolution figure"""
        
        def CreateBandSupblot(axes,x,y,ylabel):
            axes.plot(x,y,'-k')        
            axes.set_ylabel(ylabel)
            if ylabel not in ["Mean HR","HR STD","ApEn","Heart rate"]:
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
                
        if interactive:
            self.FBPosLinePresent=False
    
            def drawPosLine():
                ymin,ymax = axBottom.get_ylim()
                ypos = ymin+(ymax-ymin)*0.02
                
                xminabs = 0
                xmaxabs = 1.0/self.data["interpfreq"]*(len(self.data["HR"])-1)
                
                xminrel = (self.data["PlotFBXMin"]-xminabs)/(xmaxabs-xminabs)
                xmaxrel = (self.data["PlotFBXMax"]-xminabs)/(xmaxabs-xminabs)
                if self.FBPosLinePresent:
                    self.fgFBPosLine.remove()
                    self.bgFBPosLine.remove()
                self.bgFBPosLine = axBottom.axhline(y=ypos,color='b',linewidth=1)
                self.fgFBPosLine = axBottom.axhline(y=ypos,color='b',linewidth=5,xmin=xminrel,xmax=xmaxrel)
                self.FBPosLinePresent=True
    
    
            def zoomin(event):
                delta=(self.data["PlotFBXMax"]-self.data["PlotFBXMin"])*0.1
                self.data["PlotFBXMin"]+=delta
                self.data["PlotFBXMax"]-=delta
                for axes in FBaxesbands:
                    axes.set_xlim(self.data["PlotFBXMin"],self.data["PlotFBXMax"])
                if self.data["Verbose"]:
                    print("** FB Zoom in")
                drawPosLine()
                fig.canvas.draw()
    
            def zoomout(event):
                delta=(self.data["PlotFBXMax"]-self.data["PlotFBXMin"])*0.2
                self.data["PlotFBXMin"]-=delta
                self.data["PlotFBXMax"]+=delta
                maxtmp=1.0/self.data["interpfreq"]*(len(self.data["HR"])-1)
                self.data["PlotFBXMin"]=max(0,self.data["PlotFBXMin"])
                self.data["PlotFBXMax"]=min(maxtmp,self.data["PlotFBXMax"])
                for axes in FBaxesbands:
                    axes.set_xlim(self.data["PlotFBXMin"],self.data["PlotFBXMax"])
                if self.data["Verbose"]:
                    print("** FB Zoom out")
                drawPosLine()
                fig.canvas.draw()
    
            def zoomreset(event):
                self.data["PlotFBXMin"] = 0
                self.data["PlotFBXMax"] = 1.0/self.data["interpfreq"]*(len(self.data["HR"])-1)
                for axes in FBaxesbands:
                    axes.set_xlim(self.data["PlotFBXMin"],self.data["PlotFBXMax"])
                if self.data["Verbose"]:
                    print("** FB Zoom reset")
                drawPosLine()
                fig.canvas.draw()
    
            def panright(event):
                delta=(self.data["PlotFBXMax"]-self.data["PlotFBXMin"])*0.1
                maxtmp=1.0/self.data["interpfreq"]*(len(self.data["HR"])-1)
                delta=min(delta,maxtmp-self.data["PlotFBXMax"])
                self.data["PlotFBXMin"] += delta
                self.data["PlotFBXMax"] += delta
                for axes in FBaxesbands:
                    axes.set_xlim(self.data["PlotFBXMin"],self.data["PlotFBXMax"])
                if self.data["Verbose"]:
                    print("** FB Pan right")
                drawPosLine()
                fig.canvas.draw()
    
            def panleft(event):
                delta=(self.data["PlotFBXMax"]-self.data["PlotFBXMin"])*0.1
                delta=min(delta,self.data["PlotFBXMin"])
                self.data["PlotFBXMin"] -= delta
                self.data["PlotFBXMax"] -= delta
                for axes in FBaxesbands:
                    axes.set_xlim(self.data["PlotFBXMin"],self.data["PlotFBXMax"])
                if self.data["Verbose"]:
                    print("** FB Pan left")
                drawPosLine()
                fig.canvas.draw()
    
            def saveplot(event):
                # from matplotlib.backends.backend_agg import FigureCanvasAgg
                fileName = Utils.SavePlotFileName(self.GetName()+"_FB")
                if fileName != None:
                    if self.data["Verbose"]:
                        print(("** FB Saving figure in file: "+fileName))
                    self.CreatePlotFile('FB',fileName,zoomReset=False,automatic=True)
                    
        # end of if interactive



        
        
        
        fig.clear()
        xvectortimemin=0
        xvectortimemax=1.0/self.data["interpfreq"]*(len(self.data["HR"])-1)
        xvectortime=np.linspace(start=0, stop=xvectortimemax, num=len(self.data["HR"]))
        
        if "PlotFBXMin" not in self.data:
            self.data["PlotFBXMin"]=0
            self.data["PlotFBXMax"]=xvectortimemax
       

        lfhfvector, ulfvector, vlfvector, lfvector, hfvector, powervector, meanhrvector, hrstdvector, pnn50vector, rmssdvector, apenvector, fracdimvector, hrvector = self.GetFrameBasedDataPlot()
        xvectorframe=np.array([x*self.data["windowshift"]+self.data["windowsize"]/2.0 for x in range(len(ulfvector))])
        
        self.AllBands, self.VisibleBands=self.GetVisibleBands()
        
        hasEpisodes=self.HasVisibleEpisodes()
        if hasEpisodes:
            tags,starts,durations,tagsVisible = self.GetEpisodes()
            starts=np.array(starts)
            durations=np.array(durations)
            ends=starts+durations
            numEpisodes=len(tags)

        plotFormat={
            'left':0.07,
            'bottom':0.07,
            'top':0.94,
            'wspace':0.20,
            'hspace':.15,
            'ymintag':0.04,
            'ymaxtag':0.96,
            'littlebuttonsize':0.025,
            'buttonsmargin':0.007,
            'savebuttonwidth':0.04
        } 

        if hasEpisodes:
            plotFormat['right']=0.86
            if not interactive:
                plotFormat['right']=0.80
        else:
            plotFormat['right']=0.98

        
                              
        matplotlib.rc('xtick', labelsize=10) 
        matplotlib.rc('ytick', labelsize=10) 
        matplotlib.rc('legend', fontsize=10) 
        
        
        FBaxesbands=[]
            
        # Heart rate plot
        axBottom = fig.add_subplot(len(self.VisibleBands),1,len(self.VisibleBands))
        CreateBandSupblot(axBottom, xvectortime, hrvector, 'Heart rate')
        axBottom.tick_params(axis='x',labelbottom='on')
        axBottom.set_xlabel('Time [sec.]',fontsize=10)
        
        if hasEpisodes:
            AddEpisodesToBandSubplot(axBottom,legend=True)

            leg=axBottom.legend(bbox_to_anchor=(1.02, 0.0), loc=3, ncol=1, borderaxespad=0.)
            for t in leg.get_texts():
                t.set_fontsize('small')
                
        FBaxesbands.append(axBottom)

           
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
            if Band == "rMSSD":
                CreateBandSupblot(axBand, xvectorframe, rmssdvector, 'rMSSD')   
            if Band == "ApEn":
                CreateBandSupblot(axBand, xvectorframe, apenvector, 'ApEn')  
            if Band == "FracDim":
                CreateBandSupblot(axBand, xvectorframe, fracdimvector, 'FracDim')       
    
            if hasEpisodes :
                AddEpisodesToBandSubplot(axBand)
                
            FBaxesbands.append(axBand)
        
        if not zoomReset:        
            for axes in FBaxesbands:
                axes.set_xlim(self.data["PlotFBXMin"],self.data["PlotFBXMax"])  
        
        fig.suptitle(self.GetName() + " - frame-based evolution", fontsize=16)


        fig.subplots_adjust(
            left=plotFormat['left'],
            bottom=plotFormat['bottom'],
            right=plotFormat['right'],
            top=plotFormat['top'],
            wspace=plotFormat['wspace'],
            hspace=plotFormat['hspace']
        )

        if interactive:

            newaxzoomin = fig.add_axes(axBottom.get_position())
            newaxzoomin.set_position([
                1.0-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                1.0-plotFormat['littlebuttonsize']-plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.FBbtzoomin=Button(newaxzoomin,"+")
            self.FBbtzoomin.on_clicked(zoomin)

            newaxzoomout = fig.add_axes(axBottom.get_position())
            newaxzoomout.set_position([
                1.0-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                1.0-3*plotFormat['littlebuttonsize']-3*plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.FBbtzoomout=Button(newaxzoomout,"-")
            self.FBbtzoomout.on_clicked(zoomout)

            newaxzoomreset = fig.add_axes(axBottom.get_position())
            newaxzoomreset.set_position([
                1.0-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                1.0-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.FBbtzoomreset=Button(newaxzoomreset,"0")
            self.FBbtzoomreset.on_clicked(zoomreset)

            newaxpanright = fig.add_axes(axBottom.get_position())
            newaxpanright.set_position([
                1.0-plotFormat['littlebuttonsize']-plotFormat['buttonsmargin'],
                1.0-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.FBbtpanright=Button(newaxpanright,">")
            self.FBbtpanright.on_clicked(panright)

            newaxpanleft = fig.add_axes(axBottom.get_position())
            newaxpanleft.set_position([
                1.0-3*plotFormat['littlebuttonsize']-3*plotFormat['buttonsmargin'],
                1.0-2*plotFormat['littlebuttonsize']-2*plotFormat['buttonsmargin'],
                plotFormat['littlebuttonsize'],
                plotFormat['littlebuttonsize']
            ])
            self.FBbtpanleft=Button(newaxpanleft,"<")
            self.FBbtpanleft.on_clicked(panleft)


            newaxsaveplot = fig.add_axes(axBottom.get_position())
            newaxsaveplot.set_position([
                1.0-0.5*plotFormat['savebuttonwidth']-2*plotFormat['buttonsmargin']-1.5*plotFormat['littlebuttonsize'],
                1.0-4*plotFormat['littlebuttonsize']-4*plotFormat['buttonsmargin'],
                plotFormat['savebuttonwidth'],
                plotFormat['littlebuttonsize']
            ])
            self.FBbtsaveplot=Button(newaxsaveplot,"Save")
            self.FBbtsaveplot.on_clicked(saveplot)
            
            drawPosLine()


        # end of "if interactive"

    # End of CreatePlotFBEmbedded


                
                    
        
        



