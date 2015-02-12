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
import Utils
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from DataModel import DM
import wx.grid as gridlib
from sys import platform
import wx.lib.scrolledpanel as scrolled



class EditEpisodesWindow(wx.Frame):
    
    """ Window for editing episodes"""
    NumClicks=0
    
    def __init__(self,parent,id,title,dm):
        wx.Frame.__init__(self, parent, -1, title)
        
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
            
        self.dm = dm
        self.manualEditorPresent=False
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)
        
        
        self.WindowParent=parent
        self.panel = wx.Panel(self)
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #

        if ColoredBGPlots:
            self.fig = matplotlib.figure.Figure((5.0, 4.0),facecolor=EpisodesEditionBGColor)
        else:
            self.fig = matplotlib.figure.Figure((5.0, 4.0))
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

        self.renButton = wx.Button(self.panel, -1, "Rename", size=buttonSizeEditEpisodes)
        self.Bind(wx.EVT_BUTTON, self.OnRen, self.renButton)
        self.vboxEditEpRightColumn.Add(self.renButton, 0, border=borderSmall, flag=wx.ALL | wx.ALIGN_RIGHT)
        if not self.dm.HasEpisodes():
            self.renButton.Disable()
        

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
        
        defSize,minSize=Utils.RecalculateWindowSizes(mainWindowSize,mainWindowMinSize)
        self.SetSize(defSize)
        self.SetMinSize(minSize)
        
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
        
        if self.dm.HasVisibleEpisodes():
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

    def OnRen(self,event):
        dia = RenameEpisodesWindow(self,-1, self.EpTypes)
        if dia.ShowModal() == wx.ID_OK:
            OldTag = dia.OldTag.GetValue()
            NewTag = str(dia.NewTag.GetValue())
            dia.Destroy()
            OldTags,OldVisibleTags = self.dm.GetVisibleEpisodes()
            if NewTag in self.dm.GetVisibleEpisodes()[0]:
                Utils.ErrorWindow("New tag already in use")
            else:
                self.dm.RenameEpisodes(OldTag,NewTag)
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
        self.dm.PurgeVisibleEpisodes()
        # Eps=self.dm.GetVisibleEpisodes()
        # print "Tags: ",str(Eps[0])
        # print "Vis: ",str(Eps[1])
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
        self.renButton.Disable()
        if len(self.dm.GetVisibleEpisodes()[0]) != 0:
            self.renButton.Enable()
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

    """ Window with grid to edit episodes manually"""

    def __init__(self,parent,id,title,dm):

        wx.Frame.__init__(self, parent, -1, title)
        
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)

        self.dm = dm
        self.Bind(wx.EVT_CLOSE,self.OnEnd) 
        self.WindowParent=parent
        self.panel = wx.Panel(self)
        self.EpisodesChanged=False

        self.__GetEpisodesInfo()
       
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # ------------ Begin of episodes grid

        vboxLeft = wx.BoxSizer(wx.VERTICAL)

        scrolledPanel = scrolled.ScrolledPanel(self.panel, style = wx.EXPAND,
            size = (manualEdWindowMinSize[0]-buttonSizeManualEd[0]-borderVeryBig*4,manualEdWindowSize[1]-borderVeryBig*4))
        

        # self.__CreateGrid(scrolledPanel)

        # scrolledPanel.SetAutoLayout(1)
        # scrolledPanel.SetupScrolling(scroll_x=False)

        # self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)

        # scrolledPanel.SetSizer(vboxLeft)
        # scrolledPanel.Layout()

        self.__CreateGrid(scrolledPanel)
        vboxLeft.Add(self.myGrid)
        scrolledPanel.SetSizer(vboxLeft)
        scrolledPanel.Layout()
        #scrolledPanel.SetAutoLayout(1)
        scrolledPanel.SetupScrolling(scroll_x=False)

        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)

        
        # 
        
        


        

        # ------------ End of episodes grid

        # ------------ Begin of buttons boxsizer

        vboxRight = wx.BoxSizer(wx.VERTICAL)  

        self.newButton = wx.Button(self.panel, -1, "New", size=buttonSizeManualEd)
        self.Bind(wx.EVT_BUTTON, self.OnNew, id=self.newButton.GetId())
        self.newButton.SetToolTip(wx.ToolTip("Click to add a new episode"))
        vboxRight.Add(self.newButton, 0, border=borderSmall, flag=wx.ALL)

        self.editButton = wx.Button(self.panel, -1, "Edit", size=buttonSizeManualEd)
        self.Bind(wx.EVT_BUTTON, self.OnEdit, id=self.editButton.GetId())
        self.editButton.SetToolTip(wx.ToolTip("Click to edit selected episode"))
        vboxRight.Add(self.editButton, 0, border=borderSmall, flag=wx.ALL)
        self.editButton.Disable()

        self.delButton = wx.Button(self.panel, -1, "Delete", size=buttonSizeManualEd)
        self.Bind(wx.EVT_BUTTON, self.OnDel, id=self.delButton.GetId())
        self.delButton.SetToolTip(wx.ToolTip("Click to delete selected episodes"))
        vboxRight.Add(self.delButton, 0, border=borderSmall, flag=wx.ALL)
        self.delButton.Disable()


        vboxRight.AddStretchSpacer(prop=1)

        self.endButton = wx.Button(self.panel, -1, "End", size=buttonSizeManualEd)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=self.endButton.GetId())
        self.endButton.SetToolTip(wx.ToolTip("Click to close window"))
        vboxRight.Add(self.endButton, 0, border=borderSmall, flag=wx.ALL)

        # ------------ End of buttons boxsizer

        box = wx.StaticBox(self.panel,-1,"Episodes information: ")
        sizer2 = wx.StaticBoxSizer(box,wx.VERTICAL)
        sizer2.Add(scrolledPanel,1,flag=wx.ALL|wx.EXPAND, border=borderBig)

        sizer.Add(sizer2, 0, flag=wx.ALL, border=borderBig)
        sizer.AddStretchSpacer(prop=1)  
        sizer.Add(vboxRight, 0, flag=wx.ALL|wx.EXPAND, border=borderBig)
             

        self.panel.SetSizer(sizer)

        self.SetSize(manualEdWindowSize)
        
        # defSize,minSize=Utils.RecalculateWindowSizes(manualEdWindowSize,manualEdWindowMinSize)
        # self.SetSize(defSize)
        # self.SetMinSize(minSize)

        self.Show(True)
        # self.Layout()
        self.Refresh()
        self.Fit()

    def __GetEpisodesInfo(self):
        self.Episodes = []
        if self.dm.HasEpisodes():
            EpInfo = self.dm.GetEpisodes()[0:3]
            for index in range(len(EpInfo[0])):
                self.Episodes.append([
                    EpInfo[0][index],
                    EpInfo[1][index],
                    EpInfo[1][index]+EpInfo[2][index],
                    EpInfo[2][index]
                    ])
            self.Episodes.sort(key = lambda x: x[1])
        # print str(self.Episodes)

    def __CreateGrid(self,parent):

        #Estimates brightness of colours. If it is dark, changes text color to white



        self.myGrid = gridlib.Grid(parent)

        self.myGrid.CreateGrid(len(self.Episodes)+5, 4, selmode=wx.grid.Grid.wxGridSelectRows)

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
            colors = self.GetColors(colorTag)
            self.myGrid.SetCellBackgroundColour(row,0,colors["bg"])
            self.myGrid.SetCellTextColour(row,0,colors["fg"])

    def GetColors(self, colorTag):

        bg = wx.Colour()

        if type(colorTag) != tuple:
            bg.SetFromName(colorTag)
            CT=bg.Get(includeAlpha=False)
            colorTagBrightness = int(round(0.299*CT[0] + 0.587*CT[1] + 0.114*CT[2]))
            
        else:
            CT = colorTag
            bg.Set(CT[0]*255,CT[1]*255,CT[2]*255,0)
            colorTagBrightness = int(round(0.299*CT[0]*255 + 0.587*CT[1]*255 + 0.114*CT[2]*255))

        #Estimates brightness of colours. If it is dark, changes text color to white

        if colorTagBrightness < 100:
            fg="white"
        else:
            fg="black"

        return {"fg":fg,"bg":bg}

            
    def OnEnd(self,event):
        if self.EpisodesChanged:
            strMessage="Episodes have been changed"
            strMessage += "\nApply changes?"
            dial = wx.MessageDialog(self, strMessage, "Confirm changes", wx.CANCEL | wx.YES_NO | wx.ICON_QUESTION)
            result = dial.ShowModal()
            dial.Destroy()
            if result == wx.ID_YES: 
                if len(self.Episodes)==0:
                    self.dm.ClearEpisodes()
                    self.dm.ClearColors()
                else:
                    self.dm.SetEpisodes(self.Episodes)
                self.WindowParent.OnManualEnded()
                self.Destroy()
            elif result == wx.ID_NO:
                self.WindowParent.OnManualEnded()
                self.Destroy()
        else:   
            self.WindowParent.OnManualEnded()
            self.Destroy()

    def OnDel(self,event):
        EpToRemove=self.GetEpisodesSelected()
        # print "Going to delete: ",str(EpToRemove)

        self.Episodes=[self.Episodes[i] for i in range(len(self.Episodes)) if i not in EpToRemove]

        EpToRemove.reverse()
        for Ep in EpToRemove:
            self.myGrid.DeleteRows(Ep,1)

        self.EpisodesChanged=True
        self.RefreshButtons()

    def OnNew(self,event):
        self.DisableButtons()
        # print "Adding and episode"
        EpTags = list(set([self.Episodes[i][0] for i in range(len(self.Episodes))]))
        EpSelected=self.GetEpisodesSelected()
        if len(EpSelected)==1:
            index = EpSelected[0]
            EpSelectedInfo = {"tag":self.Episodes[index][0],"InitTime":self.Episodes[index][1],"EndTime":self.Episodes[index][2]}
        else:
            EpSelectedInfo = None
        # print "Selected: ",len(EpSelected)
        EpisodeEditWindow(self,-1,"New episode", EpTags,EpSelectedInfo)


    
    def OnNewEditEnded(self,values,EpToEdit=None):

        ErrorMsg=None

        if values["InitTime"]<0 or values["EndTime"]<0:
            ErrorMsg = "Limits of episode must be positive numbers"

        if not ErrorMsg:
            if values["InitTime"]>values["EndTime"]:
                ErrorMsg = "Limits of episode are inverted"

        if not ErrorMsg:
            if values["EndTime"]>self.dm.GetHRDataPlot()[0][-1]:
                ErrorMsg = "Limits of episode are beyond the HR signal"

        if ErrorMsg:
            self.ErrorWindow(ErrorMsg)
            return


        # print "Adding: ",str(values)
        EpToInsert = [values["tag"],values["InitTime"],values["EndTime"],values["Duration"]]

        EpTags = list(set([self.Episodes[i][0] for i in range(len(self.Episodes))]))
        if values["tag"] not in EpTags:
            self.dm.AssignEpisodeColor(values["tag"])
            self.dm.AddToVisibleEpisodes(values["tag"])

        if EpToEdit == None:
            position=0
            for index in range(len(self.Episodes)):
                # print "Values: ",values["InitTime"]
                # print "Self: ",self.Episodes[index][1]
                if values["InitTime"]>self.Episodes[index][1]:
                    position=index+1
                # print "Position: ",position

            self.myGrid.InsertRows(pos=position,numRows=1)
            self.myGrid.SetCellValue(position,0,values["tag"])
            self.myGrid.SetReadOnly(position,0)
            self.myGrid.SetCellValue(position,1,"%.2f" % values["InitTime"])
            self.myGrid.SetReadOnly(position,1)
            self.myGrid.SetCellValue(position,2,"%.2f" % values["EndTime"])
            self.myGrid.SetReadOnly(position,2)
            self.myGrid.SetCellValue(position,3,"%.2f" % values["Duration"])
            self.myGrid.SetReadOnly(position,3)

            colorTag = self.dm.GetEpisodeColor(values["tag"])
            colors = self.GetColors(colorTag)
            self.myGrid.SetCellBackgroundColour(position,0,colors["bg"])
            self.myGrid.SetCellTextColour(position,0,colors["fg"])


            self.Episodes.append(EpToInsert)
            self.Episodes.sort(key = lambda x: x[1])

            lastRow=self.myGrid.GetNumberRows()-1
            if self.myGrid.GetCellValue(lastRow,0)=="":
                self.myGrid.DeleteRows(lastRow,1)

        else:
            position=EpToEdit
            self.myGrid.SetCellValue(position,0,values["tag"])
            self.myGrid.SetCellValue(position,1,"%.2f" % values["InitTime"])
            self.myGrid.SetCellValue(position,2,"%.2f" % values["EndTime"])
            self.myGrid.SetCellValue(position,3,"%.2f" % values["Duration"])

            colorTag = self.dm.GetEpisodeColor(values["tag"])
            colors = self.GetColors(colorTag)
            self.myGrid.SetCellBackgroundColour(position,0,colors["bg"])
            self.myGrid.SetCellTextColour(position,0,colors["fg"])

            self.Episodes[position][0]=values["tag"]
            self.Episodes[position][1]=values["InitTime"]
            self.Episodes[position][2]=values["EndTime"]
            self.Episodes[position][3]=values["Duration"]
                

        self.EpisodesChanged=True
        self.RefreshButtons()

    def OnEdit(self,event):
        self.DisableButtons()
        # print "Going to edit"
        EpTags = list(set([self.Episodes[i][0] for i in range(len(self.Episodes))]))

        EpSelected=self.GetEpisodesSelected()
        
        index = EpSelected[0]
        EpSelectedInfo = {"tag":self.Episodes[index][0],"InitTime":self.Episodes[index][1],"EndTime":self.Episodes[index][2]}
        # print "Selected: ",len(EpSelected)
        EpisodeEditWindow(self,-1,"Modify episode",EpTags,EpSelectedInfo,EpToEdit=index)


    def OnRangeSelect(self,evt):
        self.RefreshButtons()
        evt.Skip()

    def RefreshButtons(self):
        self.DisableButtons()
        self.endButton.Enable()
        self.newButton.Enable()
        EpSelected=self.GetEpisodesSelected()
        if len(EpSelected)==1:
            self.editButton.Enable()
        if len(EpSelected)>=1:
            self.delButton.Enable()


    def DisableButtons(self):
        self.newButton.Disable()
        self.editButton.Disable()
        self.delButton.Disable()
        self.endButton.Disable()


    def GetEpisodesSelected(self):
        EpSelected=[]
        for row in range(len(self.Episodes)):
            if self.myGrid.IsInSelection(row,0):
                EpSelected.append(row)
        return EpSelected



    def ErrorWindow(self,messageStr,captionStr="ERROR"):
        """Generic error window"""
        dial = wx.MessageDialog(self, caption=captionStr, message=messageStr, style=wx.OK | wx.ICON_ERROR)
        result = dial.ShowModal()
        dial.Destroy()


class EpisodeEditWindow(wx.Frame):

    """Window to add or edit an episode"""

    def __init__(self, parent, id, title, EpTags, EpSelectedInfo, EpToEdit=None):
        if platform != 'darwin':
            wx.Frame.__init__(self, parent, wx.ID_ANY, size=addEpWinSize, title=title)
        else:
            wx.Frame.__init__(self, parent, wx.ID_ANY, size=addEpWinSizeMac, title=title)
            
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
            
        self.WindowParent=parent
        self.EpToEdit = EpToEdit
        # self.Bind(wx.EVT_CLOSE,self.OnEnd)
        panel=wx.Panel(self)

        if EpSelectedInfo == None:
            self.values={'tag':'','InitTime':0,'EndTime':0,'Duration':0}
        else:
            self.values={'tag':EpSelectedInfo["tag"],'InitTime':EpSelectedInfo["InitTime"],'EndTime':EpSelectedInfo["EndTime"],'Duration':0}

        self.EpTags=EpTags

        sizer=wx.BoxSizer(wx.VERTICAL)

        # ------------ Begin of tag selector

        sbTag = wx.StaticBox(panel, label="Episode Tag")
        sbTagSizer = wx.StaticBoxSizer(sbTag, wx.VERTICAL)
        if len(self.EpTags)>0:
            if EpSelectedInfo==None:
                InitValue=self.EpTags[0]
            else:
                InitValue = self.values["tag"]
        else:
            InitValue='NEW_TAG'

        self.cbCombo=wx.ComboBox(panel,choices=self.EpTags, value=InitValue, style=wx.CB_DROPDOWN)
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
        self.EndTime.Bind(wx.EVT_KILL_FOCUS, self.OnEndChanged)
        paramsSizer2.AddStretchSpacer(prop=1)
        paramsSizer2.Add(self.EndTime, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)
        paramsSizer.Add(paramsSizer2,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=borderSmall)


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

        buttonOk = wx.Button(panel, -1, label="Ok")
        buttonSizer.Add(buttonOk, flag=wx.ALL, border=borderSmall)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=buttonOk.GetId())
        buttonOk.SetToolTip(wx.ToolTip("Click to confirm"))

        sizer.Add(buttonSizer,flag=wx.ALL|wx.EXPAND, border=borderSmall)

        # ------------ End of sizer for buttons

        panel.SetSizer(sizer)

        if platform != 'darwin':
           self.SetMinSize(addEpWinMinSize)
        else:
           self.SetMinSize(addEpWinMinSizeMac)
        
        self.Show()
        self.Center()

    def OnOk(self,event):
        self.values["tag"]=str(self.cbCombo.GetValue())
        try:
            Init = float(self.InitTime.GetValue())
            End = float(self.EndTime.GetValue())
        except:
            self.InitTime.SetValue("%.2f" % self.values["InitTime"])
            self.EndTime.SetValue("%.2f" % self.values["EndTime"])
            return
        self.values["InitTime"]=Init
        self.values["EndTime"]=End
        self.values["Duration"]=End-Init
        # print "Going to add: ", str(self.values)
        if self.values["tag"] not in self.EpTags:
            self.EpTags.append(self.values["tag"])

        self.WindowParent.OnNewEditEnded(self.values,self.EpToEdit)
        self.Destroy()

    def OnInitChanged(self,event):
        try: 
            Init = float(self.InitTime.GetValue())
        except:
            self.InitTime.SetValue("%.2f" % self.values["InitTime"])
            return
        self.values["InitTime"]=Init
        self.RefreshValues()

    def OnEndChanged(self,event):
        try: 
            End = float(self.EndTime.GetValue())
        except:
            self.EndTime.SetValue("%.2f" % self.values["EndTime"])
            return
        self.values["EndTime"]=End
        self.RefreshValues()

    def RefreshValues(self):
        self.InitTime.SetValue("%.2f" % self.values["InitTime"])
        self.EndTime.SetValue("%.2f" % self.values['EndTime'])

    def OnEnd(self,event):
        self.WindowParent.RefreshButtons()
        self.Destroy()


class RenameEpisodesWindow(wx.Dialog):
    def __init__(self, parent, id, EpTypes):
        wx.Dialog.__init__(self, parent, id, "Rename episodes")

        vbox = wx.BoxSizer(wx.VERTICAL)
        sbLimits = wx.StaticBox(self,label='')
        sbLimitsSizer=wx.StaticBoxSizer(sbLimits,wx.VERTICAL)

        

        gridbox = wx.GridBagSizer(hgap=5,vgap=5)

        gridbox.Add(wx.StaticText(self,
            label="Select tag to rename:"),
            pos=(0,0),flag=wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,
            border=borderSmall)


        self.OldTag=wx.ComboBox(self,choices=EpTypes, value=EpTypes[0], style=wx.CB_DROPDOWN)


        gridbox.Add(self.OldTag,pos=(0,1),flag=wx.ALL | wx.EXPAND, border=borderSmall)

        gridbox.Add(wx.StaticText(self,
            label="Type new tag name:"),
            pos=(1,0),flag=wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,
            border=borderSmall)

        self.NewTag = wx.TextCtrl(self,-1,size=textCtrlSize)
        self.NewTag.SetValue('')
        if platform != 'darwin': 
            self.NewTag.SetWindowStyleFlag(wx.TE_RIGHT)
        gridbox.Add(self.NewTag, pos=(1,1), flag=wx.ALL|wx.EXPAND, border=borderSmall)

        sbLimitsSizer.Add(gridbox,0, flag=wx.EXPAND|wx.ALL, border=borderSmall)

        vbox.Add(sbLimitsSizer, 0, flag=wx.ALIGN_CENTER|wx.ALL, border=borderVeryBig)

        vbox.AddStretchSpacer(1)
        
        sizer =  self.CreateButtonSizer(wx.CANCEL|wx.OK)
        vbox.Add(sizer, 0, flag=wx.ALIGN_CENTER|wx.ALL, border=borderVeryBig)
        self.SetSizer(vbox)
