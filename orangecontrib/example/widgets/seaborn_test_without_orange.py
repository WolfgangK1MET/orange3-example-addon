from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns

tips = sns.load_dataset("tips")

class MainWindow(QtWidgets.QMainWindow):
    send_fig = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.main_widget = QtWidgets.QWidget(self)

        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122, sharex=self.ax1, sharey=self.ax1)
        self.axes=[self.ax1, self.ax2]
        self.canvas = FigureCanvas(self.fig)

        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        self.dropdown1 = QtWidgets.QComboBox()
        self.dropdown1.addItems(["sex", "time", "smoker"])
        self.dropdown2 = QtWidgets.QComboBox()
        self.dropdown2.addItems(["sex", "time", "smoker", "day"])
        self.dropdown2.setCurrentIndex(2)

        self.dropdown1.currentIndexChanged.connect(self.update)
        self.dropdown2.currentIndexChanged.connect(self.update)
        self.label = QtWidgets.QLabel("A plot:")

        self.layout = QtWidgets.QGridLayout(self.main_widget)
        self.layout.addWidget(QtWidgets.QLabel("Select category for subplots"))
        self.layout.addWidget(self.dropdown1)
        self.layout.addWidget(QtWidgets.QLabel("Select category for markers"))
        self.layout.addWidget(self.dropdown2)

        self.layout.addWidget(self.canvas)

        self.setCentralWidget(self.main_widget)
        self.show()
        self.update()

    def update(self):

        colors=["b", "r", "g", "y", "k", "c"]
        self.ax1.clear()
        self.ax2.clear()
        cat1 = self.dropdown1.currentText()
        cat2 = self.dropdown2.currentText()
        print (cat1, cat2)

        for i, value in enumerate(tips[cat1].unique()):
            print ("value ", value)
            df = tips.loc[tips[cat1] == value]
            self.axes[i].set_title(cat1 + ": " + value)
            for j, value2 in enumerate(df[cat2].unique()):
                print ("value2 ", value2)
                df.loc[ tips[cat2] == value2 ].plot(kind="scatter", x="total_bill", y="tip",
                                                ax=self.axes[i], c=colors[j], label=value2)
        self.axes[i].legend()
        self.fig.canvas.draw_idle()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())