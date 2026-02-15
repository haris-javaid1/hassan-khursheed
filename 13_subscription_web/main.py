from fastapi import FastAPI, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models
import auth
import stripe
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Stripe test key
stripe.api_key = "sk_test_51Suv7kGeI2OTInqlXrgjjtz67Bx8KTunfDFFsu3JFzZonJcL56ft3BUs2DIqHGryqrhE7NfSQqyys6BXW5bN68c200IUOUtLBc"

PACKAGES = {
    "basic": {"name": "Basic", "price": 9.99, "features": ["Feature 1", "Feature 2", "Email Support"]},
    "standard": {"name": "Standard", "price": 19.99, "features": ["All Basic Features", "Feature 3", "Feature 4", "Priority Support"]},
    "premium": {"name": "Premium", "price": 29.99, "features": ["All Standard Features", "Feature 5", "Feature 6", "24/7 Support"]}
}


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r") as f:
        return f.read()


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    package = request.query_params.get("package", "basic")
    if package not in PACKAGES:
        package = "basic"

    with open("signup.html", "r") as f:
        html = f.read()
        html = html.replace("{{PACKAGE}}", package)
        return html


@app.get("/signin", response_class=HTMLResponse)
async def signin_page(request: Request):
    package = request.query_params.get("package", "basic")

    with open("signin.html", "r") as f:
        html = f.read()
        html = html.replace("{{PACKAGE}}", package)
        return html


@app.get("/payment", response_class=HTMLResponse)
async def payment_page(request: Request):
    package = request.query_params.get("package", "basic")
    user_id = request.query_params.get("user_id", "")

    if package not in PACKAGES:
        package = "basic"

    with open("payment.html", "r") as f:
        html = f.read()
        html = html.replace("{{PACKAGE}}", package)
        html = html.replace("{{USER_ID}}", user_id)
        html = html.replace("{{PRICE}}", str(PACKAGES[package]["price"]))
        return html


@app.get("/confirmation", response_class=HTMLResponse)
async def confirmation_page():
    with open("confirmation.html", "r") as f:
        return f.read()


@app.post("/api/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    package: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.hash_password(password)

    new_user = models.User(
        email=email,
        password=hashed_password,
        full_name=full_name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Redirect to signin page with selected package
    return RedirectResponse(
        url=f"/signin?package={package}",
        status_code=303
    )


@app.post("/api/signin")
async def signin(
    email: str = Form(...),
    password: str = Form(...),
    package: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Redirect to dashboard using user's ID
    return RedirectResponse(
        url=f"/dashboard?user_id={user.id}",
        status_code=303
    )


@app.post("/api/payment")
async def process_payment(
    user_id: int = Form(...),
    package: str = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db)
):
    package_info = PACKAGES.get(package)
    if not package_info:
        raise HTTPException(status_code=400, detail="Invalid package")

    try:
        charge = stripe.Charge.create(
            amount=int(package_info["price"] * 100),
            currency="usd",
            source=token,
            description=f"{package_info['name']} Package Subscription"
        )

        subscription = models.Subscription(
            user_id=user_id,
            package_name=package,
            price=package_info["price"],
            stripe_payment_id=charge.id,
            status="completed"
        )

        db.add(subscription)
        db.commit()

        return RedirectResponse(url="/confirmation", status_code=303)

    except stripe.error.CardError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    subscription = db.query(models.Subscription).filter(models.Subscription.user_id == user.id).order_by(models.Subscription.created_at.desc()).first()
    
    with open("dashboard.html", "r") as f:
        html = f.read()
        html = html.replace("{{FULL_NAME}}", user.full_name)
        if subscription:
            html = html.replace("{{PACKAGE}}", subscription.package_name.capitalize())
            html = html.replace("{{PRICE}}", str(subscription.price))
            html = html.replace("{{STATUS}}", subscription.status.capitalize())
        else:
            html = html.replace("{{PACKAGE}}", "None")
            html = html.replace("{{PRICE}}", "0")
            html = html.replace("{{STATUS}}", "None")
        return html



@app.get("/api/packages")
async def get_packages():
    return PACKAGES
