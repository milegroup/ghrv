# -*- coding:utf-8 -*-

#   ----------------------------------------------------------------------
#   gHRV: a graphical application for Heart Rate Variability analysis
#   Copyright (C) 2012  Milegroup - Dpt. Informatics
#      University of Vigo - Spain
#      www.milegroup.net
#
#    Authors:
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

Verbose=False
DebugMode = False
ReportVersion = False
Version="0.999" # Things like 1.0.5 are not valid

from sys import platform
borderBig=10
borderSmall=5
borderVeryBig=20

mainWindowSize=(1200,650)
mainWindowMinSize=(1000,600)

signifWindowSize=(800,700)
signifWindowMinSize=(640,700)
signifNumMinValues = 10
signifNumBins = 10
signifAlpha = 0.01

poincareWindowSize=(650,700)
poincareWindowMinSize=(590,640)

#editNIHRWindowSize=(1024,768)
#BandsWindowSize=(1024,768)
aboutWindowSize=(800,700)
aboutWindowMinSize=(640,480)
aboutWindowSizeMac=(640,500)

confWindowSize=(500,450)
confWindowProjectSize=(500,500)
confWindowMinSize=(450,400)
confWindowProjectMinSize=(450,475)

confWindowSizeMac=(425,475)
confWindowProjectSizeMac=(425,550)

reportWindowSize=(800,800)
reportWindowMinSize=(800,700)

manualEdWindowSize=(900,480)
manualEdWindowMinSize=(900,400)

addEpWinSize=(250,235)
addEpWinMinSize=(320,235)
addEpWinSizeMac=(290,280)
addEpWinMinSizeMac=(250,280)


exportSettingsWindowSize=(500,350)
exportSettingsWindowMinSize=exportSettingsWindowSize

exportSettingsWindowSizeMac=(500,375)
exportSettingsWindowMinSizeMac=exportSettingsWindowSizeMac

updateWindowSize=(410,240)
updateWindowSizeMac=(410,240)

alphaMatplotlibTags=0.5

HRBGColor='#D9FFB3'
EditBGColor='#FF9F80'
TemporalBGColor='#80DFFF'
ReportBGColor='#B3DF5D'
EpisodesEditionBGColor='#FFD966'
SignifBGColor='#DAB4B4'
PoincareBGColor='#FF9ECE'

LogoVertColor='#5C7F19'
ReportWindowTitleColor='#5C7F19'
ReportWindowSubTitleColor='#3144CD'

buttonSizeEditNIHR=(150,35)
buttonSizeFrameBased = buttonSizeEditNIHR
buttonSizeReportWindow=buttonSizeEditNIHR
buttonSizeAbout=buttonSizeEditNIHR
buttonSizeSignif=buttonSizeEditNIHR
buttonSizeManualEd=(120,35)
buttonSizeEditEpisodes=(120,35)

textCtrlSize=(60,25)
textCtrlSizeBig=(80,25)


verticalFactorPBPlot=0.9

factorySettings={'interpfreq':'4.0','windowsize':'120.0','windowshift':'60.0','ulfmin':'0.0','ulfmax':'0.03','vlfmin':'0.03','vlfmax':'0.05','lfmin':'0.05','lfmax':'0.15','hfmin':'0.15','hfmax':'0.4'}

HTMLHead='''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"> 
<html>
<body>
'''

HTMLTail='''</body>
</html>
'''

plotDPI=50.0
HTMLPageWidth=750.0
plotHRWidth=740.0
plotHRHeight=300.0
plotHRHistogramWidth=260.0
plotHRHistogramHeight=200.0
plotPoincareWidth=300.0
plotPoincareHeight=300.0
plotFBWidth=740.0
plotFBHeight=500.0

fileTypesLinMac="EPS file (*.eps)|*.eps;*EPS|JPEG file (*.jpg,*.jpeg)|*.jpeg;*.JPEG;*.jpg;*.JPG|PDF file (*.pdf)|*.pdf;*.PDF|PNG file (*.png)|*.png;*.PNG|SVG file (*.svg)|*.svg;*.SVG|TIFF file (*.tif,*.tiff)|*.tiff;*.TIFF;*.tif;*.TIF|All files (*.*)|*.*"
extensionsLinMac=["eps","jpeg","jpg","pdf","png","svg","tif","tiff"]
fileTypesWin="EPS file (*.eps)|*.eps;*EPS|PDF file (*.pdf)|*.pdf;*.PDF|PNG file (*.png)|*.png;*.PNG|SVG file (*.svg)|*.svg;*.SVG|All files (*.*)|*.*"
extensionsWin=["eps","pdf","png","svg"]

