import seaborn as sns; sns.set(style="ticks", color_codes=True)
from Orange.data import Table
import Orange

from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from matplotlib import pyplot as plt
import seaborn as sns
from Orange.widgets import gui


from PyQt5 import QtGui, QtWidgets
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget

iris = sns.load_dataset("iris")
g = sns.pairplot(iris)

# Wenn man es außerhalb von Orange startet, wird nichts angezeigt (schwarz).
# In Orange wird es zwar angezeigt, jedoch sind die Labels auf jeden Fall nicht richtig gesetzt.
# Der Code ist zum Teil von Stackoverflow
# Generell ist es eher ein "hack" als wirklich eine vernünftige Lösung
# Das große Problem besteht darin, dass seaborn eine eigene Figure erstellt. Und diese ist,
# soweit ich weiß, von außen nicht wirklich zugreifbar.
class OWSeabornTest(OWWidget, QtWidgets.QMainWindow):
    name = "seaborn pairplot - test"
    description = "Widget Test seaborn"
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

        box = gui.vBox(self.mainArea, True, margin=0)
        box.layout().addWidget(self.graph)

        pp_rows = len(g.axes)
        pp_cols = len(g.axes[0])

        fig, axs = plt.subplots(pp_rows, pp_cols, figsize=(12, 12))

        xlabels, ylabels = [], []

        for ax in g.axes[-1, :]:
            xlabel = ax.xaxis.get_label_text()
            xlabels.append(xlabel)
        for ax in g.axes[:, 0]:
            ylabel = ax.yaxis.get_label_text()
            ylabels.append(ylabel)

        for i in range(len(xlabels)):
            for j in range(len(ylabels)):
                if i != j:
                    # Diagnol
                    sns.regplot(x=xlabels[i], y=ylabels[j], data=iris, scatter=True, fit_reg=False, ax=axs[j, i])
                else:
                    sns.kdeplot(iris[xlabels[i]], ax=axs[j, i])

                # Fix plot labels
                if i == 0:
                    axs[j, i].set_xlabel("")
                    axs[j, i].set_ylabel(ylabels[j])
                elif j == len(xlabels) - 1:
                    axs[j, i].set_xlabel(xlabels[i])
                    axs[j, i].set_ylabel("")
                else:
                    axs[j, i].set_xlabel("")
                    axs[j, i].set_ylabel("")

        self.graph.canvas.figure = fig

        self.update()
        self.show()
        self.graph.draw()

    @Inputs.data
    def set_input_data(self, data):
        self.__input_data = data

    def update(self):
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
