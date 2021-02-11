from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTabWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
import sys
import os

from Analyzer import Analyzer
from InputTabWidget import InputTabWidget
from AnalysisTabWidget import AnalysisTabWidget

from RatioBuilding import RatioBuilder
import DataFolderUtil
import warnings


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 1200, 1000)
        self.setWindowTitle("U/Th Data Analysis")
        self.setWindowIcon(QIcon('logo/PUA_logo_HiRes.png'))

        self.tabWidget = QTabWidget()

        self.ratioBuilder = RatioBuilder()
        self.analyzer = Analyzer()

        self.inputTab = InputTabWidget(self, self.ratioBuilder)
        self.analysisTab = AnalysisTabWidget(self, self.ratioBuilder, self.analyzer)
        self.tabWidget.addTab(self.inputTab, 'Input')
        self.tabWidget.addTab(self.analysisTab, 'Analysis')
        self.setCentralWidget(self.tabWidget)

        self.inputTab.dirNameEdit.textChanged.connect(lambda: self.setPaths(self.inputTab.dirNameEdit.text()))

        self.initMenu()
        self.show()

    def initMenu(self):
        # Open file action
        extractAction = QtWidgets.QAction('Open', self)
        extractAction.setShortcut('Ctrl+O')
        extractAction.setStatusTip('Open a file')
        extractAction.triggered.connect(self.inputTab.setDirectory)

        showHelpAction = QtWidgets.QAction('Nutzung', self)
        showHelpAction.setStatusTip('Shows how to use the program')
        showHelpAction.triggered.connect(self.showHelp)


        # menu
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractAction)
        helpMenu = mainMenu.addMenu('&Help')
        helpMenu.addAction(showHelpAction)

    def setPaths(self, path):
        if not os.path.isdir(path):
            return

        self.analysisTab.searchMetadataFile(path)
        self.analyzer.set_path(path)


    def calcRatios(self, path):
        DataFolderUtil.createDataFolders(path)
        self.ratioBuilder.set_path(path)
        self.ratioBuilder.set_constants(self.inputTab.get_constants())
        self.ratioBuilder.set_specific_constants(self.inputTab.get_specific_constants())
        self.ratioBuilder.yhas_uranium()
        self.ratioBuilder.yhas_thorium()
        self.ratioBuilder.calc_blank_correction()
        self.ratioBuilder.data_correction()

    def startAnalysis(self, metadatapath):
        self.analyzer.set_path(self.ratioBuilder.data_root_folder)
        self.analyzer.set_constants(self.inputTab.get_constants())
        self.analyzer.set_metadata(metadatapath)

        self.analyzer.calc_concentrations(self.ratioBuilder.ratios)

        self.analysisTab.display()

    def showHelp(self):
        helpBox = QMessageBox()
        helpBox.setIcon(QMessageBox.Information)
        helpBox.setWindowTitle('How to use')
        helpBox.setText("Nutzung (Reihenfolge beachten):\n" +
                        "1. Im Input-Tab den Datenordner auswählen.\n" +
                        "2. Falls noch nicht vorhanden: Konstanten laden oder neu erstellen.\n" +
                        "3. Falls nötig messungsspezifische Konstanten einstellen.\n"
                        "4. Im Input-Tab auf \"Run\" klicken, um die Isotopenverhältnise zu berechnen.\n" +
                        "    Im Datenordner sollten nun die Dateien \"PrBlank.xlsx\", \"Ratios.xlsx\" und\n" +
                        "    \"Ratios_add.xlsx\" sein.\n" +
                        "5. Im Analysis-Tab eine Metadaten-Datei laden oder neu erstellen.\n" +
                        "6. Auf \"Start Analysis\" klicken.\n" +
                        "7. Im Datenordner sollte nun die Datei \"Results.xlsx\" erstellt sein.\n"
                        "\n" +
                        "Falls es Probleme beim Einlesen der Daten gibt, bitte den Beispiel ordner\n" +
                        "als Vorlage nehmen.\n" +
                        "Bei weiteren Fragen oder Problemen bitte @fabi anschreiben auf Mattermost :)")
        helpBox.exec_()

    def close_application(self):
        sys.exit()

import re

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())