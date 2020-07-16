from Orange.widgets import gui
from Orange.data import Table
import Orange

import numpy as np

from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtGui, QtWidgets




class Plotdata:
    def __init__(self, x_label_name = "", y_label_names = ""):
        self.x_label_name = x_label_name
        self.y_label_names = y_label_names

class MultiplotWidget(QtWidgets.QWidget):
    def __init__(self, rows = 1, columns = 1, size=(5.0, 4.0), dpi=100):
        QtWidgets.QWidget.__init__(self)
        self.fig = None
        self.axs = []
        self.plot_data = []

        self.make_plots(rows, columns)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.toolbar)
        self.vbox.addWidget(self.canvas)

        self.setLayout(self.vbox)

        self.test_plotting()

    def getFigure(self):
        return self.fig

    def make_plots(self, rows, columns):
        self.fig, self.axs = plt.subplots(rows, columns)

        # Je nach dem welche Werte man bei der Funktion subplots übergibt, kommt ein Wert, Werte in einem numpy Array bzw. in einem
        # mehrdimensionalen numpy Array zurück. Würde man das gleich zu einer Liste umwandeln, so könnte es sein, dass man eine mehrdimensionale
        # Liste erhält. Deswegen wird das numpy Array auf eine Dimension gebracht.
        # Falls nur ein Wert zurückgegeben wird, muss dieser lediglich in eine Liste eingebracht werden.

        # Weder rows noch columns dürfte 0 bzw. kleiner als 0 sein -> ansonsten Fehler
        if type(self.axs) is np.ndarray:
            self.axs.shape = (rows * columns)
            self.axs = self.axs.tolist()
        else:
            self.axs = [self.axs]

        # Problem: Jetzt hat jeder Plot nur eine Achse, die er zeichnet.
        # Es müsste später möglich sein, dass jeder Plot mehrere zeichnen/besitzen kann.
        # Daher müssten die Achsen in Plotdata gespeichert werden.
        # Jeder Plot hätte dann eine Liste von Achsen.
        # Das hinzufügen von weiteren Achsen müsste hierfür gut gekapselt werden, da es ansonsten schnell
        # unübersichtlich werden würde.

        self.plot_data = []
        for i in range(0, len(self.axs)):
            self.plot_data.append(Plotdata())

    def add_y_to_plot(self, plot_number, x_values, y_values):
        pass

    def remove_y_from_plot(self, plot_number, y_axis_number):
        pass

    def remove_plot(self, plot_number):
        pass

    def get_plot_count(self):
        pass

    def set_y_values_of_plot(self, plot_number, y_axis_number, y_values):
        pass

    def set_x_values_of_plot(self, plot_number, x_values):
        pass

    def get_axes(self, plot_number):
        # Müsste noch abgeändert werden, dass von dem entsprechenden Plot die Daten zurückgegeben werden
        return self.axs

    def plot_axis(self, ax_number, x_values, y_values):
        # clear ax müsste noch gemacht werden
        self.axs[ax_number].plot(x_values, y_values)

    # Nur zum Testen ...
    def test_plotting(self):
        # Hier werden Testwerte angezeigt
        # Nur zum Testen ...
        test_x = [1, 2, 3, 4, 5]
        test_y = [1, 2, 3, 4, 5]

        for ax in self.axs:
            ax.plot(test_x, test_y)


    def remake_plots(self, rows, columns):
        # Es hat keine Auswirkung, liegt wohl daran, dass der Canvas in einer vbox liegt.
        # Alle Widgets neu hinzuzufügen funktioniert auch nicht.
        # Eventuell ist es möglich, dass man alle Widgets entfernt und wieder neu hinzufügt, jedoch
        # wäre das sehr umständlich, da könnte man wahrscheinlich gleich das ganze Widget im Programm neu erstellen.
        self.make_plots(rows, columns)
        self.draw()

    def draw(self):
        self.canvas.draw()


class MultiplotTest(OWWidget, QtWidgets.QMainWindow):
    name = "Multiplot"
    description = "A widget for easy plots with matplotlib"
    icon = "icons/oweasyplot.svg"
    want_main_area = True
    want_control_area = True

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
        self.graph = MultiplotWidget(1, 1)

        box = gui.vBox(self.mainArea, True, margin=0)
        box.layout().addWidget(self.graph)

        self.show()
        self.graph.draw()

    def remake_plots(self, rows, columns):
        self.graph.remake_plots(rows, columns)

    @Inputs.data
    def set_input_data(self, data):
        self.__input_data = data

if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0

    table = Table("HOA_ADMIN_HOA_DRUCK.csv")

    a = QApplication([])
    df = MultiplotTest()

    df.set_input_data(table)
    df.remake_plots(3, 3) # Funktioniert nicht 
    df.show()
    
    a.exec()
