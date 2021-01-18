from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QLineEdit, QLabel, QPushButton, QFileIconProvider, \
    QMessageBox, QTableWidget
from pyqtgraph import PlotWidget
import os
from RatioBuilding import RatioBuilder
import numpy as np
import scipy.interpolate


class AnalysisTabWidget(QLabel):
    def __init__(self, window, ratioBuilder):
        super(AnalysisTabWidget, self).__init__()
        self.window = window

        self.ratioBuilder = ratioBuilder

        self.setupResultsBox()

    def setupResultsBox(self):
        resultTable = QTableWidget()

        gridLayout = QGridLayout()
        gridLayout.addWidget(resultTable, 0, 0)

        self.setLayout(gridLayout)

    def display(self):
        pass