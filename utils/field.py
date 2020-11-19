import numpy as np

FAIL_REWARD = -100
STEP_REWARD = 0
REPEATED_STEP_REWARD = -5
WIN_REWARD = 100


class Field:
    def __init__(self, w: int = 20, h: int = 20, n_mines=80):
        self.w = w
        self.h = h
        self.size = w * h
        self.n_mines = n_mines
        self.mines = np.zeros((h, w))
        self.current_map = np.full_like(self.mines, -1)
        self.flags = np.zeros((h, w))
        self.mines_placed = False
        self.lost = False

    def _get_exclusion_zone(self, center, zone_size=4):
        cx, cy = center
        ltx, lty = cx - zone_size // 2, cy - zone_size // 2
        rbx, rby = cx + zone_size // 2, cy + zone_size // 2
        return set([self.w * y + x for x in range(ltx, rbx)
                                   for y in range(lty, rby)])

    def place_mines(self, first_step_idx):

        exclusion_zone = self._get_exclusion_zone(first_step_idx, zone_size=4)
        placed_mines = 0
        while placed_mines < self.n_mines:
            k = np.random.randint(0, self.size)
            if k in exclusion_zone:
                continue
            i, j = k // self.w, k - (k // self.w) * self.w
            self.mines[i, j] = 1
            exclusion_zone.add(k)
            placed_mines += 1
        self.mines_placed = True

    def open_near(self, stepx, stepy):
        stack = [[stepx, stepy]]
        while len(stack) > 0:
            x, y = stack.pop()

            t, b, l, r = (max(0, y - 1), min(y + 2, self.h),
                          max(0, x - 1), min(x + 2, self.w))
            n_nearest_flags = np.sum(self.flags[t:b, l:r])

            if (n_nearest_flags > 0 and n_nearest_flags == self.current_map[y, x]):
                if np.sum(self.mines[t:b, l:r][self.flags[t:b, l:r].astype(bool)]) != n_nearest_flags:
                    self.open_map()
                    return FAIL_REWARD
                for shift_x in [-1, 0, 1]:
                    for shift_y in [-1, 0, 1]:
                        if 0 <= (x + shift_x) < self.w and \
                            0 <= (y + shift_y) < self.h:
                            if (shift_x == 0 and shift_y == 0) or self.mines[
                                y + shift_y, x + shift_x]:
                                continue
                            if (self.current_map[y + shift_y, x + shift_x] == -1):
                                stack.append([x + shift_x, y + shift_y])

            if (self.current_map[y, x] == -1 and not self.mines[y, x]) and not self.flags[y, x]:
                self.current_map[y, x] = np.sum(self.mines[t:b, l:r])
                if not self.current_map[y, x]:
                    for shift_x in [-1, 0, 1]:
                        for shift_y in [-1, 0, 1]:
                            if shift_x == 0 and shift_y == 0:
                                continue
                            if 0 <= (x + shift_x) < self.w and \
                                0 <= (y + shift_y) < self.h:
                                stack.append([x + shift_x, y + shift_y])

    def step(self, stepx, stepy):
        """
        1. 0 mines --> add all surrounding
        2. > 0 mines --> put number and continue
        3. it's mine -> do nothing
        """
        if not self.mines_placed:
            self.place_mines((stepx, stepy))

        if self.current_map[stepy, stepx] == -1:
            if self.mines[stepy, stepx]:
                # self.current_map[stepy, stepx] = FAIL_REWARD
                self.open_map()
                self.lost = True
                return FAIL_REWARD

        reward = self.open_near(stepx, stepy)
        if reward is not None:
            return reward

        if np.all((self.current_map == -1) == self.mines.astype(bool)):
            return WIN_REWARD
        return STEP_REWARD

    def open_map(self):
        self.current_map[self.mines.astype(bool)] = FAIL_REWARD

    def reset(self):
        self.mines = np.zeros((self.h, self.w))
        self.current_map = np.full_like(self.mines, -1)
        self.flags = np.zeros((self.h, self.w))
        self.mines_placed = False
        self.lost = False
