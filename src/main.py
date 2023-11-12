from typing import Callable

class state:
    def __init__(self, title: str, callback: Callable[[], None]) -> None:
        self._title = title
        self._callback = callback

    @property
    def title(self) -> str:
        return self._title

    @property
    def callback(self):
        return None if not self._callback else self._callback

'''
    A multi-state class allows for storing and managing a sequentially-iteratable
    list of states. It can work with 1 up-to whatever the maximum amount of
    items a list can store at a single time.

    Note that multistate.callback() will never execute the callback, it only
    return a reference to the callback. Executing the callback must be the
    responsibility of the original caller.
'''
class multistate:
    def __init__(self, states: list[state] = None) -> None:
        self.states = [] if states == None else states

    def forward(self) -> None:
        self.states.append(self.states.pop(0))

    @property
    def title(self):
        return self.states[0].title
    
    @property
    def callback(self):
        return self.states[0].callback
