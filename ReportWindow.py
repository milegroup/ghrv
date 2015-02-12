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
from sys import platform

class ReportWindow(wx.Frame):  
    """ Window for Report"""
    
    import wx.html
    
    def __init__(self,parent,id,title,filename, dm):

        self.dm = dm
        self.fileNameTmp=filename
        
        wx.Frame.__init__(self, parent, -1, title, size=reportWindowSize)
        
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
                
        self.panel = wx.Panel(self)
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        self.WindowParent=parent

        vbox = wx.BoxSizer(wx.VERTICAL)
        

        htmlwin = wx.html.HtmlWindow(self.panel, -1, style=wx.NO_BORDER)
        #htmlwin.SetBackgroundColour(wx.RED)
        htmlwin.SetStandardFonts()
        htmlwin.LoadFile(self.fileNameTmp)

        vbox.Add(htmlwin, 1, wx.LEFT | wx.TOP | wx.GROW)
        
        
        
        # Box sizer for buttons
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.saveButton = wx.Button(self.panel, -1, "Save as HTML...", size=buttonSizeReportWindow)
        self.Bind(wx.EVT_BUTTON, self.OnSave, id=self.saveButton.GetId())
        self.saveButton.SetToolTip(wx.ToolTip("Click to generate html report"))
        hbox.Add(self.saveButton, 0, border=borderSmall, flag=wx.ALIGN_LEFT | wx.ALL)

        self.browserButton = wx.Button(self.panel, -1, "Open in browser", size=buttonSizeReportWindow)
        self.Bind(wx.EVT_BUTTON, self.OnBrowser, id=self.browserButton.GetId())
        self.browserButton.SetToolTip(wx.ToolTip("Click to open report in system's browser"))
        hbox.Add(self.browserButton, 0, border=borderSmall, flag=wx.ALIGN_LEFT | wx.ALL)
        
        hbox.AddStretchSpacer(1)
        
        self.endButton = wx.Button(self.panel, -1, "End", size=buttonSizeReportWindow)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=self.endButton.GetId())
        self.endButton.SetToolTip(wx.ToolTip("Click to close window"))
        
        hbox.Add(self.endButton, 0, border=borderSmall, flag=wx.ALIGN_RIGHT | wx.ALL)

        vbox.Add(hbox, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)

        self.panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)
        
       
        self.SetMinSize(reportWindowMinSize)
        
    def OnEnd(self,event):
        self.WindowParent.OnReportEnded()
        self.Destroy()
        
    def OnSave(self,event):
        import os,shutil
        correctSaving=False
        filetypes = "HTML files (*.html, *.htm)|*.html;*.htm;*.HTML;*.HTM|" "All files (*.*)|*.*"
        fileName=""
        dial = wx.FileDialog(self, message="Save project as...",
            wildcard = filetypes, defaultFile=self.dm.GetName()+".html", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dial.ShowModal()
        if result == wx.ID_OK:
            fileName=dial.GetPath()
            fileExt = os.path.splitext(fileName)[1][1:].strip()      
            fileCanonicalName=os.path.splitext(fileName)[0].split(os.sep)[-1]
            filePath = os.path.split(fileName)[0]
            subDirImgs= fileCanonicalName+'_imgs'

            if os.path.exists(filePath+os.sep+subDirImgs):
                shutil.rmtree(filePath+os.sep+subDirImgs)

            # print "Filename: ",fileName
            # print "File extension: ",fileExt
            # print "Canonical filename: ",fileCanonicalName
            # print "File path: ", filePath

            try:
                self.dm.CreateReport(filePath,fileCanonicalName+".html",subDirImgs)
            except UnicodeEncodeError:
                    self.ErrorWindow(messageStr="Ilegal characters in filename: "+fileName,
                                     captionStr="Error saving report")
            except:
                self.ErrorWindow(messageStr="Error saving report to file: "+fileName,captionStr="Error saving report")    

            else:
                correctSaving = True 
        dial.Destroy()

        if correctSaving == True:
            dial = wx.MessageDialog(self, "Report saved:\n"+fileName, "Report created ok", wx.OK)
            result = dial.ShowModal()
            dial.Destroy()

    def OnBrowser(self,event):
        import webbrowser
        # print "I'm going to open: ", self.fileNameTmp
        webbrowser.open(self.fileNameTmp)

    def ErrorWindow(self,messageStr,captionStr="ERROR"):
        """Generic error window"""
        dial = wx.MessageDialog(self, caption=captionStr, message=messageStr, style=wx.OK | wx.ICON_ERROR)
        result = dial.ShowModal()
        dial.Destroy()
        
