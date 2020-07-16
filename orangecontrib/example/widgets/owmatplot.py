import Orange

from Orange.data import Table, ContinuousVariable
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.data import TimeVariable
from Orange.widgets import gui
from Orange.widgets.utils.itemmodels import DomainModel
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import dateutil.parser
import matplotlib.dates as mdates
from mpldatacursor import datacursor
from AnyQt.QtCore import Qt

# Todo
# Weitere Achsen können mit dem Dictionary des Objekts hinzugefügt werden.
# self.__dict__[attribute_name] = value
# self.__dict__[attribute_name] = None // entfernen


class Plot:
    def __init__(self, x_values, y_values, y_axis):
        self._x_values = x_values
        self._y_axes = []
        y_axis = YAxisData(y_values, y_axis, '')
        self._y_axes.append(y_axis)

    # Getter and Setter #
    @property
    def x_values(self):
        return self._x_values

    @x_values.setter
    def x_values(self, values):
        self._x_values = values

    @property
    def y_axes(self):
        return self._y_axes

    @y_axes.setter
    def y_axes(self, values):
        self._y_axes = values

class YAxisData:
    def __init__(self, y_values, y_axis, color_code):
        self._y_axis_values = y_values
        self._y_axis = y_axis
        self._color_code = color_code
        self._line_size = 1
        self._line_type = '-'
        self._point_type = ''

    # Getter and Setter #
    @property
    def point_type(self):
        return self._point_type

    @point_type.setter
    def point_type(self, value):
        self._point_type = value

    @property
    def line_size(self):
        return self._line_size

    @line_size.setter
    def line_size(self, value):
        self._line_size = value

    @property
    def line_type(self):
        return self._line_type

    @line_type.setter
    def line_type(self, value):
        self._line_type = value

    @property
    def line_color(self):
        return self._color_code

    @line_color.setter
    def line_color(self, value):
        self._color_code = value

    @property
    def y_values(self):
        return self._y_axis_values

    @y_values.setter
    def y_values(self, values):
        self._y_axis_values = values

    @property
    def y_axis(self):
        return self._y_axis

    @y_axis.setter
    def y_axis(self, value):
        self._y_axis = value


class DataAccessObject:
    def __init__(self):
        pass

    def load_y_axis_data(self):
        pass

    def save_y_axis_data(self):
        pass

    def save_plot_data(self):
        pass

    def load_plot_data(self):
        pass


class AxisView:
    pass


class YAxisView:
    pass


class YAxisConfigView:
    pass


def enter_axes(event):
    print('enter_axes', event.inaxes)
    event.inaxes.patch.set_facecolor('yellow')
    event.inaxes.set_ylabel("TEST", color="b")
    event.canvas.draw()


def leave_axes(event):
    print('leave_axes', event.inaxes)
    event.inaxes.patch.set_facecolor('white')
    event.inaxes.set_ylabel("LEAVE TEST", color="b")
    event.canvas.draw()


class YAxisData:
    def __init__(self, model, number, **common_options):
        self.model = model
        self.number = number
        self.common_options = common_options

    def store_settings(self):
        print("store settings ... NOT IMPLEMENTED")


class OWMatplot(OWWidget):
    name = "Matplot"
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

        common_options = dict(labelWidth=50, orientation=Qt.Horizontal, sendSelectedValue=True, contentsLength=14)

        self.attr_box = gui.vBox(self.controlArea, True)

        self.attr_x = None
        self.attr_y1 = None

        dmod = DomainModel
        self.x_model = DomainModel(dmod.MIXED, valid_types=TimeVariable)
        self.y_model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)
        self.attr_y0 = None

        self.__dict__["edit_y0_axis"] = lambda self: print("Something")

        self.cb_attr_x = gui.comboBox(self.attr_box, self, "attr_x", label="Axis x:",
                                      callback=self.set_attr_x_from_combo, model=self.x_model, **common_options,
                                      searchable=True)
        self.axis_box = gui.vBox(self.attr_box, True)


        self.cb_attr_y0 = gui.comboBox(self.axis_box, self, "attr_y0", label="Axis y:",
                                       callback=self.set_attr_y_from_combo, model=self.y_model, **common_options,
                                       searchable=True)
        self.axis_h_box0 = gui.hBox(self.axis_box, True)
        self.b_attr_remove0 = gui.button(self.axis_h_box0, self, label="Remove", callback=self.__update_plot)
        self.b_attr_edit0 = gui.button(self.axis_h_box0, self, label="Edit", callback=self.__update_plot)


        self.graph = MatplotlibWidget()

        gui.rubber(self.attr_box)
        box = gui.vBox(self.mainArea, True, margin=0)
        box.layout().addWidget(self.graph)
        self.subplot = self.graph.getFigure().add_subplot()

        self.show()

    # Callback function for cb_attr_x
    def set_attr_x_from_combo(self):
        self.__update_plot()

    # Callback function for cb_attr_y
    def set_attr_y_from_combo(self):
        self.__update_plot()

    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset
        self.Warning.empty_data(shown=True)

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

        self.Outputs.selected.send(self.__input_data)

    def __detect_time_variable(self):
        return TableUtility.get_first_time_variable(self.__input_data)

    # Is called whenever the plot should update
    def __update_plot(self):
        self.subplot.clear()

        x = []
        for row in self.__input_data:
            x.append(dateutil.parser.parse(f'{row["DatumUhrzeit"]}'))
        y = self.selected = self.__input_data[:, self.attr_y0]  # Wie, wenn mehrere attr_y?

        self.subplot.set_xlabel(self.attr_x.name)
        self.subplot.set_ylabel(self.attr_y0.name, color="r")

        myFmt = mdates.DateFormatter('%H:%M:%S\n%d.%m.%Y')
        self.subplot.xaxis.set_major_formatter(myFmt)

        plot0 = self.subplot.plot(x, y, label=self.attr_y0.name, color="r")

        self.plots = plot0
        self.labels = [self.attr_y0.name]

        # Das Datum müsste noch auf das richtige Format gebracht werden.
        datacursor(plot0, bbox=dict(fc='white'),
                   arrowprops=dict(arrowstyle='simple', fc='white', alpha=0.5))

        self.graph.getFigure().tight_layout()
        self.__commit()

    # Update the graphic output of the plot
    def __commit(self):
        self.subplot.legend(self.plots, self.labels, loc=0)

        self.graph.draw()
        self.Outputs.selected.send(self.selected)


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


if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0

    table = Table("WK1_20200201.csv")

    a = QApplication([])
    df = OWMatplot()

    df.set_data(table)

    df.show()
    a.exec()
