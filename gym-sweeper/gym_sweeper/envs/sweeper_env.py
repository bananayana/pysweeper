import PIL
import gym
import numpy as np
from gym import spaces

from .field import Field, FAIL_REWARD


class MinerEnv(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, w=8, h=8, n=10):
        self.action_space = spaces.Discrete(w * h)
        self.observation_space = spaces.Box(low=-1., high=0.8, shape=(h, w, 1), dtype=float)
        self.game = Field(w=w, h=h, n_mines=n)

    def _current_map2observation(self):
        current_map = self.game.current_map.copy()
        current_map[current_map == -1] = -10
        current_map /= 10
        current_map = current_map[:, :, None]
        return current_map

    def step(self, action: int):
        y = action // self.game.w
        x = action - y * self.game.w
        observation = self._current_map2observation()
        reward = self.game.step(x, y)
        done = reward == FAIL_REWARD
        if done:
            self.reset()
        return observation, float(reward), done, {}

    def reset(self):
        self.game.reset()
        return self.game.current_map.copy()[:, :, None]

    def render(self, mode='human', tile_size=64):
        dst = PIL.Image.new('RGB', (int(tile_size * self.game.w), int(tile_size * self.game.h)))
        tile_map = {val: PIL.Image.open(f'data/imcrops/{val}.jpg').resize((tile_size, tile_size))
                    for val in list(range(9)) + [-1, -100]}
        for x in range(self.game.w):
            for y in range(self.game.h):
                dst.paste(tile_map[int(self.game.current_map[y, x])], (x * tile_size, y * tile_size))

        if mode == 'rgb_array':
            return np.array(dst)
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(dst.asarray())
            return self.viewer.isopen
