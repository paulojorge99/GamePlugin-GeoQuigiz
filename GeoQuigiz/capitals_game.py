# -*- coding: utf-8 -*-
"""
/****************************************************************************
 GeoQuigiz
                     A QGIS plugin
 This plugin is a game of capitals and flags of world
                             -------------------
        copyright            : (C) 2021 by João Alves, Paulo Alves
        email                : joaomsalves@hotmail.com, paulojorgealves18@gmail.com
 ****************************************************************************/

"""

import os
import sys
import inspect
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import *
from .capitals_game_dialog import CapitalsGameDialog
from .restart_box_dialog import RestartDialog
from .back_menu_box_dialog import BackDialog
from .country_box_dialog import CountryDialog
from .flag_box_dialog import FlagDialog
from .flag_box_dialog_explorer import FlagDialogExplorer
import random
from qgis.core import Qgis
from PyQt5.QtCore import QCoreApplication
from qgis.gui import QgsMapToolIdentifyFeature
from qgis.gui import (
    QgsMapCanvas,
    QgsVertexMarker,
    QgsMapCanvasItem,
    QgsRubberBand,
)
from qgis.core import *
from qgis.utils import iface
from PyQt5.QtCore import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import QAction, QMainWindow
import time
from PyQt5 import QtCore, QtGui, QtWidgets
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PIL import Image


cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

class CapitalsGamePlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
      icon = os.path.join(os.path.join(cmd_folder, 'globe-icon.png'))
      self.action = QAction(QIcon(icon), 'Capitals Game', self.iface.mainWindow())
      self.action.triggered.connect(self.start)
      self.iface.addPluginToMenu('&Capitals Game', self.action)
      self.iface.addToolBarIcon(self.action)
      self.first_start = True 
      self.c=0
      self.f=0
      self.back=0
      self.f_explorer=0
      self.back2=0
      self.ambiente=0
      
      
    

    def unload(self):
      self.iface.removeToolBarIcon(self.action)
      self.iface.removePluginMenu('&Capitals Game', self.action)  
      del self.action


    #function called when the user clicks on the map in the capitals game. It sees if the user chose the right country. If he did, they that feature is added
    # to the layer "certas", otherwise the user has two more options. If the user gets the three choices wrong, then the feature is added to the layer "erradas"
    # After five questions, the game ends and it shows a dialog with the score and the option to get back to the menu. 
    def callback(self,feat):

          """Code called when the feature is selected by the user"""
          
          if feat["countryLabel"]==self.country:
            self.score+=1

            self.i+=1
            
            pr = self.layer_certas.dataProvider()

            # Enter editing mode
            self.layer_certas.startEditing()
  
            fet = feat
          
            fet.setAttributes([feat["country"], feat["countryLabel"], feat["capitale"], feat["capitaleLabel"]])

            pr.addFeatures( [ fet ] )

            # Commit changes
            self.layer_certas.commitChanges()
            
            symbol = QgsSymbol.defaultSymbol(self.layer_certas.geometryType())
            path_green = os.path.join(os.path.join(cmd_folder, 'verde.svg'))
            new_symbol = QgsSvgMarkerSymbolLayer(path_green)
            new_symbol.setSize(5)

            # replace default symbol layer with the configured one
            symbol.changeSymbolLayer(0, new_symbol)

            self.layer_certas.renderer().setSymbol(symbol)
            
            
            layer_settings  = QgsPalLayerSettings()
            text_format = QgsTextFormat()

            text_format.setFont(QFont("Arial", 9))
            text_format.setSize(11)

            buffer_settings = QgsTextBufferSettings()
            buffer_settings.setEnabled(True)
            buffer_settings.setSize(1)
            buffer_settings.setColor(QColor("white"))

            text_format.setBuffer(buffer_settings)
            layer_settings.setFormat(text_format)

            layer_settings.isExpression = True

            layer_settings.fieldName = '''concat(to_string("''' + "countryLabel" + '''"),':' + to_string("''' + "capitaleLabel" + '''"))'''
            layer_settings.placement = 5

            layer_settings.enabled = True

            layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
            self.layer_certas.setLabelsEnabled(True)
            self.layer_certas.setLabeling(layer_settings)
            self.layer_certas.triggerRepaint()
            iface.layerTreeView().refreshLayerSymbology(self.layer_certas.id())

            if self.i==5:
              self.c =0

              self.back=1
              
              self.i=0

              self.first_start == True

              self.dlg2.deleteLater()
              
              self.dlg5 = BackDialog()

              self.dlg6 = FlagDialogExplorer(iface.mainWindow())

              self.dlg3=RestartDialog()
              self.dlg3.setWindowTitle("Capitals Game")
              self.dlg3.lineEdit.setAlignment(Qt.AlignCenter)
              self.dlg3.lineEdit.setText("You guessed " + str(self.score) + " out of 5!" )
              self.dlg3.pushButton.clicked.connect(self.run)
              self.dlg3.show()
              
            else:
              
              self.count_erradas=0
              
              self.rand = random.randint(0,183)
              while self.rand in self.lista_rand:
                self.rand = random.randint(0,183)

              self.lista_rand.append(self.rand)
              self.country=self.lista_paises_capitais[self.rand][2]
              self.capital=self.lista_paises_capitais[self.rand][4]

              self.dlg2.deleteLater()
              self.dlg2 = CountryDialog(iface.mainWindow())
              self.dlg2.setWindowTitle("Capitals Game")
              self.dlg2.setFixedSize(360, 125)
              self.dlg2.lineEdit.setAlignment(Qt.AlignCenter)
              self.dlg2.lineEdit.setText(self.capital)
              self.dlg2.show()
          
          else:
            self.count_erradas+=1
        
            if self.count_erradas==3:
              self.i+=1

              pr = self.layer_erradas.dataProvider()

              # Enter editing mode
              self.layer_erradas.startEditing()
              
              fet = self.lista_paises_capitais[self.rand][0]
            
              fet.setAttributes([self.lista_paises_capitais[self.rand][1], self.country, self.lista_paises_capitais[self.rand][3], self.capital])

              pr.addFeatures( [ fet ] )

              # Commit changes
              self.layer_erradas.commitChanges()
            
              symbol = QgsSymbol.defaultSymbol(self.layer_erradas.geometryType())
              path_red = os.path.join(os.path.join(cmd_folder, 'vermelho.svg'))
              
              new_symbol = QgsSvgMarkerSymbolLayer(path_red)
              new_symbol.setSize(7)

              # replace default symbol layer with the configured one
              symbol.changeSymbolLayer(0, new_symbol)

              self.layer_erradas.renderer().setSymbol(symbol)
              
              layer_settings  = QgsPalLayerSettings()
              text_format = QgsTextFormat()

              text_format.setFont(QFont("Arial", 9))
              text_format.setSize(11)

              buffer_settings = QgsTextBufferSettings()
              buffer_settings.setEnabled(True)
              buffer_settings.setSize(1)
              buffer_settings.setColor(QColor("white"))

              text_format.setBuffer(buffer_settings)
              layer_settings.setFormat(text_format)

              layer_settings.isExpression = True
              
              
              layer_settings.fieldName = '''concat(to_string("''' + "countryLabel" + '''"),':' + to_string("''' + "capitaleLabel" + '''"))'''
              
              layer_settings.placement = 5

              layer_settings.enabled = True

              layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
              self.layer_erradas.setLabelsEnabled(True)
              self.layer_erradas.setLabeling(layer_settings)
              self.layer_erradas.triggerRepaint()
              iface.layerTreeView().refreshLayerSymbology(self.layer_erradas.id())
              
              if self.i==5:
                self.c=0

                self.back=1

                self.i=0

                self.first_start == True
                self.dlg2.deleteLater()

                self.dlg5 = BackDialog()

                self.dlg6 = FlagDialogExplorer(iface.mainWindow())

                self.dlg3=RestartDialog()
                self.dlg3.setWindowTitle("Capitals Game")
                self.dlg3.lineEdit.setAlignment(Qt.AlignCenter)
                self.dlg3.lineEdit.setText("You guessed " + str(self.score) + " out of 5!" )
                self.dlg3.pushButton.clicked.connect(self.run)
                self.dlg3.show()
              else:
                self.count_erradas=0
              
                self.rand = random.randint(0,183)
                while self.rand in self.lista_rand:
                  self.rand = random.randint(0,183)

                self.lista_rand.append(self.rand)
                self.country=self.lista_paises_capitais[self.rand][2]
                self.capital=self.lista_paises_capitais[self.rand][4]

                self.dlg2.deleteLater()
                self.dlg2 = CountryDialog(iface.mainWindow())
                self.dlg2.setWindowTitle("Capitals Game")
                self.dlg2.setFixedSize(360, 125)
                self.dlg2.lineEdit.setAlignment(Qt.AlignCenter)
                self.dlg2.lineEdit.setText(self.capital)
                self.dlg2.show()
                  



    #function called when the user clicks on the map in the flags game. It sees if the user chose the right country that corresponds to the flag. If he did,
    #  they that feature is added to the layer "certas", otherwise the user has two more options. If the user gets the three choices wrong, then the feature 
    # is added to the layer "erradas". After five questions, the game ends and it shows a dialog with the score and the option to get back to the menu. 
    def callback2(self,featu):

      """Code called when the feature is selected by the user"""

      if featu["countryLabel"]==self.country:
        self.score+=1
        
        self.i+=1
        
        pr = self.layer_certas.dataProvider()

        # Enter editing mode
        self.layer_certas.startEditing()

        fet = featu
      
        fet.setAttributes([featu["country"], featu["countryLabel"], featu["capitale"], featu["capitaleLabel"], featu["flagimage"]])

        pr.addFeatures( [ fet ] )

        # Commit changes
        self.layer_certas.commitChanges()
        
        symbol = QgsSymbol.defaultSymbol(self.layer_certas.geometryType())
        path_green = os.path.join(os.path.join(cmd_folder, 'verde.svg'))
        new_symbol = QgsSvgMarkerSymbolLayer(path_green)
        new_symbol.setSize(5)

        # replace default symbol layer with the configured one
        symbol.changeSymbolLayer(0, new_symbol)

        self.layer_certas.renderer().setSymbol(symbol)
        
        
        layer_settings  = QgsPalLayerSettings()
        text_format = QgsTextFormat()

        text_format.setFont(QFont("Arial", 9))
        text_format.setSize(11)

        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor("white"))

        text_format.setBuffer(buffer_settings)
        layer_settings.setFormat(text_format)

        layer_settings.fieldName = "countryLabel"
        layer_settings.placement = 5

        layer_settings.enabled = True

        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        self.layer_certas.setLabelsEnabled(True)
        self.layer_certas.setLabeling(layer_settings)
        self.layer_certas.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(self.layer_certas.id())

        if self.i==5:
          self.f=0
          self.back=1
          self.i=0
        
          self.first_start == True
          self.dlg4.deleteLater()
          
          self.dlg5 = BackDialog()

          self.dlg6 = FlagDialogExplorer(iface.mainWindow())

          self.dlg3=RestartDialog()
          self.dlg3.setWindowTitle("Flags Game")
          self.dlg3.lineEdit.setAlignment(Qt.AlignCenter)
          self.dlg3.lineEdit.setText("You guessed " + str(self.score) + " out of 5!" )
          self.dlg3.pushButton.clicked.connect(self.run)
          self.dlg3.show()
          
        else:
          self.count_erradas=0
          
          self.rand = random.randint(0,183)
          while self.rand in self.lista_rand:
            self.rand = random.randint(0,183)

          self.lista_rand.append(self.rand)
          self.country=self.lista_paises_capitais[self.rand][2]
          self.capital=self.lista_paises_capitais[self.rand][4]
          self.flag=self.lista_paises_capitais[self.rand][5]

          self.dlg4.deleteLater()
          self.dlg4 = FlagDialog(iface.mainWindow())
          self.dlg4.setWindowTitle("Flags Game")
          self.dlg4.setFixedSize(350, 200)

          url=self.flag
          r = requests.get(url)
          
          if "svg" in self.flag:
            path_flag= os.path.join(os.path.join(cmd_folder, 'flag.svg'))
          
          elif "png" in self.flag:
            path_flag= os.path.join(os.path.join(cmd_folder, 'flag.png')) 
          
          else:
            path_flag= os.path.join(os.path.join(cmd_folder, 'flag.jpg'))
          
          with open(path_flag,"wb") as f:
            f.write(r.content)

          pixmap = QPixmap(path_flag)
          pixmap = pixmap.scaled(350, 200)
          self.dlg4.label.setPixmap(pixmap)
          self.dlg4.label.resize(pixmap.width(), pixmap.height())
          self.dlg4.label.setStyleSheet("background-color: white; border: 1px solid black;")
          self.dlg4.show()
    
        

      else:
        
        self.count_erradas+=1
        
        if self.count_erradas==3:

          self.i+=1

          pr = self.layer_erradas.dataProvider()

          # Enter editing mode
          self.layer_erradas.startEditing()
          
          fet = self.lista_paises_capitais[self.rand][0]
        
          fet.setAttributes([self.lista_paises_capitais[self.rand][1], self.country, self.lista_paises_capitais[self.rand][3], self.capital, self.flag])

          pr.addFeatures( [ fet ] )

          # Commit changes
          self.layer_erradas.commitChanges()

          #symbol.setColor(Qt.red)
          symbol = QgsSymbol.defaultSymbol(self.layer_erradas.geometryType())
          path_red = os.path.join(os.path.join(cmd_folder, 'vermelho.svg'))
          
          new_symbol = QgsSvgMarkerSymbolLayer(path_red)
          new_symbol.setSize(7)

          # replace default symbol layer with the configured one
          symbol.changeSymbolLayer(0, new_symbol)

          self.layer_erradas.renderer().setSymbol(symbol)
          
          layer_settings  = QgsPalLayerSettings()
          text_format = QgsTextFormat()

          text_format.setFont(QFont("Arial", 9))
          text_format.setSize(11)

          buffer_settings = QgsTextBufferSettings()
          buffer_settings.setEnabled(True)
          buffer_settings.setSize(1)
          buffer_settings.setColor(QColor("white"))

          text_format.setBuffer(buffer_settings)
          layer_settings.setFormat(text_format)

          layer_settings.fieldName = "countryLabel"
          layer_settings.placement = 5

          layer_settings.enabled = True

          layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
          self.layer_erradas.setLabelsEnabled(True)
          self.layer_erradas.setLabeling(layer_settings)
          self.layer_erradas.triggerRepaint()
          iface.layerTreeView().refreshLayerSymbology(self.layer_erradas.id())
          

          if self.i==5:
            self.f=0
            self.back=1
            self.i=0
          
            self.first_start == True
            self.dlg4.deleteLater()

            self.dlg5 = BackDialog()

            self.dlg6 = FlagDialogExplorer(iface.mainWindow())

            self.dlg3=RestartDialog()
            self.dlg3.setWindowTitle("Flags Game")
            self.dlg3.lineEdit.setAlignment(Qt.AlignCenter)
            self.dlg3.lineEdit.setText("You guessed " + str(self.score) + " out of 5!" )
            self.dlg3.pushButton.clicked.connect(self.run)
            self.dlg3.show()

          else:
            self.count_erradas=0
            
            self.rand = random.randint(0,183)
            while self.rand in self.lista_rand:
              self.rand = random.randint(0,183)

            self.lista_rand.append(self.rand)
            self.country=self.lista_paises_capitais[self.rand][2]
            self.capital=self.lista_paises_capitais[self.rand][4]
            self.flag=self.lista_paises_capitais[self.rand][5]

            self.dlg4.deleteLater()
            self.dlg4 = FlagDialog(iface.mainWindow())
            self.dlg4.setWindowTitle("Flags Game")
            self.dlg4.setFixedSize(350, 200)

            url=self.flag
            r = requests.get(url)
            
            if "svg" in self.flag:
              path_flag= os.path.join(os.path.join(cmd_folder, 'flag.svg'))
            
            elif "png" in self.flag:
              path_flag= os.path.join(os.path.join(cmd_folder, 'flag.png')) 
            
            else:
              path_flag= os.path.join(os.path.join(cmd_folder, 'flag.jpg'))
            
            with open(path_flag,"wb") as f:
              f.write(r.content)

            pixmap = QPixmap(path_flag)
            pixmap = pixmap.scaled(350, 200)
            self.dlg4.label.setPixmap(pixmap)
            self.dlg4.label.resize(pixmap.width(), pixmap.height())
            self.dlg4.label.setStyleSheet("background-color: white; border: 1px solid black;")
            self.dlg4.show()
                  
                

    #function called when the user clicks on the map in the explorer option. The user click in a country and it appears the flag of that country and the name
    # of the country and its capital as well. 
    def callback3(self, featur):
      
      self.f_explorer=1

      if self.dlg6.isVisible():
        self.dlg6.deleteLater()

      if featur["capitaleLabel"] not in self.lista_explorer:
        
        self.lista_explorer.append(featur["capitaleLabel"])

        self.flag = featur["flagimage"]

        pr = self.layer_certas.dataProvider()

        # Enter editing mode
        self.layer_certas.startEditing()

        fet = featur
      
        fet.setAttributes([featur["country"], featur["countryLabel"], featur["capitale"], featur["capitaleLabel"], self.flag])

        pr.addFeatures( [ fet ] )
        # Commit changes
        self.layer_certas.commitChanges()
      
        symbol = QgsSymbol.defaultSymbol(self.layer_certas.geometryType())
        path_red = os.path.join(os.path.join(cmd_folder, 'vermelho.svg'))
        new_symbol = QgsSvgMarkerSymbolLayer(path_red)
        new_symbol.setSize(5)

        # replace default symbol layer with the configured one
        symbol.changeSymbolLayer(0, new_symbol)

        self.layer_certas.renderer().setSymbol(symbol)
        
        
        layer_settings  = QgsPalLayerSettings()
        text_format = QgsTextFormat()

        text_format.setFont(QFont("Arial", 9))
        text_format.setSize(11)

        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor("white"))

        text_format.setBuffer(buffer_settings)
        layer_settings.setFormat(text_format)

        layer_settings.isExpression = True

        layer_settings.fieldName = '''concat(to_string("''' + "countryLabel" + '''"),':' + to_string("''' + "capitaleLabel" + '''"))'''
        layer_settings.placement = 5

        layer_settings.enabled = True

        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        self.layer_certas.setLabelsEnabled(True)
        self.layer_certas.setLabeling(layer_settings)
        self.layer_certas.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(self.layer_certas.id())

        self.dlg6 = FlagDialogExplorer(iface.mainWindow())
        self.dlg6.setWindowTitle("Explorer")
        self.dlg6.setFixedSize(350, 200)

        url=self.flag
        r = requests.get(url)
        
        if "svg" in self.flag:
          path_flag= os.path.join(os.path.join(cmd_folder, 'flag.svg'))
        
        elif "png" in self.flag:
          path_flag= os.path.join(os.path.join(cmd_folder, 'flag.png')) 
        
        else:
          path_flag= os.path.join(os.path.join(cmd_folder, 'flag.jpg')) 
        
        with open(path_flag,"wb") as f:
          f.write(r.content)

        pixmap = QPixmap(path_flag)
        pixmap = pixmap.scaled(350, 200)
        self.dlg6.label.setPixmap(pixmap)
        self.dlg6.label.resize(pixmap.width(), pixmap.height())
        self.dlg6.label.setStyleSheet("background-color: white; border: 1px solid black;")
        self.dlg6.show()
      
      else:
        self.flag = featur["flagimage"]

        self.dlg6 = FlagDialogExplorer(iface.mainWindow())
        self.dlg6.setWindowTitle("Explorer")
        self.dlg6.setFixedSize(350, 200)

        url=self.flag
        r = requests.get(url)
        
        if "svg" in self.flag:
          path_flag= os.path.join(os.path.join(cmd_folder, 'flag.svg'))
        
        elif "png" in self.flag:
          path_flag= os.path.join(os.path.join(cmd_folder, 'flag.png')) 
        
        else:
          path_flag= os.path.join(os.path.join(cmd_folder, 'flag.jpg')) 
        
        with open(path_flag,"wb") as f:
          f.write(r.content)

        pixmap = QPixmap(path_flag)
        pixmap = pixmap.scaled(350, 200)
        self.dlg6.label.setPixmap(pixmap)
        self.dlg6.label.resize(pixmap.width(), pixmap.height())
        self.dlg6.label.setStyleSheet("background-color: white; border: 1px solid black;")
        self.dlg6.show()



    #function called when the user clicks on the explorer option. The user has the chance to click in different countries. When a country is clicked,
    #the fucntion callback3 is called.
    def explore(self):

      self.back2=1

      self.s+=1
      
      self.dlg3=RestartDialog()
      self.dlg6 = FlagDialogExplorer()

      if self.dlg.isVisible():
        self.dlg.deleteLater()
      
      self.dlg5 = BackDialog()
      self.dlg5.setWindowTitle("Explorer")
      self.dlg5.setFixedSize(240, 60)
      self.dlg5.pushButton.setText("Back to Menu")
      self.dlg5.pushButton.clicked.connect(self.run)
      
      self.dlg5.show()

      if len(QgsProject.instance().mapLayersByName("erradas")) != 0:
        QgsProject.instance().removeMapLayers( [self.layer_erradas.id()] )
      else:
        pass
      
      if len(QgsProject.instance().mapLayersByName("certas")) != 0:
        QgsProject.instance().removeMapLayers( [self.layer_certas.id()] )
      else:
        pass

      vlayer=iface.mapCanvas().layers()[0]

      if self.ambiente==0:
      
        self.canvas.setCanvasColor(QtGui.QColor(135,206,250))
        
        single_symbol_renderer = vlayer.renderer()

        symbol = single_symbol_renderer.symbol()

        symbol.setColor(Qt.black)



        vlayer.triggerRepaint()

        vlayer1=iface.mapCanvas().layers()[1]

        single_symbol_renderer = vlayer1.renderer()

        symbol = single_symbol_renderer.symbol()

        symbol.setColor(QtGui.QColor(245,222,179))



        vlayer1.triggerRepaint()

        self.ambiente=1
      
      else:
        pass

      self.layer_certas = QgsVectorLayer("Point", "certas", "memory")
      pr = self.layer_certas.dataProvider()
      # Enter editing mode
      self.layer_certas.startEditing()
      pr.addAttributes( [ QgsField("country", QVariant.String),
          QgsField("countryLabel",  QVariant.String),
          QgsField("capitale", QVariant.String) , QgsField("capitaleLabel", QVariant.String), QgsField("flagimage", QVariant.String)] )
      

      QgsProject.instance().addMapLayer(self.layer_certas)

      self.lista_explorer=[]

      features=self.layer_certas.getFeatures()


      for f in features:
        self.lista_explorer.append(f["capitaleLabel"])

      self.feature_identifier = QgsMapToolIdentifyFeature(self.canvas)
      
      # indicates the layer on which the selection will be done
      self.feature_identifier.setLayer(vlayer)
      
      # use the callback as a slot triggered when the user identifies a feature
      self.feature_identifier.featureIdentified.connect(self.callback3)

      # activation of the map tool
      self.canvas.setMapTool(self.feature_identifier)

      



    #function called when the user clicks on the capitals game. The user has the chance to click in different countries. When a country is clicked,
    #the function callback is called. In this function a random country and its capital are chosen and then a dialog appears showing that the user needs to choose
    #the country of the capital that was chosen.
    def capitals_game(self):
      self.c=1

      self.s+=1

      if self.dlg.isVisible():
        self.dlg.deleteLater()

      if len(QgsProject.instance().mapLayersByName("erradas")) != 0:
        QgsProject.instance().removeMapLayers( [self.layer_erradas.id()] )
      else:
        pass
      
      if len(QgsProject.instance().mapLayersByName("certas")) != 0:
        QgsProject.instance().removeMapLayers( [self.layer_certas.id()] )
      else:
        pass
      
      vlayer=iface.mapCanvas().layers()[0]

      if self.ambiente==0:
        
        single_symbol_renderer = vlayer.renderer()

        symbol = single_symbol_renderer.symbol()

        symbol.setColor(Qt.black)

        vlayer.triggerRepaint()

        vlayer1=iface.mapCanvas().layers()[1]
        
        single_symbol_renderer = vlayer1.renderer()

        symbol = single_symbol_renderer.symbol()

        symbol.setColor(QtGui.QColor(245,222,179))

        vlayer1.triggerRepaint()

        self.canvas.setCanvasColor(QtGui.QColor(135,206,250))

        self.ambiente=1
      
      else:
        pass
      
      self.dlg2 = CountryDialog(iface.mainWindow())
      
      self.dlg2.setWindowTitle("Capitals Game")
      
      self.dlg2.setFixedSize(360, 125)
      
      features = vlayer.getFeatures()
      
      self.lista_paises_capitais=[]
      
      for feature in features:
          self.lista_paises_capitais.append((feature,feature["country"], feature["countryLabel"], feature["capitale"], feature["capitaleLabel"]))

      self.rand = random.randint(0,183)
      
      while self.rand in self.lista_rand:
        self.rand = random.randint(0,183)
      
      self.lista_rand.append(self.rand)
      
      self.country=self.lista_paises_capitais[self.rand][2]
      
      self.capital=self.lista_paises_capitais[self.rand][4]
      

      self.layer_certas = QgsVectorLayer("Point", "certas", "memory")
      
      pr = self.layer_certas.dataProvider()
      
      # Enter editing mode
      self.layer_certas.startEditing()
      
      pr.addAttributes( [ QgsField("country", QVariant.String),
          QgsField("countryLabel",  QVariant.String),
          QgsField("capitale", QVariant.String) , QgsField("capitaleLabel", QVariant.String) ] )
        
      
      self.layer_erradas = QgsVectorLayer("Point", "erradas", "memory")
      
      pr = self.layer_erradas.dataProvider()
      
      # Enter editing mode
      self.layer_erradas.startEditing()

      pr.addAttributes( [ QgsField("country", QVariant.String),
          QgsField("countryLabel",  QVariant.String),
          QgsField("capitale", QVariant.String) , QgsField("capitaleLabel", QVariant.String) ] )
        
      QgsProject.instance().addMapLayer(self.layer_certas)

      QgsProject.instance().addMapLayer(self.layer_erradas)

      self.dlg2.lineEdit.setAlignment(Qt.AlignCenter)

      self.dlg2.lineEdit.setText(self.capital)

      self.dlg2.show()
  
      self.feature_identifier = QgsMapToolIdentifyFeature(self.canvas)
      
      # indicates the layer on which the selection will be done
      self.feature_identifier.setLayer(vlayer)
      
      # use the callback as a slot triggered when the user identifies a feature
      self.feature_identifier.featureIdentified.connect(self.callback)

      # activation of the map tool
      self.canvas.setMapTool(self.feature_identifier)
      


    #function called when the user clicks on the flags game. The user has the chance to click in different countries. When a country is clicked,
    #the function callback2 is called. In this function a random country and its flag are chosen and then a dialog appears showing that the user needs to choose
    #the country of the flag that was chosen.
    def flags_game(self):

      self.f=1

      self.s+=1

      if self.dlg.isVisible():

        self.dlg.deleteLater()
      
      
      if len(QgsProject.instance().mapLayersByName("erradas")) != 0:

        QgsProject.instance().removeMapLayers( [self.layer_erradas.id()] )

      else:
        pass
      
      if len(QgsProject.instance().mapLayersByName("certas")) != 0:

        QgsProject.instance().removeMapLayers( [self.layer_certas.id()] )
      else:
        pass

      vlayer=iface.mapCanvas().layers()[0]

      if self.ambiente==0:
      
        single_symbol_renderer = vlayer.renderer()

        symbol = single_symbol_renderer.symbol()

        symbol.setColor(Qt.black)

        vlayer.triggerRepaint()

        vlayer1=iface.mapCanvas().layers()[1]

        single_symbol_renderer = vlayer1.renderer()

        symbol = single_symbol_renderer.symbol()

        symbol.setColor(QtGui.QColor(245,222,179))

        vlayer1.triggerRepaint()

        self.canvas.setCanvasColor(QtGui.QColor(135,206,250))

        self.ambiente=1
      
      else:
        pass
      
      self.dlg4 = FlagDialog(iface.mainWindow())
      
      self.dlg4.setFixedSize(350, 200)
      
      features = vlayer.getFeatures()
      
      self.lista_paises_capitais=[]
      for feature in features:
          self.lista_paises_capitais.append((feature,feature["country"], feature["countryLabel"], feature["capitale"], feature["capitaleLabel"], feature["flagimage"]))

      self.rand = random.randint(0,183)
      while self.rand in self.lista_rand:
        self.rand = random.randint(0,183)
     
      self.lista_rand.append(self.rand)
      
      self.country=self.lista_paises_capitais[self.rand][2]
      
      self.capital=self.lista_paises_capitais[self.rand][4]
      
      self.flag=self.lista_paises_capitais[self.rand][5]
      

      self.layer_certas = QgsVectorLayer("Point", "certas", "memory")

      pr = self.layer_certas.dataProvider()

      # Enter editing mode
      self.layer_certas.startEditing()

      pr.addAttributes( [ QgsField("country", QVariant.String),
          QgsField("countryLabel",  QVariant.String),
          QgsField("capitale", QVariant.String) , QgsField("capitaleLabel", QVariant.String), QgsField("flagimage", QVariant.String) ] )
        
      self.layer_erradas = QgsVectorLayer("Point", "erradas", "memory")

      
      pr = self.layer_erradas.dataProvider()
      # Enter editing mode
      self.layer_erradas.startEditing()
      
      pr.addAttributes( [ QgsField("country", QVariant.String),
          QgsField("countryLabel",  QVariant.String),
          QgsField("capitale", QVariant.String) , QgsField("capitaleLabel", QVariant.String), QgsField("flagimage", QVariant.String) ] )
        
      QgsProject.instance().addMapLayer(self.layer_certas)
      
      QgsProject.instance().addMapLayer(self.layer_erradas)


      url=self.flag
      r = requests.get(url)
      
      if "svg" in self.flag:
        path_flag= os.path.join(os.path.join(cmd_folder, 'flag.svg'))
            
      elif "png" in self.flag:
        path_flag= os.path.join(os.path.join(cmd_folder, 'flag.png')) 
      
      else:
        path_flag= os.path.join(os.path.join(cmd_folder, 'flag.jpg'))
      
     
      with open(path_flag,"wb") as f:
        f.write(r.content)

      pixmap = QPixmap(path_flag)
      
      pixmap = pixmap.scaled(350, 200)
      
      self.dlg4.label.setPixmap(pixmap)
      
      self.dlg4.label.setAlignment(QtCore.Qt.AlignCenter)
      
      self.dlg4.label.resize(pixmap.width(), pixmap.height())
      
      self.dlg4.label.setStyleSheet("background-color: white; border: 1px solid black;")
      
      self.dlg4.show()
  

      self.feature_identifier = QgsMapToolIdentifyFeature(self.canvas)
      
      # indicates the layer on which the selection will be done
      self.feature_identifier.setLayer(vlayer)
      
      # use the callback as a slot triggered when the user identifies a feature
      self.feature_identifier.featureIdentified.connect(self.callback2)

      # activation of the map tool
      self.canvas.setMapTool(self.feature_identifier)



    #function called when the user clicks on the exit option. In this option the game is ended. All the layers are removed and the main dialog is also removed. 
    def exit(self):
      if self.dlg.isVisible():

        self.dlg.deleteLater()
      
      if len(QgsProject.instance().mapLayersByName("countries")) != 0:

          QgsProject.instance().removeMapLayers( [self.countries.id()] )

      else:
        pass
      
      if len(QgsProject.instance().mapLayersByName("World Map")) != 0:

        QgsProject.instance().removeMapLayers( [self.world.id()] )

      else:
        pass

      self.canvas.setCanvasColor(QtGui.QColor(255,255,255))

      self.ambiente=0

      self.i=0
      
      self.count_erradas=0
      
      self.lista_rand=[]

      self.lista_explorer=[]

      
    #Function called when the logo of GeoQuigiz is pressed. A user can click the logo anytime when he is playing the game, whether he is in the main dialog
    #or in the middle of the explorer/capitals/flags games.
    def start(self):

      if self.c==1 and self.f==0 and self.back == 0 and self.back2==0 and self.f_explorer==0:
        self.dlg2.deleteLater()
        self.s=1
        self.dlg3= RestartDialog()
        self.dlg5 = BackDialog()
        self.dlg6 = FlagDialogExplorer()

        if self.dlg3.isVisible():
          self.dlg3.deleteLater()

        if self.dlg6.isVisible():
          self.dlg6.deleteLater()
        
        if self.dlg5.isVisible():
          self.dlg5.deleteLater()
        
        self.run()
      
      elif self.c==0 and self.f==1 and self.back == 0 and self.back2==0 and self.f_explorer==0:
        self.dlg4.deleteLater()
        self.s=1
        self.dlg3= RestartDialog()
        self.dlg5 = BackDialog()
        self.dlg6 = FlagDialogExplorer()

        if self.dlg3.isVisible():
          self.dlg3.deleteLater()

        if self.dlg6.isVisible():
          self.dlg6.deleteLater()
        
        if self.dlg5.isVisible():
          self.dlg5.deleteLater()
        
        self.run()

      elif self.c==0 and self.f==0 and self.back == 1 and self.back2==0 and self.f_explorer==0:
        self.dlg3.deleteLater()
        self.s=1
        self.dlg3= RestartDialog()
        self.dlg5 = BackDialog()
        self.dlg6 = FlagDialogExplorer()

        if self.dlg3.isVisible():
          self.dlg3.deleteLater()

        if self.dlg6.isVisible():
          self.dlg6.deleteLater()
        
        if self.dlg5.isVisible():
          self.dlg5.deleteLater()
        
        self.run()
      
      elif self.c==0 and self.f==0 and self.back == 0 and self.back2==1 and self.f_explorer==0:
        self.dlg5.deleteLater()
        self.s=1
        self.dlg3= RestartDialog()
        self.dlg5 = BackDialog()
        self.dlg6 = FlagDialogExplorer()

        if self.dlg3.isVisible():
          self.dlg3.deleteLater()

        if self.dlg6.isVisible():
          self.dlg6.deleteLater()
        
        if self.dlg5.isVisible():
          self.dlg5.deleteLater()
        
        self.run()
      
      elif self.c==0 and self.f==0 and self.back == 0 and self.back2==1 and self.f_explorer==1:
        self.dlg5.deleteLater()
        self.dlg6.deleteLater()
        self.s=1
        self.dlg3= RestartDialog()
        self.dlg5 = BackDialog()
        self.dlg6 = FlagDialogExplorer()

        if self.dlg3.isVisible():
          self.dlg3.deleteLater()

        if self.dlg6.isVisible():
          self.dlg6.deleteLater()
        
        if self.dlg5.isVisible():
          self.dlg5.deleteLater()
        
        self.run()
      
      else:
        self.s=1
        self.dlg3= RestartDialog()
        self.dlg5 = BackDialog()
        self.dlg6 = FlagDialogExplorer()

        if self.dlg3.isVisible():
          self.dlg3.deleteLater()

        if self.dlg6.isVisible():
          self.dlg6.deleteLater()
        
        if self.dlg5.isVisible():
          self.dlg5.deleteLater()
        
        self.run()



    #function called when the user clicks on the GeoQuigiz logo. The countries and world layers are set and then the main dialog appears. This dialog has
    #the explorer option where the user can click on countries and then its flag, name and capitals appears. It also has the capitals game where the user
    #plays a game to see if he knows the capitals of some countries. There are 5 questions and in the end, his score is shown. The main dialog also has the
    #flags game where the user plays a game to see if he knows the flags of some countries. There are 5 questions and in the end, his score is shown.
    #On the bottom, there is the exit option. When the users click it, the game ends, all the layers are removed and the mais dialog disappears.
    def run(self):

      self.c=0
      self.f=0
      self.back=0
      self.f_explorer=0
      self.back2=0
      
      self.score=0

      self.canvas = iface.mapCanvas()

      if len(QgsProject.instance().mapLayersByName("World Map")) == 0:
        
        path = os.path.join(os.path.join(cmd_folder, 'mundo/ne_10m_admin_0_countries.shp'))
        
        self.world = QgsVectorLayer(path, "World Map", "ogr")

        QgsProject.instance().addMapLayer(self.world)
      

      if len(QgsProject.instance().mapLayersByName("countries")) == 0:

        path2= os.path.join(os.path.join(cmd_folder, 'world_game.csv'))

        uri = "file:///{}?encoding={}&delimiter={}&crs=epsg:4326&wktField={}".format(path2,"UTF-8",",", "gps")

        self.countries = QgsVectorLayer(uri, "countries", "delimitedtext")

        QgsProject.instance().addMapLayer(self.countries)

      if self.s==1:
        pass

      else:
      
        if self.dlg3.isVisible():
          self.dlg3.deleteLater()

        if self.dlg6.isVisible():
          self.dlg6.deleteLater()
        
        if self.dlg5.isVisible():
          self.dlg5.deleteLater()
        
    
      self.first_start = False

      self.dlg = CapitalsGameDialog()

      self.dlg.setWindowTitle("GeoQuigiz")

      self.dlg.setFixedSize(600, 350)

      self.dlg.label_4.resize(700,50)


      if len(QgsProject.instance().mapLayersByName("erradas")) != 0:

        QgsProject.instance().removeMapLayers( [self.layer_erradas.id()] )

      else:
        pass
      
      if len(QgsProject.instance().mapLayersByName("certas")) != 0:

        QgsProject.instance().removeMapLayers( [self.layer_certas.id()] )

      else:
        pass
      
      self.i=0
        
      self.count_erradas=0

      self.lista_rand=[]
      
      game_list=["CapitalsGame", "FlagsGame"]

      self.dlg.pushButton.clicked.connect(self.explore)

      self.dlg.pushButton_2.setText(game_list[0])

      self.dlg.pushButton_2.clicked.connect(self.capitals_game)

      self.dlg.pushButton_3.setText(game_list[1])

      self.dlg.pushButton_3.clicked.connect(self.flags_game)

      self.dlg.pushButton_4.setText("Exit Game")

      self.dlg.pushButton_4.clicked.connect(self.exit)
      
      self.dlg.show()