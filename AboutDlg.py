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
from sys import platform
from configvalues import *

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
        self.panel = wx.Panel(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        
        
        html=wx.html.HtmlWindow(self.panel, id)
        html.SetPage(
            '<p align="center"><img src="LogoSmall.png"/></p>'
            '<h3 align="center">gHRV 0.21</h3>'
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
        
        self.vbox.Add(html, 1, wx.LEFT | wx.TOP | wx.GROW)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)   
        self.hbox.AddStretchSpacer(prop=1)

        self.endButton = wx.Button(self.panel, -1, "Close", size=buttonSizeAbout)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=self.endButton.GetId())
        self.endButton.SetToolTip(wx.ToolTip("Click to close window"))
        self.hbox.Add(self.endButton, 0, border=borderSmall, flag=wx.RIGHT)
                
        self.vbox.Add(self.hbox, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)

        self.panel.SetSizer(self.vbox)

        self.Show()
        self.Layout()
        #self.Centre()
        
        
    def OnEnd(self,event):
        self.WindowParent.OnAboutEnded()
        self.Destroy()
        