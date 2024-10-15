from .__system__.auth.loginPage import router as loginPage
from .__system__.userPage import router as userPage
from .__system__.scopePage import router as scopePage
from .__system__.repositoryPage import router as repositoryPage
from .__system__.settingsPage import router as settingsPage
from .__system__.logsPage import router as logsPage
from .__system__.documentationPage import router as documentationPage
from .dashboardPage import router as dashboardPage

__all__ = [
    "loginPage",
    "loginPage",
    ####SYSTEM#############################################################################################################
    "userPage",
    "scopePage",
    "repositoryPage",
    "settingsPage",
    "logsPage",
    "documentationPage",
    #######################################################################################################################
    "dashboardPage",
]
