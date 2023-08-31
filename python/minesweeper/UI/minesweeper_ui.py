from .Qt import QtWidgets, QtCore, QtGui
import os
import random
from functools import partial

class PushButtomIcon(QtWidgets.QPushButton):
    WIDTH = 30
    HEIGHT = 30
    ICONS_DIR = 'icons'

    def __init__(self, *args, **kwargs):
        # path
        # size
        super(PushButtomIcon, self).__init__(kwargs.get('parent'))
        size = kwargs.get('size')
        if not size:
            size = (self.WIDTH, self.HEIGHT)
        self.set_size(size)
        self.set_icon(kwargs.get('icon_file') or '')

    def set_size(self, size):
        self.setFixedSize(size[0], size[1])

    def set_icon(self, icon_file):
        icon_path = self.getFilePath(self.ICONS_DIR, icon_file)
        icon = QtGui.QImage(icon_path)
        icon = icon.scaled(self.width(), self.height(),  QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self.pixmap = QtGui.QPixmap()
        self.pixmap.convertFromImage(icon)

        self.update()

    def paintEvent(self, e):
        super(PushButtomIcon, self).paintEvent(e)
        if self.__dict__.get('pixmap'):
            painter = QtGui.QPainter(self)
            painter.drawPixmap(self.rect(), self.pixmap)

    def getFilePath(self, folder, fileName):
        path = os.path.dirname(__file__)
        path = os.path.split(path)[0]
        path = os.path.join(path, folder, fileName)
        path = os.path.realpath(path)
        return path

class Cell(PushButtomIcon):
    _revealed = False
    CELL_0 = 0
    CELL_1 = 1
    CELL_2 = 2
    CELL_3 = 3
    CELL_4 = 4
    CELL_5 = 5
    MINE = -1
    FLAG = -2
        # Icons files
    ICONS_FILES = {
        FLAG   : 'flag.jpg',
        MINE   : 'mine.jpg',
        CELL_0 :  '',
        CELL_1 : 'cell_1.png',
        CELL_2 : 'cell_2.png',
        CELL_3 : 'cell_3.png',
        CELL_4 : 'cell_4.png',
        CELL_5 : 'cell_5.png', 

    }
    #   Signals
    flaged = QtCore.Signal(int)
    revealed = QtCore.Signal()
    exploded = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        # args :
            # type 
            # column
            # row 
        # kwargs :
            # size
        self.type, self.column, self.row = args
        self.old_type = self.type

        super(PushButtomIcon, self).__init__(kwargs.get('parent'))

        self.set_size(kwargs.get('size'))


    def set_icon(self, remove = False):
        if remove :
            icon_path = ''
        else:
            icon_path = self.getFilePath(self.ICONS_DIR, self.get_icon_file())
        icon = QtGui.QImage(icon_path)
        icon = icon.scaled(self.width(), self.height(),  QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self.pixmap = QtGui.QPixmap()
        self.pixmap.convertFromImage(icon)

        self.update()

    def reveal(self):
        if self.type == self.CELL_0 :
            grid_btns = MineSweeperUI.get_grid_buttons()
            row_size = len(grid_btns[0])
            column_size = len(grid_btns)

            row_min = max(min(self.row - 1 , row_size), 0)
            row_max = max(min(self.row + 1 , row_size), 0)        
            column_min = max(min(self.column - 1 , column_size), 0)
            column_max = max(min(self.column + 1 , column_size), 0)

            for i_column in range(column_min, column_max + 1) : 
                for i_row in range(row_min, row_max + 1): 
                    try:
                        cell = grid_btns[i_column][i_row]
                        if cell != self:
                            if not cell.is_revealed():
                                cell.set_revealed()
                                cell.reveal()
                    except:
                        pass
        else:
            if self.is_flaged():
                self.remove_flag()

            self.set_icon()
            self.set_revealed()

        if self.type == self.MINE:
                self.exploded.emit()

        self.setDisabled(True)  

    def set_revealed(self):
        if not self._revealed:
            self._revealed = True
            self.revealed.emit()

    def is_revealed(self):
        return self._revealed

    def is_flaged(self):
        return self.type == self.FLAG

    def add_flag(self):
        self.type = self.FLAG
        self.set_icon()

    def remove_flag(self):
        self.type = self.old_type
        self.set_icon(remove = True)

    def get_type(self):
        return self.type

    def get_icon_file(self):
        return self.ICONS_FILES.get(self.type)

    def mousePressEvent(self, event):
        super(Cell, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.RightButton:
            if not self.is_flaged():
                self.add_flag()
                self.flaged.emit(True)
            else:
                self.remove_flag()
                self.flaged.emit(False)
        if event.button() == QtCore.Qt.LeftButton:
            if not self.is_flaged() and not self.is_revealed():
                self.reveal()

class CustomDialog(QtWidgets.QDialog):
    WINDOW_TITLE = 'Game Custom'
    nb_mines = 0
    grid_size = 0
    changesSaved = QtCore.Signal()

    def __init__(self, grid_size, nb_mines, parent = None):
        super(CustomDialog, self).__init__(parent)
        self.grid_size = grid_size
        self.nb_mines = nb_mines

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(150, 100)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.row_sb = QtWidgets.QSpinBox()
        self.row_sb.setMinimum(2)
        self.row_sb.setValue(self.grid_size[0])

        self.column_sb = QtWidgets.QSpinBox()
        self.column_sb.setMinimum(2)
        self.column_sb.setValue(self.grid_size[1])

        self.nb_mines_sb = QtWidgets.QSpinBox()
        self.nb_mines_sb.setMinimum(1)
        self.nb_mines_sb.setValue(self.nb_mines)

        self.save_changes_btn = QtWidgets.QPushButton('Save Changes')

    def create_layouts(self):
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.addWidget(QtWidgets.QLabel('Rows : '))
        row_layout.addWidget(self.row_sb)
        row_layout.setStretch(1, 1)

        column_layout = QtWidgets.QHBoxLayout()
        column_layout.addWidget(QtWidgets.QLabel('Columns : '))
        column_layout.addWidget(self.column_sb)
        column_layout.setStretch(1, 1)

        mines_layout = QtWidgets.QHBoxLayout()
        mines_layout.addWidget(QtWidgets.QLabel('Mines : '))
        mines_layout.addWidget(self.nb_mines_sb)
        mines_layout.setStretch(1, 1)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.addLayout(row_layout)
        main_layout.addLayout(column_layout)
        main_layout.addLayout(mines_layout)
        main_layout.addStretch(0)
        main_layout.addWidget(self.save_changes_btn)

    def create_connections(self):
        self.save_changes_btn.clicked.connect(self.save_changes)

    def save_changes(self):
        self.nb_mines = self.nb_mines_sb.value()
        self.grid_size = (self.row_sb.value(), self.column_sb.value())

        self.changesSaved.emit()

        self.deleteLater()

    def get_grid_size(self):
        return self.grid_size

    def get_nb_mines(self):
        return self.nb_mines   


class MineSweeperUI(QtWidgets.QDialog):
    WINDOW_TITLE = 'MineSweeper'
    grid_ratio = (600 , 750)

    MODE_CHHOICE = {
        'easy'   : [(11, 7), (50, 50), 10],
        'medium' : [(21, 12), (35, 35), 40],
        'hard'   : [(28, 17), (25, 25), 99]
    }

    mode = ''

    GRID_SIZE_KEY = 0
    CELL_SIZE_KEY = 1
    NB_MINES_KEY = 2

    grid_btns = []
    remain_count = 0

    #Icons
    ICONS_DIR = 'icons'
    SMILEY_HAPPY = 'smiley_happy.png'
    SMILEY_SAD = 'smiley_sad.png'
    SMILEY_GLASSES = 'smiley_glasses.png'
    SMILEY_HOOO = 'smiley_hooo.png'

    CELL_0 = 0
    CELL_1 = 1
    CELL_2 = 2
    CELL_3 = 3
    CELL_4 = 4
    CELL_5 = 5
    MINE = -1
    FLAG = -2

    @classmethod
    def get_grid_buttons(cls):
        return cls.grid_btns

    def __init__(self, parent = None):
        super(MineSweeperUI, self).__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)

        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.new_game('easy')
        self.create_connections()

    def create_actions(self):
        self.easy_action = QtWidgets.QAction('Easy', self)
        self.medium_action = QtWidgets.QAction('Medium', self)
        self.hard_action = QtWidgets.QAction('Hard', self)

        self.custom_action = QtWidgets.QAction('Customize...', self)

    def create_widgets(self):
        self.menu_bar_wdg = QtWidgets.QMenuBar()
        Difficulty_menu = self.menu_bar_wdg.addMenu('Difficulty')
        Difficulty_menu.addAction(self.easy_action)
        Difficulty_menu.addAction(self.medium_action)
        Difficulty_menu.addAction(self.hard_action)
        self.menu_bar_wdg.addAction(self.custom_action)

        self.nb_mines_count_sb = QtWidgets.QSpinBox()
        self.nb_mines_count_sb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.nb_mines_count_sb.setReadOnly(True)
        self.nb_mines_count_sb.setFixedSize(90,30)

        self.restart_btn = PushButtomIcon(size = (30, 30), icon_file = self.SMILEY_HAPPY)

        self.timer_sb = QtWidgets.QSpinBox()
        self.timer_sb.setMaximum(10000)
        self.timer_sb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.timer_sb.setReadOnly(True)
        self.timer_sb.setFixedSize(90,30)

        self.timer = QtCore.QTimer()

    def create_cells_widgets(self):
        self.delete_grid_buttons()
        self.grid_btns = []
        mines = self.generate_grid_values()

        #calcul cell size
        if self.grid_size[0] > self.grid_size[1]:
            l = self.grid_ratio[0] / self.grid_size[0]
        else:
            l = self.grid_ratio[1] / self.grid_size[1]

        self.cell_size = (l, l)

        for column in range(self.grid_size[1]):
            self.grid_btns.append([])

            for row in range(self.grid_size[0]):

                cell = Cell(mines[column][row], column, row, size = self.cell_size)
                cell.flaged.connect(partial(self.update_mines_count, cell))
                cell.revealed.connect(self.update_remain_cell_count)
                cell.exploded.connect(self.game_over)

                self.grid_btns[column].append(cell)
                self.grid_layout.addWidget(cell, row, column)

        MineSweeperUI.grid_btns = self.grid_btns

    def create_layouts(self):
        game_layout = QtWidgets.QHBoxLayout()
        game_layout.addWidget(self.nb_mines_count_sb)
        game_layout.addWidget(self.restart_btn)
        game_layout.addWidget(self.timer_sb)
        game_layout.setAlignment(QtCore.Qt.AlignCenter)
        game_layout.setSpacing(5)

        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setVerticalSpacing(1)
        self.grid_layout.setSpacing(1)
        self.grid_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(15)
        main_layout.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.menu_bar_wdg)
        main_layout.addLayout(game_layout)
        main_layout.addLayout(self.grid_layout)
        main_layout.addStretch()

    def create_connections(self):
        self.restart_btn.clicked.connect(self.new_game)
        self.restart_btn.pressed.connect(partial(self.restart_btn.set_icon, self.SMILEY_HOOO))
        self.restart_btn.released.connect(partial(self.restart_btn.set_icon, self.SMILEY_HAPPY))

        self.easy_action.triggered.connect(partial(self.new_game, 'easy'))
        self.medium_action.triggered.connect(partial(self.new_game, 'medium'))
        self.hard_action.triggered.connect(partial(self.new_game, 'hard'))

        self.custom_action.triggered.connect(self.show_custom_game_window)

        self.timer.timeout.connect(self.update_timer)

    def update_timer(self):
        time = self.timer_sb.value()
        self.timer_sb.setValue(time + 1)

    def new_game(self, change_mode = None):
        if change_mode :
            if change_mode != self.mode and change_mode != 'custom':
                self.grid_size = self.MODE_CHHOICE.get(change_mode)[self.GRID_SIZE_KEY]
                self.cell_size = self.MODE_CHHOICE.get(change_mode)[self.CELL_SIZE_KEY]
                self.nb_mines = self.MODE_CHHOICE.get(change_mode)[self.NB_MINES_KEY]

        self.mode = change_mode 
        self.nb_mines_count_sb.setValue(self.nb_mines)
        self.restart_btn.set_icon(self.SMILEY_HAPPY)
        self.timer_sb.setValue(0)

        if self.timer.isActive():
            self.timer.stop()

        self.remain_count = self.grid_size[0] * self.grid_size[1] - self.nb_mines

        self.create_cells_widgets() 

    def game_over(self):
        self.restart_btn.set_icon(self.SMILEY_SAD)

        if self.timer.isActive():
            self.timer.stop()

        QtWidgets.QMessageBox.critical(self, "BOOOOOM !", " Game Over ! Try Again :( !", QtWidgets.QMessageBox.Retry)

        self.new_game()

    def game_finished(self):
        self.restart_btn.set_icon(self.SMILEY_GLASSES)

        if self.timer.isActive():
            self.timer.stop()

        QtWidgets.QMessageBox.critical(self, "YEAHHHHHH !", " You win this game ! Start Again :D !", QtWidgets.QMessageBox.Retry)

        self.new_game()

    def show_custom_game_window(self):
        self.custom_dialog = CustomDialog(self.grid_size, self.nb_mines,  parent = self)
        self.custom_dialog.changesSaved.connect(self.game_custom)
        self.custom_dialog.exec_()

    def game_custom(self):
        self.nb_mines = self.custom_dialog.get_nb_mines()
        self.grid_size = self.custom_dialog.get_grid_size()

        self.new_game('custom')

    def update_mines_count(self, cell, flaged):
        value = self.nb_mines_count_sb.value()
        if flaged :
            value -= 1
        else:
            value += 1

        self.nb_mines_count_sb.setValue(value)

    def update_remain_cell_count(self):
        self.remain_count -= 1
        if self.remain_count == 0 :
            self.game_finished()

        # The game begins with the first click
        if self.remain_count == self.grid_size[0] * self.grid_size[1] - self.nb_mines - 1:
            self.timer.start(1000)

    def delete_grid_buttons(self):
        if len(self.grid_btns):
            for i_column in range(len(self.grid_btns)):
                for i_row in range(len(self.grid_btns[i_column])):
                    button = self.grid_btns[i_column][i_row]
                    button.deleteLater()

    def generate_grid_values(self):
        value_grid = []
        mines_grid = self.generate_grid_mines()

        for i_column in range(self.grid_size[1]):
            value_grid.append([])
            for i_row in range(self.grid_size[0]):
                if mines_grid[i_column][i_row] != self.MINE:
                    value = self.count_mine_neighbour(i_column,i_row, mines_grid)
                else:
                    value = self.MINE
                value_grid[i_column].append(value)

        return value_grid

    def generate_grid_mines(self):
        # -1 : Mine
        # None : Nothing
        mines_grid = [ [self.CELL_0 for i in range(self.grid_size[0])] for j in range(self.grid_size[1])]
        choice_row = [nb for nb in range(self.grid_size[0])]
        choice_column = [nb for nb in range(self.grid_size[1])]
        nb_mines = self.nb_mines
        mine_count = 0

        while mine_count < nb_mines:
            row = random.choice(choice_row)
            column = random.choice(choice_column)
            if mines_grid[column][row] != self.MINE :
                mines_grid[column][row] = self.MINE
                mine_count += 1

        return mines_grid

    def count_mine_neighbour(self, column, row, mines_grid):
        row_min = max(min(row - 1 , self.grid_size[0]), 0)
        row_max = max(min(row + 1 , self.grid_size[0]), 0)        
        column_min = max(min(column - 1 , self.grid_size[1]), 0)
        column_max = max(min(column + 1 , self.grid_size[1]), 0)

        mine_count = 0

        for i_column in range(column_min, column_max + 1) : 
            for i_row in range(row_min, row_max + 1): 
                if [i_column, i_row] != [column, row] :
                    try:
                        cell = mines_grid[i_column][i_row]
                        if cell == self.MINE:
                            mine_count += 1
                        if mine_count == 5:
                            break
                    except:
                        pass
        return mine_count

    @staticmethod
    def getFilePath(folder, fileName):
        path = os.path.dirname(__file__)
        path = os.path.split(path)[0]
        path = os.path.join(path, folder, fileName)
        path = os.path.realpath(path)
        return path

def launch_ui():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    solitaireUI = MineSweeperUI()
    solitaireUI.show()
    app.exec_()