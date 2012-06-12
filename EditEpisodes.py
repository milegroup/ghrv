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
        self.fig.subplots_adjust(left=0.07, bottom=0.07, right=0.98, top=0.94, wspace=0.20, hspace=0.15)
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
        
        self.InsertTagsSelector()

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
            if hasattr(self, 'cbList'):
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
        if hasattr(self, 'cbList'):
            self.cbList.Enable()
        self.RefreshStatus()
        self.canvas.draw()
                
    def OnClear(self, event):
        self.clearButton.Disable()
        self.cbCombo.Disable()
        if hasattr(self, 'cbList'):
            self.cbList.Enable()
        self.RefreshStatus()
        
        
    def OnEnd(self,event):
        self.Destroy()
        self.WindowParent.OnEpisodesEditEnded()            

    def OnManual(self,event):
        ManualEditionWindow(self,-1,'Episodes manual edition',self.dm)
        self.manualButton.Disable()
        self.endButton.Disable()
        if hasattr(self, 'cbList'):
            self.cbList.Disable()
        self.manualEditorPresent=True

    def OnManualEnded(self):
        self.manualButton.Enable()
        self.endButton.Enable()
        self.RefreshStatus()
        if hasattr(self, 'cbList'):
            self.cbList.Enable()
        self.manualEditorPresent=False
        
        self.canvas.draw()
            
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
        self.cbList.SetItems(self.EpTypes)
        self.cbList.SetCheckedStrings(self.EpVisibleTypes)
        self.vboxEditEpRightColumn.Layout()
        self.cbCombo.SetItems(self.EpTypes)
        self.vboxEditEpRightColumn.Layout()

# ------------------------------------------------



class ManualEditionWindow(wx.Frame):

    def __init__(self,parent,id,title,dm):

        wx.Frame.__init__(self, parent, -1, title, size=manualEdWindowSize)

        self.dm = dm
        self.Bind(wx.EVT_CLOSE,self.OnEnd)  
        self.WindowParent=parent
        self.panel = wx.Panel(self)
        self.EpisodesChanged=False

        self.__GetEpisodesInfo()
       
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # ------------ Begin of episodes grid

        vboxLeft = wx.BoxSizer(wx.VERTICAL)   

        
        self.__CreateGrid()

        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)

        # ------------ End of episodes grid

        # ------------ Begin of buttons boxsizer

        vboxRight = wx.BoxSizer(wx.VERTICAL)  

        newButton = wx.Button(self.panel, -1, "New", size=buttonSizeManualEd)
        self.Bind(wx.EVT_BUTTON, self.OnNew, id=newButton.GetId())
        newButton.SetToolTip(wx.ToolTip("Click to add a new episode"))
        vboxRight.Add(newButton, 0, border=borderSmall, flag=wx.RIGHT)

        self.delButton = wx.Button(self.panel, -1, "Delete", size=buttonSizeManualEd)
        self.Bind(wx.EVT_BUTTON, self.OnDel, id=self.delButton.GetId())
        self.delButton.SetToolTip(wx.ToolTip("Click to delete selected episodes"))
        vboxRight.Add(self.delButton, 0, border=borderSmall, flag=wx.RIGHT)
        self.delButton.Disable()

        vboxRight.AddStretchSpacer(prop=1)

        endButton = wx.Button(self.panel, -1, "Close", size=buttonSizeManualEd)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=endButton.GetId())
        endButton.SetToolTip(wx.ToolTip("Click to close window"))
        vboxRight.Add(endButton, 0, border=borderSmall, flag=wx.RIGHT)

        # ------------ End of buttons boxsizer


        sizer.Add(self.myGrid, 0, flag=wx.ALL, border=borderBig)  
        sizer.AddStretchSpacer(prop=1)      
        sizer.Add(vboxRight, 0, flag=wx.ALL|wx.EXPAND, border=borderBig)        

        self.panel.SetSizer(sizer)

        # self.SetSize(manualEdWindowSize)

        self.SetMinSize(manualEdWindowMinSize)

        self.Show(True)
        self.Layout()
        self.Refresh()

    def __GetEpisodesInfo(self):
        EpInfo = self.dm.GetEpisodes()[0:3]
        self.Episodes = []
        for index in range(len(EpInfo[0])):
            self.Episodes.append([
                EpInfo[0][index],
                EpInfo[1][index],
                EpInfo[1][index]+EpInfo[2][index],
                EpInfo[2][index]
                ])
        self.Episodes.sort(key = lambda x: x[1])
        # print str(self.Episodes)

    def __CreateGrid(self):

        #Estimates brightness of colours. If it is dark, changes text color to white

        self.myGrid = gridlib.Grid(self.panel)

        self.myGrid.CreateGrid(len(self.Episodes), 4, selmode=wx.grid.Grid.wxGridSelectRows)

        self.myGrid.SetColLabelAlignment(wx.ALIGN_RIGHT,wx.ALIGN_CENTER)
        self.myGrid.SetRowLabelAlignment(wx.ALIGN_RIGHT,wx.ALIGN_CENTER)
        self.myGrid.SetDefaultCellAlignment(wx.ALIGN_RIGHT,wx.ALIGN_CENTER)

        self.myGrid.SetColLabelValue(0, "Tag")
        self.myGrid.SetColLabelValue(1, "Init time")
        self.myGrid.SetColLabelValue(2, "End time")
        self.myGrid.SetColLabelValue(3, "Duration")

        self.myGrid.SetDefaultColSize(150)


        for row in range(len(self.Episodes)):
            for column in range(len(self.Episodes[row])):
                cellValue = self.Episodes[row][column]
                if column != 0:
                    cellValueStr = "%.2f" % cellValue
                else:
                    cellValueStr = str(cellValue)
                self.myGrid.SetCellValue(row,column,cellValueStr)
                self.myGrid.SetReadOnly(row,column)
            colorTag = self.dm.GetEpisodeColor(self.Episodes[row][0])

            # print  "Tag: ",self.Episodes[row][0],"   ",str(colorTag)
            
            #Estimates brightness of colours. If it is dark, changes text color to white

            colorwx = wx.Colour()

            if type(colorTag) != tuple:
                colorwx.SetFromName(colorTag)
                CT=colorwx.Get(includeAlpha=False)
                colorTagBrightness = int(round(0.299*CT[0] + 0.587*CT[1] + 0.114*CT[2]))
                
            else:
                CT = colorTag
                colorwx.Set(CT[0]*255,CT[1]*255,CT[2]*255,0)
                colorTagBrightness = int(round(0.299*CT[0]*255 + 0.587*CT[1]*255 + 0.114*CT[2]*255))

            self.myGrid.SetCellBackgroundColour(row,0,colorwx)
            # print "Tag: ",self.Episodes[row][0],"   -   Brightness: ",colorTagBrightness
            if colorTagBrightness < 100:
                self.myGrid.SetCellTextColour(row,0,'white')

            
    def OnEnd(self,event):
        if self.EpisodesChanged:
            self.dm.SetEpisodes(self.Episodes)
        self.WindowParent.OnManualEnded()
        self.Destroy()

    def OnDel(self,event):
        EpToRemove=[]
        for row in range(len(self.Episodes)):
            if self.myGrid.IsInSelection(row,0):
                EpToRemove.append(row)
        # print "Going to delete: ",str(EpToRemove)
        self.Episodes=[self.Episodes[i] for i in range(len(self.Episodes)) if i not in EpToRemove]

        EpToRemove.reverse()
        for Ep in EpToRemove:
            self.myGrid.DeleteRows(Ep,1)
        self.EpisodesChanged=True
        self.delButton.Disable()

    def OnNew(self,event):
        # print "Adding and episode"
        EpTags = list(set([self.Episodes[i][0] for i in range(len(self.Episodes))]))
        EpisodeEditWindow(self,-1,EpTags)


    def OnRangeSelect(self,evt):
        if self.myGrid.IsSelection():
            # print "Selection active"
            self.delButton.Enable()

        else:
            # print "No selection"
            self.delButton.Disable()
        evt.Skip()

class EpisodeEditWindow(wx.Frame):

    def __init__(self, parent, id, EpTags):
        if platform != 'darwin':
            wx.Frame.__init__(self, parent, wx.ID_ANY, size=addEpWinSize)
        else:
            wx.Frame.__init__(self, parent, wx.ID_ANY, size=addEpWinSizeMac)
        self.WindowParent=parent
        # self.Bind(wx.EVT_CLOSE,self.OnEnd)
        panel=wx.Panel(self)

        self.values={'tag':'','InitTime':0,'EndTime':0,'Duration':0}

        sizer=wx.BoxSizer(wx.VERTICAL)

        # ------------ Begin of tag selector

        sbTag = wx.StaticBox(panel, label="Episode Tag")
        sbTagSizer = wx.StaticBoxSizer(sbTag, wx.VERTICAL)
        if len(EpTags)>0:
            InitValue=EpTags[0]
        else:
            InitValue='NEW_TAG'

        self.cbCombo=wx.ComboBox(panel,choices=EpTags, value=InitValue, style=wx.CB_DROPDOWN)
        sbTagSizer.Add(self.cbCombo,flag=wx.ALL | wx.EXPAND, border=borderSmall)

        sizer.Add(sbTagSizer,flag=wx.ALL | wx.EXPAND, border=borderSmall)

        # ------------ End of tag selector

        # ------------ Begin of params block

        sbParams = wx.StaticBox(panel,label="Episode parameters")
        paramsSizer=wx.StaticBoxSizer(sbParams,wx.VERTICAL)

        paramsSizer1=wx.BoxSizer(wx.HORIZONTAL)
        paramsSizer1.Add(wx.StaticText(panel, label="Init time"), 
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.InitTime = wx.TextCtrl(panel,-1,size=textCtrlSizeBig)
        self.InitTime.Bind(wx.EVT_KILL_FOCUS, self.OnInitChanged)
        paramsSizer1.AddStretchSpacer(prop=1)
        paramsSizer1.Add(self.InitTime, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        paramsSizer.Add(paramsSizer1,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=borderSmall)

        paramsSizer2=wx.BoxSizer(wx.HORIZONTAL)
        paramsSizer2.Add(wx.StaticText(panel, label="End time"),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.EndTime = wx.TextCtrl(panel,-1,size=textCtrlSizeBig)
        self.EndTime.Bind(wx.EVT_KILL_FOCUS, self.OnValuesChanged)
        paramsSizer2.AddStretchSpacer(prop=1)
        paramsSizer2.Add(self.EndTime, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        paramsSizer.Add(paramsSizer2,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=borderSmall)

        paramsSizer3=wx.BoxSizer(wx.HORIZONTAL)
        paramsSizer3.Add(wx.StaticText(panel, label="Duration"),
                          flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=borderVeryBig)
        self.Duration = wx.TextCtrl(panel,-1,size=textCtrlSizeBig)
        self.Duration.Bind(wx.EVT_KILL_FOCUS, self.OnValuesChanged)
        paramsSizer3.AddStretchSpacer(prop=1)
        paramsSizer3.Add(self.Duration, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        paramsSizer.Add(paramsSizer3,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=borderSmall)

        self.RefreshValues()

        sizer.Add(paramsSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=borderSmall)

        # ------------ End of params block

        # ------------ Begin of sizer for buttons

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        buttonCancel = wx.Button(panel, -1, label="Cancel")
        buttonSizer.Add(buttonCancel, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=buttonCancel.GetId())
        buttonCancel.SetToolTip(wx.ToolTip("Click to cancel"))

        buttonSizer.AddStretchSpacer(prop=1)

        buttonAdd = wx.Button(panel, -1, label="Ok")
        buttonSizer.Add(buttonAdd, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, id=buttonAdd.GetId())
        buttonAdd.SetToolTip(wx.ToolTip("Click to add episode"))

        sizer.Add(buttonSizer,flag=wx.ALL|wx.EXPAND, border=borderSmall)

        # ------------ End of sizer for buttons

        panel.SetSizer(sizer)

        if platform != 'darwin':
            self.SetMinSize(addEpWinMinSize)
        else:
            self.SetMinSize(addEpWinMinSizeMac)
        
        self.Show()
        self.Center()

    def OnAdd(self,event):
        return

    def OnInitChanged(self,event):
        try: 
            Init = float(self.InitTime.GetValue())
        except:
            self.InitTime.SetValue("%.2f" % self.values["InitTime"])
            return
        self.values["InitTime"]=Init
        self.values["Duration"]=self.values["EndTime"]-self.values["InitTime"]
        self.RefreshValues()
        

    def RefreshValues(self):
        self.InitTime.SetValue("%.2f" % self.values["InitTime"])
        self.EndTime.SetValue("%.2f" % self.values['EndTime'])
        self.Duration.SetValue("%.2f" % self.values["Duration"])
        

    def OnValuesChanged(self,event):
        End = self.EndTime.GetValue()
        Dur = self.Duration.GetValue()


        return

    def OnEnd(self,event):
        self.Destroy()



