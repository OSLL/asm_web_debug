from enum import Enum


class DebugCommands(Enum):
    START_DEBUG = "1"
    CONTINUE = "2"
    STEP_INTO = "3"
    STEP_OVER = "4"
    STEP_OUT = "5"
