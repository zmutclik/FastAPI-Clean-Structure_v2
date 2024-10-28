from fastapi import FastAPI
from .__system__.auth.loginPage import router as loginPage
from .__system__.auth.profilePage import router as profilePage
from .__system__.userPage import router as userPage
from .__system__.scopePage import router as scopePage
from .__system__.repositoryPage import router as repositoryPage
from .__system__.settingsPage import router as settingsPage
from .__system__.logsPage import router as logsPage
from .__system__.documentationPage import router as documentationPage
from .dashboardPage import router as dashboardPage

###################################################################################################################
app = FastAPI(
    title="Pages",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="1.0.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    redoc_url=None,
)


@app.get("/")
def read_sub():
    return {"message": "Hello BOZ, ini API AUTH !"}


### Sub FastAPI ###
app.include_router(dashboardPage)
app.include_router(profilePage)
app.include_router(userPage)
app.include_router(scopePage)
app.include_router(repositoryPage)
app.include_router(settingsPage)
app.include_router(logsPage)
app.include_router(documentationPage)
