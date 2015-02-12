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
from sys import platform
from configvalues import *

class AboutDlg(wx.Frame):
    """About box"""
    
    import wx.html
 
    def __init__(self, parent, id):
        
        if platform != 'darwin':
            wx.Frame.__init__(self, parent, size=aboutWindowSize)
        else:
            wx.Frame.__init__(self, parent, size=aboutWindowSizeMac)
            
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
        
        self.WindowParent=parent
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        panel = wx.Panel(self)

        if platform != "win32": 
            self.SetWindowStyle(wx.STAY_ON_TOP)
        else:
            self.ToggleWindowStyle(wx.STAY_ON_TOP)

        self.SetTitle("About gHRV")

        vbox = wx.BoxSizer(wx.VERTICAL)
        
        PageStr = """<center>
            <p><img src="LogoSmall.png"/></p>
            <h3>gHRV %s</h3>
            <p><b>gHRV: a graphical application for Heart Rate Variability analysis</b></p>
            <p>Copyright (C) 2015  Milegroup - Dpt. Informatics - University of Vigo - Spain</p>
            <p><i>http://www.milegroup.net</i></p>
            </center>
            <hr/>
            <p><b>Authors:</b></p>
            <ul>
            <li>Leandro Rodr&iacute;guez-Li&ntilde;ares</li>
            <li>Arturo M&eacute;ndez</li>
            <li>Mar&iacute;a Jos&eacute; Lado</li>
            <li>Xos&eacute; Ant&oacute;n Vila</li>
            </ul>
            <hr/>
            <p> This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.</p>
            <p>This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details (http://www.gnu.org/licenses/).</p>""" % Version

        html=wx.html.HtmlWindow(panel, id)
        html.SetPage(PageStr)
        
        vbox.Add(html, 1, wx.LEFT | wx.TOP | wx.GROW)

        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.AddStretchSpacer(prop=1)

        self.endButton = wx.Button(panel, -1, "Close", size=buttonSizeAbout)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=self.endButton.GetId())
        self.endButton.SetToolTip(wx.ToolTip("Click to close window"))
        hbox.Add(self.endButton, 0, border=borderSmall, flag=wx.RIGHT)
                
        vbox.Add(hbox, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)

        panel.SetSizer(vbox)

        self.Show()
        self.CentreOnParent()
        
    def OnEnd(self,event):
        self.WindowParent.OnAboutEnded()
        self.Destroy()





        
