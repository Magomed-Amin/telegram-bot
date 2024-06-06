import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import tkinter as tk
import numpy as np
import math
from PIL import Image, ImageTk


def get_matrix_size(): # Создание 1ого окна ввода размеров матрицы смежности
    def on_submit_size(): # При нажатии на кнопку "Подтвердить" в 1 окне
        nonlocal rows, cols
        rows = int(row_entry.get())
        cols = int(col_entry.get())
        root_size.destroy()
        create_matrix_input_window()

    def create_matrix_input_window(): # Создание 2ого окна ввода матрицы смежности
        nonlocal matrix
        matrix = []

        root_matrix = tk.Tk()
        root_matrix.title("Ввод матрицы")

        for i in range(rows):
            row = []
            for j in range(cols):
                entry_var = tk.StringVar()
                entry = tk.Entry(root_matrix, textvariable=entry_var, width=5)
                entry.grid(row=i, column=j)
                row.append(entry_var)
            matrix.append(row)

        def on_submit_matrix(): # При нажатии на кнопку "Подтвердить" во 2ом окне
            result_matrix = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    value = matrix[i][j].get()
                    if value.strip():
                        row.append(int(value))
                    else:
                        row.append(0)
                result_matrix.append(row)
            root_matrix.destroy()

        submit_button_matrix = tk.Button(root_matrix, text="Подтвердить", command=on_submit_matrix)
        submit_button_matrix.grid(row=rows, columnspan=cols)

        root_matrix.mainloop()

    rows = 0
    cols = 0
    matrix = []

    root_size = tk.Tk()
    root_size.title("Введите размеры матрицы")

    row_label = tk.Label(root_size, text="Количество строк:")
    row_label.pack()
    row_entry = tk.Entry(root_size)
    row_entry.pack()

    col_label = tk.Label(root_size, text="Количество столбцов:")
    col_label.pack()
    col_entry = tk.Entry(root_size)
    col_entry.pack()

    submit_button_size = tk.Button(root_size, text="Подтвердить", command=on_submit_size)
    submit_button_size.pack()

    root_size.mainloop()

    return [[int(j.get()) for j in i if j.get() != ''] for i in matrix]

def draw(array, colors):
    num_vertices = len(colors) # кол-во вершин
    adj_matrix = np.array(array) # перевод в массив

    radius = 2 * num_vertices # радиус круга вокруг которых будут распределяться вершины графа

    # Создание графа из матрицы смежности
    plt.figure()
    ax = plt.gca() # оси
    for i in range(num_vertices):
        angle = (2 * math.pi / num_vertices) * i # угол на котором будет распологаться {i} вершина
        # получаем координаты для i вершины
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        # Выполняем соединения вершин
        for j in range(i+1, num_vertices):
            if adj_matrix[i, j] == 1:
                angle_j = (2 * math.pi / num_vertices) * j
                x_j = radius * math.cos(angle_j)
                y_j = radius * math.sin(angle_j)
                ax.plot([x, x_j], [y, y_j], color='black')
        ax.plot(x, y, 'o', color=colors[i], markersize=17)
        ax.text(x, y, str(i), fontsize=12, ha='center', va='center')

    plt.axis('equal')
    plt.axis('off')
    plt.savefig("graph.png")
    plt.show()


class graph: # Класс, который хранит в себе все вершины
    def __init__(self, matrix):
        self.nodes = {i:node(i, matrix[i]) for i in range(len(matrix))}
    
    def getColor(self): # возвращает список цветов в порядке: от первой вершины -> к последней
        colours = list(mcolors.CSS4_COLORS)
        color = []
        for i in self.nodes.keys():
            color.append(colours[self.nodes[i].color])
        return color

    def getPowPeaks(self): # возвращает словарь со степенями каждой вершины
        dic = dict()
        arr = list(sorted(self.nodes.values(), key=lambda x:x.powe, reverse=True))
        for i in range(len(arr)):
            dic |= arr[i].connect
        return (dic, list(dic.keys()))
    
    def drawing(self): # Сам алгоритм, который возвращает словарь вида key=вершина value=цвет
        c, p = self.getPowPeaks()
        lastColor = 1
        i = 0
        while i < len(p):
            if self.nodes[p[i]].color is None:
                self.nodes[p[i]].color = lastColor
                j = 0
                while j < len(p):
                    if not self.nodes[p[j]].color is None:
                        j += 1
                        continue
                    t = False
                    for k in c[self.nodes[p[j]].number]:
                        if self.nodes[k].color == lastColor:
                            t = True
                            break
                    if not t:
                        self.nodes[p[j]].color = lastColor
                    j += 1
                lastColor += 1
            i += 1


class node: # класс отдельной вершины
    def __init__(self, number, connect):
        self.number = number # номер вершины
        self.color = None # цвет вершины
        self.connect = {number:[]} # связи с вершиной
        for i in range(len(connect)):
            if (connect[i] == 1):
                self.connect[number].append(i)
        self.powe = len(self.connect[number]) # степень вершины


def main():
    matrix = get_matrix_size()

    gr = graph(matrix)
    gr.drawing()
    color = (gr.getColor
             ())
    draw(matrix, color)


if __name__ == "__main__":
    main()