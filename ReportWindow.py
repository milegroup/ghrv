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
        