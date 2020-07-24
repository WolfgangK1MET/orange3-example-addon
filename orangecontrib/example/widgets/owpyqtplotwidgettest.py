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
import datetime
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


class PyQtMultiplePlot(OWWidget):
    name = "PyQt Multiple Plot Test"
    description = "PyQt Multiple Plot Test"
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

        self.plots = []

        self.__input_data = None
        self.Warning.empty_data(shown=True)

        self.graph = pg.GraphicsLayoutWidget()

        self.p1 = self.graph.addPlot(axisItems = {'bottom': DateAxisItem()})

        self.mainArea.layout().addWidget(self.graph)

        self.x_model = DomainModel(DomainModel.MIXED, valid_types=TimeVariable)
        self.y_model = DomainModel(DomainModel.MIXED, valid_types=ContinuousVariable)

        self.show()

    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset

        if dataset is not None:
            self.Warning.empty_data(shown=False)

            self.x_model.set_domain(dataset.domain)
            self.y_model.set_domain(dataset.domain)

            # Reagieren, falls nichts gefunden wird.
            self.attr_y0 = self.__detect_time_variable()

            if self.attr_y0 is not None:
                self.__update_plot()
            else:
                pass

        self.Outputs.selected.send(None)

    # Adds a new plot and initialize it if data is available
    def __add_plot(self):
        new_plot = self.graph.addPlot()
        # Die neue Linie irgendwo speichern?
        self.plots.append(new_plot)

        return new_plot

    # Maybe with context menu (if possible)
    def __remove_plot(self, plot_number):
        plot = self.plots[plot_number]
        self.plots.remove(plot)

    def __remove_axis(self, plot_number, axis_number):
        plot = self.plots[plot_number]
        y_values = plot.y_axes[axis_number]
        plot.y_axes.remove(y_values)

    def __add_axis(self, plot_number, axis_type):
        plot = self.plots[plot_number]
        # Todo Werte herausholen
        values = None
        plot.plot(values)

    def __get_values_from_y_axis(self, y_axis):
        y = self.__input_data[:, y_axis]

        return y

    def __get_time_values_of_axis(self, x_axis_name):
        x = []

        for row in self.__input_data:
            x.append((dateutil.parser.parse(f'{row[x_axis_name]}') - datetime.datetime(1970, 1, 1)).total_seconds())

        return x

    @staticmethod
    def __merge_x_and_y_values(x, y):
        n = []
        for i, v in enumerate(x):
            n.append([v, y[i][0]])

        return np.array(n)

    def __update_plot(self):
        y = self.__get_values_from_y_axis(self.attr_y0)
        for v in y:
            print(v)
        x = self.__get_time_values_of_axis("DatumUhrzeit")

        n = OwSimplePyQtGraph.__merge_x_and_y_values(x, y)

        self.p1.plot(n)

    def __detect_time_variable(self):
        time_var = TableUtility.get_first_time_variable(self.__input_data)

        return time_var


if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication

    table = Table("WK1_20200201.csv")

    a = QApplication([])
    df = PyQtMultiplePlot()

    df.set_data(table)

    df.show()
    a.exec()
