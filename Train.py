from stable_baselines3.dqn import MlpPolicy, CnnPolicy

from CustomBaselines3.DoubleDQN import DoubleDQN

from stable_baselines3.common.callbacks import CheckpointCallback

import os

def train(env,
          eval_env,
          name,
          total_timesteps=300000,
          eval_freq=1000,
          n_eval_episodes=5,
          learning_rate=1e-5,
          learning_starts=10000,
          buffer_size=100000,
          batch_size=32,
          exploration_initial_eps=0.9,
          exploration_fraction=0.5,
          exploration_final_eps=0.0055,
          gamma=0.98,
          target_update_interval=1,
          gradient_steps=-1,
          tau=0.96,
          use_prioritized_replay=True,
          prioritized_replay_eps=1e-5,
          prioritized_replay_initial_beta=1.0,
          prioritized_replay_final_beta=0.1,
          prioritized_replay_beta_fraction=0.55,
          device="auto",
          use_cnn=True,
          ):
    """
    Function to begin training with provided training-parameters. Creates folders for checkpoints with provided name-variable.
    """

    path1 = "dDQN-checkpoints/" + name
    if not os.path.exists(path1):
        os.makedirs(path1)
    else:
        raise Exception("Traning name already exists")

    checkpoint_callback = CheckpointCallback(
        save_freq=5000,
        save_path=path1,
        name_prefix="checkpoint",
        save_replay_buffer=False,
        save_vecnormalize=True
    )

    if use_cnn:
        policy = CnnPolicy
        policy_kwargs = dict(net_arch=[64])
    else:
        policy = MlpPolicy
        policy_kwargs = None

    model = DoubleDQN(
        env=env,
        policy=policy,
        learning_rate=learning_rate,
        learning_starts=learning_starts,
        buffer_size=buffer_size,
        exploration_initial_eps=exploration_initial_eps,
        exploration_fraction=exploration_fraction,
        exploration_final_eps=exploration_final_eps,
        gamma=gamma,
        target_update_interval=target_update_interval,
        gradient_steps=gradient_steps,
        batch_size=batch_size,
        tau=tau,
        tensorboard_log="./DQN_steve_tensorboard/",
        use_prioritized_replay=use_prioritized_replay,
        prioritized_replay_eps=prioritized_replay_eps,
        prioritized_replay_initial_beta=prioritized_replay_initial_beta,
        prioritized_replay_beta_fraction=prioritized_replay_beta_fraction,
        prioritized_replay_final_beta=prioritized_replay_final_beta,
        device=device,
        policy_kwargs=policy_kwargs
    )

    model.learn(total_timesteps=total_timesteps,
                eval_env=eval_env,
                eval_freq=eval_freq,
                n_eval_episodes=n_eval_episodes,
                callback=checkpoint_callback,
                tb_log_name=name
                )

    path2 = "dDQN-checkpoints/" + name
    if not os.path.exists(path2):
        os.makedirs(path2)

    model.save(path1 + "/" + "final_model")
