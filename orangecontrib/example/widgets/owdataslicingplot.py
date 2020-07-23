import Orange

from Orange.data import Table, ContinuousVariable
from Orange.widgets.widget import OWWidget, Input, Output, Msg
import pyqtgraph as pg
import numpy as np
import dateutil.parser
from Orange.data import TimeVariable
from Orange.widgets.utils.itemmodels import DomainModel
import datetime
from PyQt5.QtWidgets import QApplication
from dateaxisitem import DateAxisItem


class TableUtility:
    @staticmethod
    def get_first_time_variable(dataset):
        for attribute in list(dataset.domain.metas) + list(dataset.domain.attributes):
            if type(attribute) == TimeVariable:
                return attribute

        return None

    @staticmethod
    def get_first_continuous_variable(dataset):
        for attribute in list(dataset.domain.metas) + list(dataset.domain.attributes):
            if type(attribute) == ContinuousVariable and type(attribute) != TimeVariable:
                return attribute

        return None


class PyQtTest(OWWidget):
    name = "PyQt Graph - 2 Graphs"
    description = "Test to show 2 graphs"
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

        dmod = DomainModel

        self.__input_data = None
        self.Warning.empty_data(shown=True)
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle("Test")

        self.label = pg.LabelItem(justify='right')
        self.win.addItem(self.label)

        self.mainArea.layout().addWidget(self.win)

        self.p1 = self.win.addPlot(row = 1, col = 0, axisItems = {'bottom': DateAxisItem()})
        self.p2 = self.win.addPlot(row=2, col=0, axisItems = {'bottom': DateAxisItem()})

        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
        # item when doing auto-range calculations.
        self.p2.addItem(self.region, ignoreBounds=True)

        self.p1.setAutoVisible(y=True)

        self.region.sigRegionChanged.connect(self.update)

        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.p1.addItem(self.vLine, ignoreBounds=True)
        self.p1.addItem(self.hLine, ignoreBounds=True)

        self.vb = self.p1.vb

        self.p1.sigRangeChanged.connect(self.updateRegion)

        self.region.setRegion([1000, 2000])

        self.x_model = DomainModel(dmod.MIXED, valid_types=TimeVariable)
        self.y_model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)
        self.region.sigRegionChanged.connect(self.update)

    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if index > 0 and index < len(self.data1):
                self.label.setText(
                    "<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (
                    mousePoint.x(), self.data1[index], self.data2[index]))
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def updateRegion(self, evt, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)

    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset

        if dataset is not None:
            self.Warning.empty_data(shown=False)
            time_var = self.__detect_time_variable()

            self.x_model.set_domain(dataset.domain)
            self.y_model.set_domain(dataset.domain)

            # TODO: Throw exception if there is no datetime or/and number type
            self.attr_x = time_var
            self.attr_y0 = TableUtility.get_first_continuous_variable(self.__input_data)

            self.__update_plot()
            self.update()

        self.Outputs.selected.send(None)

    def __update_plot(self):
        x = []
        y = self.selected = self.__input_data[:, self.attr_y0]

        for row in self.__input_data:
            # Die Daten stimmen
            dt = dateutil.parser.parse(f'{row["DatumUhrzeit"]}')
            print(dt)
            # Es ist nicht klar auf welches Datum sich die vergangenen Sekunden beziehen müssen
            v = dt - datetime.datetime(1970, 1, 1)
            # Es wird auf jeden Fall falsch dargestellt.
            v = v.total_seconds()
            x.append(v)
            # print(dateutil.parser.parse(f'{row["DatumUhrzeit"]}'))

        n = []
        for i, v in enumerate(x):
            n.append([v, y[i][0]])
            print(v, y[i][0])

        self.region.setRegion([n[0][0], n[10][0]])
        n = np.array(n)

        self.p1.plot(n, pen="w")
        self.p2.plot(n, pen="r")

    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)

    def __detect_time_variable(self):
        time_var = TableUtility.get_first_time_variable(self.__input_data)

        return time_var


if __name__ == "__main__":

    table = Table("WK1_20200201.csv")

    a = QApplication([])
    df = PyQtTest()

    df.set_data(table)

    df.show()
    a.exec()


