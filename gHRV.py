#!/usr/bin/python
# -*- coding:utf-8 -*-

#   ----------------------------------------------------------------------
#   gHRV: a graphical application for Heart Rate Variability analysis
#   Copyright (C) 2013  Milegroup - Dpt. Informatics
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
    
# TODO: 
#   - cambiar interacción con las figuras
#   - check overwrite in plot save
#   - seleccionar tipos de latidos cargados en ficheros physionet
#   - cuando se importa un fichero de una versión anterior se recalculan parámetros por trama. Usar progress bar
#   - report con un fichero grande es muy lento
#   - colores/monocromo
#   - Las ventanas que lanza la aplicación son bastante anchas. En mi equipo no cogen a lo ancho. Idealmente, la aplicación debería comprobar el tamaño de la pantalla antes de lanzar la ventana y asegurarse que el tamaño de ventana que usa inicial es menor que el tamaño de ventana.
#   - Yo hubiese empleado el icono de la herramienta (el dibujo de Leonardo) como icono de todas las ventanas, y no ese icono con forma de libreta de notas que tienen.
#   - Yo veo muy interesante el poder especificar una fecha base para el registro, y visualizar sobre el eje horizontal fechas absolutas y no sólo el tiempo en segundos. Esto es muy importante para añadir episodios manualmente


import wx
import matplotlib
# matplotlib.use('WXAgg')
# from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.pyplot
import os
import numpy as np
from sys import platform

from DataModel import DM
from configvalues import *
from AboutDlg import AboutDlg
from FrameBased import *
from EditEpisodes import EditEpisodesWindow
from EditNIHR import EditNIHRWindow
from PoincarePlot import PoincarePlotWindow
from ReportWindow import *
import Utils

# os.chdir("/usr/share/ghrv") # Uncomment when building a .deb package

dm=DM(Verbose)

# For debugging errors
# import sys
# sys.stdout = open('~/program.out', 'w')
# sys.stderr = open('~/program.err', 'w')
 



        
class MainWindow(wx.Frame):
    """ Main window application"""

    configDir = os.path.expanduser('~')+os.sep+'.ghrv'
    configFile = configDir+os.sep+"ghrv.cfg"
    sbDefaultText="  gHRV %s - http://ghrv.milegroup.net" % Version
        
    def __init__(self, parent, id, title):



        self.ConfigInit()
                        
        wx.Frame.__init__(self, parent, id, title, size=mainWindowSize)

        
        
        self.Bind(wx.EVT_CLOSE,self.OnExit)
        
        self.MainPanel=wx.Panel(self)
        self.fbWindowPresent=False
        self.configWindowPresent=False
        self.updateWindowPresent=False
        self.editNIHRWindowPresent=False
        self.editEpisodesWindowPresent=False
        self.aboutWindowPresent=False
        self.reportWindowPresent=False
        self.signifWindowPresent=False
        self.poincareWindowPresent=False
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        vboxLeftLeft = wx.BoxSizer(wx.VERTICAL)
        panel11 = wx.Panel(self.MainPanel, 1, size=(30, 80))
        panel11.SetBackgroundColour(LogoVertColor)
        
        
        vboxLeftLeft.Add(panel11, proportion=1, flag=wx.GROW)
        LogoBitmap=wx.Bitmap('LogoVert.png')
        
        Logo = wx.StaticBitmap(self.MainPanel, bitmap=LogoBitmap )
        vboxLeftLeft.Add(Logo, flag=wx.ALIGN_BOTTOM)
        self.sizer.Add(vboxLeftLeft,flag=wx.EXPAND|wx.ALL, border=0)
        
        
        vboxLeft = wx.BoxSizer(wx.VERTICAL)
        
        # ----------------------------------
        # Begin of sizer for project buttons
        
        sbProjectButtons = wx.StaticBox(self.MainPanel, label="Projects")
        sbProjectButtonsSizer = wx.StaticBoxSizer(sbProjectButtons, wx.VERTICAL)
        
        sbProjectButtonsSizerRow1=wx.BoxSizer(wx.HORIZONTAL)
        
        self.buttonLoadProject = wx.Button(self.MainPanel, -1, label="Load...")
        sbProjectButtonsSizerRow1.Add(self.buttonLoadProject, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnProjectLoad, id=self.buttonLoadProject.GetId())
        self.buttonLoadProject.SetToolTip(wx.ToolTip("Click to load gHRV project"))
        
        sbProjectButtonsSizerRow1.AddStretchSpacer(1)
        
        self.buttonSaveProject = wx.Button(self.MainPanel, -1, label="Save...")
        sbProjectButtonsSizerRow1.Add(self.buttonSaveProject, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnProjectSave, id=self.buttonSaveProject.GetId())
        self.buttonSaveProject.SetToolTip(wx.ToolTip("Click to save gHRV project"))
        self.buttonSaveProject.Disable()
        
        self.buttonClearProject = wx.Button(self.MainPanel, -1, label="Clear")
        sbProjectButtonsSizerRow1.Add(self.buttonClearProject, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnProjectClear, id=self.buttonClearProject.GetId())
        self.buttonClearProject.SetToolTip(wx.ToolTip("Click to clear all data"))
        self.buttonClearProject.Disable()
        
        sbProjectButtonsSizerRow2=wx.BoxSizer(wx.HORIZONTAL)
        
        #sbProjectButtonsSizerRow2.AddStretchSpacer(1)
        
        self.buttonOptionsProject = wx.Button(self.MainPanel, -1, label="Settings")
        sbProjectButtonsSizerRow2.Add(self.buttonOptionsProject, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnProjectOptions, id=self.buttonOptionsProject.GetId())
        self.buttonOptionsProject.SetToolTip(wx.ToolTip("Click to set project options"))
        self.buttonOptionsProject.Disable()
        
        sbProjectButtonsSizer.Add(sbProjectButtonsSizerRow1,flag=wx.EXPAND)
        sbProjectButtonsSizer.Add(sbProjectButtonsSizerRow2,flag=wx.EXPAND)
        
        vboxLeft.Add(sbProjectButtonsSizer, flag=wx.EXPAND | wx.TOP, border=borderVeryBig)
        
        # End of sizer for project buttons
        # --------------------------------
        
        
        # --------------------------------
        # Begin of sizer for beats buttons
        
        sbBeatsButtons = wx.StaticBox(self.MainPanel, label="Heart rate data")
        sbBeatsButtonsSizer = wx.StaticBoxSizer(sbBeatsButtons, wx.VERTICAL)
        
        sbBeatsButtonsSizerRow1=wx.BoxSizer(wx.HORIZONTAL)
        
        self.buttonLoadBeats = wx.Button(self.MainPanel, -1, label="Load...")
        sbBeatsButtonsSizerRow1.Add(self.buttonLoadBeats, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnLoadBeat, id=self.buttonLoadBeats.GetId())
        self.buttonLoadBeats.SetToolTip(wx.ToolTip("Click to load file"))
                
        self.buttonFilterHR = wx.Button(self.MainPanel, -1, label="Filter")
        sbBeatsButtonsSizerRow1.Add(self.buttonFilterHR, flag=wx.ALL, border=borderSmall) 
        self.Bind(wx.EVT_BUTTON, self.OnFilterNIHR, id=self.buttonFilterHR.GetId())
        self.buttonFilterHR.SetToolTip(wx.ToolTip("Automatic removal of outliers"))
        self.buttonFilterHR.Disable()
        
        self.buttonEditHR = wx.Button(self.MainPanel, -1, label="Edit...")
        sbBeatsButtonsSizerRow1.Add(self.buttonEditHR, flag=wx.ALL, border=borderSmall)
        self.MainPanel.Bind(wx.EVT_BUTTON, self.OnNIHREdit, id=self.buttonEditHR.GetId())
        self.buttonEditHR.SetToolTip(wx.ToolTip("Interactive removal of outliers"))
        if platform != 'darwin' and ColoredButtons:
            self.buttonEditHR.SetBackgroundColour(EditBGColor)
        self.buttonEditHR.Disable()
                
        
        sbBeatsButtonsSizer.Add(sbBeatsButtonsSizerRow1, flag=wx.EXPAND)
        
        vboxLeft.Add(sbBeatsButtonsSizer, flag=wx.EXPAND | wx.TOP, border=borderVeryBig)
        
        # End of sizer for beats buttons
        # --------------------------------
          
       
        
        # ---------------------------------
        # Begin of sizer for episodes buttons
        
        sbEpisodesButtons = wx.StaticBox(self.MainPanel, label="Episodes")
        sbEpisodesButtonsSizer = wx.StaticBoxSizer(sbEpisodesButtons, wx.VERTICAL)
        
        sbEpisodesButtonsSizerRow1=wx.BoxSizer(wx.HORIZONTAL)
        
        self.buttonLoadEpisodes = wx.Button(self.MainPanel, -1, label="Load...")
        sbEpisodesButtonsSizerRow1.Add(self.buttonLoadEpisodes, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnLoadEpisodes, id=self.buttonLoadEpisodes.GetId())
        self.buttonLoadEpisodes.SetToolTip(wx.ToolTip("Click to load ascii episodes file"))
        self.buttonLoadEpisodes.Disable()
        
        
        self.buttonClearEpisodes = wx.Button(self.MainPanel, -1, label="Clear")
        sbEpisodesButtonsSizerRow1.Add(self.buttonClearEpisodes, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnEpisodesClear, id=self.buttonClearEpisodes.GetId())
        self.buttonClearEpisodes.SetToolTip(wx.ToolTip("Click to clear episodes information"))
        self.buttonClearEpisodes.Disable()
        
        self.buttonEditEpisodes = wx.Button(self.MainPanel, -1, label="Edit...")
        sbEpisodesButtonsSizerRow1.Add(self.buttonEditEpisodes, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnEpisodesEdit, id=self.buttonEditEpisodes.GetId())
        self.buttonEditEpisodes.SetToolTip(wx.ToolTip("Click to open episodes editor"))
        self.buttonEditEpisodes.Disable()
        if platform != 'darwin' and ColoredButtons:
            self.buttonEditEpisodes.SetBackgroundColour(EpisodesEditionBGColor)
                            
        sbEpisodesButtonsSizer.Add(sbEpisodesButtonsSizerRow1, flag=wx.EXPAND)
        
        vboxLeft.Add(sbEpisodesButtonsSizer,flag=wx.EXPAND | wx.TOP, border=borderVeryBig)
        
        # End of sizer for episodes buttons
        # ---------------------------------
        
        
        
        # --------------------------------  
        # Begin of sizer for tools buttons
        
        sbToolsButtons = wx.StaticBox(self.MainPanel, label="Tools")
        sbToolsButtonsSizer = wx.StaticBoxSizer(sbToolsButtons, wx.VERTICAL)
        
        self.buttonAnalyze = wx.Button(self.MainPanel, -1, label="Interpolate")
        sbToolsButtonsSizer.Add(self.buttonAnalyze, flag=wx.ALL | wx.EXPAND , border=borderSmall)
        self.MainPanel.Bind(wx.EVT_BUTTON, self.OnInterpolateNIHR, id=self.buttonAnalyze.GetId())
        self.buttonAnalyze.SetToolTip(wx.ToolTip("Interpolate heart rate signal"))
        self.buttonAnalyze.Disable()
        
        
        self.buttonTemporal = wx.Button(self.MainPanel, -1, label="Frame-based evolution")
        sbToolsButtonsSizer.Add(self.buttonTemporal, flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnFrameBased, id=self.buttonTemporal.GetId())
        self.buttonTemporal.SetToolTip(wx.ToolTip("Temporal evolution of parameters"))
        if platform != 'darwin' and ColoredButtons:
            self.buttonTemporal.SetBackgroundColour(TemporalBGColor)
        self.buttonTemporal.Disable()
        
        self.buttonReport = wx.Button(self.MainPanel, -1, label="Report")
        sbToolsButtonsSizer.Add(self.buttonReport, flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnReport, id=self.buttonReport.GetId())
        self.buttonReport.SetToolTip(wx.ToolTip("Create report"))
        if platform != 'darwin' and ColoredButtons:
            self.buttonReport.SetBackgroundColour(ReportBGColor)
        self.buttonReport.Disable()

        self.buttonPoincare = wx.Button(self.MainPanel, -1, label="Poincare plot")
        sbToolsButtonsSizer.Add(self.buttonPoincare, flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnPoincare, id=self.buttonPoincare.GetId())
        self.buttonPoincare.SetToolTip(wx.ToolTip("Poincare plot tool"))
        if platform != 'darwin' and ColoredButtons:
            self.buttonPoincare.SetBackgroundColour(PoincareBGColor)
        self.buttonPoincare.Disable()
        
        vboxLeft.Add(sbToolsButtonsSizer,flag=wx.TOP | wx.EXPAND, border=borderVeryBig)
        
        # End of sizer for tools buttons
        # ------------------------------
        
        vboxLeft.AddStretchSpacer(1)
        
        
        # ----------------------------------
        # Begin of sizer for control buttons
        
        sbControlButtons = wx.StaticBox(self.MainPanel, label="gHRV")
        sbControlButtonsSizer = wx.StaticBoxSizer(sbControlButtons, wx.VERTICAL)
        
        sbControlButtonsSizerRow1=wx.BoxSizer(wx.HORIZONTAL)
        
        buttonQuit = wx.Button(self.MainPanel, -1, label="Quit")
        sbControlButtonsSizerRow1.Add(buttonQuit, flag=wx.ALL, border=borderSmall) 
        self.Bind(wx.EVT_BUTTON, self.OnExit, id=buttonQuit.GetId())
        buttonQuit.SetToolTip(wx.ToolTip("Click to quit using gHRV"))
        
        self.buttonAbout = wx.Button(self.MainPanel, -1, label="About")
        sbControlButtonsSizerRow1.Add(self.buttonAbout,flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, id=self.buttonAbout.GetId())
        self.buttonAbout.SetToolTip(wx.ToolTip("Click to see information about gHRV"))
        
        self.buttonConfig = wx.Button(self.MainPanel, -1, label="Config")
        sbControlButtonsSizerRow1.Add(self.buttonConfig, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnConfig, id=self.buttonConfig.GetId())
        self.buttonConfig.SetToolTip(wx.ToolTip("Click to open configuration window"))
        
        sbControlButtonsSizer.Add(sbControlButtonsSizerRow1, flag=wx.EXPAND)
        
        vboxLeft.Add(sbControlButtonsSizer,flag=wx.EXPAND|wx.TOP, border=borderVeryBig)
        
        # End of sizer for control buttons
        # --------------------------------
        
        self.sizer.Add(vboxLeft,flag=wx.ALL|wx.EXPAND, border=borderBig)

        
        
        # ------------------
        # Begin of plot area
        
        if ColoredBGPlots:
            self.fig = matplotlib.figure.Figure((4,5),facecolor=HRBGColor)
        else:
            self.fig = matplotlib.figure.Figure((4,5))
        #self.fig.set_figwidth(5)
        #self.fig.set_figheight(5)
        self.canvas = FigureCanvas(self.MainPanel, -1, self.fig)
        #self.axes = self.fig.add_axes([0,0,1,1])
        #self.axes.imshow(self.data, interpolation="quadric")  
        
        
        self.sizer.Add(self.canvas,1, wx.ALL | wx.GROW, border=borderSmall)
        
        # End of plot area
        # ----------------
        
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText(self.sbDefaultText)
        
        
        self.SetMinSize(mainWindowMinSize)
        self.SetTitle('gHRV')
        self.Centre()
        self.MainPanel.SetSizer(self.sizer)
        self.MainPanel.Layout()

        
        
        if DebugMode:
            dm.LoadFileAscii("./beats.txt", self.settings)
            
            dm.FilterNIHR()

            dm.LoadEpisodesAscii("./beats_ep.txt")
            EpisodesTags=dm.GetEpisodesTags()
            for Tag in EpisodesTags:
                dm.AssignEpisodeColor(Tag)
            self.RefreshMainWindow()
            # PoincarePlotWindow(self,-1,'Poincaré plot',dm)
            # self.poincareWindowPresent=True
            # self.RefreshMainWindowButtons()

            # if dm.HasFrameBasedParams()==False:
            #     dm.CalculateFrameBasedParams(showProgress=True)
            # self.fbWindow = FrameBasedEvolutionWindow(self,-1,"Temporal evolution of parameters",dm)
            # self.fbWindowPresent=True
            # self.RefreshMainWindowButtons()
            # EditEpisodesWindow(self,-1,'Episodes Edition',dm)
            # self.editEpisodesWindowPresent=True
            import tempfile
            reportName="report.html"
            reportDir=tempfile.mkdtemp(prefix="gHRV_Report_")
            dm.CreateReport(reportDir,reportName,'report_files')
            ReportWindow(self,-1,'Report: '+dm.GetName(),reportDir+os.sep+reportName, dm)
            self.reportWindowPresent=True
            self.RefreshMainWindowButtons()

            
        
        self.canvas.SetFocus()

        self.CheckVersion()

    
   
    def ConfigInit(self):
        """If config dir and file does not exist, it is created
        If config file exists, it is loaded"""
        
        from ConfigParser import SafeConfigParser

        # print "Intializing configuration"
        
        if not os.path.exists(self.configDir):
            # print "Directory does not exists ... creating"
            os.makedirs(self.configDir)
            
        if os.path.exists(self.configFile):
            self.ConfigLoad()
        else:
            self.settings=factorySettings
            self.ConfigSave()


    def ConfigLoad(self):
        """ Loads configuration file"""
        
        from ConfigParser import SafeConfigParser
        self.settings={}

        options=SafeConfigParser()
        options.read(self.configFile)
        for section in options.sections():
            for param,value in options.items(section):
                self.settings[param]=value

        #print self.settings
        
    def ConfigSave(self):
        """ Saves configuration file"""
        
        from ConfigParser import SafeConfigParser
        options = SafeConfigParser()
        
        options.add_section('ghrv')
        
        for param in self.settings.keys():
            options.set('ghrv',param,self.settings[param])
        
        tempF = open(self.configFile,'w')
        options.write(tempF)
        tempF.close()
        
        if platform=="win32":
            import win32api,win32con
            win32api.SetFileAttributes(self.configDir,win32con.FILE_ATTRIBUTE_HIDDEN)

        #print self.settings

    def CheckVersion(self):
        from ConfigParser import SafeConfigParser
        from sys import argv
        import urllib2

        if "lastcheckedversion" not in self.settings.keys(): # First run of the program
            self.settings["lastcheckedversion"]=Version
            self.ConfigSave()

        if Version > self.settings["lastcheckedversion"]: # gHRV was just updated
            self.settings["lastcheckedversion"]=Version
            self.ConfigSave()
        
        remoteVersion = ""
        remoteVersionFile = ""
        string =""
        platformString=""

        if argv[0].endswith("gHRV.py"):
            string = string + "Running gHRV from source. Version: " + Version + "\n"
            platformString = "src"
            remoteVersionFile = "https://raw.github.com/milegroup/ghrv/master/ProgramVersions/src.txt"

        if platform=="linux2" and argv[0]=="/usr/share/ghrv/gHRV.pyc":
            string = string + "Running gHRV deb package. Version: " + Version + "\n"
            platformString = "deb"
            remoteVersionFile = "https://raw.github.com/milegroup/ghrv/master/ProgramVersions/deb.txt"

        if platform=="darwin" and "gHRV.app" in argv[0]:
            string = string +  "Running gHRV mac package. Version: " + Version + "\n"
            platformString = "mac"
            remoteVersionFile = "https://raw.github.com/milegroup/ghrv/master/ProgramVersions/mac.txt"

        if platform=="win32" and "gHRV.exe" in argv[0]:
            string = string + "Running gHRV win package. Version: " + Version + "\n"
            platformString = "win"
            remoteVersionFile = "https://raw.github.com/milegroup/ghrv/master/ProgramVersions/win.txt"

        try:
            remoteFile = urllib2.urlopen(remoteVersionFile)
            remoteVersion=remoteFile.readline().strip()
            remoteFile.close()
            string = string + "Version avalaible in gHRV web page: " + remoteVersion + "\n"
        except urllib2.URLError:
            string = string + "I couldn't check for updates\n"

        string = string + "Last checked version "+self.settings["lastcheckedversion"]+"\n"

        if remoteVersion:
            if remoteVersion > self.settings["lastcheckedversion"]:                
                string = string + "Now I ask if the user wants to update!!!\n"
                self.UpdateWindowOpen(remoteVersion,platformString)
    
        if argv[0]=="gHRV.py":
            print string

        if ReportVersion:
            dial = wx.MessageDialog(self, caption="Version info", message=string, style=wx.OK)
            result = dial.ShowModal()
            dial.Destroy()

    def UpdateWindowOpen(self,remoteVersion,platformString):
        self.updateWindowPresent=True
        self.RefreshMainWindowButtons()
        #print 'Before configuration: ',self.settings
        UpdateSoftwareWindow(self,-1,remoteVersion,platformString)

    def UpdateWindowClose(self):
        self.updateWindowPresent=False
        self.RefreshMainWindowButtons()
        #print 'After configuration: ',self.settings

        self.canvas.SetFocus()
        
        
    def DisableAllButtons(self):
        self.buttonLoadProject.Disable()
        self.buttonSaveProject.Disable()
        self.buttonClearProject.Disable()
        self.buttonOptionsProject.Disable()
        self.buttonLoadBeats.Disable()
        self.buttonFilterHR.Disable()
        self.buttonEditHR.Disable()
        self.buttonAnalyze.Disable()
        self.buttonLoadEpisodes.Disable()
        self.buttonEditEpisodes.Disable()
        self.buttonClearEpisodes.Disable()
        self.buttonTemporal.Disable()
        self.buttonPoincare.Disable()
        self.buttonConfig.Disable()
        self.buttonAbout.Disable()
        self.buttonReport.Disable()

    def RefreshMainWindowButtons(self):
        """Redraws main window buttons"""
        
        self.DisableAllButtons() # by default all disabled
        
        if self.configWindowPresent or self.updateWindowPresent or self.aboutWindowPresent or self.editNIHRWindowPresent or self.editEpisodesWindowPresent or self.reportWindowPresent or self.signifWindowPresent or self.poincareWindowPresent:
            return
        
        self.buttonAbout.Enable()
        self.buttonConfig.Enable()
        
        
        if dm.HasHR():
            self.buttonSaveProject.Enable()
            if not self.fbWindowPresent:
                self.buttonClearProject.Enable()
                self.buttonOptionsProject.Enable()
            self.buttonEditEpisodes.Enable()
            self.buttonPoincare.Enable()
            if not self.reportWindowPresent:
                self.buttonReport.Enable()
        else:
            self.buttonLoadBeats.Enable()
            self.buttonLoadProject.Enable()

            
        if dm.HasHR() and not dm.HasEpisodes():
            self.buttonLoadEpisodes.Enable()
            
        if dm.HasHR() and dm.HasEpisodes():
            self.buttonClearEpisodes.Enable()
    
            
        if dm.HasHR() and not dm.HasInterpolatedHR():
            self.buttonEditHR.Enable()
            self.buttonFilterHR.Enable()
            self.buttonAnalyze.Enable()
       
            
        if dm.HasInterpolatedHR() and not self.fbWindowPresent:
            self.buttonTemporal.Enable()


            
    def RefreshMainWindow(self):
        """Redraws main window"""
        
        self.RefreshMainWindowButtons()
        self.RefreshMainWindowPlot()
        self.canvas.SetFocus()
    
    def RefreshMainWindowPlot(self):
        """Redraws the plot of the main window"""
        
        self.fig.clear()
        dm.CreatePlotHREmbedded(self.fig)
        self.canvas.draw()
        self.canvas.SetFocus()
        
    
    def WarningWindow(self,messageStr,captionStr="WARNING"):
        """Generic warning window"""
        dial = wx.MessageDialog(self, caption=captionStr, message=messageStr, style=wx.OK | wx.ICON_WARNING)
        result = dial.ShowModal()
        dial.Destroy()
        self.canvas.SetFocus()
       

    def OnLoadBeat(self, event):
        filetypes = "Supported files (*.txt;*.hrm;*sdf;*.hea)|*.txt;*.TXT;*.hrm;*.HRM;*.sdf;*.SDF;*.hea;*.HEA|TXT ascii files (*.txt)|*.txt;*.TXT|Polar files (*.hrm)|*.hrm;*.HRM|Suunto files (*.sdf)|*.sdf;*.SDF|WFDB header files (*.hea)|*.hea;*.HEA|All files (*.*)|*.*"
        fileName=""
        dial = wx.FileDialog(self, message="Load file", wildcard=filetypes, style=wx.FD_OPEN)
        result = dial.ShowModal()
        if result == wx.ID_OK:
            fileName=dial.GetPath()
            # ext=fileName[-3:].lower()  
            ext = os.path.splitext(fileName)[1][1:].strip()          
            dial.Destroy()
            if ext=="txt":
                try:
                    dm.LoadFileAscii(str(unicode(fileName)),self.settings)
                except UnicodeEncodeError:
                    Utils.ErrorWindow(messageStr="Ilegal characters in filename: "+fileName,
                                     captionStr="Error loading ascii file")
                except:
                    Utils.ErrorWindow(messageStr=fileName+" does not seem to be a valid ascii file",
                                     captionStr="Error loading ascii file")
                else:
                    self.RefreshMainWindow()
            elif ext=="hrm":
                try:
                    dm.LoadFilePolar(str(unicode(fileName)),self.settings)
                except UnicodeEncodeError:
                    Utils.ErrorWindow(messageStr="Ilegal characters in filename: "+fileName,
                                     captionStr="Error loading polar file")
                except:
                    Utils.ErrorWindow(messageStr=fileName+" does not seem to be a valid polar file",
                                     captionStr="Error loading polar file")
                else:
                    self.RefreshMainWindow()
            elif ext=="sdf":
                try:
                    dm.LoadFileSuunto(str(unicode(fileName)),self.settings)
                    
                except UnicodeEncodeError:
                    Utils.ErrorWindow(messageStr="Ilegal characters in filename: "+fileName,
                                     captionStr="Error loading suunto file")
                except:
                    Utils.ErrorWindow(messageStr=fileName+" does not seem to be a valid suunto file",
                                     captionStr="Error loading suunto file")
                else:
                    self.RefreshMainWindow()
            elif ext=="hea":
                # dial = wx.MessageDialog(self, "Not yet implemented", "Soon...", wx.OK)
                # result = dial.ShowModal()
                # dial.Destroy()
                try: 
                    dm.LoadBeatWFDB(str(unicode(fileName)),self.settings)
                except UnicodeEncodeError:
                    Utils.ErrorWindow(messageStr="Ilegal characters in filename:\n"+fileName,
                                     captionStr="Error loading WFDB file")
                except:
                    Utils.ErrorWindow(messageStr="Problem loading WFDB file:\n"+fileName,
                                     captionStr="Error loading WFDB file")
                else:
                    self.RefreshMainWindow()
            else:
                try:
                    dm.LoadFileAscii(str(unicode(fileName)),self.settings)
                except UnicodeEncodeError:
                    Utils.ErrorWindow(messageStr="Ilegal characters in filename: "+fileName,
                                     captionStr="Error loading ascii file")
                except:
                    Utils.ErrorWindow(messageStr=fileName+" does not seem to be a valid ascii file",
                                     captionStr="Error loading ascii file")
                else:
                    self.RefreshMainWindow() 
        self.canvas.SetFocus()
        
        
        
    def OnLoadEpisodes(self,event):
        fileName=""
        filetypes = "TXT episodes files (*.txt)|*.txt|" "All files (*.*)|*.*"
        dial = wx.FileDialog(self, message="Load episodes file", wildcard=filetypes, style=wx.FD_OPEN)
        result = dial.ShowModal()
        if result == wx.ID_OK:
            fileName=dial.GetPath()
            dial.Destroy()
            try:
                dm.LoadEpisodesAscii(str(unicode(fileName)))
            except UnicodeEncodeError:
                    Utils.ErrorWindow(messageStr="Ilegal characters in filename: "+fileName,
                                     captionStr="Error loading episodes file")
            except:
                Utils.ErrorWindow(messageStr=fileName+" does not seem to be a valid episodes file",captionStr="Error loading episodes file")
            else:
                EpisodesTags=dm.GetEpisodesTags()
                for Tag in EpisodesTags:
                    dm.AssignEpisodeColor(Tag)
                self.RefreshMainWindow()
                if self.fbWindowPresent:
                    self.fbWindow.Refresh()
                EpInit = dm.GetEpisodes()[1]
                EpDur = dm.GetEpisodes()[2]
                EpFin = [float(EpInit[x])+float(EpDur[x]) for x in range(len(EpInit))]
                EpFinMax = max(EpFin)
                if EpFinMax > dm.GetHRDataPlot()[0][-1]:
                    self.WarningWindow(messageStr="WARNING: one or more episodes are outside of time axis",captionStr="Episodes warning")

        self.canvas.SetFocus()
        
    def OnProjectLoad(self,event):
        filetypes = "gHRV project files (*.ghrv)|*.ghrv|" "All files (*.*)|*.*"
        fileName=""
        dial = wx.FileDialog(self, message="Load ghrv project", wildcard=filetypes, style=wx.FD_OPEN)
        result = dial.ShowModal()
        if result == wx.ID_OK:
            fileName=dial.GetPath()
            dial.Destroy()
                            
            try:
                dm.LoadProject(str(unicode(fileName)))
            except UnicodeEncodeError:
                    Utils.ErrorWindow(messageStr="Ilegal characters in filename: "+fileName,
                                     captionStr="Error loading project file")
            except:
                Utils.ErrorWindow(messageStr=fileName+" does not seem to be a valid project file",captionStr="Error loading project file")
            else:
                self.RefreshMainWindow()                
            
        
    def OnProjectSave(self,event):
        fileName=""
        dial = wx.FileDialog(self, message="Save project as...", defaultFile=dm.GetName()+".ghrv", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dial.ShowModal()
        if result == wx.ID_OK:
            fileName=dial.GetPath()
            try:
                dm.SaveProject(str(unicode(fileName)))
            except UnicodeEncodeError:
                    Utils.ErrorWindow(messageStr="Ilegal characters in filename: "+fileName,
                                     captionStr="Error saving project file")
            except:
                Utils.ErrorWindow(messageStr="Error saving project to file: "+fileName,captionStr="Error saving project file")
        dial.Destroy()
                   
    def OnProjectClear(self,event):
        dial = wx.MessageDialog(self, "Deletting data\nAre you sure?", "Confirm clear", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        result = dial.ShowModal()
        dial.Destroy()
        if result == wx.ID_YES:
            dm.ClearAll()
            self.RefreshMainWindowButtons()
            self.fig.clear()
            self.canvas.draw()
    
    def OnEpisodesEdit(self,event):
        EditEpisodesWindow(self,-1,'Episodes Edition',dm)
        self.editEpisodesWindowPresent=True
        self.RefreshMainWindowButtons()
    
    def OnEpisodesEditEnded(self):
        self.editEpisodesWindowPresent=False
        self.RefreshMainWindow()
        if self.fbWindowPresent:
            self.fbWindow.Refresh()

    def OnPoincare(self,event):
        PoincarePlotWindow(self,-1,'Poincare plot',dm)
        self.poincareWindowPresent=True
        self.RefreshMainWindowButtons()

    def OnPoincareEnded(self):
        self.poincareWindowPresent=False
        self.RefreshMainWindowButtons()

    def OnEpisodesClear(self,event):
        dm.ClearEpisodes()
        dm.ClearColors()
        self.RefreshMainWindow()
        if self.fbWindowPresent:
            self.fbWindow.Refresh()
                    
    def OnFilterNIHR(self,event):
        dm.FilterNIHR()
        self.RefreshMainWindow()
        
    def OnNIHREdit(self,event):
        EditNIHRWindow(self,-1,'Non interpolated HR Edition',dm)
        self.editNIHRWindowPresent=True
        self.RefreshMainWindowButtons()
        
    def OnNIHREditEnded(self):
        self.editNIHRWindowPresent=False
        self.RefreshMainWindow()
        
    
    def OnInterpolateNIHR(self,event):
        dm.InterpolateNIHR()
        self.RefreshMainWindow()
        

    def OnReport(self,event):
        import tempfile
        reportName="report.html"
        reportDir=tempfile.mkdtemp(prefix="gHRV_Report_")
        dm.CreateReport(reportDir,reportName,'report_files')
        ReportWindow(self,-1,'Report: '+dm.GetName(),reportDir+os.sep+reportName, dm)
        self.reportWindowPresent=True
        self.RefreshMainWindowButtons()

        
    def OnReportEnded(self):
        self.reportWindowPresent=False
        self.RefreshMainWindow()
        self.canvas.SetFocus()
        
        
    def OnFrameBased(self,event):
        if dm.HasFrameBasedParams()==False:
            try:
                dm.CalculateFrameBasedParams(showProgress=True)
            except Utils.FewFramesException as e:
                Utils.ErrorWindow(messageStr="Too few data for analysis: "+str(max(0,e.NumOfFrames))+" frames\nMinimum number of frames is "+str(minNumFrames),
                                     captionStr="Error calculating frame-based parameters")
        if dm.HasFrameBasedParams():
            self.fbWindow = FrameBasedEvolutionWindow(self,-1,"Temporal evolution of parameters",dm)
            self.fbWindowPresent=True
            self.RefreshMainWindowButtons()
        
    def OnFrameBasedEnded(self):
        self.fbWindowPresent=False
        self.RefreshMainWindowButtons()
        self.canvas.SetFocus()
        
    
    
    def OnExit(self, event):
        dial = wx.MessageDialog(self, "Quitting gHRV\nAre you sure?", "Confirm exit", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        result = dial.ShowModal()
        dial.Destroy()
        if result == wx.ID_YES:
            self.Destroy()

    def Abort(self):
        self.Destroy()
        
    def OnAbout(self, event):
        self.aboutWindowPresent=True
        self.RefreshMainWindowButtons()
        AboutDlg(self,-1)
        
        
    def OnAboutEnded(self):
        self.aboutWindowPresent=False
        self.RefreshMainWindowButtons()
        self.canvas.SetFocus()
       
        
    def OnConfig(self,event):
        self.configWindowPresent=True
        self.RefreshMainWindowButtons()
        #print 'Before configuration: ',self.settings
        ConfigurationWindow(self,-1,self.settings,conftype="general")
    
    def OnConfigEnded(self):
        self.ConfigSave()     
        self.configWindowPresent=False
        self.RefreshMainWindowButtons()
        #print 'After configuration: ',self.settings
        self.canvas.SetFocus()
        
    def OnProjectOptions(self,event):
        self.projectSettings=dm.GetSettings()
        self.oldProjectSettings=dict(self.projectSettings)
        ConfigurationWindow(self,-1,self.projectSettings,conftype="project",settings2=self.settings)
        self.configWindowPresent=True
        self.RefreshMainWindowButtons()
        
    def OnProjectOptionsEnded(self):
        self.configWindowPresent=False
        self.RefreshMainWindowButtons()
                
        nothingChanges = True
        for k in self.projectSettings.keys():
            if self.projectSettings[k] != self.oldProjectSettings[k]:
                nothingChanges = False
        
        if nothingChanges:
            return # No changes in options
        
        onlyNameChanges = True
        for k in self.projectSettings.keys():
            if k != 'name':
                if self.projectSettings[k] != self.oldProjectSettings[k]:
                    onlyNameChanges = False
        
        dial = wx.MessageDialog(self, "Applying new settings to project\nThis may change some results\nAre you sure?", "Confirm applying", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        result = dial.ShowModal()
        dial.Destroy()
        if result == wx.ID_NO:
            return
        
        dm.SetSettings(self.projectSettings)
        
        if dm.HasInterpolatedHR():
            if not onlyNameChanges:
                dm.ClearHR()
                dm.InterpolateNIHR()
        
        self.RefreshMainWindowPlot()
            
        if dm.HasFrameBasedParams():
            if not onlyNameChanges:
                dm.ClearFrameBasedParams()
                dm.CalculateFrameBasedParams(showProgress=True)
            if self.fbWindowPresent:
                self.fbWindow.Refresh()
    
class ConfigurationWindow(wx.Frame):
    
    def __init__(self, parent, id, settings, conftype, settings2=None):
        # conftype: project or general
        # settings2 used for main settings when conftype="project"
        self.conftype = conftype
        if platform != 'darwin':
            if conftype=="general":
                wx.Frame.__init__(self, parent, wx.ID_ANY, size=confWindowSize)
            else:
                wx.Frame.__init__(self, parent, wx.ID_ANY, size=confWindowProjectSize)
        else:
            if conftype=="general":
                wx.Frame.__init__(self, parent, wx.ID_ANY, size=confWindowSizeMac)
            else:
                wx.Frame.__init__(self, parent, wx.ID_ANY, size=confWindowProjectSizeMac)
        
        self.WindowParent=parent
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        panel=wx.Panel(self)
        
        self.settings = settings
        self.conftype=conftype
        
        if self.conftype=='general':
            self.SetTitle("gHRV Configuration Window")
        else:
            self.SetTitle(dm.GetName()+" options")
            self.settings2 = settings2
            
        #print(str(self.settings))

        sizer=wx.BoxSizer(wx.VERTICAL)
        
        if self.conftype=="project":
            sbName = wx.StaticBox(panel, label="Project name")
            sbNameSizer = wx.StaticBoxSizer(sbName, wx.VERTICAL)
            self.ProjName=wx.TextCtrl(panel,-1)
            self.ProjName.SetValue(self.settings['name'])
            self.ProjName.Bind(wx.EVT_TEXT,self.OnChange)
            if platform != 'darwin':   
                self.ProjName.SetWindowStyleFlag(wx.TE_RIGHT)
            sbNameSizer.Add(self.ProjName,flag=wx.ALL|wx.EXPAND,border=borderSmall)
            sizer.Add(sbNameSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        
# ----------------- Beginning of sizer for interpolation frequency

        sbInterpol = wx.StaticBox(panel, label="Interpolation")

        sbInterpolSizer = wx.StaticBoxSizer(sbInterpol, wx.HORIZONTAL)
        
        sbInterpolSizer.AddStretchSpacer(1)
        sbInterpolSizer.Add(wx.StaticText(panel, label="Interpolation frequency"),
                            flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
             
        self.InterpolFreq = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.InterpolFreq.SetValue(self.settings['interpfreq'])
        if platform != 'darwin':   
            self.InterpolFreq.SetWindowStyleFlag(wx.TE_RIGHT)
        self.InterpolFreq.SetToolTip(wx.ToolTip("Frequency in Hz."))
        self.InterpolFreq.Bind(wx.EVT_TEXT,self.OnChange)
        
        sbInterpolSizer.Add(self.InterpolFreq, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sizer.Add(sbInterpolSizer, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=borderBig)

# ----------------- End of sizer for for interpolation frequency


# ----------------- Beginning of sizer for windows parameters
        sbWindow = wx.StaticBox(panel,label="Window parameters")
        
        sbWindowSizer=wx.StaticBoxSizer(sbWindow,wx.HORIZONTAL)
        
        
        sbWindowSizer.Add(wx.StaticText(panel, label="Window size"),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        
        self.WindowSize = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.WindowSize.SetValue(self.settings['windowsize'])
        if platform != 'darwin': 
            self.WindowSize.SetWindowStyleFlag(wx.TE_RIGHT)
        self.WindowSize.SetToolTip(wx.ToolTip("Length in seconds"))
        self.WindowSize.Bind(wx.EVT_TEXT,self.OnChange)
        sbWindowSizer.Add(self.WindowSize, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sbWindowSizer.AddStretchSpacer(1)
        
        sbWindowSizer.Add(wx.StaticText(panel, label="Window shift"),
                          flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        self.WindowShift = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.WindowShift.SetValue(self.settings['windowshift'])
        if platform != 'darwin': 
            self.WindowShift.SetWindowStyleFlag(wx.TE_RIGHT)
        self.WindowShift.SetToolTip(wx.ToolTip("Shift in seconds"))
        self.WindowShift.Bind(wx.EVT_TEXT,self.OnChange)
        sbWindowSizer.Add(self.WindowShift, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sizer.Add(sbWindowSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=borderBig)
# ----------------- End of sizer for windows parameters

# ----------------- Beginning of sizer for bands limits
        sbBandsLimits = wx.StaticBox(panel,label="Frequency bands limits")
        sbBandsLimitsSizer=wx.StaticBoxSizer(sbBandsLimits,wx.VERTICAL)
        
        sbBandsLimitsSizer1=wx.GridBagSizer(hgap=5,vgap=5)
        
        sbBandsLimitsSizer1.Add(wx.StaticText(panel, label="ULF min"), pos=(0,0),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.ULFMin = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.ULFMin.SetValue(self.settings['ulfmin'])
        if platform != 'darwin': 
            self.ULFMin.SetWindowStyleFlag(wx.TE_RIGHT)
        self.ULFMin.SetToolTip(wx.ToolTip("ULF band lower limit in Hz."))
        self.ULFMin.Bind(wx.EVT_TEXT,self.OnChange)
        sbBandsLimitsSizer1.Add(self.ULFMin, pos=(0,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sbBandsLimitsSizer1.Add(wx.StaticText(panel, label="ULF max"), pos=(0,3),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.ULFMax = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.ULFMax.SetValue(self.settings['ulfmax'])
        if platform != 'darwin': 
            self.ULFMax.SetWindowStyleFlag(wx.TE_RIGHT)
        self.ULFMax.SetToolTip(wx.ToolTip("ULF band lower limit in Hz."))
        self.ULFMax.Bind(wx.EVT_TEXT,self.OnChange)
        sbBandsLimitsSizer1.Add(self.ULFMax, pos=(0,4), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sbBandsLimitsSizer1.Add(wx.StaticText(panel, label="VLF min"), pos=(1,0),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.VLFMin = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.VLFMin.SetValue(self.settings['vlfmin'])
        if platform != 'darwin': 
            self.VLFMin.SetWindowStyleFlag(wx.TE_RIGHT)
        self.VLFMin.SetToolTip(wx.ToolTip("VLF band lower limit in Hz."))
        self.VLFMin.Bind(wx.EVT_TEXT,self.OnChange)
        sbBandsLimitsSizer1.Add(self.VLFMin, pos=(1,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sbBandsLimitsSizer1.Add(wx.StaticText(panel, label="VLF max"), pos=(1,3),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.VLFMax = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.VLFMax.SetValue(self.settings['vlfmax'])
        if platform != 'darwin': 
            self.VLFMax.SetWindowStyleFlag(wx.TE_RIGHT)
        self.VLFMax.SetToolTip(wx.ToolTip("VLF band lower limit in Hz."))
        self.VLFMax.Bind(wx.EVT_TEXT,self.OnChange)
        sbBandsLimitsSizer1.Add(self.VLFMax, pos=(1,4), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sbBandsLimitsSizer1.Add(wx.StaticText(panel, label="LF min"), pos=(2,0),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.LFMin = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.LFMin.SetValue(self.settings['lfmin'])
        if platform != 'darwin': 
            self.LFMin.SetWindowStyleFlag(wx.TE_RIGHT)
        self.LFMin.SetToolTip(wx.ToolTip("LF band lower limit in Hz."))
        self.LFMin.Bind(wx.EVT_TEXT,self.OnChange)
        sbBandsLimitsSizer1.Add(self.LFMin, pos=(2,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sbBandsLimitsSizer1.Add(wx.StaticText(panel, label="LF max"), pos=(2,3),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.LFMax = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.LFMax.SetValue(self.settings['lfmax'])
        if platform != 'darwin': 
            self.LFMax.SetWindowStyleFlag(wx.TE_RIGHT)
        self.LFMax.SetToolTip(wx.ToolTip("LF band lower limit in Hz."))
        self.LFMax.Bind(wx.EVT_TEXT,self.OnChange)
        sbBandsLimitsSizer1.Add(self.LFMax, pos=(2,4), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sbBandsLimitsSizer1.Add(wx.StaticText(panel, label="HF min"), pos=(3,0),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.HFMin = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.HFMin.SetValue(self.settings['hfmin'])
        if platform != 'darwin': 
            self.HFMin.SetWindowStyleFlag(wx.TE_RIGHT)
        self.HFMin.SetToolTip(wx.ToolTip("HF band lower limit in Hz."))
        self.HFMin.Bind(wx.EVT_TEXT,self.OnChange)
        sbBandsLimitsSizer1.Add(self.HFMin, pos=(3,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sbBandsLimitsSizer1.Add(wx.StaticText(panel, label="HF max"), pos=(3,3),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.HFMax = wx.TextCtrl(panel,-1,size=textCtrlSize)
        self.HFMax.SetValue(self.settings['hfmax'])
        if platform != 'darwin': 
            self.HFMax.SetWindowStyleFlag(wx.TE_RIGHT)
        self.HFMax.SetToolTip(wx.ToolTip("HF band lower limit in Hz."))
        self.HFMax.Bind(wx.EVT_TEXT,self.OnChange)
        sbBandsLimitsSizer1.Add(self.HFMax, pos=(3,4), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        
        sbBandsLimitsSizer1.Add(wx.StaticText(panel, label=""), pos=(0,2),
                          flag=wx.LEFT|wx.EXPAND, border=borderVeryBig)
        
        sbBandsLimitsSizer1.AddGrowableCol(2,proportion=1)
        
        sbBandsLimitsSizer.Add(sbBandsLimitsSizer1, flag=wx.ALL|wx.EXPAND, border=borderSmall)
                
        sizer.Add(sbBandsLimitsSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=borderBig)

# ----------------- End of sizer for bands limits

        sizer.AddStretchSpacer(1)

# ----------------- Beginning of sizer for buttons


        sbButtonsSizer=wx.BoxSizer(wx.HORIZONTAL)
        
        
        buttonLeft = wx.Button(panel, -1)
        if self.conftype=="general":
            buttonLeft.SetLabel("Reset")
            buttonLeft.SetToolTip(wx.ToolTip("Click to revert to factory settings"))
        else:
            buttonLeft.SetLabel("Default")
            buttonLeft.SetToolTip(wx.ToolTip("Click apply default settings to the project"))
        sbButtonsSizer.Add(buttonLeft, flag=wx.ALL|wx.ALIGN_LEFT, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnButtonLeft, id=buttonLeft.GetId())
        
        
        sbButtonsSizer.AddStretchSpacer(1)
        
        buttonCancel = wx.Button(panel, -1, label="Cancel")
        sbButtonsSizer.Add(buttonCancel, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=buttonCancel.GetId())
        buttonCancel.SetToolTip(wx.ToolTip("Click to cancel"))
        

        self.buttonRight = wx.Button(panel, -1)
        if self.conftype=="general":
            self.buttonRight.SetLabel("Set as default")
            self.buttonRight.SetToolTip(wx.ToolTip("Click to set this values as default"))
        else:
            self.buttonRight.SetLabel("Apply")
            self.buttonRight.SetToolTip(wx.ToolTip("Click apply these settings to the project"))
        
        sbButtonsSizer.Add(self.buttonRight, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnButtonRight, id=self.buttonRight.GetId())
        self.buttonRight.Disable()
        

        sizer.Add(sbButtonsSizer,flag=wx.ALL|wx.EXPAND, border=borderSmall)
        
# ----------------- End of sizer for buttons
        
        
        panel.SetSizer(sizer)
        
        if self.conftype=="general":
            self.SetMinSize(confWindowMinSize)
        else:
            self.SetMinSize(confWindowProjectMinSize)
        #self.MakeModal(True)
        self.Show()
        self.Center()
        
    def OnChange(self,event):
        self.buttonRight.Enable()

    def OnButtonRight(self,event):
        error = False
        messageError=""
        tmpSettings={}
        tmpSettings['interpfreq'] = str(self.InterpolFreq.GetValue())
        tmpSettings['windowsize'] = str(self.WindowSize.GetValue())
        tmpSettings['windowshift'] = str(self.WindowShift.GetValue())
        tmpSettings['ulfmin'] = str(self.ULFMin.GetValue())
        tmpSettings['ulfmax'] = str(self.ULFMax.GetValue())
        tmpSettings['vlfmin'] = str(self.VLFMin.GetValue())
        tmpSettings['vlfmax'] = str(self.VLFMax.GetValue())
        tmpSettings['lfmin'] = str(self.LFMin.GetValue())
        tmpSettings['lfmax'] = str(self.LFMax.GetValue())
        tmpSettings['hfmin'] = str(self.HFMin.GetValue())
        tmpSettings['hfmax'] = str(self.HFMax.GetValue())
            
        try:
            for k in tmpSettings.keys():
                x=float(tmpSettings[k])
        except:
            messageError="One or more of the parameters are not valid numbers"
            error=True
        
        if not error:
            for k in tmpSettings.keys():
                if float(tmpSettings[k])<0:
                    messageError="Parameters must be positive numbers"
                    error = True
                       
        if not error:
            p = ['ulfmin','ulfmax','vlfmin','vlfmax','lfmin','lfmax','hfmin','hfmax']
            for k in p:
                if float(tmpSettings[k])>float(tmpSettings['interpfreq']):
                    messageError="Frequency limits must be lower than interpolation frequency"
                    error = True
                    
        if not error:
            p = [['ulfmin','ulfmax'],['vlfmin','vlfmax'],['lfmin','lfmax'],['hfmin','hfmax']]
            for k in p:
                if float(tmpSettings[k[0]])>float(tmpSettings[k[1]]):
                    messageError="In some band limits are inverted"
                    error = True
                    
        if not error and self.conftype=="project":
            try:
                tmp = str(unicode(str(self.ProjName.GetValue())))
            except:
                error = True
                messageError="Illegal characters in project name"

        if not error and dm.HasFrameBasedParams():
            numframes = dm.GetNumFrames(float(tmpSettings['interpfreq']),float(tmpSettings['windowsize']),float(tmpSettings['windowshift']))
            if (numframes < minNumFrames):
                messageError="Too few data for analysis: "+str(max(0,numframes))+" frames\nMinimum number of frames is "+str(minNumFrames)
                error = True
        
        if error:
            self.WindowParent.ErrorWindow(messageStr=messageError)
            self.Raise()
        else:
            for k in tmpSettings.keys():
                self.settings[k] = str(float(tmpSettings[k]))
            if self.conftype=="project":
                self.settings['name']=str(self.ProjName.GetValue())
            self.Close()

    def OnButtonLeft(self,event):
        """Reset for general, default for project"""
        if self.conftype=="general":
            self.InterpolFreq.SetValue(factorySettings['interpfreq'])
            self.WindowSize.SetValue(factorySettings['windowsize'])
            self.WindowShift.SetValue(factorySettings['windowshift'])
            self.ULFMin.SetValue(factorySettings['ulfmin'])
            self.ULFMax.SetValue(factorySettings['ulfmax'])
            self.VLFMin.SetValue(factorySettings['vlfmin'])
            self.VLFMax.SetValue(factorySettings['vlfmax'])
            self.LFMin.SetValue(factorySettings['lfmin'])
            self.LFMax.SetValue(factorySettings['lfmax'])
            self.HFMin.SetValue(factorySettings['hfmin'])
            self.HFMax.SetValue(factorySettings['hfmax'])
        else:
            self.InterpolFreq.SetValue(self.settings2['interpfreq'])
            self.WindowSize.SetValue(self.settings2['windowsize'])
            self.WindowShift.SetValue(self.settings2['windowshift'])
            self.ULFMin.SetValue(self.settings2['ulfmin'])
            self.ULFMax.SetValue(self.settings2['ulfmax'])
            self.VLFMin.SetValue(self.settings2['vlfmin'])
            self.VLFMax.SetValue(self.settings2['vlfmax'])
            self.LFMin.SetValue(self.settings2['lfmin'])
            self.LFMax.SetValue(self.settings2['lfmax'])
            self.HFMin.SetValue(self.settings2['hfmin'])
            self.HFMax.SetValue(self.settings2['hfmax'])
        
        
    def OnEnd(self,event):
        if self.conftype == 'general':
            self.WindowParent.OnConfigEnded()
        else:
            self.WindowParent.OnProjectOptionsEnded()
        #self.MakeModal(False)
        self.Destroy()

class UpdateSoftwareWindow(wx.Frame):
    """Parameters and working options"""

    
    def __init__(self, parent, id, NetworkVersion, platformString):


        if platform == 'darwin':
            wx.Frame.__init__(self, parent, size=updateWindowSizeMac)
        elif platform == 'win32':
            wx.Frame.__init__(self, parent, size=updateWindowSizeWin)
        else:
            wx.Frame.__init__(self, parent, size=updateWindowSize)

        
        self.WindowParent=parent
        self.NetworkVersion = NetworkVersion
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        # self.Bind(wx.EVT_SIZE,self.OnResize)
        panel=wx.Panel(self)


        if platform != "win32":        
            self.SetWindowStyle(wx.STAY_ON_TOP)
        else:
            self.ToggleWindowStyle(wx.STAY_ON_TOP)

        self.SetTitle("gHRV Update Window")
            
        sizer=wx.BoxSizer(wx.VERTICAL)

        PageStr = '''<p><img src="LogoSmall.png" width="50" height="50"/></p>
            <center><p><b>There is a new version of gHRV!</b><>
            <p>You are running gHRV version %s (%s package)</p>
            <p>gHRV version %s is available for this platform</p>
            <p>Use <b>Go to web site</b> button for downloading</p></center>''' % (Version, platformString, self.NetworkVersion)

        html=wx.html.HtmlWindow(panel, id)
        html.SetPage(PageStr)
        
        sizer.Add(html, 1, wx.LEFT | wx.TOP | wx.GROW)

# ----------------- Beginning of sizer for buttons


        sbButtonsSizer=wx.BoxSizer(wx.HORIZONTAL)
        
        
        buttonLeft = wx.Button(panel, -1)
        buttonLeft.SetLabel("Skip gHRV %s" % self.NetworkVersion)
        buttonLeft.SetToolTip(wx.ToolTip("Click to permanently hide notification of this version"))
        sbButtonsSizer.Add(buttonLeft, flag=wx.ALL|wx.ALIGN_LEFT, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnSkip, id=buttonLeft.GetId())
        
        
        sbButtonsSizer.AddStretchSpacer(1)
        
        buttonLater = wx.Button(panel, -1, label="Later")
        sbButtonsSizer.Add(buttonLater, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=buttonLater.GetId())
        buttonLater.SetToolTip(wx.ToolTip("Click to decide later"))
        

        self.buttonDownload = wx.Button(panel, -1)
        self.buttonDownload.SetLabel("Go to web site")
        self.buttonDownload.SetToolTip(wx.ToolTip("Click to download new gHRV version"))
        
        sbButtonsSizer.Add(self.buttonDownload, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnBrowser, id=self.buttonDownload.GetId())
        # self.buttonRight.Disable()
        

        sizer.Add(sbButtonsSizer,flag=wx.ALL|wx.EXPAND, border=borderSmall)

# ----------------- End of sizer for buttons
        
        
        panel.SetSizer(sizer)
        
        self.Show()
        self.CenterOnParent()


    def OnSkip(self,event):
        self.WindowParent.settings["lastcheckedversion"]=self.NetworkVersion
        self.WindowParent.ConfigSave()
        self.WindowParent.UpdateWindowClose()
        self.Destroy()

    def OnBrowser(self,event):
        import webbrowser
        webbrowser.open("http://milegroup.github.com/ghrv/packages.html")
        self.WindowParent.Destroy()

        
    def OnEnd(self,event):
        self.WindowParent.UpdateWindowClose()
        self.Destroy()

    # def OnResize(self, event):
    #     w, h = self.GetSize()
    #     print "Width, height: ",w,", ",h
    #     event.Skip()


  
class MainApp(wx.App):
    def OnInit(self):
        self.frame = MainWindow(None, -1, '')
        self.frame.Show(True)
        return True

app = MainApp(0)
app.MainLoop()
