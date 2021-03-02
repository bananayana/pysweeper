import imageio
from catalyst_rl.rl.offpolicy.trainer import OffpolicyTrainer as OffpolicyTrainer
from catalyst_rl.rl.onpolicy.trainer import OnpolicyTrainer as OnpolicyTrainer

from catalyst_rl.rl.registry import (
    DATABASES, ENVIRONMENTS, OFFPOLICY_ALGORITHMS, ONPOLICY_ALGORITHMS
)
from catalyst_rl.rl.scripts.misc import (
    OFFPOLICY_ALGORITHMS_NAMES, ONPOLICY_ALGORITHMS_NAMES
)
from catalyst_rl.dl import utils
from catalyst_rl.rl.core.policy_handler import PolicyHandler
from catalyst_rl.rl.exploration import Greedy


def save_video(frames, filename='temp.mp4'):
    """Save video."""
    # Write video
    with imageio.get_writer(filename, fps=60) as video:
        for frame in frames:
            for _ in range(60):
                video.append_data(frame)


def infer():
    config = utils.load_config('catarl/configs/basic.yml', ordered=True)

    environment_name = config["environment"].pop("environment")
    environment_fn = ENVIRONMENTS.get(environment_name)

    mode = "infer"
    env = environment_fn(
        **config["environment"],
        visualize=False,
        mode=mode,
        sampler_id=id,
    )

    algorithm_name = config["algorithm"].pop("algorithm")
    if algorithm_name in OFFPOLICY_ALGORITHMS_NAMES:
        ALGORITHMS = OFFPOLICY_ALGORITHMS
        trainer_fn = OffpolicyTrainer
        sync_epoch = False
    elif algorithm_name in ONPOLICY_ALGORITHMS_NAMES:
        ALGORITHMS = ONPOLICY_ALGORITHMS
        trainer_fn = OnpolicyTrainer
        sync_epoch = True
    else:
        raise NotImplementedError()

    algorithm_fn = ALGORITHMS.get(algorithm_name)
    algorithm = algorithm_fn.prepare_for_trainer(env_spec=env, config=config)

    checkpoint = utils.load_checkpoint(filepath='catarl/logs/basic/30.pth')
    checkpoint = utils.any2device(checkpoint, utils.get_device())
    algorithm.unpack_checkpoint(
        checkpoint=checkpoint, with_optimizer=False
    )

    ph = PolicyHandler(env=env, agent=algorithm.critic, device='cuda')
    frames = []
    done = False
    observation = env.reset()
    while not done:
        states_t = utils.any2device(observation[None, :, :, :], 'cuda')
        frames.append(env.env.render(mode='rgb_array'))
        action = ph.action_fn(state=states_t, agent=algorithm.critic, device='cuda', deterministic=True,
                              exploration_strategy=Greedy)
        observation, _, done, _ = env.step(int(action))

    frames.append(env.env.render(mode='rgb_array'))
    save_video(frames)
    print()


if __name__ == '__main__':
    infer()