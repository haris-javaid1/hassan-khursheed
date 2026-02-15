const API_URL = 'http://localhost:8000/api';

const form = document.getElementById('reportForm');
const messageDiv = document.getElementById('message');

const urlParams = new URLSearchParams(window.location.search);
const editSerial = urlParams.get('serial');
let isEditMode = false;

if (editSerial && form) {
    isEditMode = true;
    loadReportForEdit(editSerial);
}

function loadReportForEdit(serial) {
    fetch(`${API_URL}/reports/serial/${serial}`)
        .then(response => response.json())
        .then(data => {
            fillFormField('uhid', data.uhid);
            fillFormField('sl_no', data.sl_no);
            fillFormField('reg_no', data.reg_no);
            fillFormField('patient_no', data.patient_no);
            fillFormField('patient_name', data.patient_name);
            fillFormField('report_date', data.report_date);
            fillFormField('age_sex', data.age_sex);
            fillFormField('origin_ethe', data.origin_ethe);
            fillFormField('ref_by', data.ref_by);
            fillFormField('film_no', data.film_no);
            fillFormField('scan_time', data.scan_time);
            fillFormField('report_time', data.report_time);
            fillFormField('tat', data.tat);
            fillFormField('scan_type', data.scan_type);
            fillFormField('doctor_description', data.doctor_description);
            fillFormField('impression', data.impression);

            document.querySelector('h2').textContent = 'Update Report';
            document.querySelector('button[type="submit"]').textContent = 'Update Report';
        })
        .catch(error => {
            console.error('Error loading report:', error);
            showMessage('Error loading report for editing', 'error');
        });
}

function fillFormField(name, value) {
    const element = document.querySelector(`[name="${name}"]`);
    if (element) {
        element.value = value || '';
    }
}

if (form) {
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            if (value) {
                data[key] = value;
            }
        });

        if (!data.patient_name) {
            showMessage('Patient name is required!', 'error');
            return;
        }

        const url = isEditMode
            ? `${API_URL}/reports/serial/${editSerial}`
            : `${API_URL}/reports`;

        const method = isEditMode ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    const message = isEditMode
                        ? 'Report updated successfully!'
                        : `Report created! Serial Number: ${result.serial_number}`;

                    showMessage(message, 'success');

                    // Auto redirect to reports page after 2 seconds
                    setTimeout(() => {
                        window.location.href = 'reports.html';
                    }, 2000);
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

function showMessage(message, type) {
    messageDiv.textContent = message;
    messageDiv.className = type;
    messageDiv.style.display = 'block';

    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

function resetForm() {
    form.reset();
    messageDiv.style.display = 'none';
}