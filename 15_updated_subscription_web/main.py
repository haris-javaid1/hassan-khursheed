from fastapi import FastAPI, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models
import auth
import stripe
from typing import Optional

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Subscription Platform",
    description="A modern subscription management platform"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Stripe configuration (use environment variable in production)
stripe.api_key = "sk_test_51Suv7kGeI2OTInqlXrgjjtz67Bx8KTunfDFFsu3JFzZonJcL56ft3BUs2DIqHGryqrhE7NfSQqyys6BXW5bN68c200IUOUtLBc"

# Package configurations
PACKAGES = {
    "basic": {
        "name": "Basic",
        "price": 9.99,
        "features": [
            "Feature 1",
            "Feature 2",
            "Email Support"
        ]
    },
    "standard": {
        "name": "Standard",
        "price": 19.99,
        "features": [
            "All Basic Features",
            "Feature 3",
            "Feature 4",
            "Priority Support"
        ]
    },
    "premium": {
        "name": "Premium",
        "price": 29.99,
        "features": [
            "All Standard Features",
            "Feature 5",
            "Feature 6",
            "24/7 Support"
        ]
    }
}


def read_html_file(filename: str, replacements: dict = None) -> str:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
            
            if replacements:
                for key, value in replacements.items():
                    html = html.replace(f"{{{{{key}}}}}", str(value))
            
            return html
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Template {filename} not found")


# ---------- ROUTE HANDLERS ----------

@app.get("/", response_class=HTMLResponse)
async def home():
    """Display the package selection page."""
    return read_html_file("index.html")


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Display the signup page with selected package."""
    package = request.query_params.get("package", "basic")
    
    # Validate package
    if package not in PACKAGES:
        package = "basic"
    
    return read_html_file("signup.html", {"PACKAGE": package})


@app.get("/signin", response_class=HTMLResponse)
async def signin_page(request: Request):
    """Display the signin page."""
    package = request.query_params.get("package", "basic")
    
    # Validate package
    if package not in PACKAGES:
        package = "basic"
    
    return read_html_file("signin.html", {"PACKAGE": package})


@app.get("/payment", response_class=HTMLResponse)
async def payment_page(request: Request):
    """Display the payment page."""
    package = request.query_params.get("package", "basic")
    user_id = request.query_params.get("user_id", "")
    
    # Validate package
    if package not in PACKAGES:
        package = "basic"
    
    package_info = PACKAGES[package]
    
    replacements = {
        "PACKAGE": package,
        "USER_ID": user_id,
        "PRICE": str(package_info["price"])
    }
    
    return read_html_file("payment.html", replacements)


@app.get("/confirmation", response_class=HTMLResponse)
async def confirmation_page():
    """Display the payment confirmation page."""
    return read_html_file("confirmation.html")



# ---------- API ENDPOINTS ----------

@app.post("/api/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    package: str = Form(...),
    db: Session = Depends(get_db)
):
    
    # Validate package
    if package not in PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package selected")
    
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate password length
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Hash password
    hashed_password = auth.hash_password(password)
    
    # Create new user
    new_user = models.User(
        email=email,
        password=hashed_password,
        full_name=full_name
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create account")
    
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
    # Find user by email
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # Verify user exists and password is correct
    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Check if user already has an active subscription
    subscription = (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == user.id)
        .order_by(models.Subscription.created_at.desc())
        .first()
    )
    
    # If user has a subscription, redirect to dashboard
    if subscription:
        return RedirectResponse(
            url=f"/dashboard?user_id={user.id}",
            status_code=303
        )
    
    # Otherwise, redirect to payment page
    return RedirectResponse(
        url=f"/payment?package={package}&user_id={user.id}",
        status_code=303
    )


@app.post("/api/payment")
async def process_payment(
    user_id: int = Form(...),
    package: str = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate package
    package_info = PACKAGES.get(package)
    if not package_info:
        raise HTTPException(status_code=400, detail="Invalid package selected")
    
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Process payment with Stripe
    try:
        charge = stripe.Charge.create(
            amount=int(package_info["price"] * 100),  # Convert to cents
            currency="usd",
            source=token,
            description=f"{package_info['name']} Package Subscription for {user.email}"
        )
        
        # Create subscription record
        subscription = models.Subscription(
            user_id=user_id,
            package_name=package,
            price=package_info["price"],
            stripe_payment_id=charge.id,
            status="completed"
        )
        
        db.add(subscription)
        db.commit()
        
        # Redirect to confirmation page
        return RedirectResponse(url="/confirmation", status_code=303)
        
    except stripe.error.CardError as e:
        # Card was declined
        raise HTTPException(status_code=400, detail=f"Card declined: {str(e)}")
    except stripe.error.RateLimitError as e:
        # Too many requests to Stripe API
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe failed
        raise HTTPException(status_code=500, detail="Payment service authentication failed")
    except stripe.error.APIConnectionError as e:
        # Network communication failed
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    except stripe.error.StripeError as e:
        # Generic Stripe error
        raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")
    except Exception as e:
        # Rollback database changes
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@app.get("/api/packages")
async def get_packages():
    """
    Get all available packages.
    
    Returns:
        Dictionary of available packages
    """
    return PACKAGES


@app.get("/api/user/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user information.
    
    Args:
        user_id: ID of the user
        db: Database session
    
    Returns:
        User information (without password)
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": user.created_at,
        "is_active": user.is_active
    }


@app.get("/api/subscription/{user_id}")
async def get_subscription(user_id: int, db: Session = Depends(get_db)):
    subscription = (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == user_id)
        .order_by(models.Subscription.created_at.desc())
        .first()
    )
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    return {
        "id": subscription.id,
        "package_name": subscription.package_name,
        "price": subscription.price,
        "status": subscription.status,
        "created_at": subscription.created_at
    }


# ---------- ERROR HANDLERS ----------

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors."""
    return HTMLResponse(
        content="<h1>404 - Page Not Found</h1><p>The page you're looking for doesn't exist.</p>",
        status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors."""
    return HTMLResponse(
        content="<h1>500 - Internal Server Error</h1><p>Something went wrong. Please try again later.</p>",
        status_code=500
    )


