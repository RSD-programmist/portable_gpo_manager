"""
Windows module - классы окон интерфейса
"""
from .group_policy import GroupPolicyWindow
from .accounts import AccountsWindow
from .network import NetworkCheckWindow
from .profiles import ProfilesWindow
from .logs import LogsWindow

__all__ = [
    'GroupPolicyWindow', 'AccountsWindow',
    'NetworkCheckWindow', 'ProfilesWindow', 'LogsWindow'
]