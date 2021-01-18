from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtCore import Qt

import json


class ConstantsDialog(QDialog):

    def __init__(self, inputTab, path=None):
        super(ConstantsDialog, self).__init__()

        self.inputTab = inputTab
        self.path = path

        if path is None:
            self.setWindowTitle('Set new constants')
        else:
            self.setWindowTitle('Edit constants')

        self.initUI()
        self.setEdits()

    def initUI(self):
        layout = QFormLayout()
        self.mf48Edit = QLineEdit()
        self.mf36Edit = QLineEdit()
        self.mf56Edit = QLineEdit()
        self.mf68Edit = QLineEdit()
        self.mf92Edit = QLineEdit()
        self.mf38Edit = QLineEdit()
        self.mf35Edit = QLineEdit()
        self.mf43Edit = QLineEdit()
        self.mf45Edit = QLineEdit()
        self.mf09Edit = QLineEdit()
        self.mf29Edit = QLineEdit()
        self.mf34Edit = QLineEdit()
        self.mf58Edit = QLineEdit()
        self.mf02Edit = QLineEdit()
        self.l230Edit = QLineEdit()
        self.l232Edit = QLineEdit()
        self.l234Edit = QLineEdit()
        self.l238Edit = QLineEdit()
        self.NAEdit = QLineEdit()
        self.NR85Edit = QLineEdit()
        self.cpsEdit = QLineEdit()
        self.slopeEdit = QLineEdit()
        self.R3433Edit = QLineEdit()
        self.R3533Edit = QLineEdit()
        self.R3029Edit = QLineEdit()
        self.tri236Edit = QLineEdit()
        self.tri233Edit = QLineEdit()
        self.tri229Edit = QLineEdit()
        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        layout.addRow(QLabel('Mf 234 / 238:'), self.mf48Edit)
        layout.addRow(QLabel('Mf 233 / 236:'), self.mf36Edit)
        layout.addRow(QLabel('Mf 235 / 236:'), self.mf56Edit)
        layout.addRow(QLabel('Mf 236 / 238:'), self.mf68Edit)
        layout.addRow(QLabel('Mf 229 / 232:'), self.mf92Edit)
        layout.addRow(QLabel('Mf 233 / 238:'), self.mf38Edit)
        layout.addRow(QLabel('Mf 233 / 235:'), self.mf35Edit)
        layout.addRow(QLabel('Mf 234 / 233:'), self.mf43Edit)
        layout.addRow(QLabel('Mf 234 / 235:'), self.mf45Edit)
        layout.addRow(QLabel('Mf 230 / 229:'), self.mf09Edit)
        layout.addRow(QLabel('Mf 232 / 239:'), self.mf29Edit)
        layout.addRow(QLabel('Mf 233 / 234:'), self.mf34Edit)
        layout.addRow(QLabel('Mf 235 / 238:'), self.mf58Edit)
        layout.addRow(QLabel('Mf 230 / 232:'), self.mf02Edit)
        layout.addRow(QLabel('\u03BB<sup>230</sup>'), self.l230Edit)
        layout.addRow(QLabel('\u03BB<sup>232</sup>'), self.l232Edit)
        layout.addRow(QLabel('\u03BB<sup>234</sup>'), self.l234Edit)
        layout.addRow(QLabel('\u03BB<sup>238</sup>'), self.l238Edit)
        layout.addRow(QLabel('NA'), self.NAEdit)
        layout.addRow(QLabel('NR85'), self.NR85Edit)
        layout.addRow(QLabel('Counts per second'), self.cpsEdit)
        layout.addRow(QLabel('Slope correction'), self.slopeEdit)
        layout.addRow(QLabel('R34_33'), self.R3433Edit)
        layout.addRow(QLabel('R35_33'), self.R3533Edit)
        layout.addRow(QLabel('R30_29'), self.R3029Edit)
        layout.addRow(QLabel('TRI-13 U236 (ng/g)'), self.tri236Edit)
        layout.addRow(QLabel('TRI-13 U233 (ng/g)'), self.tri233Edit)
        layout.addRow(QLabel('TRI-13 U229 (ng/g)'), self.tri229Edit)

        layout.addRow(self.saveButton)

        self.setLayout(layout)

    def setEdits(self):
        if self.path is None:
            self.mf48Edit.setText('0.0')
            self.mf36Edit.setText('0.0')
            self.mf56Edit.setText('0.0')
            self.mf68Edit.setText('0.0')
            self.mf92Edit.setText('0.0')
            self.mf38Edit.setText('0.0')
            self.mf35Edit.setText('0.0')
            self.mf43Edit.setText('0.0')
            self.mf45Edit.setText('0.0')
            self.mf09Edit.setText('0.0')
            self.mf29Edit.setText('0.0')
            self.mf34Edit.setText('0.0')
            self.mf58Edit.setText('0.0')
            self.mf02Edit.setText('0.0')
            self.l230Edit.setText('0.0')
            self.l232Edit.setText('0.0')
            self.l234Edit.setText('0.0')
            self.l238Edit.setText('0.0')
            self.NAEdit.setText('0.0')
            self.NR85Edit.setText('0.0')
            self.cpsEdit.setText('0.0')
            self.slopeEdit.setText('0.0')
            self.R3433Edit.setText('0.0')
            self.R3533Edit.setText('0.0')
            self.R3029Edit.setText('0.0')
            self.tri236Edit.setText('0.0')
            self.tri233Edit.setText('0.0')
            self.tri229Edit.setText('0.0')
        else:
            constants = {}
            with open(self.path, 'r') as file:
                constants = json.loads(file.read().replace('\n', ''))

            self.mf48Edit.setText(str(constants['mf48']))
            self.mf36Edit.setText(str(constants['mf36']))
            self.mf56Edit.setText(str(constants['mf56']))
            self.mf68Edit.setText(str(constants['mf68']))
            self.mf92Edit.setText(str(constants['mf92']))
            self.mf38Edit.setText(str(constants['mf38']))
            self.mf35Edit.setText(str(constants['mf35']))
            self.mf43Edit.setText(str(constants['mf43']))
            self.mf45Edit.setText(str(constants['mf45']))
            self.mf09Edit.setText(str(constants['mf09']))
            self.mf29Edit.setText(str(constants['mf29']))
            self.mf34Edit.setText(str(constants['mf34']))
            self.mf58Edit.setText(str(constants['mf58']))
            self.mf02Edit.setText(str(constants['mf02']))
            self.l230Edit.setText(str(constants['l230']))
            self.l232Edit.setText(str(constants['l232']))
            self.l234Edit.setText(str(constants['l234']))
            self.l238Edit.setText(str(constants['l238']))
            self.NAEdit.setText(str(constants['NA']))
            self.NR85Edit.setText(str(constants['NR85']))
            self.cpsEdit.setText(str(constants['cps']))
            self.slopeEdit.setText(str(constants['slope']))
            self.R3433Edit.setText(str(constants['R3433']))
            self.R3533Edit.setText(str(constants['R3533']))
            self.R3029Edit.setText(str(constants['R3029']))
            self.tri236Edit.setText(str(constants['tri236']))
            self.tri233Edit.setText(str(constants['tri233']))
            self.tri229Edit.setText(str(constants['tri229']))

    def save(self):
        fileName = None

        if self.path is None:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "constants.cfg",
                                                      "Config files (*.cfg)", options=options)
            try:
                open(fileName, 'w')
            except OSError:
                return
        else:
            fileName = self.path

        fileDict = {}
        fileDict['mf48'] = float(self.mf48Edit.text())
        fileDict['mf36'] = float(self.mf36Edit.text())
        fileDict['mf56'] = float(self.mf56Edit.text())
        fileDict['mf68'] = float(self.mf68Edit.text())
        fileDict['mf92'] = float(self.mf92Edit.text())
        fileDict['mf38'] = float(self.mf38Edit.text())
        fileDict['mf35'] = float(self.mf35Edit.text())
        fileDict['mf43'] = float(self.mf43Edit.text())
        fileDict['mf45'] = float(self.mf45Edit.text())
        fileDict['mf09'] = float(self.mf09Edit.text())
        fileDict['mf29'] = float(self.mf29Edit.text())
        fileDict['mf34'] = float(self.mf34Edit.text())
        fileDict['mf58'] = float(self.mf58Edit.text())
        fileDict['mf02'] = float(self.mf02Edit.text())
        fileDict['l230'] = float(self.l230Edit.text())
        fileDict['l232'] = float(self.l232Edit.text())
        fileDict['l234'] = float(self.l234Edit.text())
        fileDict['l238'] = float(self.l238Edit.text())
        fileDict['NA'] = float(self.NAEdit.text())
        fileDict['NR85'] = float(self.NR85Edit.text())
        fileDict['cps'] = float(self.cpsEdit.text())
        fileDict['slope'] = float(self.slopeEdit.text())
        fileDict['R3433'] = float(self.R3433Edit.text())
        fileDict['R3533'] = float(self.R3533Edit.text())
        fileDict['R3029'] = float(self.R3029Edit.text())
        fileDict['tri236'] = float(self.tri236Edit.text())
        fileDict['tri233'] = float(self.tri233Edit.text())
        fileDict['tri229'] = float(self.tri229Edit.text())

        with open(fileName, 'w') as file:
            json.dump(fileDict, file, indent=4)

        self.inputTab.constantsFileEdit.setText(fileName)

        self.close()
