import Orange

from Orange.data import Table, ContinuousVariable
from Orange.widgets.widget import OWWidget, Input, Output, Msg
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets


class OWEasyMatplot(OWWidget):
    name = "Matplot - test"
    description = "A widget for easy plots with matplotlib"
    icon = "icons/oweasyplot.svg"
    want_main_area = True

    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        selected = Output("Selected Data", Orange.data.Table)

    class Error(OWWidget.Error):
        pass

    class Warning(OWWidget.Warning):
        empty_data = Msg("There is no data to show.")

    def __init__(self):
        super().__init__()

        self.__input_data = None
        self.Warning.empty_data(shown=True)
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle("Test")
        self.mainArea.layout().addWidget(self.win)

        self.p1 = self.win.addPlot(row = 1, col = 0)
        self.p2 = self.win.addPlot(row=2, col=0)

        self.region = pg.LinearRegionItem()
        self.fregion.setZValue(10)
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
        # item when doing auto-range calculations.
        self.p2.addItem(self.region, ignoreBounds=True)

        self.p1.setAutoVisible(y=True)
        data1 = 10000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(
            size=10000)
        data2 = 15000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(
            size=10000)

        self.p1.plot(data1, pen="r")
        self.p2.plot(data1, pen="w")

    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset

        self.Warning.empty_data(shown=self.__input_data)
        self.Outputs.selected.send(None)

    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)

if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication

    table = Table("WK1_20200201.csv")

    a = QApplication([])
    df = OWEasyMatplot()

    df.set_data(table)

    df.show()
    a.exec()
