#!/usr/bin/python
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
import Utils
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from DataModel import DM
import numpy as np
from sys import platform

class EditNIHRWindow(wx.Frame):  
    """ Window for outliers removal in non interpolated HR"""
    NumClicks=0
    NumRemovedPoints=0
    
    def __init__(self,parent,id,title, dm):
        wx.Frame.__init__(self, parent, -1, title)
        
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)

        self.dm = dm
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        
        self.WindowParent=parent
                        
        self.panel = wx.Panel(self)
        
        if ColoredBGPlots:
            self.fig = matplotlib.figure.Figure((5.0, 4.0),facecolor=EditBGColor)
        else:
            self.fig = matplotlib.figure.Figure((5.0, 4.0))
        self.canvas = FigureCanvas(self.panel, -1, self.fig)
        self.canvas.mpl_connect('button_press_event', self.onClick)
        
        self.axes = self.fig.add_subplot(111)
        self.xvector, self.yvector, self.rrvector = self.dm.DataEditHR()
        
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
        
        defSize,minSize=Utils.RecalculateWindowSizes(mainWindowSize,mainWindowMinSize)
        self.SetSize(defSize)
        self.SetMinSize(minSize)
        
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
                self.dm.ReplaceHRVectors(self.xvector, self.yvector, self.rrvector)
                self.WindowParent.OnNIHREditEnded()
                self.Destroy()
            elif result == wx.ID_NO:
                self.WindowParent.OnNIHREditEnded()
                self.Destroy()
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
        
 
            
