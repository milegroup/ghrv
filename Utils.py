#!/usr/bin/python
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

from sys import platform
import os
from configvalues import *
import wx

class Error(Exception):
	pass

class FewFramesException(Error):
	def __init__(self,NumOfFrames):
		self.NumOfFrames = NumOfFrames

def SavePlotFileName(fileNameTmp):
	fileName=""
	dial = wx.FileDialog(None, message="Save figure as...", defaultFile=fileNameTmp, style=wx.FD_SAVE, wildcard=fileTypes)
	result = dial.ShowModal()
	if result == wx.ID_OK:
		fileName=dial.GetPath()
		fileExt = os.path.splitext(fileName)[1][1:].strip()
		if fileExt not in extensions:
			fileName = fileName + "." + automaticExtensions[dial.GetFilterIndex()]
		# print "Saving ",fileName
		dial.Destroy()
		return fileName
	else:
		dial.Destroy()
		return None

def ErrorWindow(messageStr,captionStr="ERROR"):
	"""Generic error window"""
	dial = wx.MessageDialog(None, caption=captionStr, message=messageStr, style=wx.OK | wx.ICON_ERROR)
	result = dial.ShowModal()
	dial.Destroy()
	
def OverwriteConfirm(filename):
	dial = wx.MessageDialog(None,message=filename+" already exists.\nDo you want to replace it?",caption="Warning",style=wx.YES|wx.NO|wx.ICON_QUESTION)
	if dial.ShowModal() != wx.ID_YES:
		dial.Destroy()
		return False
	else:
		dial.Destroy()
		return True
	
def InformCorrectFile(filename):
	dial = wx.MessageDialog(None,message="File saved: " +filename, caption="Result ok",style=wx.OK|wx.ICON_INFORMATION)
	if dial.ShowModal() != wx.ID_YES:
		dial.Destroy()
		return

def InformEpisodesFile(filename,num):
	dial = wx.MessageDialog(None,message=str(num)+" episodes loaded from file " +filename, caption="Result ok",style=wx.OK|wx.ICON_INFORMATION)
	if dial.ShowModal() != wx.ID_YES:
		dial.Destroy()
		return

def RecalculateWindowSizes(DefaultSize,MinSize):
	screenWidth,screenHeight = wx.GetDisplaySize()
	if screenWidth < DefaultSize[0]:
		factor = float(DefaultSize[0])/screenWidth
		DefaultSize = int(DefaultSize[0]/factor),DefaultSize[1]
		MinSize = int(MinSize[0]/factor),MinSize[1]
	return DefaultSize,MinSize



class SelectAnnotator(wx.Frame):
	def __init__(self,extensionsFound):
		self.result=''
		self.dlg = wx.SingleChoiceDialog(
				None, "Please, select annotator", 'WFDB format annotation loading',
				extensionsFound, 
				wx.CHOICEDLG_STYLE
				)
		if self.dlg.ShowModal() == wx.ID_OK:
			self.result = self.dlg.GetStringSelection()
	def GetValue(self):
		self.dlg.Destroy()
		return self.result


class SelectEpisodesTags(wx.Frame):
	def __init__(self,tagsFound):
		self.result=''
		self.dlg = wx.MultiChoiceDialog(
				None, "Please, select Tags to load", 'WFDB episodes loading',
				choices=tagsFound, 
				style=wx.CHOICEDLG_STYLE
				)
 
		if self.dlg.ShowModal() == wx.ID_OK:
			self.result = self.dlg.GetSelections()
	def GetValues(self):
		self.dlg.Destroy()
		return self.result

class ConfigPoincarePlot(wx.Dialog):
    def __init__(self, parent, id, MinPrev, MaxPrev):
        wx.Dialog.__init__(self, parent, id, u"Poincaré Plot configuration")

        vbox = wx.BoxSizer(wx.VERTICAL)

        sbLimits = wx.StaticBox(self,label='')

        sbLimitsSizer=wx.StaticBoxSizer(sbLimits,wx.VERTICAL)
        
        sbLimitsSizer1=wx.GridBagSizer(hgap=5,vgap=5)

        sbLimitsSizer1.Add(wx.StaticText(self,
        	label="Axes minimum (msec.)"),
        	pos=(0,0),flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL,
        	border=borderVeryBig)
        self.AxesMin = wx.TextCtrl(self,-1,size=textCtrlSize)
        self.AxesMin.SetValue(str(MinPrev))
        if platform != 'darwin': 
            self.AxesMin.SetWindowStyleFlag(wx.TE_RIGHT)
        sbLimitsSizer1.Add(self.AxesMin, pos=(0,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)

        sbLimitsSizer1.Add(wx.StaticText(self,
        	label="Axes maximum (msec.)"),
        	pos=(1,0),flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL,
        	border=borderVeryBig)
        self.AxesMax = wx.TextCtrl(self,-1,size=textCtrlSize)
        self.AxesMax.SetValue(str(MaxPrev))
        if platform != 'darwin': 
            self.AxesMax.SetWindowStyleFlag(wx.TE_RIGHT)
        sbLimitsSizer1.Add(self.AxesMax, pos=(1,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=borderSmall)

        sbLimitsSizer.Add(sbLimitsSizer1, flag=wx.ALL|wx.EXPAND, border=borderSmall)
        vbox.Add(sbLimitsSizer,0, flag=wx.ALIGN_CENTER|wx.ALL, border=borderVeryBig)

        vbox.AddStretchSpacer(1)
        
        sizer =  self.CreateButtonSizer(wx.CANCEL|wx.OK)
        vbox.Add(sizer, 0, flag=wx.ALIGN_CENTER|wx.ALL, border=borderVeryBig)
        self.SetSizer(vbox)


 
		