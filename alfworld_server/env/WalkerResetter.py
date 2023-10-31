class WalkerResetter:
    def reset(self, env, steps):
        env.reset()
        [env.step(step) for step in steps]
        return env
