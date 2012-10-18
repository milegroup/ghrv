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


import wx
from configvalues import *
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from DataModel import DM
import numpy as np
import os

class PoincarePlotWindow(wx.Frame):

    sbDefaultText="   Keys: 's' saves plot"

    def __init__(self,parent,id,title,dm):

        wx.Frame.__init__(self, parent, -1, title, size=poincareWindowSize)

        self.poincareDelta = 1
        self.dm = dm
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)  
        
        self.WindowParent=parent

        sizer=wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)



        # -------------- Begin of figure

        self.fig = matplotlib.figure.Figure((5.0, 5.0),facecolor=PoincareBGColor)
        # self.fig.subplots_adjust(left=0.05, bottom=0.18, right=0.98, top=0.92, wspace=0.20, hspace=0.15)
        self.canvas = FigureCanvas(panel, -1, self.fig)
        
        self.axes = self.fig.add_subplot(111, aspect='equal')

        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

        # -------------- End of figure

        # # -------------- Begin of buttons

        hbox = wx.BoxSizer(wx.HORIZONTAL)   

        hbox.AddStretchSpacer(prop=1)

        endButton = wx.Button(panel, -1, "Close", size=buttonSizeSignif)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=endButton.GetId())
        endButton.SetToolTip(wx.ToolTip("Click to close window"))
        hbox.Add(endButton, 0, border=borderSmall, flag=wx.RIGHT)
                
        sizer.Add(hbox, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)

        # # -------------- End of buttons

        panel.SetSizer(sizer)

        self.SetMinSize(poincareWindowMinSize)

        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText(self.sbDefaultText)

        self.canvas.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)

        self.Show(True)
        self.Layout()
        self.Refresh()
        self.canvas.SetFocus()

    def OnKeyPress(self,event):

        keycode = event.GetKeyCode()

        if keycode==83:
            fileName=""
            if platform != "win32":
                filetypes = fileTypesLinMac
                extensions= extensionsLinMac
            else:
                filetypes = fileTypesWin
                extensions= extensionsWin
                
            dial = wx.FileDialog(self, message="Save figure as...", defaultFile=self.dm.GetName()+"_SIG", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=filetypes)
            result = dial.ShowModal()
            if result == wx.ID_OK:
                fileName=dial.GetPath()
                fileExt = os.path.splitext(fileName)[1][1:].strip()
                if fileExt=="":
                    self.ErrorWindow(messageStr="Filename extension missing",captionStr="Error saving figure    ")
                elif fileExt not in extensions:
                    self.ErrorWindow(messageStr="Filetype not supported: "+fileExt,captionStr="Error saving figure    ")
                else:
                    try:
                        self.canvas.print_figure(fileName)
                    except:
                        self.ErrorWindow(messageStr="Error saving figure to file: "+fileName,captionStr="Error saving figure    ")
            dial.Destroy()

        self.canvas.SetFocus()

        event.Skip()

    def OnEnd(self,event):
        self.WindowParent.OnPoincareEnded()
        self.Destroy()

    def Refresh(self):
        from matplotlib.patches import Ellipse
        

        self.axes.clear()
        xvector,yvector = self.dm.GetPoincareDataPlot()

        maxval=max(max(xvector),max(yvector))
        maxplot=maxval*1.05
        maxcoord=maxval*1.1

        minval=min(min(xvector),min(yvector))
        minplot=minval*0.95
        mincoord=minval*0.9

        meanx=np.mean(xvector)
        meany=np.mean(yvector)

        self.axes.plot(xvector,yvector,'.r')

        self.axes.arrow(minplot,minplot,(maxplot-minplot),(maxplot-minplot),
            lw=1, head_width=(maxcoord-mincoord)/100,
            head_length=(maxcoord-mincoord)/50,
            length_includes_head=True, fc='k', zorder=3)

        if (meanx<(min(xvector)+max(xvector))/2):
            self.axes.arrow(
                2*meanx-minplot,
                minplot,
                2*minplot-2*meanx,
                2*meany-2*minplot,
                lw=1, head_width=(maxcoord-mincoord)/100,
                head_length=(maxcoord-mincoord)/50,
                length_includes_head=True, fc='k', zorder=4)
        else:
            self.axes.arrow(
                maxplot,
                2*meany-maxplot,
                -2*maxplot+2*meanx,
                2*maxplot-2*meany,
                lw=1, head_width=(maxcoord-mincoord)/100,
                head_length=(maxcoord-mincoord)/50,
                length_includes_head=True, fc='k', zorder=4)

        self.axes.set_xlim(mincoord,maxcoord)
        self.axes.set_ylim(mincoord,maxcoord)
        self.axes.set_xlabel("$RR_i (msec.)$")
        self.axes.set_ylabel("$RR_{i+1} (msec.)$")
        self.axes.set_title(self.dm.GetPoincarePlotTitle())

        sd1 = np.std((xvector-yvector)/np.sqrt(2.0),ddof=1)
        sd2 = np.std((xvector+yvector)/np.sqrt(2.0),ddof=1)

        ell=Ellipse(xy=(np.mean(xvector),np.mean(yvector)),width=2*sd1,height=2*sd2,angle=-45,linewidth=1, color='k', fc="none")
        self.axes.add_artist(ell)
        # ell.set_alpha(0.7)
        ell.set(zorder=2)

        if self.dm.data["Verbose"]==True:
            print (u"** Creating Poincaré Plot")
            print("   SD1: {0:.3f}".format(sd1))
            print("   SD2: {0:.3f}".format(sd2))
        
        self.axes.grid()

  
        self.canvas.draw()

    