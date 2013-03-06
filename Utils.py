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

class Error(Exception):
    pass

class FewFramesException(Error):
    def __init__(self,NumOfFrames):
        self.NumOfFrames = NumOfFrames
  
