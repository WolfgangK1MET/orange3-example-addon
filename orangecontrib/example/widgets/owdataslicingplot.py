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
from pyqtgraph.graphicsItems import AxisItem
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
        self.data1 = 10000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(
            size=10000)
        self.data2 = 15000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(
            size=10000)

        self.c1 = self.p1.plot(pen="r")
        self.c2 = self.p2.plot(pen="w")

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

            # self.cid = self.graph.canvas.mpl_connect('on_click', onclick)
            self.__update_plot()

        self.Outputs.selected.send(None)

    def __update_plot(self):
        print("Update Plot")

        x = []
        for row in self.__input_data:
            x.append(dateutil.parser.parse(f'{row["DatumUhrzeit"]}'))
        y = self.selected = self.__input_data[:, self.attr_y0]

        self.c1

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
    df = OWEasyMatplot()

    df.set_data(table)

    df.show()
    a.exec()


