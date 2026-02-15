// API URL
const API_URL = 'http://localhost:8000/api';

// Get form element
const form = document.getElementById('reportForm');
const messageDiv = document.getElementById('message');

// Handle form submission
if (form) {
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        // Get form data
        const formData = new FormData(form);
        const data = {};

        // Convert to object
        formData.forEach((value, key) => {
            if (value) {
                data[key] = value;
            }
        });

        // Check if patient name is filled
        if (!data.patient_name) {
            showMessage('Patient name is required!', 'error');
            return;
        }

        // Send to backend
        fetch(`${API_URL}/reports`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showMessage('Report saved successfully!', 'success');

                    // Ask user
                    setTimeout(() => {
                        if (confirm('Report saved! Go to view reports?')) {
                            window.location.href = 'reports.html';
                        } else {
                            form.reset();
                        }
                    }, 1000);
                } else {
                    showMessage('Error saving report', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Network error. Check if backend is running.', 'error');
            });
    });
}

// Function to show message
function showMessage(message, type) {
    messageDiv.textContent = message;
    messageDiv.className = type;
    messageDiv.style.display = 'block';

    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

// Function to reset form
function resetForm() {
    form.reset();
    messageDiv.style.display = 'none';
}