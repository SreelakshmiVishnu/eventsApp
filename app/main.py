from fastapi import FastAPI, Depends, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
import json
from itsdangerous import URLSafeSerializer

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Session management
SECRET_KEY = "mysecretkey123"
serializer = URLSafeSerializer(SECRET_KEY)

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get current admin
def get_current_admin(request: Request):
    cookie = request.cookies.get("admin_session")
    if cookie:
        try:
            username = serializer.loads(cookie)
            if username == ADMIN_USERNAME:
                return username
        except:
            return None
    return None

# Protect admin pages
def require_admin(request: Request):
    return get_current_admin(request) is not None

# Home page
@app.get("/")
def read_events(request: Request, db: Session = Depends(get_db)):
    events = crud.get_events(db)
    featured = crud.get_featured_events(db)
    for e in events + featured:
        if isinstance(e.dates, str):
            e.dates = json.loads(e.dates)
    return templates.TemplateResponse(
        "index.html", {"request": request, "events": events, "featured": featured}
    )

# Event details
@app.get("/event/{event_id}")
def event_detail(request: Request, event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if event and isinstance(event.dates, str):
        event.dates = json.loads(event.dates)
    return templates.TemplateResponse("event_detail.html", {"request": request, "event": event})

# Admin login page
@app.get("/admin/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# Handle login
@app.post("/admin/login")
def admin_login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session_cookie = serializer.dumps(username)
        response = RedirectResponse(url="/admin/events/create", status_code=303)
        response.set_cookie(key="admin_session", value=session_cookie, httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

# Admin logout
@app.get("/admin/logout")
def admin_logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("admin_session")
    return response

# Admin create event form
@app.get("/admin/events/create")
def create_event_form(request: Request):
    if not require_admin(request):
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse("create_event.html", {"request": request})

# Handle event creation
@app.post("/admin/events/create")
def create_event(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    dates: str = Form(...),
    place: str = Form(None),
    outstanding: bool = Form(False),
    image_url: str = Form(None),
    db: Session = Depends(get_db)
):
    if not require_admin(request):
        return RedirectResponse(url="/admin/login")
    
    dates_list = [d.strip() for d in dates.split(",")]
    event = schemas.EventCreate(
        name=name, description=description, dates=dates_list,
        place=place, outstanding=outstanding, image_url=image_url
    )
    crud.create_event(db, event)
    return RedirectResponse(url="/", status_code=303)
