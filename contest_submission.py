"""Official SDK entry; all model access is owned by the platform host."""

from ite.contest_submission import TASKS, predict, train

__all__ = ["TASKS", "train", "predict"]
