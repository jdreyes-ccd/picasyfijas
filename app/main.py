from fastapi import FastAPI, Request
from app.numbers import validate_number
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
template = Jinja2Templates(directory="app/templates")
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return template.TemplateResponse("index.html", {"request": request})

@app.get("/validate/{number}")
def validate_number_endpoint(number: str):
    return {"valid": validate_number(number)}