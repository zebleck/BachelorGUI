from PyQt5.QtWidgets import QGridLayout, QGroupBox, QLineEdit, QLabel, QPushButton, \
    QMessageBox, QHBoxLayout, QFileDialog, QTableView, QHeaderView, QCheckBox, QWidget
from PyQt5 import QtGui
import os
from DataFrameModel import DataFrameModel
from MetadataDialog import MetadataDialog


class AnalysisTabWidget(QWidget):
    def __init__(self, window, ratioBuilder, analyzer):
        super(AnalysisTabWidget, self).__init__()
        self.window = window

        self.ratioBuilder = ratioBuilder
        self.analyzer = analyzer

        self.currentRatiosFolder = None

        self.initSettingsBox()
        self.initResultsBox()

        layout = QGridLayout()
        layout.addWidget(self.settingsBox, 0, 0)
        layout.addWidget(self.resultsBox, 1, 0)

        self.setLayout(layout)

    ''' +-----------------------------+ '''
    ''' |       Settings-Code         | '''
    ''' +-----------------------------+ '''

    def initSettingsBox(self):
        self.settingsBox = QGroupBox('Settings')
        #self.settingsBox.setMaximumHeight(400)

        self.metadataFileEdit = QLineEdit()
        self.loadFileButton = QPushButton('Load')
        self.loadFileButton.clicked.connect(self.setMetadataFile)
        self.createButton = QPushButton('Create')
        self.createButton.clicked.connect(self.createMetadata)
        self.editButton = QPushButton('Edit')
        self.editButton.clicked.connect(self.editMetadata)
        self.runAnalysisButton = QPushButton('Start Analysis')
        self.runAnalysisButton.clicked.connect(self.runEvent)

        topLayout = QHBoxLayout()
        topLayout.addWidget(QLabel('Metadata:'))
        topLayout.addWidget(self.metadataFileEdit)
        topLayout.addWidget(self.loadFileButton)
        topLayout.addWidget(self.createButton)
        topLayout.addWidget(self.editButton)
        topLayout.addWidget(self.runAnalysisButton)
        topLayoutWidget = QWidget()
        topLayoutWidget.setLayout(topLayout)

        layout = QGridLayout()
        layout.addWidget(topLayoutWidget, 0, 0)

        self.settingsBox.setLayout(layout)

    def setMetadataFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path, _ = QFileDialog.getOpenFileName(self, 'Select metadata file', "", "Metadata/Wägeprotokolle (*.csv *.xlsx)", options=options)

        if not os.path.isfile(path):
            return

        self.metadataFileEdit.setText(path)

    def searchMetadataFile(self, path):
        self.currentRatiosFolder = path
        for entry in os.listdir(path):
            entrypath = os.path.join(path, entry)
            if os.path.isfile(entrypath) and entry.endswith('.csv'):
                self.metadataFileEdit.setText(os.path.normpath(entrypath))
                return
            elif os.path.isfile(entrypath) and entry.endswith('.xlsx') and 'Wägeprotokoll' in entry:
                self.metadataFileEdit.setText(os.path.normpath(entrypath))
                return

    def createMetadata(self):
        dialog = MetadataDialog(self, folderPath=self.currentRatiosFolder)
        dialog.exec_()

    def editMetadata(self):
        path = self.metadataFileEdit.text()
        if os.path.isfile(path) and path.endswith('.xlsx'):
            QMessageBox.critical(self, 'Not valid', 'Can only edit .csv metadata files.')
            return
        elif not os.path.isfile(path) or not path.endswith('.csv'):
            QMessageBox.critical(self, 'Not valid', 'Please select a valid metadata file (*.csv).',
                                 QMessageBox.Ok)
            return
        dialog = MetadataDialog(self, folderPath=self.currentRatiosFolder, filePath=path)
        dialog.exec_()

    def runEvent(self):
        path = self.metadataFileEdit.text()
        if not os.path.isfile(path) or (not path.endswith('.csv') and not path.endswith('.xlsx')):
            QMessageBox.critical(self, 'Not valid', 'Please select a valid metadata file (*.csv or *.xlsx).', QMessageBox.Ok)
        elif self.ratioBuilder.ratios is None:
            QMessageBox.critical(self, 'Not so fast!', 'Please run the ratio calculation first.', QMessageBox.Ok)
        else:
            self.window.startAnalysis(path)


    ''' +-----------------------------+ '''
    ''' |        Results-Code         | '''
    ''' +-----------------------------+ '''

    def initResultsBox(self):
        self.resultsBox = QGroupBox('Results')
        #self.resultsBox.setMaximumHeight(400)

        self.resultTable = QTableView()
        self.resultTable.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.resultTable.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

        layout = QGridLayout()
        layout.addWidget(self.resultTable, 0, 0)

        self.resultsBox.setLayout(layout)

    def display(self):
        self.resultTable.setModel(DataFrameModel(self.analyzer.results, self.analyzer.standard, showIndex=False))
        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)