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
    def __init__(self, x_values, y_values, y_axis_name, y_axis, y_model, common_options):
        self._x_values = x_values
        self._y_axes = []
        y_axis = YAxisData(y_values, y_axis, y_axis_name, '', y_model, common_options)
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

    def append_y_axis(self, y_axis):
        self._y_axes.append(y_axis)

    def remove_y_axis(self, axis_name):
        pass

    def get_y_axis(self, y_axis_number):
        return self._y_axes[y_axis_number]


class YAxisData:
    def __init__(self, y_values = None, attr_y = None, y_axis = None, name = "", color_code = "", model = None, common_options = None):
        self._y_axis_values = y_values
        self._y_axis = y_axis
        self._color_code = color_code
        self._line_size = 1
        self._line_type = '-'
        self._point_type = ''
        self._name = name
        self._model = model
        self._common_options = common_options
        self._attr_y = attr_y

    # Getter and Setter #
    @property
    def attr_y(self):
        return self._attr_y

    @attr_y.setter
    def attr_y(self, value):
        self._attr_y = value

    @property
    def common_options(self):
        return self._common_options

    @common_options.setter
    def common_options(self, value):
        self._common_options = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

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
    def __init__(self, attr_box):
        pass

class YAxisView:
    def __init__(self, axis_box, axis_data):
        self._axis_data = axis_data
        self.attr_y = None
        self._axis_box = axis_box

        # Aus Gründen auch immer fehlt connect_control bei YAxisView
        # Evtl. passen die Callbacks oder die Variablen nicht.
        self._cb_attr_y = gui.comboBox(self._axis_box, self, "attr_y", label=self._axis_data.name,
                                       callback=self._on_attr_y_change, model=self._axis_data.model,
                                       **self._axis_data.common_options,
                                       searchable=True)
        
        self._axis_h_box = gui.hBox(self._axis_box, True)
        self._b_attr_remove = gui.button(self._axis_h_box, self, label="Remove", callback=self._on_remove)
        self._b_attr_edit = gui.button(self._axis_h_box, self, label="Edit", callback=self._on_edit)

    def _on_attr_y_change(self):
        pass

    def _on_edit(self):
        pass

    def _on_remove(self):
        pass

class YAxisConfigView:
    def __init__(self, axis_data, attr_y_label = ""):
        pass

class PlotConfigView:
    def __init(self):
        pass


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
        self.y_axis_data = YAxisData()

        common_options = dict(labelWidth=50, orientation=Qt.Horizontal, sendSelectedValue=True, contentsLength=14)
        self.y_axis_data.common_options = common_options

        self.attr_box = gui.vBox(self.controlArea, True)

        self.attr_x = None
        self.attr_y0 = None

        dmod = DomainModel
        self.x_model = DomainModel(dmod.MIXED, valid_types=TimeVariable)
        self.y_axis_data.model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)

        self.cb_attr_x = gui.comboBox(self.attr_box, self, "attr_x", label="Axis x:",
                                      callback=self.set_attr_x_from_combo, model=self.x_model, **common_options,
                                      searchable=True)
        self.axis_box = gui.vBox(self.attr_box, True)
        self.y_view = YAxisView(self.axis_box, self.y_axis_data)

        self.graph = MatplotlibWidget()

        gui.rubber(self.attr_box)
        box = gui.vBox(self.mainArea, True, margin=0)
        box.layout().addWidget(self.graph)
        self.subplot = self.graph.getFigure().add_subplot()

        self.show()

    # Callback function for cb_attr_x
    def set_attr_x_from_combo(self):
        self.__update_plot()

    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset
        self.Warning.empty_data(shown=True)

        if dataset is not None:
            self.Warning.empty_data(shown=False)
            time_var = self.__detect_time_variable()

            self.x_model.set_domain(dataset.domain)
            self.y_axis_data.model.set_domain(dataset.domain)

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
