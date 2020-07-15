import Orange

from Orange.data import Table
import Orange

from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from matplotlib import pyplot as plt
import seaborn as sns
from Orange.widgets import gui

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtGui, QtWidgets
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
from pyqtgraph.widgets.LayoutWidget import LayoutWidget
from pyqtgraph.widgets.ColorButton import ColorButton

class SeabornWidget2(QtWidgets.QWidget):
    def __init__(self, size=(5.0, 4.0), dpi=100):
        QtWidgets.QWidget.__init__(self)
        self.fig = Figure(size, dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.toolbar)
        self.vbox.addWidget(self.canvas)

        self.setLayout(self.vbox)

    def getFigure(self):
        return self.fig

    def draw(self):
        self.canvas.draw()



tips = sns.load_dataset("tips")


def seabornplot():
    g = sns.FacetGrid(tips, col="sex", hue="time", palette="Set1",hue_order=["Dinner", "Lunch"])
    g.map(plt.scatter, "total_bill", "tip", edgecolor="w")
    return g.fig


class OWSeabornTest(OWWidget,QtWidgets.QMainWindow):
    name = "Matplot - test"
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
        self.graph = MatplotlibWidget()
        self.grid = LayoutWidget()
        box = gui.vBox(self.mainArea, True, margin=0)
        box.layout().addWidget(self.graph)
        self.ax1 = self.graph.getFigure().add_subplot(121)
        self.ax2 = self.graph.getFigure().add_subplot(122, sharex=self.ax1, sharey=self.ax1)
        self.axes = [self.ax1, self.ax2]
        self.canvas = FigureCanvas(self.graph.getFigure())
        self.dropdown1 = QtWidgets.QComboBox()
        self.dropdown1.addItems(["sex", "time", "smoker"])
        self.dropdown2 = QtWidgets.QComboBox()
        self.dropdown2.addItems(["sex", "time", "smoker", "day"])
        self.dropdown2.setCurrentIndex(2)

        control_box = gui.vBox(self.controlArea, True, margin=0)
        control_box.layout().addWidget(self.grid)

        self.grid.addWidget(QtWidgets.QLabel("Select category for subplots"), 0, 0)
        self.grid.addWidget(self.dropdown1, 0, 1, 1, 1)
        self.grid.addWidget(QtWidgets.QLabel("Select category for markers"), 1, 0)
        self.grid.addWidget(self.dropdown2, 1, 1, 1, 1)
        self.grid.addWidget(ColorButton(), 1, 2, 1, 1)

        self.dropdown1.currentIndexChanged.connect(self.update)
        self.dropdown2.currentIndexChanged.connect(self.update)

        self.left_side_scrolling = True

        self.update()
        self.show()
        self.graph.draw()

    @Inputs.data
    def set_input_data(self, data):
        self.__input_data = data

    def update(self):
        colors = ["b", "r", "g", "y", "k", "c"]
        self.ax1.clear()
        self.ax2.clear()
        cat1 = self.dropdown1.currentText()
        cat2 = self.dropdown2.currentText()
        print(cat1, cat2)

        for i, value in enumerate(tips[cat1].unique()):
            print("value ", value)
            df = tips.loc[tips[cat1] == value]
            self.axes[i].set_title(cat1 + ": " + value)
            for j, value2 in enumerate(df[cat2].unique()):
                print("value2 ", value2)
                df.loc[tips[cat2] == value2].plot(kind="scatter", x="total_bill", y="tip",
                                                  ax=self.axes[i], c=colors[j], label=value2)
        self.axes[i].legend()
        self.graph.draw()
        
if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    
    table = Table("HOA_ADMIN_HOA_DRUCK.csv")
    
    a = QApplication([])
    df = OWSeabornTest()

    df.set_input_data(table)
    
    df.show()
    a.exec()
