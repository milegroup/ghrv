# -*- coding:utf-8 -*-


#   ----------------------------------------------------------------------
#   gHRV: a graphical application for Heart Rate Variability analysis
#   Copyright (C) 2015  Milegroup - Dpt. Informatics
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

import wx
from configvalues import *
import matplotlib
import Utils
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import os
from sys import platform
import numpy as np
from Significance import SignificanceWindow


class FrameBasedEvolutionWindow(wx.Frame):  
    """ Window for temporal evolution of parameters obtained from interpolated HR"""
    
    sbDefaultText=""
    
    def __init__(self,parent,id,title,dm):

        self.dm = dm
        
        wx.Frame.__init__(self, parent, -1, title)
        
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
                        
        self.panel = wx.Panel(self)
        self.WindowParent=parent
        
        if ColoredBGPlots:
            self.fig = matplotlib.figure.Figure(facecolor=TemporalBGColor)
        else:
            self.fig = matplotlib.figure.Figure()
            
        self.canvas = FigureCanvas(self.panel, -1, self.fig)
                   
        self.mainBox = wx.BoxSizer(wx.HORIZONTAL)
        self.mainBox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        
        self.vboxRightArea = wx.BoxSizer(wx.VERTICAL)        
        
        self.AllBands, self.VisibleBands=self.dm.GetVisibleBands()
        self.insertBandsSelector()
        
        self.refreshButton = wx.Button(self.panel, -1, "Refresh")
        self.vboxRightArea.Add(self.refreshButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_LEFT)
        self.Bind(wx.EVT_BUTTON, self.onRefresh, self.refreshButton)
        
        self.vboxRightArea.AddStretchSpacer(prop=1)

        self.signifButton = wx.Button(self.panel, -1, "Significance...", size=buttonSizeFrameBased)
        self.Bind(wx.EVT_BUTTON, self.OnSignif, id=self.signifButton.GetId())
        self.signifButton.SetToolTip(wx.ToolTip("Click to perform significance analysis"))
        self.vboxRightArea.Add(self.signifButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)
        if platform != 'darwin' and ColoredButtons:
            self.signifButton.SetBackgroundColour(SignifBGColor)
        if self.dm.HasVisibleEpisodes():
            self.signifButton.Enable()
        else:
            self.signifButton.Disable()

        
        self.exportButton = wx.Button(self.panel, -1, "Export txt...", size=buttonSizeFrameBased)
        self.Bind(wx.EVT_BUTTON, self.OnExport, id=self.exportButton.GetId())
        self.exportButton.SetToolTip(wx.ToolTip("Click to export to txt file"))
        self.vboxRightArea.Add(self.exportButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)
        #self.exportButton.Disable()
   
        self.endButton = wx.Button(self.panel, -1, "End", size=buttonSizeFrameBased)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=self.endButton.GetId())
        self.endButton.SetToolTip(wx.ToolTip("Click to close window"))
        self.vboxRightArea.Add(self.endButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)
                
        self.mainBox.Add(self.vboxRightArea, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)
        
        self.panel.SetSizer(self.mainBox)
        
        self.sb = self.CreateStatusBar()
        self.sbDefaultText = "Window size: "+str(dm.data["windowsize"])+" sec."
        self.sbDefaultText += "   -   "
        self.sbDefaultText += "Window shift: "+str(dm.data["windowshift"])+" sec."
        self.sbDefaultText += "   -   "
        numFrames = dm.GetNumFrames(dm.data["interpfreq"],dm.data["windowsize"],dm.data["windowshift"])
        self.sbDefaultText += "No. of frames: "+str(numFrames)

        self.sb.SetStatusText(self.sbDefaultText)
        
        self.dm.CreatePlotFBEmbedded(self.fig)
        self.canvas.draw()
        
        defSize,minSize=Utils.RecalculateWindowSizes(mainWindowSize,mainWindowMinSize)
        self.SetSize(defSize)
        self.SetMinSize(minSize)
                
        self.Show(True)
        self.Layout()
        self.canvas.SetFocus()
        
      

    def insertBandsSelector(self):
        
         # Begin of select/unselect bands checklist box
                
        sbBands = wx.StaticBox(self.panel, label="Visible bands")
        sbBandsSizer = wx.StaticBoxSizer(sbBands, wx.VERTICAL)
        
        self.bandsRB=[]
        for band in self.AllBands:
            if len(self.bandsRB)==0:
                tmp = wx.CheckBox(self.panel, label=band,style=wx.RB_GROUP)
            else:
                tmp = wx.CheckBox(self.panel, label=band)
            tmp.SetValue(False)
            if band in self.VisibleBands:
                tmp.SetValue(True)
            if band == "Heart rate":
                tmp.Disable()
            self.bandsRB.append(tmp)
            sbBandsSizer.Add(tmp, wx.EXPAND)
        
        self.vboxRightArea.Insert(0,sbBandsSizer, flag=wx.ALL, border=borderSmall)
        
    def onRefresh(self,event):
        checkedBands=[]
        for indexband in range(len(self.AllBands)):
            bandname = self.AllBands[indexband]
            bandstatus = self.bandsRB[indexband].GetValue()
            if bandstatus:
                checkedBands.append(bandname)
            #print "Band: ",bandname,"  - Checked: ",bandstatus
        
        self.dm.SetVisibleBands(checkedBands)
        
        self.dm.CreatePlotFBEmbedded(self.fig)
        self.canvas.draw()


    def Refresh(self):
        self.dm.CreatePlotFBEmbedded(self.fig)
        self.canvas.draw()

        if self.dm.HasVisibleEpisodes():
            self.signifButton.Enable()
        else:
            self.signifButton.Disable()
    
        
    def OnEnd(self,event):
        self.WindowParent.OnFrameBasedEnded()
        self.Destroy()
        
    def OnExport(self,event):
        exportSettingsWindow=FrameBasedExportSettings(self,-1,"Export options", self.dm)
        self.exportButton.Disable()
        
    def OnExportEnded(self):
        self.exportButton.Enable()

    def OnSignif(self,event):
        SignificanceWindow(self,-1,'Significance analysis',self.dm)
        self.signifButton.Disable()
        self.WindowParent.signifWindowPresent=True
        self.WindowParent.RefreshMainWindowButtons()
        # exportSettingsWindow=FrameBasedExportSettings(self,-1,"Export options", self.dm)
        # self.exportButton.Disable()
    def OnSignifEnded(self):
        self.signifButton.Enable()
        self.WindowParent.signifWindowPresent=False
        self.WindowParent.RefreshMainWindowButtons()


class FrameBasedExportSettings(wx.Frame):
    
    """Export options for frame-based parameters"""
    
    def __init__(self, parent, id, title, dm):

        self.dm = dm
        
        if platform != 'darwin':
            WindowSize=exportSettingsWindowSize
            WindowMinSize=exportSettingsWindowMinSize
        else:
            WindowSize=exportSettingsWindowSizeMac
            WindowMinSize=exportSettingsWindowMinSizeMac
        
        wx.Frame.__init__(self, parent, wx.ID_ANY, size=WindowSize)
        
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        
        panel=wx.Panel(self)
        self.WindowParent=parent
        self.SetTitle("Export options")        
        

        sizer=wx.BoxSizer(wx.VERTICAL)
        
# ----------------- Beginning of sizer for bands

        sbBands = wx.StaticBox(panel, label="Bands")
        sbBandsSizer = wx.StaticBoxSizer(sbBands, wx.VERTICAL)
        sbBandsSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sbBandsSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sbBandsSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        
        AllBandsOrig,VisibleBandsOrig = self.dm.GetVisibleBands()
        self.AllBands=list(AllBandsOrig)
        VisibleBands=list(VisibleBandsOrig)
        
        VisibleBands.remove("Heart rate")
        self.AllBands.remove("Heart rate")
        
        self.cbDict={}
        bandsInSizer1=0
        bandsInSizer2=0
        for Band in self.AllBands:
            self.cbDict[Band]=wx.CheckBox(panel,-1,Band,size=wx.DefaultSize)
            if bandsInSizer1 < 5:
                sbBandsSizer1.Add(self.cbDict[Band], wx.EXPAND)
                bandsInSizer1 += 1
            else:
                if bandsInSizer2 < 5:
                    sbBandsSizer2.Add(self.cbDict[Band], wx.EXPAND)
                    bandsInSizer2 += 1
                else:
                    sbBandsSizer3.Add(self.cbDict[Band], wx.EXPAND)
            if Band in VisibleBands:
                self.cbDict[Band].SetValue(True)
    
        sbBandsSizer.Add(sbBandsSizer1,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        sbBandsSizer.Add(sbBandsSizer2,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        sbBandsSizer.Add(sbBandsSizer3,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        sizer.Add(sbBandsSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        
        
# ----------------- End of sizer for bands

# ----------------- Beginning of sizer for separator
        
        sbSepChar = wx.StaticBox(panel, label="Separation character")
        sbSepCharSizer = wx.StaticBoxSizer(sbSepChar, wx.HORIZONTAL)
        
      
        self.scSemiColon = wx.RadioButton(panel, label=';',style=wx.RB_GROUP)
        sbSepCharSizer.Add(self.scSemiColon,wx.EXPAND)
        self.scSemiColon.SetValue(True)
        
        self.scColon = wx.RadioButton(panel, label=':')
        sbSepCharSizer.Add(self.scColon,wx.EXPAND)
        
        self.scComma = wx.RadioButton(panel, label=',')
        sbSepCharSizer.Add(self.scComma,wx.EXPAND)
        
        self.scSpace = wx.RadioButton(panel, label='Space')
        sbSepCharSizer.Add(self.scSpace,wx.EXPAND)
        
        self.scTab = wx.RadioButton(panel, label='Tab')
        sbSepCharSizer.Add(self.scTab,wx.EXPAND)
        
        
        sizer.Add(sbSepCharSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        
        
# ----------------- End of sizer for separator

# ----------------- Beginning of sizer for Options

        sbOptions = wx.StaticBox(panel, label="Options")
        sbOptionsSizer = wx.StaticBoxSizer(sbOptions, wx.VERTICAL)
        
        self.RowHeader = wx.CheckBox(panel,-1,"Header row (name of bands)",size=wx.DefaultSize)
        self.RowHeader.SetValue(True)
        sbOptionsSizer.Add(self.RowHeader)
        self.ColumnHeader = wx.CheckBox(panel,-1,"Header column (frame index)",size=wx.DefaultSize)
        self.ColumnHeader.SetValue(True)
        sbOptionsSizer.Add(self.ColumnHeader)
        
        
        sizer.Add(sbOptionsSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        
# ----------------- End of sizer for Options

        sizer.AddStretchSpacer(1)
        
# ----------------- Beginning of sizer for buttons


        sbButtonsSizer=wx.BoxSizer(wx.HORIZONTAL)
    
        
        
        buttonCancel = wx.Button(panel, -1, label="Cancel")
        sbButtonsSizer.Add(buttonCancel, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=buttonCancel.GetId())
        buttonCancel.SetToolTip(wx.ToolTip("Click to cancel"))
        
        sbButtonsSizer.AddStretchSpacer(1)

        buttonOk = wx.Button(panel, -1, label="Ok")
        sbButtonsSizer.Add(buttonOk, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=buttonOk.GetId())
        buttonOk.SetToolTip(wx.ToolTip("Click to proceed"))
        
        

        sizer.Add(sbButtonsSizer,flag=wx.ALL|wx.EXPAND, border=borderSmall)
        
# ----------------- End of sizer for buttons
        
        
        panel.SetSizer(sizer)
        
        self.SetMinSize(WindowMinSize)
        self.Center()
        self.Show()
        
    def OnEnd(self,event):
        self.WindowParent.OnExportEnded()
        self.Destroy()
        
    def OnOk(self,event):
        listOfBands=[]
        for cbkey in self.AllBands:
            if self.cbDict[cbkey].GetValue():
                listOfBands.append(cbkey)
        
        if len(listOfBands)==0:
            return
        
        if self.scSemiColon.GetValue():
            SepChar=";"
        elif self.scColon.GetValue():
            SepChar=':'
        elif self.scComma.GetValue():
            SepChar=','
        elif self.scSpace.GetValue():
            SepChar=' '
        elif self.scTab.GetValue():
            SepChar='\t'
                    
        dial = wx.FileDialog(self, message="Save data as...", defaultFile=self.dm.GetName()+".txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dial.ShowModal()


        if result == wx.ID_OK:        
            fileName=dial.GetPath()
            if result == wx.ID_OK:
                fileName=dial.GetPath()
                try:
                    self.dm.SaveFrameBasedData(fileName,listOfBands,SepChar,self.RowHeader.GetValue(),self.ColumnHeader.GetValue()) 
                    Utils.InformCorrectFile(fileName)
                except:
                    Utils.ErrorWindow(messageStr="Error saving data to file: "+fileName,captionStr="Error saving data file")
                    self.Raise()
        dial.Destroy()
        self.WindowParent.OnExportEnded()
        self.Destroy()

