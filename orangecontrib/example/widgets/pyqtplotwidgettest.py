import Orange

from Orange.data import Table
import dateutil.parser
from Orange.data import Table, ContinuousVariable
from Orange.widgets.widget import OWWidget, Input, Output, Msg
import pyqtgraph as pg
import numpy as np
import dateutil.parser
from Orange.data import TimeVariable
from Orange.widgets.utils.itemmodels import DomainModel
from dateaxisitem import DateAxisItem
import datetime

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

        self.__input_data = None
        self.Warning.empty_data(shown=True)

        self.graph = pg.PlotWidget(axisItems = {'bottom': DateAxisItem()})

        self.graph.setAutoVisible(y=True)

        self.c1 = self.graph.plot(pen="r")

        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.graph.addItem(self.vLine, ignoreBounds=True)
        self.graph.addItem(self.hLine, ignoreBounds=True)

        dmod = DomainModel
        self.x_model = DomainModel(dmod.MIXED, valid_types=TimeVariable)
        self.y_model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)

        # box = gui.vBox(self.mainArea, True, margin=0)
        self.mainArea.layout().addWidget(self.graph)
        self.show()

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
        y = self.selected = self.__input_data[:, self.attr_y0]

        for row in self.__input_data:
            x.append((dateutil.parser.parse(f'{row["DatumUhrzeit"]}') - datetime.datetime(1970, 1, 1)).total_seconds())

        n = []
        for i, v in enumerate(x):
            n.append([v, y[i][0]])
            print(v, y[i][0])

        n = np.array(n)

        self.graph.plot(n, pen="r")
        # self.c1.setData(n)
        # self.c2.setData(n)

    def __detect_time_variable(self):
        time_var = TableUtility.get_first_time_variable(self.__input_data)

        return time_var

if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication

    table = Table("WK1_20200201.csv")

    a = QApplication([])
    df = OWEasyMatplot()

    df.set_data(table)

    df.show()
    a.exec()
