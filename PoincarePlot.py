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


import wx
from configvalues import *
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from DataModel import DM
import numpy as np
import os
from sys import platform

class PoincarePlotWindow(wx.Frame):

    sbDefaultText="   Keys: 's' saves plot"

    def __init__(self,parent,id,title,dm):

        wx.Frame.__init__(self, parent, -1, title, size=poincareWindowSize)

        # wx.Frame.__init__(self, parent, -1, title)

        self.dm = dm

        self.HasTwoPlots=False
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)  
        
        self.WindowParent=parent

        sizer=wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)

        if not dm.HasVisibleEpisodes():
            self.ActiveTagLeft = "Global"


        if dm.HasVisibleEpisodes():

            # -------------- Begin of tags selector

            sbTags = wx.StaticBox(panel, label="Episodes")
            sbTagsSizer = wx.StaticBoxSizer(sbTags, wx.HORIZONTAL)

            self.AllTags = self.dm.GetVisibleEpisodes()[0]

            # tagsRB = []
            ChoicesLeft = self.GetChoicesLeft()
            self.ActiveTagLeft = ChoicesLeft[0]
            self.ActiveTagRight = "None"
            self.cbComboLeft=wx.ComboBox(panel,
                choices=ChoicesLeft,
                value=self.ActiveTagLeft,
                style=wx.CB_DROPDOWN|wx.CB_READONLY
                )
            sbTagsSizer.Add(self.cbComboLeft,flag=wx.ALL | wx.EXPAND, border=borderSmall)
            self.Bind(wx.EVT_COMBOBOX, self.OnComboLeft, id=self.cbComboLeft.GetId())
            

            sbTagsSizer.AddStretchSpacer(prop=1)

            ChoicesRight=self.GetChoicesRight()

            # ChoicesRight = ["None"]+self.AllTags
            # ChoicesRight.remove(self.ActiveTagLeft)

            self.cbComboRight=wx.ComboBox(panel,
                choices=ChoicesRight, 
                value=self.ActiveTagRight, 
                style=wx.CB_DROPDOWN|wx.CB_READONLY
                )
            sbTagsSizer.Add(self.cbComboRight,flag=wx.ALL | wx.EXPAND, border=borderSmall)
            self.Bind(wx.EVT_COMBOBOX, self.OnComboRight, id=self.cbComboRight.GetId())


            sizer.Add(sbTagsSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)

            # -------------- End of tags selector





        # -------------- Begin of figure

        self.fig = matplotlib.figure.Figure((5.0, 5.0),facecolor=PoincareBGColor)
        # self.fig.subplots_adjust(left=0.05, bottom=0.18, right=0.98, top=0.92, wspace=0.20, hspace=0.15)
        self.canvas = FigureCanvas(panel, -1, self.fig)
        
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

        # -------------- End of figure

        # # -------------- Begin of buttons

        hbox = wx.BoxSizer(wx.HORIZONTAL)   

        self.textOutput = wx.TextCtrl(panel, id, 'Information', size=(400, 50), style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2)
        self.textOutput.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL));
        hbox.Add(self.textOutput, 1, wx.LEFT | wx.TOP | wx.GROW)

        # hbox.AddStretchSpacer(prop=1)

        endButton = wx.Button(panel, -1, "Close", size=buttonSizeSignif)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=endButton.GetId())
        endButton.SetToolTip(wx.ToolTip("Click to close window"))
        hbox.Add(endButton, 0, border=borderBig, flag=wx.LEFT | wx.ALIGN_BOTTOM)
                
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
                automaticExtensions = automaticExtensionsLinMac
            else:
                filetypes = fileTypesWin
                extensions= extensionsWin
                automaticExtensions = automaticExtensionsWin
                
            dial = wx.FileDialog(self, message="Save figure as...", defaultFile=self.dm.GetName()+"_PP", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=filetypes)
            result = dial.ShowModal()
            if result == wx.ID_OK:
                fileName=dial.GetPath()
                fileExt = os.path.splitext(fileName)[1][1:].strip()
                if fileExt not in extensions:
                    fileName = fileName + "." + automaticExtensions[dial.GetFilterIndex()]
                    # print "Saving ",fileName
                try:
                    self.canvas.print_figure(fileName)
                except:
                    self.ErrorWindow(messageStr="Error saving figure to file: "+fileName,captionStr="Error saving figure    ")
            dial.Destroy()

        self.canvas.SetFocus()

        event.Skip()


    def OnComboLeft(self,event):
        self.ActiveTagLeft = self.cbComboLeft.GetValue()
        self.cbComboRight.Clear()
        ch = self.GetChoicesRight()
        for item in ch:
            self.cbComboRight.Append(item)
        self.Refresh()

    def GetChoicesLeft(self):
        Choices = ["Global"]
        for Tag in self.AllTags:
            Choices += [Tag]
            Choices += ["Outside "+Tag]
        return Choices

    def GetChoicesRight(self):
        Choices = ["None"]
        for Tag in self.AllTags:
            Choices += [Tag]
            Choices += ["Outside "+Tag]
        if self.ActiveTagLeft != "Global":
            Choices.remove(self.ActiveTagLeft)
        return Choices

    def OnComboRight(self,event):
        self.ActiveTagRight = self.cbComboRight.GetValue()
        if self.ActiveTagRight=="None":
            self.HasTwoPlots=False
        else:
            self.HasTwoPlots=True
        self.Refresh()
        

    def OnEnd(self,event):
        self.WindowParent.OnPoincareEnded()
        self.Destroy()


    def Refresh(self):

        


        def RefreshSubplot(axes, xdata, ydata, titlestr=None, pos="left"):

            if pos=="left":
                color=".r"
            else:
                color=".c"

            meanx=np.mean(xdata)
            meany=np.mean(ydata)

            sd1 = np.std((xdata-ydata)/np.sqrt(2.0),ddof=1)
            sd2 = np.std((xdata+ydata)/np.sqrt(2.0),ddof=1)

            cad =""

            if self.HasTwoPlots:
                cad += " "+titlestr+" - "
                cad += "SD1: %.2f ms. - SD2: %.2f ms." % (sd1,sd2)
                if pos=="left":
                    cad += "\n"
            else:
                cad += " SD1: %.2f ms. - SD2: %.2f ms." % (sd1,sd2)
            

            from matplotlib.patches import Ellipse

            axes.plot(xdata,ydata,color)

            coordarrow1 =np.sqrt(sd2*sd2/2)
            coordarrow2 =np.sqrt(sd1*sd1/2)

            axes.arrow(meanx,meany,coordarrow1,coordarrow1,
                lw=1, head_width=(maxcoord-mincoord)/100,
                head_length=(maxcoord-mincoord)/50,
                length_includes_head=True, fc='k', zorder=3)

            axes.arrow(meanx, meany, -coordarrow2, coordarrow2,
                lw=1, head_width=(maxcoord-mincoord)/100,
                head_length=(maxcoord-mincoord)/50,
                length_includes_head=True, fc='k', zorder=4)

            axes.set_xlim(mincoord,maxcoord)
            axes.set_ylim(mincoord,maxcoord)
            axes.set_xlabel("$RR_i (msec.)$")
            if pos=="left":
                axes.set_ylabel("$RR_{i+1} (msec.)$")

            if not self.HasTwoPlots:
                if self.ActiveTagLeft=="Global":
                    axes.set_title(self.dm.GetPoincarePlotTitle())
                else:
                    axes.set_title(self.ActiveTagLeft)

            else:
                axes.set_title(titlestr)
                self.fig.suptitle(self.dm.GetPoincarePlotTitle())

            

            if self.dm.data["Verbose"]==True:
                if titlestr:
                    print ("** Creating Poincare Plot  -  " + titlestr)
                else:
                    print ("** Creating Poincare Plot")
                print("   SD1: {0:.3f}".format(sd1))
                print("   SD2: {0:.3f}".format(sd2))
        
            ell=Ellipse(xy=(meanx,meany),width=2*sd1,height=2*sd2,angle=-45,linewidth=1, color='k', fc="none")
            axes.add_artist(ell)
            # ell.set_alpha(0.7)
            ell.set(zorder=2)

            axes.grid(True)

            return cad


        self.fig.clear()

        cad =""

        if not self.HasTwoPlots:
            axes = self.fig.add_subplot(111, aspect='equal')
            xvector,yvector = self.dm.GetPoincareDataPlot(tag=self.ActiveTagLeft)
            maxval=max(max(xvector),max(yvector))
            minval=min(min(xvector),min(yvector))
        else:
            axes1 = self.fig.add_subplot(121, aspect='equal')
            axes2 = self.fig.add_subplot(122, aspect='equal')
            xvector1,yvector1 = self.dm.GetPoincareDataPlot(tag=self.ActiveTagLeft)
            xvector2,yvector2 = self.dm.GetPoincareDataPlot(tag=self.ActiveTagRight)
            minval=min(min(xvector1),min(yvector1),min(xvector2),min(yvector2))
            maxval=max(max(xvector1),max(yvector1),max(xvector2),max(yvector2))


        
        maxplot=maxval*1.05
        maxcoord=maxval*1.1

        minplot=minval*0.95
        mincoord=minval*0.9


        if not self.HasTwoPlots:
            cad += RefreshSubplot(axes, xvector, yvector)
        else:
            cad +=RefreshSubplot(axes1, xvector1, yvector1, titlestr=self.ActiveTagLeft)
            cad +=RefreshSubplot(axes2, xvector2, yvector2, titlestr=self.ActiveTagRight, pos="right")

        self.textOutput.SetValue(cad)
  
        self.canvas.draw()



    
