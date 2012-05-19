#!/usr/bin/python
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
    
# TODO: MacOSX change dialog messages as in http://www.blog.pythonlibrary.org/2010/07/10/the-dialogs-of-wxpython-part-2-of-2/
# TODO: Comprobar cuando la ventana es más grande que la señal
# TODO: Comprobar la edición de puntos en windows
# TODO: Error en settings cuando hay acentos en nombre fichero
# TODO: problema con color navyblue en mac

import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.pyplot
import os
import numpy as np
from sys import platform

from DataModel import DM
from configvalues import *

#os.chdir("/usr/share/ghrv") # Uncomment when building a .deb package

dm=DM(Verbose)
 

class FrameBasedEvolutionWindow(wx.Frame):  
    """ Window for temporal evolution of parameters obtained from interpolated HR"""
    
    sbDefaultText="  Press +, -, 0, left, right for zooming/panning. Press s to save plot"
    
    def __init__(self,parent,id,title):
        
        wx.Frame.__init__(self, parent, -1, title, size=mainWindowSize)
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
                        
        self.panel = wx.Panel(self)
        self.WindowParent=parent
        
        self.fig = matplotlib.figure.Figure(facecolor=TemporalBGColor)
        self.canvas = FigureCanvas(self.panel, -1, self.fig)
                   
        self.mainBox = wx.BoxSizer(wx.HORIZONTAL)
        self.mainBox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        
        self.vboxRightArea = wx.BoxSizer(wx.VERTICAL)        
        
        self.AllBands, self.VisibleBands=dm.GetVisibleBands()
        self.insertBandsSelector()
        
        self.refreshButton = wx.Button(self.panel, -1, "Refresh")
        self.vboxRightArea.Add(self.refreshButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_LEFT)
        self.Bind(wx.EVT_BUTTON, self.onRefresh, self.refreshButton)
        
        self.vboxRightArea.AddStretchSpacer(prop=1)
        
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
        self.sb.SetStatusText(self.sbDefaultText)
        
        dm.CreatePlotFBEmbedded(self.fig)
        self.canvas.draw()
        self.canvas.Bind(wx.EVT_CHAR, self.OnKeyPress)
        
        self.SetMinSize(mainWindowMinSize)
        self.Show(True)
        self.Layout()
        self.canvas.SetFocus()
        
    def OnKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == 43:
            dm.PlotFBZoomIn()
            self.canvas.draw()
        #if keycode == 45:
        #    dm.PlotHRZoomOut()
        #    self.canvas.draw()
        if keycode == 48:
            dm.PlotFBZoomReset()
            self.canvas.draw()
        if keycode == 316:
            dm.PlotFBPanRight()
            self.canvas.draw()
        if keycode == 314:
            dm.PlotFBPanLeft()
            self.canvas.draw()
        if keycode==115:
            fileName=""
            filetypes = "JPEG file (*.jpeg)|*.jpeg;*.JPEG;*.jpg;*.JPG|PDF file (*.pdf)|*.pdf;*.PDF|PNG file (*.png)|*.png;*.PNG|SVG file (*.svg)|*.svg;*.SVG|TIFF file (*.tiff)|*.tiff;*.TIFF;*.tif;*.TIF|All files (*.*)|*.*"
            dial = wx.FileDialog(self, message="Save figure as...", defaultFile=dm.GetName()+"_FB", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=filetypes)
            result = dial.ShowModal()
            if result == wx.ID_OK:
                fileName=dial.GetPath()
                try:
                    print "File: ",fileName
                    self.canvas.print_figure(fileName)
                except:
                    self.ErrorWindow(messageStr="Error saving figure to file: "+fileName,captionStr="Error saving figure    ")
            dial.Destroy()
        event.Skip()
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
        
        dm.SetVisibleBands(checkedBands)
        
        dm.CreatePlotFBEmbedded(self.fig)
        self.canvas.draw()


    def Refresh(self):
        dm.CreatePlotFBEmbedded(self.fig)
        self.canvas.draw()
    
        
    def OnEnd(self,event):
        self.WindowParent.OnFrameBasedEnded()
        self.Destroy()
        
    def OnExport(self,event):
        exportSettingsWindow=FrameBasedExportSettings(self,-1,"Export options")
        self.exportButton.Disable()
        
    def OnExportEnded(self):
        self.exportButton.Enable()
        

            
class FrameBasedExportSettings(wx.Frame):
    
    """Export options for frame-based parameters"""
    
    def __init__(self, parent, id, title):
        
        if platform != 'darwin':
            WindowSize=exportSettingsWindowSize
            WindowMinSize=exportSettingsWindowMinSize
        else:
            WindowSize=exportSettingsWindowSizeMac
            WindowMinSize=exportSettingsWindowMinSizeMac
        
        wx.Frame.__init__(self, parent, wx.ID_ANY, size=WindowSize)
        
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
        
        AllBandsOrig,VisibleBandsOrig = dm.GetVisibleBands()
        self.AllBands=list(AllBandsOrig)
        VisibleBands=list(VisibleBandsOrig)
        
        VisibleBands.remove("Heart rate")
        self.AllBands.remove("Heart rate")
        
        self.cbDict={}
        bandsInSizer1=0
        for Band in self.AllBands:
            self.cbDict[Band]=wx.CheckBox(panel,-1,Band,size=wx.DefaultSize)
            if bandsInSizer1 < 5:
                sbBandsSizer1.Add(self.cbDict[Band], wx.EXPAND)
                bandsInSizer1 += 1
            else:
                sbBandsSizer2.Add(self.cbDict[Band], wx.EXPAND)
            if Band in VisibleBands:
                self.cbDict[Band].SetValue(True)
    
        sbBandsSizer.Add(sbBandsSizer1,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        sbBandsSizer.Add(sbBandsSizer2,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
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
                    
        dial = wx.FileDialog(self, message="Save data as...", defaultFile=dm.GetName()+".txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dial.ShowModal()
        if result == wx.ID_OK:
            
                
            fileName=dial.GetPath()
            if result == wx.ID_OK:
                fileName=dial.GetPath()
                try:
                    dm.SaveFrameBasedData(fileName,listOfBands,SepChar,self.RowHeader.GetValue(),self.ColumnHeader.GetValue()) 
                except:
                    self.WindowParent.ErrorWindow(messageStr="Error saving data to file: "+fileName,captionStr="Error saving data file")
                    self.Raise()
        dial.Destroy()
        self.WindowParent.OnExportEnded()
        self.Destroy()



class EditNIHRWindow(wx.Frame):  
    """ Window for outliers removal in non interpolated HR"""
    NumClicks=0
    NumRemovedPoints=0
    
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self, parent, -1, title, size=mainWindowSize)
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        
        self.WindowParent=parent
                        
        self.panel = wx.Panel(self)
        
        self.fig = matplotlib.figure.Figure((5.0, 4.0),facecolor=EditBGColor)
        self.canvas = FigureCanvas(self.panel, -1, self.fig)
        self.canvas.mpl_connect('button_press_event', self.onClick)
        
        self.axes = self.fig.add_subplot(111)
        self.xvector, self.yvector, self.rrvector = dm.DataEditHR()
        
        self.ymin=min(self.yvector)
        self.ymax=max(self.yvector)
        self.xmin=self.xvector[0]
        self.xmax=self.xvector[-1]
        
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)        
        
        self.removeButton = wx.Button(self.panel, -1, "Remove", size=buttonSizeEditNIHR)
        self.Bind(wx.EVT_BUTTON, self.onRemove, self.removeButton)
        self.hbox.Add(self.removeButton, 0, border=borderSmall, flag=wx.LEFT)
        self.removeButton.Disable()
        
        
        self.clearButton = wx.Button(self.panel, -1, "Clear", size=buttonSizeEditNIHR)
        self.Bind(wx.EVT_BUTTON, self.onClear, self.clearButton)
        self.hbox.Add(self.clearButton, 0, border=borderSmall, flag=wx.LEFT)
        self.clearButton.Disable()
        
        self.hbox.AddStretchSpacer(prop=1)
        
        self.endButton = wx.Button(self.panel, -1, "End", size=buttonSizeEditNIHR)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=self.endButton.GetId())
        self.endButton.SetToolTip(wx.ToolTip("Click to finish removing outliers"))
        self.hbox.Add(self.endButton, 0, border=borderSmall, flag=wx.RIGHT)
                
        self.vbox.Add(self.hbox, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)
        
        self.panel.SetSizer(self.vbox)
        #self.vbox.Fit(self)
        
        self.drawFigure()
        
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText("Selected: 0 points  -  Removed: 0 points")
        
        self.SetMinSize(mainWindowMinSize)
        self.Show(True)
        
        self.Layout()
        #self.Centre()
        
        

   

    def drawFigure(self):
        """ Redraws the figure
        """
        # clear the axes and drawFigure the plot anew
        #
        self.axes.clear()        
        
        
        self.axes.plot(self.xvector,self.yvector,'k-')
        self.axes.set_xlabel("Time (sec.)")
        self.axes.set_ylabel("HR (beats/min.)")
        self.axes.set_title("Non interpolated heart rate")
        
        self.axes.set_xlim(self.xmin-0.05*(self.xmax-self.xmin),self.xmax+0.05*(self.xmax-self.xmin)) 
        self.axes.set_ylim(self.ymin-0.05*(self.ymax-self.ymin),self.ymax+0.05*(self.ymax-self.ymin))
        self.axes.grid()
        
        self.canvas.draw()
        
    def onClick(self,event):
        
        if event.xdata==None:
            return None
        
        if event.button == 1:
            if self.NumClicks==0:
                self.c1x=event.xdata
                self.c1y=event.ydata
                #self.axes.plot(event.xdata,event.ydata,'g.')
                self.axes.axvline(x=self.c1x, ymin=0, ymax=1, linewidth=2, color='g',linestyle='--')
                self.axes.axhline(y=self.c1y, xmin=0, xmax=1, linewidth=2, color='g',linestyle='--')
                self.canvas.draw()
                self.NumClicks += 1
                self.clearButton.Enable()
                self.endButton.Disable()
            elif self.NumClicks==1:
                self.Corner2=(event.xdata,event.ydata)
                self.c2x=event.xdata
                self.c2y=event.ydata
                inAreaList=[self.xvector[i]>min(self.c1x,self.c2x) and self.xvector[i]<max(self.c1x,self.c2x) and self.yvector[i]>min(self.c1y,self.c2y) and self.yvector[i]<max(self.c1y,self.c2y) for i in range(len(self.xvector))]
                if inAreaList.count(True)>0:
                    inArea=np.array(inAreaList,dtype=bool)
                    outAreaList=[ not inAreaList[i] for i in range(len(inAreaList))]
                    self.outArea=np.array(outAreaList,dtype=bool)
                    self.drawFigure()
                    self.axes.axvline(x=self.c1x, ymin=0, ymax=1, linewidth=2, color='g',linestyle='--')
                    self.axes.axhline(y=self.c1y, xmin=0, xmax=1, linewidth=2, color='g',linestyle='--')
                    self.axes.axvline(x=self.c2x, ymin=0, ymax=1, linewidth=2, color='g',linestyle='--')
                    self.axes.axhline(y=self.c2y, xmin=0, xmax=1, linewidth=2, color='g',linestyle='--')
                    self.axes.bar(self.c1x,self.c2y-self.c1y,self.c2x-self.c1x,self.c1y,alpha=0.2, facecolor='green')
                    self.axes.plot(self.xvector[inArea],self.yvector[inArea],'r.')
#                self.axes.plot(self.xvector[outArea],self.yvector[outArea],'b.')
                    strMessage="Selected: "+str(inAreaList.count(True))+" point"
                    if inAreaList.count(True) != 1:
                        strMessage += "s"
                    strMessage += "  -  Removed: "+str(self.NumRemovedPoints)+" point"
                    if self.NumRemovedPoints != 1:
                        strMessage += "s"
                    self.sb.SetStatusText(strMessage)
                    self.canvas.draw()
                    self.NumClicks+=1
                    self.endButton.Disable()
                    self.removeButton.Enable()
                else:
                    self.refreshStatus()
                    
                    
                
    def onRemove(self,event):
        toRemove=len(self.xvector)-len(self.outArea[self.outArea])
        self.NumRemovedPoints += toRemove
        self.xvector=self.xvector[self.outArea]
        self.yvector=self.yvector[self.outArea]
        self.rrvector=self.rrvector[self.outArea]
        self.refreshStatus()
                
    def onClear(self, event):
        self.refreshStatus()
        
        
    def OnEnd(self,event):
        if self.NumRemovedPoints>0:
            strMessage="Removing "+str(self.NumRemovedPoints)+" point"
            if self.NumRemovedPoints>1:
                strMessage +="s"
            strMessage += "\nAre you sure?"
            dial = wx.MessageDialog(self, strMessage, "Confirm removal", wx.CANCEL | wx.YES_NO | wx.ICON_QUESTION)
            result = dial.ShowModal()
            dial.Destroy()
            if result == wx.ID_YES:
                self.Destroy()
                dm.ReplaceHRVectors(self.xvector, self.yvector, self.rrvector)
                self.WindowParent.OnNIHREditEnded()
            elif result == wx.ID_NO:
                self.Close()
        else:
            self.WindowParent.OnNIHREditEnded()
            self.Destroy()
            
    
            
    def refreshStatus(self):
        self.drawFigure()
        self.canvas.draw()
        self.NumClicks=0
        self.clearButton.Disable()
        self.endButton.Enable()
        self.removeButton.Disable()
        strMessage="Selected: 0 points  -  Removed: "+str(self.NumRemovedPoints)+" point"
        if self.NumRemovedPoints!=1:
            strMessage += "s"
        self.sb.SetStatusText(strMessage)
        
 

class EditEpisodesWindow(wx.Frame):
    
    """ Window for editing episodes"""
    NumClicks=0
    
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self, parent, -1, title, size=mainWindowSize)
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        
        
        self.WindowParent=parent
        self.panel = wx.Panel(self)
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.fig = matplotlib.figure.Figure((5.0, 4.0),facecolor=EpisodesEditionBGColor)
        self.canvas = FigureCanvas(self.panel, -1, self.fig)
        self.canvas.mpl_connect('button_press_event', self.OnClick)
        
        self.axes = self.fig.add_subplot(111)
        self.xvector, self.yvector= dm.GetHRDataPlot()
        
        self.ymin=min(self.yvector)
        self.ymax=max(self.yvector)
        self.xmin=self.xvector[0]
        self.xmax=self.xvector[-1]
        
        
        self.hboxEditEpisodes = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxEditEpisodes.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

# ----------------- Begin of sizer for buttons in edit episodes
        
        self.vboxEditEpRightColumn = wx.BoxSizer(wx.VERTICAL)  
        
        self.EpTypes,self.EpVisibleTypes = dm.GetVisibleEpisodes()
        
        if len(self.EpTypes)>0:
            self.InsertTagsSelector()
            self.TagsSelectorPresent = True
        else:
            self.TagsSelectorPresent = False

        # Begin of AddEpisode staticbox
        
        sbAdd = wx.StaticBox(self.panel, label="Add")
        sbAddSizer = wx.StaticBoxSizer(sbAdd, wx.VERTICAL)
        
        if len(self.EpTypes)>0:
            InitValue=self.EpTypes[0]
        else:
            InitValue='NEW_TAG'
        self.cbCombo=wx.ComboBox(self.panel,choices=self.EpTypes, value=InitValue, style=wx.CB_DROPDOWN)
        sbAddSizer.Add(self.cbCombo,flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.cbCombo.Disable()
        
        
        self.addButton = wx.Button(self.panel, -1, "Add episode", size=buttonSizeEditEpisodes)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.addButton)
        sbAddSizer.Add(self.addButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)
        self.addButton.Disable()
        
        self.clearButton = wx.Button(self.panel, -1, "Clear", size=buttonSizeEditEpisodes)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clearButton)
        sbAddSizer.Add(self.clearButton, 0, border=borderSmall, flag=wx.RIGHT | wx.ALIGN_RIGHT)
        self.clearButton.Disable()
        
        self.vboxEditEpRightColumn.Add(sbAddSizer, flag=wx.ALL, border=borderSmall)
        
        # End of AddEpisode staticbox
        
        
        
        self.vboxEditEpRightColumn.AddStretchSpacer(prop=1)

        
        self.endButton = wx.Button(self.panel, -1, "End", size=buttonSizeEditEpisodes)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=self.endButton.GetId())
        self.endButton.SetToolTip(wx.ToolTip("Click to finish editing episodes"))
        self.vboxEditEpRightColumn.Add(self.endButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)
                
        self.hboxEditEpisodes.Add(self.vboxEditEpRightColumn, 0, flag=wx.EXPAND, border=borderBig)
        
# ----------------- End of sizer for buttons in edit episodes

        self.panel.SetSizer(self.hboxEditEpisodes)
        #self.hboxEditEpisodes.Fit(self)
        
        self.DrawFigure()
        
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText('')
        
        self.SetMinSize(mainWindowMinSize)
        self.Show(True)
        self.Layout()
        #self.Centre()
        
        
    def InsertTagsSelector(self):
        
        # Begin of select/unselect episodes checklist box
                
        sbEpisodes = wx.StaticBox(self.panel, label="Episodes")
        sbEpisodesSizer = wx.StaticBoxSizer(sbEpisodes, wx.VERTICAL)
        
        self.cbList = wx.CheckListBox(self.panel,choices=self.EpTypes)
        self.cbList.SetCheckedStrings(self.EpVisibleTypes)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnEpisodesList, self.cbList)
        sbEpisodesSizer.Add(self.cbList)
        
        self.vboxEditEpRightColumn.Insert(0,sbEpisodesSizer, flag=wx.ALL, border=borderSmall)
       
        
        # End of select/unselect episodes checklist box
        

    def DrawFigure(self):
        """ Redraws the figure
        """
        # clear the axes and DrawFigure the plot anew
        #
        self.axes.clear()        
        
        self.axes.plot(self.xvector,self.yvector,'k-')
        self.axes.set_xlabel("Time (sec.)")
        self.axes.set_ylabel("HR (beats/min.)")
        self.axes.set_title(dm.GetHeartRatePlotTitle())
        
        if dm.DataPlotHasVisibleEpisodes():
            tags,starts,durations,tagsVisible = dm.GetEpisodes()
            numEpisodes=len(tags)
#            print("Number: "+str(numEpisodes))
            i=0
            for tag in tagsVisible:
                startsvector=[starts[w] for w in range(numEpisodes) if tags[w]==tag]
                durationsvector=[durations[w] for w in range(numEpisodes) if tags[w]==tag]
                endsvector=[starts[w]+durations[w] for w in range(numEpisodes) if tags[w]==tag]
                for j in range(len(startsvector)):
                    if j==0:
                        self.axes.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=dm.GetEpisodeColor(tag), alpha=alphaMatplotlibTags, label=tag)
                    else:
                        self.axes.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=dm.GetEpisodeColor(tag), alpha=alphaMatplotlibTags)
                i=i+1
            leg=self.axes.legend(fancybox=True,shadow=True)
            for t in leg.get_texts():
                t.set_fontsize('small')
        
        self.axes.set_xlim(self.xmin,self.xmax) 
        self.axes.set_ylim(self.ymin-0.05*(self.ymax-self.ymin),self.ymax+0.05*(self.ymax-self.ymin))
        self.axes.grid()
        
        self.canvas.draw()
        
    def OnClick(self,event):
                
        if event.xdata==None:
            return None
        
        if event.button != 1:
            return None
        
        if self.NumClicks==0:
            self.cxleft=event.xdata
            self.axes.axvline(x=self.cxleft, ymin=0, ymax=1, linewidth=2, color='k',linestyle='--')
            self.canvas.draw()
            if self.clearButton.Enabled == False:
                self.clearButton.Enable()
            self.NumClicks += 1
            strMessage="Episode: ({0:.2f},--)".format(self.cxleft)
            self.sb.SetStatusText(strMessage)
            self.endButton.Disable()
                
        elif self.NumClicks==1:
            self.cxright=event.xdata
            self.axes.axvline(x=self.cxright, ymin=0, ymax=1, linewidth=2, color='k',linestyle='--')
            self.canvas.draw()
            if self.clearButton.Enabled == False:
                self.clearButton.Enable()
            if (self.cxleft > self.cxright):
                aux=self.cxleft
                self.cxleft=self.cxright
                self.cxright=aux
            self.NumClicks +=1
            self.axes.axvspan(self.cxleft,self.cxright,ymin=0,ymax=1,facecolor='k',alpha=0.3)
            self.canvas.draw()
            strMessage="Episode: ({0:.2f},{1:.2f})".format(self.cxleft,self.cxright)
            self.sb.SetStatusText(strMessage)
            self.addButton.Enable()
            self.cbCombo.Enable()
            
    def OnEpisodesList(self,event):
        dm.SetVisibleEpisodes(list(self.cbList.GetCheckedStrings()))
        self.DrawFigure()
        self.canvas.draw()
        self.RefreshStatus()
        
                
    def OnAdd(self,event):
        Tag=str(self.cbCombo.GetValue())
        self.EpTypes,self.EpVisibleTypes = dm.GetVisibleEpisodes()
        if Tag not in self.EpTypes:
            dm.AssignEpisodeColor(Tag)
        dm.AddEpisode(self.cxleft,self.cxright,Tag)
        self.cbCombo.Disable()
        self.RefreshStatus()
                
    def OnClear(self, event):
        self.clearButton.Disable()
        self.cbCombo.Disable()
        self.RefreshStatus()
        
        
    def OnEnd(self,event):
        self.Destroy()
        self.WindowParent.OnEpisodesEditEnded()            
            
    def RefreshStatus(self):
        self.DrawFigure()
        self.canvas.draw()
        self.clearButton.Disable()
        self.endButton.Enable()
        self.addButton.Disable()
        strMessage=""
        self.sb.SetStatusText(strMessage)
        self.NumClicks=0
        self.EpTypes,self.EpVisibleTypes = dm.GetVisibleEpisodes()
        if self.TagsSelectorPresent:
            self.cbList.SetItems(self.EpTypes)
            self.cbList.SetCheckedStrings(self.EpVisibleTypes)
            self.vboxEditEpRightColumn.Layout()
        else:
            self.InsertTagsSelector()
            self.TagsSelectorPresent = True
        self.cbCombo.SetItems(self.EpTypes)
        self.vboxEditEpRightColumn.Layout()
        
            
            
        
class ReportWindow(wx.Frame):  
    """ Window for Report"""
    
    import wx.html
    
    def __init__(self,parent,id,title,filename):
        
        wx.Frame.__init__(self, parent, -1, title, size=reportWindowSize)
        
        #print "Going to show:"+filename
        
        self.panel = wx.Panel(self)
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        self.WindowParent=parent

        vbox = wx.BoxSizer(wx.VERTICAL)
        

        htmlwin = wx.html.HtmlWindow(self.panel, -1, style=wx.NO_BORDER)
        #htmlwin.SetBackgroundColour(wx.RED)
        htmlwin.SetStandardFonts()
        htmlwin.LoadFile(filename)

        vbox.Add(htmlwin, 1, wx.LEFT | wx.TOP | wx.GROW)
        
        
        
        # Box sizer for buttons
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.pdfButton = wx.Button(self.panel, -1, "Save as PDF...", size=buttonSizeReportWindow)
        self.Bind(wx.EVT_BUTTON, self.OnPDF, id=self.pdfButton.GetId())
        self.pdfButton.SetToolTip(wx.ToolTip("Click to generate pdf report"))
        hbox.Add(self.pdfButton, 0, border=borderSmall, flag=wx.ALIGN_LEFT)
        
        hbox.AddStretchSpacer(1)
        
        self.endButton = wx.Button(self.panel, -1, "End", size=buttonSizeReportWindow)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=self.endButton.GetId())
        self.endButton.SetToolTip(wx.ToolTip("Click to close window"))
        
        hbox.Add(self.endButton, 0, border=borderSmall, flag=wx.ALIGN_RIGHT)

        vbox.Add(hbox, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)

        self.panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)
        
       
        self.SetMinSize(reportWindowMinSize)
        
    def OnEnd(self,event):
        self.WindowParent.OnReportEnded()
        self.Destroy()
        
    def OnPDF(self,event):
        dial = wx.MessageDialog(self, "Not yet implemented", "Soon...", wx.OK)
        result = dial.ShowModal()
        dial.Destroy()
        
       
        
class MainWindow(wx.Frame):
    """ Main window application"""

    configDir = os.path.expanduser('~')+os.sep+'.ghrv'
    configFile = configDir+os.sep+"ghrv.cfg"
    sbDefaultText="  gHRV 0.19 - http://ghrv.milegroup.net"
    sbPlotHRText="  Press +, -, 0, left, right for zooming/panning. Press s to save plot"
        
    def __init__(self, parent, id, title):

        self.ConfigInit()
                        
        wx.Frame.__init__(self, parent, id, title, size=mainWindowSize)

        
        
        self.Bind(wx.EVT_CLOSE,self.OnExit)
        
        self.MainPanel=wx.Panel(self)
        self.fbWindowPresent=False
        self.configWindowPresent=False
        self.editNIHRWindowPresent=False
        self.editEpisodesWindowPresent=False
        self.aboutWindowPresent=False
        self.reportWindowPresent=False
        
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
        if platform != 'darwin':
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
        if platform != 'darwin':
            self.buttonEditEpisodes.SetBackgroundColour(EpisodesEditionBGColor)
                            
        sbEpisodesButtonsSizer.Add(sbEpisodesButtonsSizerRow1, flag=wx.EXPAND)
        
        vboxLeft.Add(sbEpisodesButtonsSizer,flag=wx.EXPAND | wx.TOP, border=borderVeryBig)
        
        # End of sizer for episodes buttons
        # ---------------------------------
        
        
        
        # --------------------------------  
        # Begin of sizer for tools buttons
        
        sbToolsButtons = wx.StaticBox(self.MainPanel, label="Tools")
        sbToolsButtonsSizer = wx.StaticBoxSizer(sbToolsButtons, wx.VERTICAL)
        
        self.buttonAnalyze = wx.Button(self.MainPanel, -1, label="Analyze")
        sbToolsButtonsSizer.Add(self.buttonAnalyze, flag=wx.ALL | wx.EXPAND , border=borderSmall)
        self.MainPanel.Bind(wx.EVT_BUTTON, self.OnInterpolateNIHR, id=self.buttonAnalyze.GetId())
        self.buttonAnalyze.SetToolTip(wx.ToolTip("Interpolate heart rate signal"))
        self.buttonAnalyze.Disable()
        
        
        self.buttonTemporal = wx.Button(self.MainPanel, -1, label="Frame-based evolution...")
        sbToolsButtonsSizer.Add(self.buttonTemporal, flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnFrameBased, id=self.buttonTemporal.GetId())
        self.buttonTemporal.SetToolTip(wx.ToolTip("Temporal evolution of parameters"))
        if platform != 'darwin':
            self.buttonTemporal.SetBackgroundColour(TemporalBGColor)
        self.buttonTemporal.Disable()
        
        self.buttonReport = wx.Button(self.MainPanel, -1, label="Report")
        sbToolsButtonsSizer.Add(self.buttonReport, flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnReport, id=self.buttonReport.GetId())
        self.buttonReport.SetToolTip(wx.ToolTip("Create report"))
        if platform != 'darwin':
            self.buttonReport.SetBackgroundColour(ReportBGColor)
        self.buttonReport.Disable()
        
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
        
        self.fig = matplotlib.figure.Figure((4,5),facecolor=HRBGColor)
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
        
        self.canvas.Bind(wx.EVT_CHAR, self.OnKeyPress)
        
        self.SetMinSize(mainWindowMinSize)
        self.SetTitle('gHRV')
        self.Centre()
        self.MainPanel.SetSizer(self.sizer)
        self.MainPanel.Layout()
        
        if DebugMode:
            dm.LoadDataModel("/home/leandro/Documentos/Programacion/gHRV/data_0_17/caca2.ghrv")
            self.RefreshMainWindow()
            if dm.HasFrameBasedParams()==False:
                dm.CalculateFrameBasedParams(showProgress=True)
            self.fbWindow = FrameBasedEvolutionWindow(self,-1,"Temporal evolution of parameters")
            self.fbWindowPresent=True
            self.RefreshMainWindowButtons()
            
        
        self.canvas.SetFocus()
        
    def OnKeyPress(self, event):
        if not dm.HasHR():
            event.Skip()
            return
        keycode = event.GetKeyCode()
        if keycode == 43:
            dm.PlotHRZoomIn()
            self.canvas.draw()
        if keycode == 45:
            dm.PlotHRZoomOut()
            self.canvas.draw()
        if keycode == 48:
            dm.PlotHRZoomReset()
            self.canvas.draw()
        if keycode == 316:
            dm.PlotHRPanRight()
            self.canvas.draw()
        if keycode == 314:
            dm.PlotHRPanLeft()
            self.canvas.draw()
        if keycode==115:
            fileName=""
            filetypes = "JPEG file (*.jpeg)|*.jpeg;*.JPEG;*.jpg;*.JPG|PDF file (*.pdf)|*.pdf;*.PDF|PNG file (*.png)|*.png;*.PNG|SVG file (*.svg)|*.svg;*.SVG|TIFF file (*.tiff)|*.tiff;*.TIFF;*.tif;*.TIF|All files (*.*)|*.*"
            dial = wx.FileDialog(self, message="Save figure as...", defaultFile=dm.GetName()+"_HR", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=filetypes)
            result = dial.ShowModal()
            if result == wx.ID_OK:
                fileName=dial.GetPath()
                try:
                    print "File: ",fileName
                    self.canvas.print_figure(fileName)
                except:
                    self.ErrorWindow(messageStr="Error saving figure to file: "+fileName,captionStr="Error saving figure    ")
            dial.Destroy()
        event.Skip()
        self.canvas.SetFocus()
    
   
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
        self.buttonConfig.Disable()
        self.buttonAbout.Disable()
        self.buttonReport.Disable()

    def RefreshMainWindowButtons(self):
        """Redraws main window buttons"""
        
        self.DisableAllButtons() # by default all disabled
        
        if self.configWindowPresent or self.editNIHRWindowPresent or self.editEpisodesWindowPresent:
            return
        
        self.buttonConfig.Enable()
        
        if self.aboutWindowPresent:
            self.buttonAbout.Disable()
        else:
            self.buttonAbout.Enable()
            
        
        if dm.HasHR():
            self.buttonSaveProject.Enable()
            if not self.fbWindowPresent:
                self.buttonClearProject.Enable()
            self.buttonOptionsProject.Enable()
            self.buttonEditEpisodes.Enable()
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
        if dm.HasHR():
            self.sb.SetStatusText(self.sbPlotHRText)
    
    def RefreshMainWindowPlot(self):
        """Redraws the plot of the main window"""
        
        self.fig.clear()
        dm.CreatePlotHREmbedded(self.fig)
        self.canvas.draw()
        self.canvas.SetFocus()
        
        
    def ErrorWindow(self,messageStr,captionStr="ERROR"):
        """Generic error window"""
        dial = wx.MessageDialog(self, caption=captionStr, message=messageStr, style=wx.OK | wx.ICON_ERROR)
        result = dial.ShowModal()
        dial.Destroy()
        self.canvas.SetFocus()
    
    def WarningWindow(self,messageStr,captionStr="WARNING"):
        """Generic warning window"""
        dial = wx.MessageDialog(self, caption=captionStr, message=messageStr, style=wx.OK | wx.ICON_WARNING)
        result = dial.ShowModal()
        dial.Destroy()
        self.canvas.SetFocus()
       

    def OnLoadBeat(self, event):
        filetypes = "Supported files (*.txt;*.hrm;*sdf)|*.txt;*.TXT;*.hrm;*.HRM;*.sdf;*.SDF|TXT ascii files (*.txt)|*.txt;*.TXT|Polar files (*.hrm)|*.hrm;*.HRM|Suunto files (*.sdf)|*.sdf;*.SDF|All files (*.*)|*.*"
        fileName=""
        dial = wx.FileDialog(self, message="Load file", wildcard=filetypes, style=wx.FD_OPEN)
        result = dial.ShowModal()
        if result == wx.ID_OK:
            fileName=dial.GetPath()
            ext=fileName[-3:].lower()            
            dial.Destroy()
            if ext=="txt":
                try:
                    dm.LoadFileAscii(fileName,self.settings)
                except:
                    self.ErrorWindow(messageStr=fileName+" does not seem to be a valid ascii file",
                                     captionStr="Error loading ascii file")
                else:
                    self.RefreshMainWindow()
            if ext=="hrm":
                try:
                    dm.LoadFilePolar(fileName,self.settings)
                except:
                    self.ErrorWindow(messageStr=fileName+" does not seem to be a valid polar file",
                                     captionStr="Error loading polar file")
                else:
                    self.RefreshMainWindow()
            if ext=="sdf":
                try:
                    dm.LoadFileSuunto(fileName,self.settings)
                except:
                    self.ErrorWindow(messageStr=fileName+" does not seem to be a valid suunto file",
                                     captionStr="Error loading suunto file")
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
                dm.LoadEpisodesAscii(fileName)
            except:
                self.ErrorWindow(messageStr=fileName+" does not seem to be a valid episodes file",captionStr="Error loading episodes file")
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
                dm.LoadDataModel(fileName)
            except:
                self.ErrorWindow(messageStr=fileName+" does not seem to be a valid project file",captionStr="Error loading project file")
            else:
                self.RefreshMainWindow()                
            
        
    def OnProjectSave(self,event):
        fileName=""
        dial = wx.FileDialog(self, message="Save project as...", defaultFile=dm.GetName()+".ghrv", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dial.ShowModal()
        if result == wx.ID_OK:
            fileName=dial.GetPath()
            try:
                dm.SaveDataModel(fileName)      
            except:
                self.ErrorWindow(messageStr="Error saving project to file: "+fileName,captionStr="Error saving project file")
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
            self.sb.SetStatusText(self.sbDefaultText)
    
    def OnEpisodesEdit(self,event):
        EditEpisodesWindow(self,-1,'Episodes Edition')
        self.editEpisodesWindowPresent=True
        self.RefreshMainWindowButtons()
    
    def OnEpisodesEditEnded(self):
        self.editEpisodesWindowPresent=False
        self.RefreshMainWindow()
        if self.fbWindowPresent:
            self.fbWindow.Refresh()
    
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
        EditNIHRWindow(self,-1,'Non interpolated HR Edition')
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
        dm.CreateReport(reportDir,reportName)
        ReportWindow(self,-1,'Report: '+dm.GetName(),reportDir+os.sep+reportName)
        self.reportWindowPresent=True
        self.RefreshMainWindowButtons()

        
    def OnReportEnded(self):
        self.reportWindowPresent=False
        self.RefreshMainWindow()
        self.canvas.SetFocus()
        
        
    def OnFrameBased(self,event):
        if dm.HasFrameBasedParams()==False:
            dm.CalculateFrameBasedParams(showProgress=True)
        self.fbWindow = FrameBasedEvolutionWindow(self,-1,"Temporal evolution of parameters")
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
    """Parameters and working options"""
    
    def __init__(self, parent, id, settings, conftype, settings2=None):
        # conftype: project or general
        # settings2 used for main settings when conftype="project"
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
        
  

        

class AboutDlg(wx.Frame):
    """About box"""
    
    import wx.html
 
    def __init__(self, parent, id):
        if platform != 'darwin':
            wx.Frame.__init__(self, parent, wx.ID_ANY, title="About", size=aboutWindowSize)
            self.SetMinSize(aboutWindowMinSize)
        else:
            wx.Frame.__init__(self, parent, wx.ID_ANY, title="About", size=aboutWindowSizeMac)
            self.SetMinSize(aboutWindowSizeMac)
        
        self.WindowParent=parent
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        
        html=wx.html.HtmlWindow(self, id)
        html.SetPage(
            '<p align="center"><img src="LogoSmall.png"/></p>'
            '<h3 align="center">gHRV 0.19</h3>'
            '<p align="center"><b>gHRV: a graphical application for Heart Rate Variability analysis</b></p>'
            '<p align="center">Copyright (C) 2012  Milegroup - Dpt. Informatics - University of Vigo - Spain</p>'
            '<p align="center"><i>http://www.milegroup.net</i></p>'
            "<hr/>"
            '<p align="left"><b>Authors:</b></p>'
            '<ul>'
            '<li>Leandro Rodr&iacute;guez-Li&ntilde;ares</li>'
            '<li>Arturo M&eacute;ndez</li>'
            '<li>Mar&iacute;a Jos&eacute; Lado</li>'
            '<li>Xos&eacute; Ant&oacute;n Vila</li>'
            '</ul>'
            "<hr/>"
            '<p align="justify"> This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.</p>'
            '<p align="justify">This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details (http://www.gnu.org/licenses/).</p>'
            )
        
        self.Show()
        self.Layout()
        #self.Centre()
        
        
    def OnEnd(self,event):
        self.WindowParent.OnAboutEnded()
        self.Destroy()
        
    
        

  
class MainApp(wx.App):
    def OnInit(self):
        self.frame = MainWindow(None, -1, '')
        self.frame.Show(True)
        return True

app = MainApp(0)
app.MainLoop()
