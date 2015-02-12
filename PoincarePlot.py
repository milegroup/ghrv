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
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from DataModel import DM
import Utils
import numpy as np
import os
from sys import platform
from matplotlib.widgets import Button


class PoincarePlotWindow(wx.Frame):

#     sbDefaultText="   Keys: 's' saves plot"

    def __init__(self,parent,id,title,dm):

        wx.Frame.__init__(self, parent, -1, title, size=poincareWindowSize)
        
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)

        # wx.Frame.__init__(self, parent, -1, title)

        self.dm = dm

        self.HasTwoPlots=False
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)  
        
        self.WindowParent=parent

        sizer=wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)

        if not self.dm.HasVisibleEpisodes():
            self.dm.SetPoincarePlotTagLeft("Global")


        if self.dm.HasVisibleEpisodes():

            # -------------- Begin of tags selector

            sbTags = wx.StaticBox(panel, label="Episodes")
            sbTagsSizer = wx.StaticBoxSizer(sbTags, wx.HORIZONTAL)

            self.AllTags = self.dm.GetVisibleEpisodes()[0]

            # tagsRB = []
            ChoicesLeft = self.GetChoicesLeft()
            self.dm.SetPoincarePlotTagLeft(ChoicesLeft[0])
            self.dm.SetPoincarePlotTagRight("None")
            self.cbComboLeft=wx.ComboBox(panel,
                choices=ChoicesLeft,
                value=self.dm.GetPoincarePlotTagLeft(),
                style=wx.CB_DROPDOWN|wx.CB_READONLY
                )
            sbTagsSizer.Add(self.cbComboLeft,flag=wx.ALL | wx.EXPAND, border=borderSmall)
            self.Bind(wx.EVT_COMBOBOX, self.OnComboLeft, id=self.cbComboLeft.GetId())
            

            sbTagsSizer.AddStretchSpacer(prop=1)

            ChoicesRight=self.GetChoicesRight()

            self.cbComboRight=wx.ComboBox(panel,
                choices=ChoicesRight, 
                value=self.dm.GetPoincarePlotTagRight(), 
                style=wx.CB_DROPDOWN|wx.CB_READONLY
                )
            sbTagsSizer.Add(self.cbComboRight,flag=wx.ALL | wx.EXPAND, border=borderSmall)
            self.Bind(wx.EVT_COMBOBOX, self.OnComboRight, id=self.cbComboRight.GetId())


            sizer.Add(sbTagsSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)

            # -------------- End of tags selector





        # -------------- Begin of figure


        if ColoredBGPlots:
            self.fig = matplotlib.figure.Figure((5.0, 5.0),facecolor=PoincareBGColor)
        else:
            self.fig = matplotlib.figure.Figure((5.0, 5.0))
            
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

        self.Show(True)
        self.Layout()
        self.Refresh()
        
        self.canvas.draw()


    def OnComboLeft(self,event):
        self.dm.SetPoincarePlotTagLeft(self.cbComboLeft.GetValue())
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
        if self.dm.GetPoincarePlotTagLeft() != "Global":
            Choices.remove(self.dm.GetPoincarePlotTagLeft())
        return Choices

    def OnComboRight(self,event):
        self.dm.SetPoincarePlotTagRight(self.cbComboRight.GetValue())
        if self.dm.GetPoincarePlotTagRight()=="None":
            self.HasTwoPlots=False
        else:
            self.HasTwoPlots=True
        self.Refresh()
        

    def OnEnd(self,event):
        self.WindowParent.OnPoincareEnded()
        self.Destroy()
        
    def Refresh(self):
        cad = self.dm.CreatePlotPoincareEmbedded(self.fig,parentWindow=self)
        self.textOutput.SetValue(cad)
        self.canvas.draw()


    
