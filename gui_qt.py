import sys

from PySide2 import QtCore
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, \
    QPushButton

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
        self.setPixmap(pixmap.scaled(QtCore.QSize(32, 32)))
        self.setObjectName(f'{x}_{y}')
        self.setMinimumSize(32, 32)

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
        # self.setMinimumSize(temp, temp)

        self.setPixmap(pixmap.scaled(temp, temp, QtCore.Qt.KeepAspectRatio))
        self.setMaximumSize(10000000, 10000000)
        # self.setMinimumSize(1, 1)


def lock_all_tiles(game, grid):
    for x in range(0, game.w):
        for y in range(0, game.h):
            label_ = grid.itemAtPosition(y, x).widget()
            label_.clickable = False
            if game.won and game.mines[y, x] and not game.flags[y, x]:
                game.flags[y, x] = 1
                label_.update_label('flag')


from PySide2.QtWidgets import QBoxLayout, QSpacerItem, QWidget


class AspectRatioWidget(QWidget):
    def __init__(self, widget):
        super(AspectRatioWidget, self).__init__()
        self.aspect_ratio = widget.size().width() / widget.size().height()
        self.setLayout(QBoxLayout(QBoxLayout.LeftToRight, self))
        #  add spacer, then widget, then spacer
        self.layout().addItem(QSpacerItem(0, 0))
        self.layout().addWidget(widget)
        self.layout().addItem(QSpacerItem(0, 0))

    def resizeEvent(self, e):
        w = e.size().width()
        h = e.size().height()

        if w / h > self.aspect_ratio:  # too wide
            self.layout().setDirection(QBoxLayout.RightToLeft)
            widget_stretch = h * self.aspect_ratio
            outer_stretch = (w - widget_stretch) / 2 * 1.5
        else:  # too tall
            self.layout().setDirection(QBoxLayout.BottomToTop)
            widget_stretch = w / self.aspect_ratio
            outer_stretch = (h - widget_stretch) / 2 + 0.5

        self.layout().setStretch(0, outer_stretch)
        self.layout().setStretch(1, widget_stretch)
        self.layout().setStretch(2, outer_stretch)


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
            label_ = button_grid.itemAtPosition(0, 0)
            label_.widget().setText('Congrats, get in there Lewis')
            lock_all_tiles(game, grid)

        if reward == FAIL_REWARD:
            label_ = button_grid.itemAtPosition(0, 0)
            label_.widget().setText('Bono, my tyres are gone')
            lock_all_tiles(game, grid)

    layout.addLayout(grid, 0, 0)

    button_grid = QGridLayout()
    label = QLabel('')
    new_game_button = QPushButton('New Game')

    def new_game():
        game.reset()
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
        label_ = button_grid.itemAtPosition(0, 0)
        label_.widget().setText(' ' * 28)

    new_game_button.clicked.connect(new_game)
    button_grid.addWidget(label, 0, 0)
    button_grid.addWidget(new_game_button, 1, 0)
    layout.addLayout(button_grid, 0, 1)
    layout.setColumnStretch(0, 9)
    layout.setColumnStretch(1, 1)

    new_game()

    win.setLayout(layout)
    win_parent = AspectRatioWidget(win)
    win_parent.setWindowTitle("Sweep all that shet")
    win_parent.setGeometry(50, 50, 200, 200)
    win_parent.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
