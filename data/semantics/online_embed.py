import numpy as np

class OnlineEmbedder:
    def __init__(self, dim=16):
        self.dim = dim
        self.proj = np.eye(dim)  # simple linear projection (stub)
        self.memory_bank = []

    def update(self, x):
        # Simulate online update (e.g., InfoNCE or similar)
        self.proj += 0.01 * np.outer(x, x)
        self.memory_bank.append(x)
        if len(self.memory_bank) > 100:
            self.memory_bank.pop(0)

    def embed(self, x):
        return np.dot(self.proj, x)
