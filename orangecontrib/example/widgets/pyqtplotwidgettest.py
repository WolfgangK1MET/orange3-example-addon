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


class OwSimplePyQtGraph(OWWidget):
    name = "PyQt Graph"
    description = ""
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

        self.graph = pg.GraphicsLayoutWidget()
        self.p1 = self.graph.addPlot()
        self.graph.removeItem(self.p1)

        self.p1 = self.graph.addPlot()
        self.p2 = self.graph.addPlot()
        self.graph.removeItem(self.p1)
        self.mainArea.layout().addWidget(self.graph)

        dmod = DomainModel
        self.x_model = DomainModel(dmod.MIXED, valid_types=TimeVariable)
        self.y_model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)

        self.show()

    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset

        if dataset is not None:
            self.Warning.empty_data(shown=False)
            time_var = self.__detect_time_variable()

            self.x_model.set_domain(dataset.domain)
            self.y_model.set_domain(dataset.domain)

        self.Outputs.selected.send(None)

    # Adds a new plot and initialize it if data is available
    def __add_plot(self):
        pass

    # Maybe with context menu (if possible)
    def __remove_plot(self, plot_number):
        pass

    def __remove_plot(self):
        pass

    def __add_axis(self, plot_number, axis_type):
        pass

    def __remove_axis(self, plot_number, axis_name):
        pass

    def __get_values_from_y_axis(self, y_axis):
        y = self.__input_data[:, y_axis]
        return y

    def __get_time_values_of_axis(self, x_axis_name):
        for row in self.__input_data:
            x.append((dateutil.parser.parse(f'{row[x_axis_name]}') - datetime.datetime(1970, 1, 1)).total_seconds())
            
    def __update_plot(self):
        x = []
        y = self.__get_values_from_y_axis(self.attr_y0)

        for row in self.__input_data:
            x.append((dateutil.parser.parse(f'{row["DatumUhrzeit"]}') - datetime.datetime(1970, 1, 1)).total_seconds())

        n = []
        for i, v in enumerate(x):
            n.append([v, y[i][0]])

        n = np.array(n)

        self.graph.plot(n, pen="r")

    def __detect_time_variable(self):
        time_var = TableUtility.get_first_time_variable(self.__input_data)

        return time_var


if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication

    table = Table("WK1_20200201.csv")

    a = QApplication([])
    df = OwSimplePyQtGraph()

    df.set_data(table)

    df.show()
    a.exec()
