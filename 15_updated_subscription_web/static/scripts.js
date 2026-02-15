// ---------- UTILITY FUNCTIONS ----------
function showError(message) {
    const errorMsg = document.getElementById('errorMsg');
    if (errorMsg) {
        errorMsg.textContent = message;
        errorMsg.classList.add('show');
        setTimeout(() => {
            errorMsg.classList.remove('show');
        }, 5000);
    }
}

function showSuccess(message) {
    const successMsg = document.getElementById('successMsg');
    if (successMsg) {
        successMsg.textContent = message;
        successMsg.classList.add('show');
        setTimeout(() => {
            successMsg.classList.remove('show');
        }, 5000);
    }
}

// ---------- PACKAGE SELECTION ----------
function selectPackage(packageName) {
    // Add loading animation
    const event = window.event;
    if (event && event.target) {
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<span>Loading...</span>';
        button.disabled = true;

        setTimeout(() => {
            window.location.href = `/signup?package=${packageName}`;
        }, 300);
    } else {
        window.location.href = `/signup?package=${packageName}`;
    }
}

// ---------- FORM HANDLING ----------
document.addEventListener('DOMContentLoaded', () => {

    // Signup Form Handler
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            const submitBtn = signupForm.querySelector('button[type="submit"]');

            // Validate form
            const password = signupForm.querySelector('input[name="password"]').value;
            if (password.length < 6) {
                e.preventDefault();
                showError('Password must be at least 6 characters long');
                return false;
            }

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>Creating Account...</span>';

            // Let the form submit naturally
            return true;
        });
    }

    // Signin Form Handler
    const signinForm = document.getElementById('signinForm');
    if (signinForm) {
        signinForm.addEventListener('submit', (e) => {
            const submitBtn = signinForm.querySelector('button[type="submit"]');

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>Signing In...</span>';

            // Let the form submit naturally
            return true;
        });
    }

    // Payment Form Handler
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', (e) => {
            const payBtn = document.getElementById('payBtn');

            // Validate token
            const token = paymentForm.querySelector('input[name="token"]').value.trim();
            if (!token) {
                e.preventDefault();
                showError('Please enter a payment token');
                return false;
            }

            // Show loading state
            payBtn.disabled = true;
            payBtn.innerHTML = `
                <svg class="btn-icon-left animate-spin" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"/>
                </svg>
                <span>Processing Payment...</span>
            `;

            // Let the form submit naturally
            return true;
        });
    }

    // Confirmation Page - Set current date
    const dateElement = document.getElementById('date');
    if (dateElement) {
        const today = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        dateElement.textContent = today.toLocaleDateString('en-US', options);
    }

    // Input Focus Effects
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('focus', (e) => {
            e.target.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', (e) => {
            e.target.parentElement.classList.remove('focused');
        });
    });

    // Package name capitalization
    const packageNameElements = document.querySelectorAll('#packageName');
    packageNameElements.forEach(element => {
        if (element.textContent) {
            element.textContent = element.textContent.charAt(0).toUpperCase() +
                element.textContent.slice(1);
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    const cards = document.querySelectorAll('.package-card, .dashboard-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(card);
    });
});

// ---------- FORM VALIDATION ----------
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

function validatePassword(password) {
    return password.length >= 6;
}

// ---------- PRICE FORMATTING ----------
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

// ---------- DATE FORMATTING ----------
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

// ---------- KEYBOARD ACCESSIBILITY ----------
document.addEventListener('keydown', (e) => {
    // Close alerts with Escape key
    if (e.key === 'Escape') {
        const alerts = document.querySelectorAll('.alert.show');
        alerts.forEach(alert => alert.classList.remove('show'));
    }
});

// ---------- PREVENT DOUBLE SUBMISSION ----------
let isSubmitting = false;

document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (e) => {
        if (isSubmitting) {
            e.preventDefault();
            return false;
        }
        isSubmitting = true;

        // Reset after 5 seconds as a safety measure
        setTimeout(() => {
            isSubmitting = false;
        }, 5000);
    });
});

// ---------- RESPONSIVE MENU TOGGLE (if needed) ----------
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    if (menu) {
        menu.classList.toggle('show');
    }
}

// ---------- CONSOLE MESSAGE ----------
console.log('%c🚀 Subscription Platform Loaded', 'color: #6366f1; font-size: 16px; font-weight: bold;');
console.log('%c✨ Modern UI Design Active', 'color: #10b981; font-size: 12px;');
