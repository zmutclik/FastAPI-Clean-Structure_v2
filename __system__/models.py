from app.models.__system__.logs import TableLogs
from app.models.__system__.auth.scope import ScopeTable
from app.models.__system__.auth.users import UsersTable
from app.models.__system__.auth.userscope import UserScopeTable

__all__ = [
    "TableLogs",
    "ScopeTable",
    "UsersTable",
    "UserScopeTable",
]
