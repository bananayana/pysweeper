from typing import Tuple

import gym
import PIL

from field import Field, FAIL_REWARD


class MinerEnv(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, w=8, h=8, n=10):
        self.game = Field(w=w, h=h, n_mines=n)

    def step(self, action: Tuple[int, int]):
        observation = self.game.current_map.copy()
        reward = self.game.step(*action)
        done = reward == FAIL_REWARD
        if done:
            self.reset()
        return observation, reward, done, {}

    def reset(self):
        self.game.reset()
        return self.game.current_map.copy()

    def render(self, mode='human', tile_size=64):
        dst = PIL.Image.new('RGB', (int(tile_size * self.game.w), int(tile_size * self.game.h)))
        tile_map = {val: PIL.Image.open(f'data/imcrops/{val}').resize((tile_size, tile_size))
                    for val in list(range(9)) + [-1, -100]}
        for x in range(self.game.w):
            for y in range(self.game.h):
                dst.paste(tile_map[int(self.game.current_map[y, y])], (x * tile_size, y * tile_size))
        
        if mode == 'rgb_array':
            return dst.asarray()
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(dst.asarray())
            return self.viewer.isopen
