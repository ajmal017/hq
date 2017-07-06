#!/usr/bin/env python
#coding:utf-8

from PyQt5.QtCore import QRect, QRectF, QSize, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPalette, QPen
from PyQt5.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
                             QSizePolicy, QWidget)


class AutoGrid(QWidget):

    def __init__(self, parent=None):
        super(AutoGrid, self).__init__(parent)

        # 表格距边框距离
        self.marginLeft = 80
        self.marginRight = 80
        self.marginTop = 20
        self.marginBottom = 20

        # 当前表格中最小表格的宽度和高度
        self.atomGridHeight = 60
        self.atomGridWidth = 60

        # 当前表格中最小表格宽度和高度的最小值
        self.atomGridHeightMin = 60
        self.atomGridWidthMin = 60

        # 当前widget的宽度和高度
        self.widgetHeight = 0
        self.widgetWidth = 0

        # 当前表格的宽度和高度
        self.gridHeight = 0
        self.gridWidth = 0

        # 表格中小格子的数量
        self.hGridNum = 0
        self.wGridNum = 0

        self.drawBK()

    def drawBK(self):
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor("#000000"))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.widgetHeight = self.height()
        self.widgetWidth = self.width()

        self.gridHeight = self.widgetHeight - self.marginTop - self.marginBottom
        self.gridWidth = self.widgetWidth - self.marginLeft - self.marginRight

        self.hGridNum = self.gridHeight / self.atomGridHeightMin
        self.wGridNum = self.gridWidth / self.atomGridWidthMin

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen();
        pen.setColor(QColor("#FF0000"))
        painter.setPen(pen)

        x0 = self.marginLeft
        y0 = self.marginTop
        x1 = self.widgetWidth - self.marginRight
        y1 = self.marginTop

        # 画横线
        for i in range(0, self.hGridNum+1):
            painter.drawLine(x0, y0 + i*self.atomGridWidth,
                             x1, y1 + i*self.atomGridWidth)
        # 画竖线
        x1 = self.marginLeft
        y1 = self.widgetHeight - self.marginBottom
        for i in range(0, self.wGridNum+1):
            painter.drawLine(x0+i*self.atomGridHeight, y0,
                             x1+i*self.atomGridHeight, y1)


class KLineGrid(AutoGrid):

    def __init__(self, parent=None):
        super(KLineGrid, self).__init__(parent)

    def paintEvent(self, event):
        super(KLineGrid, self).paintEvent(event)

        # 获取y轴坐标
        self.getIndicator()
        # 显示y轴价格
        self.drawYtick()
        # 画K线
        self.drawKline()
        # 画5日均线
        self.drawAverageLine(5)

    def getIndicator(self):
        pass

    def drawYtick(self):
        pass

    def drawKline(self):
        pass

    def drawAverageLine(self, days):
        pass


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    w = KLineGrid()
    w.resize(1280, 1280)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())

