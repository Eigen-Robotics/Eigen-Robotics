import pickle

class EigenPolicy:
    def __init__(self, pickle_path: str, arch: str = "mlp", device: str = "cpu"):
        # Load list of list of numbers from pickle file
        with open(pickle_path, "rb") as f:
            self.trajectory = pickle.load(f)
        
        if not isinstance(self.trajectory, list):
            raise ValueError("Pickle file must contain a list of actions.")
        
        self.index = 0  # pointer to current action

    def __call__(self, observation):
        """
        Ignore observation, return next action in sequence.
        Raises StopIteration when trajectory ends.
        """
        if self.index >= len(self.trajectory):
            raise StopIteration("No more actions available in trajectory.")
        
        action = self.trajectory[self.index]
        self.index += 25
        print(f"Action Index: {self.index}/{len(self.trajectory)}")
        return action

    def is_finished(self) -> bool:
        """Return True if policy has no more actions left."""
        return self.index >= len(self.trajectory)