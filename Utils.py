#!/usr/bin/python
# -*- coding:utf-8 -*-

#   ----------------------------------------------------------------------
#   gHRV: a graphical application for Heart Rate Variability analysis
#   Copyright (C) 2013  Milegroup - Dpt. Informatics
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
	if platform != "win32":
		filetypes = fileTypesLinMac
		extensions= extensionsLinMac
		automaticExtensions = automaticExtensionsLinMac
	else:
		filetypes = fileTypesWin
		extensions= extensionsWin
		automaticExtensions = automaticExtensionsWin

	dial = wx.FileDialog(None, message="Save figure as...", defaultFile=fileNameTmp, style=wx.FD_SAVE, wildcard=filetypes)
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
	dial = wx.MessageDialog(None,message="Plot saved: " +filename, caption="Result ok",style=wx.OK|wx.ICON_INFORMATION)
	if dial.ShowModal() != wx.ID_YES:
		dial.Destroy()
		return
	