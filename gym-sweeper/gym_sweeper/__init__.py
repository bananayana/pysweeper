from gym.envs.registration import register

register(
     id='sweeper-v0',
     entry_point='gym_sweeper.envs:MinerEnv',
 )