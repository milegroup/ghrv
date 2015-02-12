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
import numpy as np
import os
from sys import platform



class SignificanceWindow(wx.Frame):
    """Window for significance analysis"""

    sbSignifText="  Keys: 'i'/'m' increase/lower no. of bins, '0' resets, 's' saves plot"

    def __init__(self,parent,id,title,dm):
        wx.Frame.__init__(self, parent, -1, title, size=signifWindowSize)
        
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)

        self.signifNumBins=signifNumBins
        self.dm = dm
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)  
        
        self.WindowParent=parent
        sizer=wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)

        # -------------- Begin of parameter selector

        sbParam = wx.StaticBox(panel, label="Parameter")
        sbParamSizer = wx.StaticBoxSizer(sbParam, wx.VERTICAL)
        sbParamSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sbParamSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        AllBandsOrig = self.dm.GetVisibleBands()[0]
        AllBands=list(AllBandsOrig)
        AllBands.remove("Heart rate")

        bandsRB=[]

        for band in AllBands:
            if len(bandsRB)==0:
                tmp = wx.RadioButton(panel, label=band, style=wx.RB_GROUP)
                tmp.SetValue(True)
            else:
                tmp = wx.RadioButton(panel, label=band)
            bandsRB.append(tmp)
            if len(bandsRB)<=6:
                sbParamSizer1.Add(tmp, wx.EXPAND) 
            else:      
                sbParamSizer2.Add(tmp, wx.EXPAND) 
        
        sbParamSizer.Add(sbParamSizer1,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        sbParamSizer.Add(sbParamSizer2,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        sizer.Add(sbParamSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)

        for eachRB in bandsRB:
            self.Bind(wx.EVT_RADIOBUTTON,self.OnParam,eachRB)

        self.ActiveParam = AllBands[0]

        # -------------- End of parameter selector



        # -------------- Begin of tags selector

        sbTags = wx.StaticBox(panel, label="Episodes")
        sbTagsSizer = wx.StaticBoxSizer(sbTags, wx.HORIZONTAL)

        # tagsRB = []
        self.AllTags = self.dm.GetVisibleEpisodes()[0]
        self.ActiveTagLeft = self.AllTags[0]
        self.ActiveTagRight = None
        self.dm.SetSignifPlotParams(self.ActiveTagLeft,self.ActiveTagRight,self.ActiveParam)
        
        self.cbComboLeft=wx.ComboBox(panel,
            choices=self.AllTags,
            value=self.ActiveTagLeft,
            style=wx.CB_DROPDOWN|wx.CB_READONLY
            )
        sbTagsSizer.Add(self.cbComboLeft,flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.Bind(wx.EVT_COMBOBOX, self.OnComboLeft, id=self.cbComboLeft.GetId())
        

        sbTagsSizer.AddStretchSpacer(prop=1)

        ChoicesRight = ["Outside "+self.ActiveTagLeft]+self.AllTags
        ChoicesRight.remove(self.ActiveTagLeft)

        self.cbComboRight=wx.ComboBox(panel,
            choices=ChoicesRight, 
            value="Outside "+self.ActiveTagLeft, 
            style=wx.CB_DROPDOWN|wx.CB_READONLY
            )
        sbTagsSizer.Add(self.cbComboRight,flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.Bind(wx.EVT_COMBOBOX, self.OnComboRight, id=self.cbComboRight.GetId())


        sizer.Add(sbTagsSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)

        # -------------- End of tags selector


        # -------------- Begin of figure
        if ColoredBGPlots:
            self.fig = matplotlib.figure.Figure((5.0, 4.0),facecolor=SignifBGColor)
        else:
            self.fig = matplotlib.figure.Figure((5.0, 4.0))
            
        self.fig.subplots_adjust(left=0.05, bottom=0.18, right=0.98, top=0.92, wspace=0.20, hspace=0.15)
        self.canvas = FigureCanvas(panel, -1, self.fig)
        
        self.axes = self.fig.add_subplot(111)

        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

        # -------------- End of figure

        # -------------- Begin of textbox and buttons

        hbox = wx.BoxSizer(wx.HORIZONTAL)   


        self.textOutput = wx.TextCtrl(panel, id, 'Information', size=(400, 75), style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2)
        self.textOutput.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL));
        hbox.Add(self.textOutput, 1, wx.LEFT | wx.TOP | wx.GROW)

        endButton = wx.Button(panel, -1, "Close", size=buttonSizeSignif)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=endButton.GetId())
        endButton.SetToolTip(wx.ToolTip("Click to close window"))
        hbox.Add(endButton, 0, border=borderBig, flag=wx.LEFT|wx.ALIGN_BOTTOM)
                
        sizer.Add(hbox, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)

        # -------------- End of textbox and buttons

        panel.SetSizer(sizer)

        self.SetMinSize(signifWindowMinSize)

#        self.sb = self.CreateStatusBar()
#        self.sb.SetStatusText(self.sbSignifText)

#        self.canvas.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)

        self.Show(True)
        self.Layout()
        self.Refresh()



    def ErrorWindow(self,messageStr,captionStr="ERROR"):
        """Generic error window"""
        dial = wx.MessageDialog(self, caption=captionStr, message=messageStr, style=wx.OK | wx.ICON_ERROR)
        result = dial.ShowModal()
        dial.Destroy()
        self.canvas.SetFocus()

    def OnEnd(self,event):
        self.WindowParent.OnSignifEnded()
        self.Destroy()

    def OnParam(self,event):
        (ATL,ATR,AP) = self.dm.GetSignifPlotParams()
        self.ActiveParam = event.GetEventObject().GetLabel()
        self.dm.SetSignifPlotParams(ATL,ATR,self.ActiveParam)
        self.Refresh()

    def OnComboLeft(self,event):
        (ATL,ATR,AP) = self.dm.GetSignifPlotParams()
        self.ActiveTagLeft = self.cbComboLeft.GetValue()
        self.cbComboRight.Clear()
        ChoicesRight = ["Outside "+self.ActiveTagLeft]+self.AllTags
        ChoicesRight.remove(self.ActiveTagLeft)
        for item in ChoicesRight:
            self.cbComboRight.Append(item)
        self.cbComboRight.SetValue("Outside "+self.ActiveTagLeft)
        self.ActiveTagRight = None
        self.dm.SetSignifPlotParams(self.ActiveTagLeft,self.ActiveTagRight,AP)
        self.Refresh()

    def OnComboRight(self,event):
        (ATL,ATR,AP) = self.dm.GetSignifPlotParams()
        self.ActiveTagRight = self.cbComboRight.GetValue()
        if self.ActiveTagRight[0:7] == "Outside":
            self.ActiveTagRight=None
        self.dm.SetSignifPlotParams(ATL,self.ActiveTagRight,AP)
        self.Refresh()
        
        
    def Refresh(self):
        valuesLeft,valuesRight = self.dm.CreatePlotSignifEmbedded(self.fig)
        numValuesLeft=len(valuesLeft)
        numValuesRight=len(valuesRight)

        cad = ""
        if self.ActiveTagRight:
            cad = cad + "%s: %s (%d points) vs. %s  (%d points)\n" % (self.ActiveParam, self.ActiveTagLeft, numValuesLeft, self.ActiveTagRight, numValuesRight)
        else: 
            cad = cad + "%s: %s  -  inside (%d points) vs. outside  (%d points)\n" % (self.ActiveParam, self.ActiveTagLeft, numValuesLeft, numValuesRight)

        if (numValuesLeft>signifNumMinValues) and (numValuesRight>signifNumMinValues):
            if self.ActiveTagRight:
                cad=cad+ u"%s: %g\u00b1%g, %s: %g\u00b1%g\n" % (self.ActiveTagLeft,np.mean(valuesLeft),np.std(valuesLeft,ddof=1),self.ActiveTagRight,np.mean(valuesRight),np.std(valuesRight,ddof=1))
            else:
                cad=cad+ u"Inside: %g\u00b1%g, Outside: %g\u00b1%g\n" % (np.mean(valuesLeft),np.std(valuesLeft,ddof=1),np.mean(valuesRight),np.std(valuesRight,ddof=1))

            # from scipy.stats import normaltest   
            # z,pval = normaltest(valuesLeft)
            # if(pval < 0.055):
            #     print self.ActiveTagLeft, "- not normal distribution"
            # else:
            #     print self.ActiveTagLeft, "- Ok!"
            # z,pval = normaltest(valuesRight)
            # if(pval < 0.055):
            #     print self.ActiveTagRight, "- not normal distribution"
            # else:
            #     print self.ActiveTagRight, "- Ok!"

            from scipy.stats import ks_2samp

            pvalue = ks_2samp(valuesLeft,valuesRight)[1]

            cad=cad+ "KS test: "
            if pvalue<signifPMaxValue:
                cad=cad+ "significative differences found!!" 
                cad=cad+"  (p-value=%g < %g)" % (pvalue, signifPMaxValue)
            else:
                cad=cad+ "significative differences not found"
                cad=cad+"  (p-value=%g >= %g)" % (pvalue, signifPMaxValue)
            
#            
        else:
            cad=cad+"Not enough data: minimum no. of points is "+str(signifNumMinValues)
#            
        self.textOutput.SetValue(cad)
        self.canvas.draw()

