from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTabWidget, QMessageBox, QStyleFactory
from PyQt5.QtGui import QIcon
import sys
import os

from Analyzer import Analyzer
from InputTabWidget import InputTabWidget
from AnalysisTabWidget import AnalysisTabWidget

from RatioBuilding import RatioBuilder
import DataFolderUtil
import Util
import warnings
import webbrowser
from Settings import Settings


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 1200, 1000)
        self.setWindowTitle("U/Th Data Analysis")
        self.setWindowIcon(QIcon('logo/PUA_logo_HiRes.png'))

        self.settings = Settings()

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
        self.change_style(self.settings['style'])

        self.show()

    def initMenu(self):
        # Open file action
        extractAction = QtWidgets.QAction('Open', self)
        extractAction.setShortcut('Ctrl+O')
        extractAction.setStatusTip('Open a file')
        extractAction.triggered.connect(self.inputTab.setDirectory)

        closeAction = QtWidgets.QAction('Exit', self)
        closeAction.setStatusTip('Closes the program')
        closeAction.triggered.connect(self.close_application)

        showHelpAction = QtWidgets.QAction('Nutzung', self)
        showHelpAction.setStatusTip('Shows how to use the program')
        showHelpAction.triggered.connect(self.showHelp)

        openGitHubAction = QtWidgets.QAction('GitHub', self)
        openGitHubAction.setStatusTip('Opens the GitHub repository of this GUI')
        openGitHubAction.triggered.connect(self.openGitHub)

        fullscreenAction = QtWidgets.QAction('Toggle fullscreen', self)
        fullscreenAction.setShortcut('F11')
        fullscreenAction.triggered.connect(self.toggle_fullscreen)

        self.styleActions = {}
        for style in QStyleFactory.keys():
            styleAction = QtWidgets.QAction(style, self)
            styleAction.triggered.connect(self.get_change_style_action(style))
            styleAction.setCheckable(True)
            self.styleActions[style] = styleAction


        # menu
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractAction)
        fileMenu.addAction(closeAction)
        viewMenu = mainMenu.addMenu('&View')
        viewMenu.addAction(fullscreenAction)
        styleMenu = viewMenu.addMenu('&Style')
        for action in self.styleActions.values():
            styleMenu.addAction(action)
        helpMenu = mainMenu.addMenu('&Help')
        helpMenu.addAction(showHelpAction)
        helpMenu.addAction(openGitHubAction)

    def setPaths(self, path):
        if not os.path.isdir(path):
            return

        self.analysisTab.searchMetadataFile(path)
        self.analyzer.set_path(path)


    def calcRatios(self, path):
        DataFolderUtil.createDataFolders(path)
        DataFolderUtil.removeUnnecessaryFiles(path)
        self.ratioBuilder.set_path(path)
        constants = Util.load_constants(self.inputTab.get_constants_path())
        self.ratioBuilder.set_constants(constants)
        self.ratioBuilder.set_specific_constants(self.inputTab.get_specific_constants())
        self.ratioBuilder.data_correction()

    def startAnalysis(self, metadatapath):
        self.analyzer.set_path(self.ratioBuilder.data_root_folder)
        constants = Util.load_constants(self.inputTab.get_constants_path())
        self.analyzer.set_constants(constants)
        self.analyzer.set_metadata(metadatapath, self.ratioBuilder.ratios)
        try:
            self.analyzer.calc_concentrations(self.ratioBuilder.ratios)
            self.analysisTab.display()
        except PermissionError:
            self.analysisTab.display()
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle('Permission error')
            error_dialog.setText('Could not save \"Results.xlsx\". Please close the related \"Results.xlsx\" file if it is open.')
            error_dialog.exec_()


    def showHelp(self):
        helpBox = QMessageBox()
        helpBox.setIcon(QMessageBox.Information)
        helpBox.setWindowTitle('How to use')
        helpBox.setText("Nutzung (Reihenfolge beachten):\n\n" +
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
                        "Falls es Probleme beim Einlesen der Daten gibt, bitte den Beispiel"
                        "ordner als Vorlage nehmen. Bei weiteren Fragen oder Problemen bitte "
                        "@fabi anschreiben auf Mattermost oder Email an f.kontor@stud.uni-heidelberg.de.")
        helpBox.exec_()

    def get_change_style_action(self, style):
        return lambda: self.change_style(style)

    def change_style(self, style):
        if style in QStyleFactory.keys():
            app = QtWidgets.QApplication.instance()
            app.setStyle(style)
            self.settings['style'] = style
            for action in self.styleActions.values():
                action.setChecked(False)
            self.styleActions[style].setChecked(True)
        else:
            style = QStyleFactory.keys()[0]
            app = QtWidgets.QApplication.instance()
            app.setStyle(style)
            self.settings['style'] = style
            for action in self.styleActions.values():
                action.setChecked(False)
            self.styleActions[style].setChecked(True)

    def toggle_fullscreen(self):
        if self.windowState() & QtCore.Qt.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()

    def openGitHub(self):
        webbrowser.open('https://github.com/zebleck/BachelorGUI')

    def close_application(self):
        sys.exit()

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())