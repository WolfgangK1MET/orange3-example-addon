import Orange

from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input, Output, Msg
import pyqtgraph as pg


class OWEasyMatplot(OWWidget):
    name = "PYQT Plot --- Test"
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

        self.graph = pg.PlotWidget()

        # box = gui.vBox(self.mainArea, True, margin=0)
        self.mainArea.layout().addWidget(self.graph)
        self.show()

    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset

        self.Outputs.selected.send(None)


if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication

    table = Table("WK1_20200201.csv")

    a = QApplication([])
    df = OWEasyMatplot()

    df.set_data(table)

    df.show()
    a.exec()
