import sys
import psutil
import datetime
import sqlite3
from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import animation


class CustomMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setGeometry(100, 100, 1200, 600)
        self.setCentralWidget(self._main)

        try:
            self.sqlite_connection = sqlite3.connect('CPUload.db')
            self.cursor = self.sqlite_connection.cursor()

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS cpulog(
               time TEXT,
               cpuPercent REAL);
            """)
            self.sqlite_connection.commit()

        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setFixedWidth(100)
        self.comboBox.addItems(["1 секунда", "10 секунд", "1 минута"])
        self.comboBox.activated.connect(self.changeTime)

        layout = QtWidgets.QHBoxLayout(self._main)

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)

        layout.addWidget(self.canvas)
        layout.addWidget(self.comboBox)

        self.anim = animation.FuncAnimation(self.fig, self.draw_graph)

        self.ax = self.fig.subplots()
        self.x = []
        self.y = []
        self.inter_time = 1

    def draw_graph(self, step):
        x = datetime.datetime.now().time().strftime("%H:%M:%S")
        y = psutil.cpu_percent(interval=self.inter_time)
        self.x.append(x)  # есть глюки с отображением времени (запаздывает)
        self.y.append(y)

        self.sqlite_connection = sqlite3.connect('CPUload.db')
        self.cursor = self.sqlite_connection.cursor()
        percentInfo = (x, y)
        self.cursor.execute("INSERT INTO cpulog VALUES(?, ?);", percentInfo)
        self.sqlite_connection.commit()

        self.ax.clear()
        self.ax.plot(self.x, self.y, '-o')
        self.ax.set_xlabel('Время')  # отображается под данными (видимость изменяется в зависимости от размера окна)
        self.ax.set_ylabel('Процент загрузки ЦП')

        self.ax.set_ylim(0, 70)  # лучше видно график, можно изменить на (0, 100)
        self.ax.tick_params(axis='x', rotation=45)

        repeat_length = 10  # сдвиг графика (количество отображаемых точек)
        if step > repeat_length:
            self.ax.set_xlim(step - repeat_length, step)
        else:
            self.ax.set_xlim(0, repeat_length)

        self.ax.grid()

    def changeTime(self, _):
        ctext = self.comboBox.currentText()

        # подтормаживает при выборе, при переключении первые 2-3 точки выводит с неправильным временем
        if ctext == "1 секунда":
            self.inter_time = 1
        elif ctext == "10 секунд":
            self.inter_time = 10
        elif ctext == "1 минута":
            self.inter_time = 60

    def closeEvent(self, event):
        '''
        при закрытии окна "через крестик", база дозаписывает данные и соединение отключается
        выдаёт ошибку, что окно не отвечает, если ничего не трогать (не закрывать окно и не нажимать одну из кнопок),
        программа завершается корректно
        '''
        self.sqlite_connection.commit()
        self.sqlite_connection.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myGUI = CustomMainWindow()
    myGUI.show()

    sys.exit(app.exec_())
