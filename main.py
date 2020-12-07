import sys
import os
import re

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import networkx as nx
import numpy as np

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, \
                            QHBoxLayout, QPushButton, QGridLayout, QInputDialog,\
                            QMessageBox, QTableWidget, QFileDialog,  QTableWidgetItem,\
                            QTextEdit, QLabel
from PyQt5.QtGui import QFont

from matrix_from_file.read_matrix import read_matrix_from_file, error_handler, check_orgraph
from ostov import Ostov


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.title = 'Индивидуальное задание по КДМ'
        self.left = 200
        self.top = 200
        self.width = 800
        self.height = 600
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        widget = QWidget(self)
        self.setCentralWidget(widget)
        vlay = QVBoxLayout(widget)
        hlay = QHBoxLayout(widget)
        vlay.addLayout(hlay)
        self.setGeometry(self.left, self.top, self.width, self.height)

        main_window = WidgetPlot(self)
        vlay.addWidget(main_window)


class WidgetPlot(QWidget):

    nX_count = 5
    adj_matrix = []
    weight_matrix = []
    min_ostov = []
    isGraphPlotted = False

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.grid = QGridLayout()
        
        # Graph canvas definition
        self.graph_canvas = Plotcanvas()
        self.toolbar = NavigationToolbar(self.graph_canvas, self)
        self.graph_canvas.setMinimumWidth(900)
        # Adj Table definition
        self.adj_table = QTableWidget(self)
        self.adj_table.setMinimumHeight(400)
        self.adj_table.setMinimumWidth(500)
        self.change_table(5, self.adj_table)
        # Weight Table definition
        self.weight_table = QTableWidget(self)
        self.weight_table.setMinimumHeight(400)
        self.weight_table.setMinimumWidth(500)
        self.change_table(5, self.weight_table)
        # Change vertex amount button
        self.change_vertex_amount = QPushButton("Изменить кол-во вершин")
        self.change_vertex_amount.setFixedHeight(50)
        # Draw graph button
        self.draw_graph = QPushButton("Построить граф")
        self.draw_graph.setFixedHeight(50)
        # Load adj from file button
        self.matrix_from_file = QPushButton("Ввод м.смежности с файла")
        self.matrix_from_file.setFixedHeight(50)
        # Load weight from file button
        self.weight_matrix_from_file = QPushButton("Ввод м.весов с файла")
        self.weight_matrix_from_file.setFixedHeight(50)
        # Generate min ostov button
        self.min_ostov_generate = QPushButton("Построить минимальный остов")
        self.min_ostov_generate.setFixedHeight(50)
        # Setuping font to lables
        font = QFont()
        font.setPointSize(14)
        self.label_weight = QLabel(self)
        self.label_weight.setText("Матрица весов")
        self.label_weight.setFont(font)
        self.label_adj = QLabel(self)
        self.label_adj.setText("Матрица смежности")
        self.label_adj.setFont(font)
        # Connecting btns to funcs
        self.change_vertex_amount.clicked.connect(self.change_vertex_amount_handler)
        self.draw_graph.clicked.connect(self.draw_graph_handler)
        self.matrix_from_file.clicked.connect(self.matrix_from_file_handler)
        self.weight_matrix_from_file.clicked.connect(self.weight_matrix_from_file_handler)
        self.min_ostov_generate.clicked.connect(self.min_ostov_generate_handler)
        # Building grid
        self.grid.setColumnMinimumWidth(0, 200)
        self.grid.addWidget(self.change_vertex_amount, 0,0)
        self.grid.addWidget(self.matrix_from_file, 1,0)
        self.grid.addWidget(self.draw_graph, 2,0)
        self.grid.addWidget(self.min_ostov_generate, 8,0)
        self.grid.addWidget(self.weight_matrix_from_file, 7,0)
        self.grid.addWidget(self.adj_table, 0,1, 5,2)
        self.grid.addWidget(self.label_adj, 5,1)
        self.grid.addWidget(self.weight_table, 7,1, 5,2)
        self.grid.addWidget(self.label_weight, 13,1)
        self.grid.addWidget(self.graph_canvas, 0,3, 13,2)
        self.grid.addWidget(self.toolbar, 13,3)
        self.setLayout(self.grid)
        self.adj_matrix.clear()

    def show_msg(self, title, text):
        """ This function shows message to user with given title and text.
        """

        msg = QMessageBox()
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec_()

    def change_table(self, nX_count, table):
        """ This method changes count of given table rows and columns. 
            
        Additionally, this method changes width and height of columns to 5, 
        so table becomes more square, and vertical and horizontal labels
        of table.
        """
        
        table.setColumnCount(nX_count)
        table.setRowCount(nX_count)
        for i in range(nX_count):
            table.setVerticalHeaderItem(i, QTableWidgetItem(str(i)))
            table.setHorizontalHeaderItem(i, QTableWidgetItem(str(i)))
            table.setColumnWidth(i, 5)
            table.setRowHeight(i, 5)

    def read_table(self, table, matrix, regexp_desire_elements=False):
        """ This method reads given table to  given matrix, when user asks 
        to draw graph, along with checking erorrs which can occure with matrix, 
        such as not null main diagonal, strings in table or not full filled matrix.
        """

        matrix.clear()
        for i in range(self.nX_count):
            row = []
            for j in range(self.nX_count):
                try:
                    item = int(table.item(i, j).text())

                    if not regexp_desire_elements:
                        if item == 0 or item == 1:
                            row.append(item)
                        else:
                            return "Таблица заполнена некорректно"

                    else:
                        match = re.findall(regexp_desire_elements, str(item))
                        if match == [i for i in str(item)]:
                            row.append(item)
                        else:
                            return "Таблица заполнена некорректно"

                except AttributeError:
                    return "Заполните таблицу"
                except ValueError:
                    return "Таблица заполнена некорректно"
            matrix.append(row)
        status = error_handler(matrix)
        if status != '':
            return status

    def fill_table(self, matrix, table):
        """ This method fills given table with given matrix, which was received from file or, 
        in case of weight matrix, when graph drew from adjacency matrix."""

        i = 0
        for row in matrix:
            k = 0
            for element in row:
                table.setItem(i, k, QTableWidgetItem(str(element)))
                k += 1
            i += 1

    def change_vertex_amount_handler(self):
        """ This method asks user to enter amount of vertexes in adjacency matrix """

        self.isGraphPlotted = False
        nxCount, ok = QInputDialog.getInt(self, 'Ввод', 'Введите кол-во вершин:',
                                            min=1, max=100)
        if ok:
            self.nX_count = nxCount
            self.change_table(self.nX_count, self.adj_table)
        else:
            pass

    def draw_graph_handler(self):
        """ This method draws graph. It takes no argument, due to adj_matrix array was
        saved previously in class variable. This func analyzes matrix for symmetry
        and draw graph or digraph.
        """
        
        status = self.read_table(self.adj_table, self.adj_matrix)
        if status:
            self.adj_matrix.clear()
            self.isGraphPlotted = False
            self.show_msg("Ошибка", status)
        else:
            np_matrix = np.array(self.adj_matrix)

            status = check_orgraph(self.adj_matrix)
            if status == True:
                graph = nx.DiGraph(np_matrix)
            else:
                graph = nx.Graph(np_matrix)
            self.isGraphPlotted = True
            self.graph_canvas.plot(graph)
            self.change_table(self.nX_count, self.weight_table)
            self.fill_table(self.adj_matrix, self.weight_table)


    def matrix_from_file_handler(self):
        """ This method read adjacency matrix from txt file and fill table with its 
        elements. 
        """

        fileName, ok = QFileDialog.getOpenFileName(self, "Выбор файла",
                                                    "*.txt")
        if ok:
            nX_count, adj_matrix, error = read_matrix_from_file(fileName)
            if error:
                self.show_msg("Ошибка", error)
            else:
                self.adj_matrix = adj_matrix
                self.nX_count = nX_count
                self.change_table(self.nX_count, self.adj_table)
                self.fill_table(self.adj_matrix, self.adj_table)
        else:
            pass

    def weight_matrix_from_file_handler(self):
        """ This method read weight matrix from txt file and fill table with its 
        elements. 
        """

        if not self.isGraphPlotted:
            self.show_msg("Ошибка", "Сначала задайте м. смежности и постройте граф")
            return
        fileName, ok = QFileDialog.getOpenFileName(self, "Выбор файла",
                                                    "*.txt")
        if ok:
            nX_count, weight_matrix, error = read_matrix_from_file(fileName)
            if error:
                self.show_msg("Ошибка", error)
            else:
                if self.nX_count != nX_count:
                    self.show_msg("Ошибка", "Не соответствие кол-во вершин с м. смежности")
                self.weight_matrix = weight_matrix
                self.change_table(self.nX_count, self.weight_table)
                self.fill_table(self.weight_matrix, self.weight_table)
        else:
            pass

    def min_ostov_generate_handler(self):
        """ This function generates min ostov for given graph.

        Generates error message, if graph hadn't been given already.

        After generation shows min ostov in graph_canvas.
        """

        if not self.adj_matrix:
            self.show_msg("Ошибка", "Сначала задайте матрицу смежности и постройте граф")
            return
        else:
            status = self.read_table(self.weight_table, self.weight_matrix, '[0-9]')
            if status:
                self.show_msg("Ошибка", status)
                return

            is_or_graph = check_orgraph(self.weight_matrix)
            ostov = Ostov(self.weight_matrix, self.nX_count, is_or_graph)
            ostov.generate_ribs()

            if not ostov.ribs:
                self.show_msg("Ошибка", "Граф не имеет ребер")
                return

            min_ostov = ostov.find_min_ostov()
            self.write_and_show_listing_to_file(ostov.listing)

            if is_or_graph == True:
                min_G = nx.DiGraph()
            else:
                min_G = nx.Graph()
            min_G.add_edges_from(min_ostov)
            self.graph_canvas.plot(min_G)

    def write_and_show_listing_to_file(self, listing):
        """ This method shows listing to a screen and write it to txt file.
        """
        
        self.view = QTextEdit()
        self.view.setFixedSize(1200, 600)
        with open("listing.txt", "w") as file:
            for line in listing:
                self.view.append(line+"\n")
                file.write(line+"\n")
        self.view.setWindowTitle("Листинг")
        self.view.show()


class Plotcanvas(FigureCanvas):

    def __init__(self):
        figure = plt.figure()
        FigureCanvas.__init__(self, figure)
        self.setParent(None)
        FigureCanvas.updateGeometry(self)

    def plot(self, graph):
        self.figure.clear()
        nx.draw_circular(graph, with_labels=True, node_size=850)
        self.draw_idle()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
