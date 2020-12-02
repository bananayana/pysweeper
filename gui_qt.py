import sys

from PySide2 import QtCore, QtGui
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, \
    QPushButton, QBoxLayout, QSpacerItem, QLineEdit
from utils.field import Field, FAIL_REWARD, WIN_REWARD


class ClickableLabel(QLabel):
    clicked = QtCore.Signal(tuple)

    def __init__(self, x, y, val):
        super(ClickableLabel, self).__init__()
        self.setScaledContents(True)
        self.x = x
        self.y = y
        self.clickable = True
        self.val = val
        pixmap = QPixmap(f'data/imcrops/{val}.jpg')
        self.setPixmap(pixmap.scaled(QtCore.QSize(64, 64)))
        self.setObjectName(f'{x}_{y}')
        self.setMinimumSize(64, 64)

    def mousePressEvent(self, event):
        flag = event.button() == QtCore.Qt.MouseButton.RightButton
        self.clicked.emit((self.x, self.y, flag))

    def update_label(self, val):
        self.val = val
        pixmap = QPixmap(f'data/imcrops/{val}.jpg')
        self.setPixmap(pixmap.scaled(self.pixmap().size()))

    def hasScaledContents(self) -> bool:
        return True

    def resizeEvent(self, event):
        temp = max(event.size().height(), event.size().width())
        pixmap = QPixmap(f'data/imcrops/{self.val}.jpg')
        self.setMaximumSize(temp, temp)

        self.setPixmap(pixmap.scaled(temp, temp, QtCore.Qt.KeepAspectRatio))
        self.setMaximumSize(10000000, 10000000)


class AspectRatioWidget(QWidget):
    def __init__(self, widget):
        super(AspectRatioWidget, self).__init__()
        self.aspect_ratio = None
        self.setLayout(QBoxLayout(QBoxLayout.LeftToRight, self))
        #  add spacer, then widget, then spacer
        self.layout().addItem(QSpacerItem(0, 0))
        self.layout().addWidget(widget)
        self.layout().addItem(QSpacerItem(0, 0))

    def resizeEvent(self, e):
        w = e.size().width()
        h = e.size().height()

        if self.aspect_ratio is None:
            self.aspect_ratio = w / h

        if w / h > self.aspect_ratio:  # too wide
            self.layout().setDirection(QBoxLayout.LeftToRight)
            widget_stretch = h * self.aspect_ratio
            outer_stretch = (w - widget_stretch) / 2
        else:  # too tall
            self.layout().setDirection(QBoxLayout.BottomToTop)
            widget_stretch = w / self.aspect_ratio
            outer_stretch = (h - widget_stretch) / 2

        self.layout().setStretch(0, outer_stretch)
        self.layout().setStretch(1, widget_stretch)
        self.layout().setStretch(2, outer_stretch)


def lock_all_tiles(game, grid):
    for x in range(0, game.w):
        for y in range(0, game.h):
            label_ = grid.itemAtPosition(y, x).widget()
            label_.clickable = False
            if game.won and game.mines[y, x] and not game.flags[y, x]:
                game.flags[y, x] = 1
                label_.update_label('flag')


def reset_layout(self, layout):
    try:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.delete_layout(item.layout())
    except Exception as e:
        print(e)


def main():
    game = Field(w=30, h=16, n_mines=20)

    app = QApplication(sys.argv)
    win = QWidget()
    layout = QGridLayout()
    grid = QGridLayout()
    grid.setSpacing(0)

    def update_label_img(args):
        x, y, flag = args
        label_ = grid.itemAtPosition(y, x).widget()
        if flag and not (game.lost or game.won):
            if game.current_map[y, x] == -1:
                if label_.clickable:
                    game.flags[y, x] = 1
                    label_.update_label('flag')
                    label_.clickable = False
                else:
                    game.flags[y, x] = 0
                    label_.update_label('-1')
                    label_.clickable = True
            flags_mines_number_label.setText(f'Flags: {int(game.flags.sum())} / {game.n_mines}')
            return
        elif flag:
            return

        if not label_.clickable:
            return

        reward = game.step(x, y)
        for x in range(0, game.w):
            for y in range(0, game.h):
                label_ = grid.itemAtPosition(y, x).widget()
                if label_.clickable:
                    label_.update_label(int(game.current_map[y, x]))
        if reward == WIN_REWARD:
            flags_mines_number_label.setText(f'Flags: {game.n_mines} / {game.n_mines}')
            final_msg_label.setText('Congrats, get in there Lewis')
            lock_all_tiles(game, grid)

        if reward == FAIL_REWARD:
            final_msg_label.setText('Bono, my tyres are gone')
            lock_all_tiles(game, grid)

    input_grid = QGridLayout()
    width_label = QLabel()
    width_label.setText('Width: ')
    width_input = QLineEdit()
    width_input.setText('30')
    width_input.setValidator(QtGui.QIntValidator())
    width_input.setMaxLength(2)

    input_grid.addWidget(width_label, 0, 0)
    input_grid.addWidget(width_input, 0, 1)

    height_label = QLabel()
    height_label.setText('Height: ')
    height_input = QLineEdit()
    height_input.setText('16')
    height_input.setValidator(QtGui.QIntValidator())
    height_input.setMaxLength(2)

    input_grid.addWidget(height_label, 1, 0)
    input_grid.addWidget(height_input, 1, 1)

    n_mines_label = QLabel()
    n_mines_label.setText('Mines: ')
    n_mines_input = QLineEdit()
    n_mines_input.setText('99')
    n_mines_input.setValidator(QtGui.QIntValidator())
    n_mines_input.setMaxLength(3)

    input_grid.addWidget(n_mines_label, 2, 0)
    input_grid.addWidget(n_mines_input, 2, 1)

    button_grid = QGridLayout()
    button_grid.setColumnMinimumWidth(0, 300)
    final_msg_label = QLabel()
    final_msg_label.setAlignment(QtCore.Qt.AlignCenter)
    flags_mines_number_label = QLabel()
    flags_mines_number_label.setAlignment(QtCore.Qt.AlignHCenter)
    new_game_button = QPushButton('New Game')

    def new_game():
        old_game_w, old_game_h = game.w, game.h
        game.w = int(width_input.text())
        game.h = int(height_input.text())
        game.n_mines = int(n_mines_input.text())
        game.size = game.w * game.h
        game.reset()

        if not (old_game_h == game.h and old_game_w == game.w):
            layout.removeItem(grid)
            layout.update()

            for i in reversed(range(grid.count())):
                grid.takeAt(i).widget().deleteLater()
            grid.layout().update()

            current_w, current_h = win_parent.size().width(), win_parent.size().height()
            new_win_w, new_win_h = int(game.w * current_w / old_game_w), int(game.h * current_h / old_game_h)
            win_parent.aspect_ratio = new_win_w / new_win_h
            win_parent.resizeEvent(QtGui.QResizeEvent(QtCore.QSize(new_win_w, new_win_h),
                                                      QtCore.QSize(current_w, current_h)))
            win.adjustSize()
            win_parent.adjustSize()

        for x in range(0, game.w):
            for y in range(0, game.h):
                label = grid.itemAtPosition(y, x)
                if label is None:
                    label = ClickableLabel(x, y, -1)
                    label.clicked.connect(update_label_img)
                    grid.addWidget(label, y, x)
                else:
                    label = label.widget()
                    label.update_label(-1)
                    label.clickable = True
        flags_mines_number_label.setText(f'Flags: 0 / {game.n_mines}')
        final_msg_label.setText(' ' * 28)
        layout.addLayout(grid, 0, 0)

    new_game_button.clicked.connect(new_game)
    button_grid.addWidget(flags_mines_number_label, 0, 0)
    button_grid.addLayout(input_grid, 1, 0)
    button_grid.addWidget(final_msg_label, 2, 0)
    button_grid.addWidget(new_game_button, 3, 0)
    layout.addLayout(button_grid, 0, 1)
    layout.setColumnStretch(0, 9)
    layout.setColumnStretch(1, 1)

    win.setLayout(layout)
    win_parent = AspectRatioWidget(win)

    new_game()

    win_parent.setWindowTitle("Sweep all that shet")
    win_parent.setGeometry(50, 50, 200, 200)
    win_parent.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
