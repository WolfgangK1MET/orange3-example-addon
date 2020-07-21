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
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.win.setWindowTitle("Test")
        l = QtWidgets.QGridLayout()
        l.addItem(self.win, 0, 0)
        self.mainArea.addWidget(l)

        p1 = self.win.addPlot(row = 1, col = 0)
        p2 = self.win.addPlot(row=2, col=0)



    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset

        self.Warning.empty_data(shown=self.__input_data)
        self.Outputs.selected.send(None)


if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication

    table = Table("WK1_20200201.csv")

    a = QApplication([])
    df = OWEasyMatplot()

    df.set_data(table)

    df.show()
    a.exec()
