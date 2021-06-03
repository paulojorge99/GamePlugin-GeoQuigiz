# -*- coding: utf-8 -*-
"""
/*************************************************************************************
 GeoQuigiz
                     A QGIS plugin
 This plugin is a game of capitals and flags of world
                             -------------------
        copyright            : (C) 2021 by João Alves, Paulo Alves
        email                : joaomsalves@hotmail.com, paulojorgealves18@gmail.com
 *************************************************************************************/
"""

from .capitals_game import CapitalsGamePlugin

def classFactory(iface):
    return CapitalsGamePlugin(iface)


