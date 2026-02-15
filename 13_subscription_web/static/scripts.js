// Package selection
function selectPackage(packageName) {
    window.location.href = `/signup?package=${packageName}`;
}

// Payment button loading state
document.addEventListener("DOMContentLoaded", () => {
    const paymentForm = document.getElementById("paymentForm");

    if (paymentForm) {
        paymentForm.addEventListener("submit", () => {
            const payBtn = document.getElementById("payBtn");
            if (payBtn) {
                payBtn.disabled = true;
                payBtn.textContent = "Processing...";
            }
        });
    }

    // Confirmation date
    const dateElement = document.getElementById("date");
    if (dateElement) {
        const today = new Date();
        const options = { year: "numeric", month: "long", day: "numeric" };
        dateElement.textContent = today.toLocaleDateString("en-US", options);
    }
});
