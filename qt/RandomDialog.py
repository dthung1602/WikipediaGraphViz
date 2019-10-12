import numpy as np
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QComboBox, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.uic import loadUi

from canvas import Canvas
from .utils import BuddyLabel, clearLayout, textEdited

DIST = [
    'Normal distribution',
    'Uniform distribution'
]


class RandomDialog(QDialog):
    def __init__(self, canvas: Canvas, type):
        super().__init__()
        self.canvas = canvas
        self.type = type
        self.g = canvas.g
        self.attr = self.sender().objectName()
        loadUi('resource/gui/RandomDialog.ui', self)
        self.setWindowIcon(QIcon('resource/gui/icon.ico'))
        self.setWindowTitle("Random data")
        self.distLayout = self.findChild(QVBoxLayout, 'distLayout')
        self.selectDistribution = self.findChild(QComboBox, 'distBox')
        self.randomLayout = self.findChild(QVBoxLayout, 'randomLayout')
        self.randomLayout2 = self.findChild(QVBoxLayout, 'randomLayout2')
        self.generateBtn = self.findChild(QPushButton, 'generate_btn')
        self.notiLabel = self.findChild(QLabel, 'notiLabel')
        self.notiLabel.setWordWrap(True)
        self.addDistSelectOptions()
        self.labelStyleSheet = ("color: rgb(180,180,180);"
                                "font-size: 15px;"
                                "background-color: transparent;")
        self.buttonStyleSheet = ("QPushButton{"
                                 "color: rgb(200, 200, 200);"
                                 "border-style: 2px solid rgb(200, 200, 200);"
                                 "border-radius: 7px;"
                                 "background-color: #383838;"
                                 "}"
                                 "QPushButton:hover{"
                                 " background-color: #303030;"
                                 "}"
                                 )

        self.meanEdit = QLineEdit()
        self.mean = BuddyLabel(self.meanEdit)

        self.standardDeviationEdit = QLineEdit()
        self.standardDeviation = BuddyLabel(self.standardDeviationEdit)

        self.minEdit = QLineEdit()
        self.min = BuddyLabel(self.minEdit)

        self.maxEdit = QLineEdit()
        self.max = BuddyLabel(self.maxEdit)

        self.valueLabelStyleSheet = ("QLabel {  font-size: 11px; border: 1px solid rgb(150, 150, 150); "
                                    "padding: 2px; color: rgb(220,220,220); background-color: #383838;"
                                    "border-radius: 5px; }"
                                    "QLabel:hover{background-color: #242424;}"
                                    "QLineEdit {  font-size: 11px; border: 1px solid rgb(150, 150, 150); "
                                    "padding: 2px; color: rgb(220,220,220); background-color: #383838;"
                                    "border-radius: 5px; }"
                                    "QLineEdit:hover{background-color: #242424;}")
        self.attrBack = []

        self.randomArr = []
        self.update = True

    def changeDist(self, opt):
        [
            self.default,
            self.normalDistribution,
            self.uniformDistribution,
        ][opt]()

    def addDistSelectOptions(self):
        self.selectDistribution.addItems(['-- None --'])
        self.selectDistribution.addItems([opt for opt in DIST])
        self.selectDistribution.currentIndexChanged.connect(self.changeDist)

    def default(self):
        clearLayout(self.randomLayout)

    def normalDistribution(self):
        clearLayout(self.randomLayout)
        meanLabel = QLabel('Mean: ')
        meanLabel.setStyleSheet(self.labelStyleSheet)
        self.mean.setStyleSheet(self.valueLabelStyleSheet)
        self.meanEdit.setStyleSheet(self.valueLabelStyleSheet)
        self.randomLayout.addWidget(meanLabel)
        self.randomLayout.addWidget(self.mean)
        self.randomLayout.addWidget(self.meanEdit)

        stdevLabel = QLabel('Standard Deviation: ')
        stdevLabel.setStyleSheet(self.labelStyleSheet)
        self.standardDeviationEdit.setStyleSheet(self.valueLabelStyleSheet)
        self.standardDeviation.setStyleSheet(self.valueLabelStyleSheet)
        self.randomLayout2.addWidget(stdevLabel)
        self.randomLayout2.addWidget(self.standardDeviation)
        self.randomLayout2.addWidget(self.standardDeviationEdit)

        # acceptBtn = QPushButton('Generate', self)
        # acceptBtn.setStyleSheet(self.buttonStyleSheet)
        # self.randomLayout.addWidget(acceptBtn)
        # self.meanEdit.textEdited(self.mean, self.meanEdit))
        # acceptBtn.clicked.connect(textEdited(self.standardDeviation, self.standardDeviationEdit))
        # acceptBtn.clicked.connect(self.generateNormalDistribution)
        self.meanEdit.editingFinished.connect(textEdited(self.mean, self.meanEdit))
        self.standardDeviationEdit.editingFinished.connect(
            textEdited(self.standardDeviation, self.standardDeviationEdit))
        self.generateBtn.pressed.connect(self.generateNormalDistribution)

    def uniformDistribution(self):
        clearLayout(self.randomLayout)
        minLabel = QLabel('Min: ')
        minLabel.setStyleSheet(self.labelStyleSheet)
        self.minEdit.setStyleSheet(self.valueLabelStyleSheet)
        self.min.setStyleSheet(self.valueLabelStyleSheet)
        self.randomLayout.addWidget(minLabel)
        self.randomLayout.addWidget(self.min)
        self.randomLayout.addWidget(self.minEdit)

        maxLabel = QLabel('Max: ')
        maxLabel.setStyleSheet(self.labelStyleSheet)
        self.max.setStyleSheet(self.valueLabelStyleSheet)
        self.maxEdit.setStyleSheet(self.valueLabelStyleSheet)
        self.randomLayout2.addWidget(maxLabel)
        self.randomLayout2.addWidget(self.max)
        self.randomLayout2.addWidget(self.maxEdit)

        # acceptBtn = QPushButton('Generate', self)
        # acceptBtn.setStyleSheet(self.buttonStyleSheet)
        # self.randomLayout.addWidget(acceptBtn)
        self.minEdit.editingFinished.connect(textEdited(self.min, self.minEdit))
        self.maxEdit.editingFinished.connect(textEdited(self.max, self.maxEdit))
        self.generateBtn.pressed.connect(self.generateUniformDistribution)
        # acceptBtn.clicked.connect(self.generateUniformDistribution)

    def generateNormalDistribution(self):
        mean = float(self.meanEdit.text())
        stdDeviation = float(self.standardDeviationEdit.text())
        if self.type == 'EDGE':
            if self.update:
                size = self.g.ecount()
                self.randomArr = np.random.normal(mean, stdDeviation, size)
                self.changeEdge(self.attr, self.randomArr)
        else:
            if self.update:
                size = self.g.vcount()
                self.randomArr = np.random.normal(mean, stdDeviation, size)
                self.changeVertex(self.attr, self.randomArr)

        self.notiLabel.setText(
            "Generated Normal Distribution with \n Mean = "+str(mean)+" Standard Deviation = "+str(stdDeviation))
        self.attrBack.append("Normal Distribution")
        self.attrBack.append(mean)
        self.attrBack.append(stdDeviation)

    def generateUniformDistribution(self):
        minValue = float(self.minEdit.text())
        maxValue = float(self.maxEdit.text())
        if self.type == 'EDGE':
            if self.update:
                size = self.g.ecount()
                self.randomArr = np.random.uniform(minValue, maxValue, size)
                self.changeEdge(self.attr, self.randomArr)
        else:
            if self.update:
                size = self.g.vcount()
                self.randomArr = np.random.uniform(minValue, maxValue, size)
                self.changeVertex(self.attr, self.randomArr)
        self.notiLabel.setText(
            "Generated Uniform Distribution with \n Min = "+str(minValue)+" Max = "+str(maxValue))
        self.attrBack.append("Uniform Distribution")
        self.attrBack.append(minValue)
        self.attrBack.append(maxValue)

    def changeEdge(self, attributeName, randomArr):
        count = 0
        for i in self.g.es:
            i[attributeName] = randomArr[count]
            count = count + 1

    def changeVertex(self, attributeName, randomArr):
        count = 0
        for i in self.g.vs:
            i[attributeName] = randomArr[count]
            count = count + 1

    def getAttr(self):
        return self.attrBack
