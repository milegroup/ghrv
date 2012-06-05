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
import os
from sys import platform
import numpy as np


class FrameBasedEvolutionWindow(wx.Frame):  
    """ Window for temporal evolution of parameters obtained from interpolated HR"""
    
    sbDefaultText="  Keys: 'i'/'m' zoom in/out, 'j'/'k' pan left/right, '0' resets, 's' saves plot"
    
    def __init__(self,parent,id,title,dm):

        self.dm = dm
        
        wx.Frame.__init__(self, parent, -1, title, size=mainWindowSize)
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
                        
        self.panel = wx.Panel(self)
        self.WindowParent=parent
        
        self.fig = matplotlib.figure.Figure(facecolor=TemporalBGColor)
        self.canvas = FigureCanvas(self.panel, -1, self.fig)
                   
        self.mainBox = wx.BoxSizer(wx.HORIZONTAL)
        self.mainBox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        
        self.vboxRightArea = wx.BoxSizer(wx.VERTICAL)        
        
        self.AllBands, self.VisibleBands=self.dm.GetVisibleBands()
        self.insertBandsSelector()
        
        self.refreshButton = wx.Button(self.panel, -1, "Refresh")
        self.vboxRightArea.Add(self.refreshButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_LEFT)
        self.Bind(wx.EVT_BUTTON, self.onRefresh, self.refreshButton)
        
        self.vboxRightArea.AddStretchSpacer(prop=1)

        self.signifButton = wx.Button(self.panel, -1, "Significance...", size=buttonSizeFrameBased)
        self.Bind(wx.EVT_BUTTON, self.OnSignif, id=self.signifButton.GetId())
        self.signifButton.SetToolTip(wx.ToolTip("Click to perform significance analysis"))
        self.vboxRightArea.Add(self.signifButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)
        if platform != 'darwin':
            self.signifButton.SetBackgroundColour(SignifBGColor)
        
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
        
        self.dm.CreatePlotFBEmbedded(self.fig)
        self.canvas.draw()
        self.canvas.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
        
        self.SetMinSize(mainWindowMinSize)
        self.Show(True)
        self.Layout()
        self.canvas.SetFocus()
        
    def ErrorWindow(self,messageStr,captionStr="ERROR"):
        """Generic error window"""
        dial = wx.MessageDialog(self, caption=captionStr, message=messageStr, style=wx.OK | wx.ICON_ERROR)
        result = dial.ShowModal()
        dial.Destroy()
        self.canvas.SetFocus()
        
    def OnKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == 73:
            self.dm.PlotFBZoomIn()
            self.canvas.draw()
        if keycode == 77:
            self.dm.PlotFBZoomOut()
            self.canvas.draw()
        if keycode == 48:
            self.dm.PlotFBZoomReset()
            self.canvas.draw()
        if keycode == 75:
            self.dm.PlotFBPanRight()
            self.canvas.draw()
        if keycode == 74:
            self.dm.PlotFBPanLeft()
            self.canvas.draw()
        if keycode==83:
            fileName=""
            if platform != "win32":
                filetypes = fileTypesLinMac
                extensions= extensionsLinMac
            else:
                filetypes = fileTypesWin
                extensions= extensionsWin
            dial = wx.FileDialog(self, message="Save figure as...", defaultFile=self.dm.GetName()+"_FB", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=filetypes)
            result = dial.ShowModal()
            if result == wx.ID_OK:
                fileName=dial.GetPath()
                fileExt = os.path.splitext(fileName)[1][1:].strip()
                if fileExt=="":
                    self.ErrorWindow(messageStr="Filename extension missing ",captionStr="Error saving figure    ")
                elif fileExt not in extensions:
                    self.ErrorWindow(messageStr="Filetype not supported: "+fileExt,captionStr="Error saving figure    ")
                else:
                    try:
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
        
        self.dm.SetVisibleBands(checkedBands)
        
        self.dm.CreatePlotFBEmbedded(self.fig)
        self.canvas.draw()


    def Refresh(self):
        self.dm.CreatePlotFBEmbedded(self.fig)
        self.canvas.draw()
    
        
    def OnEnd(self,event):
        self.WindowParent.OnFrameBasedEnded()
        self.Destroy()
        
    def OnExport(self,event):
        exportSettingsWindow=FrameBasedExportSettings(self,-1,"Export options", self.dm)
        self.exportButton.Disable()
        
    def OnExportEnded(self):
        self.exportButton.Enable()

    def OnSignif(self,event):
        if not self.dm.DataPlotHasVisibleEpisodes():
            self.ErrorWindow(messageStr="No visible episodes present",captionStr="Error in significance analysis")
        else:
            SignificanceWindow(self,-1,'Significance analysis',self.dm)
            self.signifButton.Disable()
        # exportSettingsWindow=FrameBasedExportSettings(self,-1,"Export options", self.dm)
        # self.exportButton.Disable()
    def OnSignifEnded(self):
        self.signifButton.Enable()
        

class SignificanceWindow(wx.Frame):
    """Window for significance analysis"""

    def __init__(self,parent,id,title,dm):
        wx.Frame.__init__(self, parent, -1, title, size=signifWindowSize)

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
            if len(bandsRB)<=5:
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

        sbTags = wx.StaticBox(panel, label="Episodes tags")
        sbTagsSizer = wx.StaticBoxSizer(sbTags, wx.HORIZONTAL)

        tagsRB = []
        AllTags = self.dm.GetVisibleEpisodes()[0]
        for tag in AllTags:
            if len(tagsRB)==0:
                tmp = wx.RadioButton(panel, label=tag, style=wx.RB_GROUP)
                tmp.SetValue(True)
            else:
                tmp = wx.RadioButton(panel, label=tag)
            tagsRB.append(tmp)
            sbTagsSizer.Add(tmp,wx.EXPAND)

            # if len(bandsRB)<=5:
            #     sbParamSizer1.Add(tmp, wx.EXPAND) 
            # else:       
            #     sbParamSizer2.Add(tmp, wx.EXPAND) 
        

        sizer.Add(sbTagsSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)

        for eachRB in tagsRB:
            self.Bind(wx.EVT_RADIOBUTTON,self.OnTag,eachRB)

        self.ActiveTag = AllTags[0]
        
        # -------------- End of tags selector


        # -------------- Begin of figure

        self.fig = matplotlib.figure.Figure((5.0, 4.0),facecolor=SignifBGColor)
        self.fig.subplots_adjust(left=0.05, bottom=0.07, right=0.98, top=0.92, wspace=0.20, hspace=0.15)
        self.canvas = FigureCanvas(panel, -1, self.fig)
        
        self.axes = self.fig.add_subplot(111)

        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

        # -------------- End of figure

        # -------------- Begin of textbox and buttons

        hbox = wx.BoxSizer(wx.HORIZONTAL)   


        self.textOutput = wx.TextCtrl(panel, id, 'Information', size=(350, 75), style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2)
        self.textOutput.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL));
        hbox.Add(self.textOutput, 1, wx.LEFT | wx.TOP | wx.GROW)

        hbox.AddStretchSpacer(prop=1)

        endButton = wx.Button(panel, -1, "Close", size=buttonSizeSignif)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=endButton.GetId())
        endButton.SetToolTip(wx.ToolTip("Click to close window"))
        hbox.Add(endButton, 0, border=borderSmall, flag=wx.RIGHT)
                
        sizer.Add(hbox, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)

        # -------------- End of textbox and buttons

        panel.SetSizer(sizer)

        self.SetMinSize(signifWindowMinSize)
        self.Show(True)
        self.Layout()
        self.Refresh()

    def OnEnd(self,event):
        self.WindowParent.OnSignifEnded()
        self.Destroy()

    def OnParam(self,event):
        self.ActiveParam = event.GetEventObject().GetLabel()
        self.Refresh()

    def OnTag(self,event):
        self.ActiveTag = event.GetEventObject().GetLabel()
        self.Refresh()

    def Refresh(self):
        # print "Param: ",self.ActiveParam
        # print "Tag: ",self.ActiveTag
        cad ="Parameter: "+self.ActiveParam+"   -   "+"Tag: "+self.ActiveTag
        ActiveParamTmp = self.ActiveParam
        if ActiveParamTmp=="LF/HF":
            ActiveParamTmp="LFHF"
        total,inside,outside = self.dm.GetFrameBasedData(ActiveParamTmp,self.ActiveTag)
        cad=cad+"\n"+str(len(total))+" points (in: "+str(len(inside))+", out: "+str(len(outside))+")"
        # print "Length total: ",len(total)
        # print "Length inside: ",len(inside)
        # print "Length outside: ",len(outside)




        totalweight=np.ones_like(total)/len(total)
        insideweight=np.ones_like(inside)/len(inside)
        outsideweight=np.ones_like(outside)/len(outside)

        self.axes.clear()

        # self.axes.hist([total,inside,outside], 10, 
        #                 weights = [totalweight,insideweight,outsideweight],
        #                 normed=False, histtype='bar',
        #                 color=['orange', 'cyan', 'red'],
        #                 label=['Global', 'Inside '+self.ActiveTag, 'Outside '+self.ActiveTag])

        if (len(inside)>signifNumMinValues) and (len(outside)>signifNumMinValues):
            self.axes.hist([inside,outside], signifNumBins, 
                            weights = [insideweight,outsideweight],
                            normed=False, histtype='bar',
                            color=['red', 'cyan'],
                            label=['Inside '+self.ActiveTag, 'Outside '+self.ActiveTag])
            # self.axes.set_xlabel("Time (sec.)")
            # self.axes.set_ylabel("HR (beats/min.)")
            self.axes.set_title('Histogram: '+self.ActiveParam)

            self.axes.legend()
            self.axes.grid()
            cad=cad+ "\nMean  -  in: %.3f, out: %.3f" % (np.mean(inside),np.mean(outside))
            from scipy.stats import ttest_ind
            pvalue=ttest_ind(inside,outside)[1]
            cad=cad+ "\np-value: %.3g" % pvalue
        else:
            cad=cad+" - Insufficient data"
            self.axes.set_xlim(-1,1)
            self.axes.set_ylim(-1,1)
            self.axes.text(0.0, 0.0, "Insufficient data", size=20,
                            horizontalalignment='center',
                            verticalalignment='center',
                            bbox=dict(boxstyle='round',facecolor='red', alpha=0.5))
            
            
        self.textOutput.SetValue(cad)
        self.canvas.draw()



class FrameBasedExportSettings(wx.Frame):
    
    """Export options for frame-based parameters"""
    
    def __init__(self, parent, id, title, dm):

        self.dm = dm
        
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
        
        AllBandsOrig,VisibleBandsOrig = self.dm.GetVisibleBands()
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
                    
        dial = wx.FileDialog(self, message="Save data as...", defaultFile=self.dm.GetName()+".txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dial.ShowModal()
        if result == wx.ID_OK:
            
                
            fileName=dial.GetPath()
            if result == wx.ID_OK:
                fileName=dial.GetPath()
                try:
                    self.dm.SaveFrameBasedData(fileName,listOfBands,SepChar,self.RowHeader.GetValue(),self.ColumnHeader.GetValue()) 
                except:
                    self.WindowParent.ErrorWindow(messageStr="Error saving data to file: "+fileName,captionStr="Error saving data file")
                    self.Raise()
        dial.Destroy()
        self.WindowParent.OnExportEnded()
        self.Destroy()
