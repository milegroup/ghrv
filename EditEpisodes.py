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
import wx.grid as gridlib

class EditEpisodesWindow(wx.Frame):
    
    """ Window for editing episodes"""
    NumClicks=0
    
    def __init__(self,parent,id,title,dm):
        wx.Frame.__init__(self, parent, -1, title, size=mainWindowSize)
        self.dm = dm
        self.manualEditorPresent=False
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        
        
        self.WindowParent=parent
        self.panel = wx.Panel(self)
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.fig = matplotlib.figure.Figure((5.0, 4.0),facecolor=EpisodesEditionBGColor)
        self.canvas = FigureCanvas(self.panel, -1, self.fig)
        self.canvas.mpl_connect('button_press_event', self.OnClick)
        
        self.axes = self.fig.add_subplot(111)
        self.xvector, self.yvector= self.dm.GetHRDataPlot()
        
        self.ymin=min(self.yvector)
        self.ymax=max(self.yvector)
        self.xmin=self.xvector[0]
        self.xmax=self.xvector[-1]
        
        
        self.hboxEditEpisodes = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxEditEpisodes.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

# ----------------- Begin of sizer for buttons in edit episodes
        
        self.vboxEditEpRightColumn = wx.BoxSizer(wx.VERTICAL)  
        
        self.EpTypes,self.EpVisibleTypes = self.dm.GetVisibleEpisodes()
        
        if len(self.EpTypes)>0:
            self.InsertTagsSelector()
            self.TagsSelectorPresent = True
        else:
            self.TagsSelectorPresent = False

        # Begin of AddEpisode staticbox
        
        sbAdd = wx.StaticBox(self.panel, label="Add")
        sbAddSizer = wx.StaticBoxSizer(sbAdd, wx.VERTICAL)
        
        if len(self.EpTypes)>0:
            InitValue=self.EpTypes[0]
        else:
            InitValue='NEW_TAG'
        self.cbCombo=wx.ComboBox(self.panel,choices=self.EpTypes, value=InitValue, style=wx.CB_DROPDOWN)
        sbAddSizer.Add(self.cbCombo,flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.cbCombo.Disable()
        
        
        self.addButton = wx.Button(self.panel, -1, "Add episode", size=buttonSizeEditEpisodes)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.addButton)
        sbAddSizer.Add(self.addButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)
        self.addButton.Disable()
        
        self.clearButton = wx.Button(self.panel, -1, "Clear", size=buttonSizeEditEpisodes)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clearButton)
        sbAddSizer.Add(self.clearButton, 0, border=borderSmall, flag=wx.RIGHT | wx.ALIGN_RIGHT)
        self.clearButton.Disable()
        
        self.vboxEditEpRightColumn.Add(sbAddSizer, flag=wx.ALL, border=borderSmall)
        
        # End of AddEpisode staticbox
        
        
        
        self.vboxEditEpRightColumn.AddStretchSpacer(prop=1)

        self.manualButton = wx.Button(self.panel, -1, "Manual...", size=buttonSizeEditEpisodes)
        self.Bind(wx.EVT_BUTTON, self.OnManual, id=self.manualButton.GetId())
        self.manualButton.SetToolTip(wx.ToolTip("Click to edit episodes manually"))
        self.vboxEditEpRightColumn.Add(self.manualButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)

        
        self.endButton = wx.Button(self.panel, -1, "End", size=buttonSizeEditEpisodes)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=self.endButton.GetId())
        self.endButton.SetToolTip(wx.ToolTip("Click to finish editing episodes"))
        self.vboxEditEpRightColumn.Add(self.endButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)
                
        self.hboxEditEpisodes.Add(self.vboxEditEpRightColumn, 0, flag=wx.EXPAND, border=borderBig)
        
# ----------------- End of sizer for buttons in edit episodes

        self.panel.SetSizer(self.hboxEditEpisodes)
        #self.hboxEditEpisodes.Fit(self)
        
        self.DrawFigure()
        
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText('')
        
        self.SetMinSize(mainWindowMinSize)
        self.Show(True)
        self.Layout()
        #self.Centre()
        
        
    def InsertTagsSelector(self):
        
        # Begin of select/unselect episodes checklist box
                
        sbEpisodes = wx.StaticBox(self.panel, label="Episodes")
        sbEpisodesSizer = wx.StaticBoxSizer(sbEpisodes, wx.VERTICAL)
        
        self.cbList = wx.CheckListBox(self.panel,choices=self.EpTypes)
        self.cbList.SetCheckedStrings(self.EpVisibleTypes)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnEpisodesList, self.cbList)
        sbEpisodesSizer.Add(self.cbList)
        
        self.vboxEditEpRightColumn.Insert(0,sbEpisodesSizer, flag=wx.ALL, border=borderSmall)
       
        
        # End of select/unselect episodes checklist box
        

    def DrawFigure(self):
        """ Redraws the figure
        """
        # clear the axes and DrawFigure the plot anew
        #
        self.axes.clear()        
        
        self.axes.plot(self.xvector,self.yvector,'k-')
        self.axes.set_xlabel("Time (sec.)")
        self.axes.set_ylabel("HR (beats/min.)")
        self.axes.set_title(self.dm.GetHeartRatePlotTitle())
        
        if self.dm.DataPlotHasVisibleEpisodes():
            tags,starts,durations,tagsVisible = self.dm.GetEpisodes()
            numEpisodes=len(tags)
#            print("Number: "+str(numEpisodes))
            i=0
            for tag in tagsVisible:
                startsvector=[starts[w] for w in range(numEpisodes) if tags[w]==tag]
                durationsvector=[durations[w] for w in range(numEpisodes) if tags[w]==tag]
                endsvector=[starts[w]+durations[w] for w in range(numEpisodes) if tags[w]==tag]
                for j in range(len(startsvector)):
                    if j==0:
                        self.axes.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=self.dm.GetEpisodeColor(tag), alpha=alphaMatplotlibTags, label=tag)
                    else:
                        self.axes.axvspan(startsvector[j], endsvector[j], ymin=0.04, ymax=0.96, facecolor=self.dm.GetEpisodeColor(tag), alpha=alphaMatplotlibTags)
                i=i+1
            leg=self.axes.legend(fancybox=True,shadow=True)
            for t in leg.get_texts():
                t.set_fontsize('small')
        
        self.axes.set_xlim(self.xmin,self.xmax) 
        self.axes.set_ylim(self.ymin-0.05*(self.ymax-self.ymin),self.ymax+0.05*(self.ymax-self.ymin))
        self.axes.grid()
        
        self.canvas.draw()
        
    def OnClick(self,event):

        if self.manualEditorPresent:
            return None
                
        if event.xdata==None:
            return None
        
        if event.button != 1:
            return None
        
        if self.NumClicks==0:
            self.cxleft=event.xdata
            self.axes.axvline(x=self.cxleft, ymin=0, ymax=1, linewidth=2, color='k',linestyle='--')
            self.canvas.draw()
            if self.clearButton.Enabled == False:
                self.clearButton.Enable()
            self.NumClicks += 1
            strMessage="Episode: ({0:.2f},--)".format(self.cxleft)
            self.sb.SetStatusText(strMessage)
            self.endButton.Disable()
            self.manualButton.Disable()
            self.cbList.Disable()
                
        elif self.NumClicks==1:
            self.cxright=event.xdata
            self.axes.axvline(x=self.cxright, ymin=0, ymax=1, linewidth=2, color='k',linestyle='--')
            self.canvas.draw()
            if self.clearButton.Enabled == False:
                self.clearButton.Enable()
            if (self.cxleft > self.cxright):
                aux=self.cxleft
                self.cxleft=self.cxright
                self.cxright=aux
            self.NumClicks +=1
            self.axes.axvspan(self.cxleft,self.cxright,ymin=0,ymax=1,facecolor='k',alpha=0.3)
            self.canvas.draw()
            strMessage="Episode: ({0:.2f},{1:.2f})".format(self.cxleft,self.cxright)
            self.sb.SetStatusText(strMessage)
            self.addButton.Enable()
            self.cbCombo.Enable()
            
    def OnEpisodesList(self,event):
        self.dm.SetVisibleEpisodes(list(self.cbList.GetCheckedStrings()))
        self.DrawFigure()
        self.canvas.draw()
        self.RefreshStatus()
        
                
    def OnAdd(self,event):
        Tag=str(self.cbCombo.GetValue())
        self.EpTypes,self.EpVisibleTypes = self.dm.GetVisibleEpisodes()
        if Tag not in self.EpTypes:
            self.dm.AssignEpisodeColor(Tag)
        self.dm.AddEpisode(self.cxleft,self.cxright,Tag)
        self.cbCombo.Disable()
        self.cbList.Enable()
        self.RefreshStatus()
                
    def OnClear(self, event):
        self.clearButton.Disable()
        self.cbCombo.Disable()
        self.cbList.Enable()
        self.RefreshStatus()
        
        
    def OnEnd(self,event):
        self.Destroy()
        self.WindowParent.OnEpisodesEditEnded()            

    def OnManual(self,event):
        print "Manual edition"
        ManualEditionWindow(self,-1,'Episodes manual edition',self.dm)
        self.manualButton.Disable()
        self.endButton.Disable()
        self.cbList.Disable()
        self.manualEditorPresent=True

    def OnManualEnded(self):
        self.manualButton.Enable()
        self.endButton.Enable()
        self.cbList.Enable()
        self.manualEditorPresent=False
            
    def RefreshStatus(self):
        self.DrawFigure()
        self.canvas.draw()
        self.clearButton.Disable()
        self.endButton.Enable()
        self.manualButton.Enable()
        self.addButton.Disable()
        strMessage=""
        self.sb.SetStatusText(strMessage)
        self.NumClicks=0
        self.EpTypes,self.EpVisibleTypes = self.dm.GetVisibleEpisodes()
        if self.TagsSelectorPresent:
            self.cbList.SetItems(self.EpTypes)
            self.cbList.SetCheckedStrings(self.EpVisibleTypes)
            self.vboxEditEpRightColumn.Layout()
        else:
            self.InsertTagsSelector()
            self.TagsSelectorPresent = True
        self.cbCombo.SetItems(self.EpTypes)
        self.vboxEditEpRightColumn.Layout()

# ------------------------------------------------



class ManualEditionWindow(wx.Frame):

    def __init__(self,parent,id,title,dm):

        data = [['OBS_APNEA',1,10],['GEN_HYPO',8,4.5],['OBS_APNEA',67,34.25]]
        wx.Frame.__init__(self, parent, -1, title)

        self.dm = dm

        self.Bind(wx.EVT_CLOSE,self.OnEnd)  
        
        self.WindowParent=parent

        panel = wx.Panel(self)
       
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        myGrid = gridlib.Grid(panel)

        myGrid.CreateGrid(len(data), 4)

        myGrid.SetColLabelAlignment(wx.ALIGN_RIGHT,wx.ALIGN_CENTER)
        myGrid.SetRowLabelAlignment(wx.ALIGN_RIGHT,wx.ALIGN_CENTER)
        myGrid.SetDefaultCellAlignment(wx.ALIGN_RIGHT,wx.ALIGN_CENTER)

        myGrid.SetColLabelValue(0, "Tag")
        myGrid.SetColLabelValue(1, "Init time")
        myGrid.SetColLabelValue(2, "End time")
        myGrid.SetColLabelValue(3, "Duration")

        myGrid.SetDefaultColSize(150)

        for row in range(len(data)):
            for column in range(len(data[row])):
                myGrid.SetCellValue(row,column,str(data[row][column]))
            myGrid.SetCellBackgroundColour(row,0,dm.GetEpisodeColor(data[row][0]))

 
        sizer.Add(myGrid, flag = wx.EXPAND| wx.ALL, border=borderBig)

        hbox = wx.BoxSizer(wx.VERTICAL)   

        hbox.AddStretchSpacer(prop=1)

        endButton = wx.Button(panel, -1, "Close", size=buttonSizeManualEd)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=endButton.GetId())
        endButton.SetToolTip(wx.ToolTip("Click to close window"))
        hbox.Add(endButton, 0, border=borderSmall, flag=wx.RIGHT)

                
        sizer.Add(hbox, 0, flag=wx.ALL| wx.EXPAND, border=borderBig)        

        panel.SetSizer(sizer)

        self.SetSize(manualEdWindowSize)

        self.SetMinSize(manualEdWindowMinSize)

        self.Show(True)
        self.Layout()
        self.Refresh()

    def OnEnd(self,event):
        self.WindowParent.OnManualEnded()
        self.Destroy()

