import sys

from PySide2 import QtCore
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, \
    QPushButton, QHBoxLayout

from utils.field import Field, FAIL_REWARD, WIN_REWARD


class ClickableLabel(QLabel):
    clicked = QtCore.Signal(tuple)

    def __init__(self, x, y, val):
        super(ClickableLabel, self).__init__()
        self.setScaledContents(True)
        self.x = x
        self.y = y
        self.clickable = True
        pixmap = QPixmap(f'data/imcrops/{val}.jpg')
        self.setPixmap(pixmap.scaled(QtCore.QSize(32, 32)))
        self.setObjectName(f'{x}_{y}')

    def mousePressEvent(self, event):
        flag = event.button() == QtCore.Qt.MouseButton.RightButton
        self.clicked.emit((self.x, self.y, flag))

    def update_label(self, val):
        pixmap = QPixmap(f'data/imcrops/{val}.jpg')
        self.setPixmap(pixmap.scaled(self.pixmap().size()))

    def hasScaledContents(self) -> bool:
        return True


def lock_all_tiles(game, grid):
    for x in range(0, game.w):
        for y in range(0, game.h):
            label_ = grid.itemAtPosition(y, x).widget()
            label_.clickable = False
            if game.won and game.mines[y, x] and not game.flags[y, x]:
                game.flags[y, x] = 1
                label_.update_label('flag')


def main():
    game = Field(w=10, h=10, n_mines=20)

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
    win.setWindowTitle("Sweep all that shet")
    win.setGeometry(50, 50, 200, 200)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
