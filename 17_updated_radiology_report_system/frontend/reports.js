const API_URL = 'http://localhost:8000/api';

window.addEventListener('DOMContentLoaded', () => {
    loadReports();
});

async function loadReports() {
    try {
        const response = await fetch(`${API_URL}/reports`);
        const data = await response.json();

        document.getElementById('loading').style.display = 'none';

        if (!data || data.length === 0) {
            document.getElementById('noReports').style.display = 'block';
        } else {
            document.getElementById('reportsContainer').style.display = 'block';
            displayReports(data);
        }
    } catch (err) {
        console.error('Error loading reports:', err);
        document.getElementById('loading').innerText =
            'Error loading reports. Make sure backend is running.';
    }
}

function displayReports(reports) {
    const tableBody = document.getElementById('reportsTable');
    tableBody.innerHTML = '';

    reports.forEach(report => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${report.serial_number}</td>
            <td>${report.patient_name}</td>
            <td>${report.age_sex || '-'}</td>
            <td>${report.scan_type || '-'}</td>
            <td>
                <button class="btn-export" onclick="viewQR('${report.serial_number}')">QR Code</button>
                <button class="btn-export" onclick="uploadFile('${report.serial_number}')">Upload</button>
                <button class="btn-export" onclick="updateReport('${report.serial_number}')">Update</button>
                <button class="btn-export" onclick="deleteReport('${report.serial_number}')">Delete</button>
                <button class="btn-export" onclick="exportReport(${report.id})">Export</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function viewQR(serial) {
    const qrImageUrl = `${API_URL}/reports/serial/${serial}/qr`;
    const reportUrl = `http://192.168.100.9:8000/api/view/${serial}`;

    const baseUrl = window.location.href.substring(0, window.location.href.lastIndexOf('/'));
    const popupUrl = `${baseUrl}/qr_popup.html?serial=${encodeURIComponent(serial)}&qrUrl=${encodeURIComponent(qrImageUrl)}&reportUrl=${encodeURIComponent(reportUrl)}`;

    const popup = window.open(popupUrl, 'QR Code', 'width=550,height=700,scrollbars=no,resizable=yes');

    if (!popup) {
        showNotification('Please allow popups for this site to view QR code', 'error');
    }
}

function uploadFile(serial) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.docx';

    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        showNotification('Uploading file...', 'info');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/reports/serial/${serial}/upload`, {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.success) {
                showNotification(result.message || 'File uploaded successfully!', 'success');
                setTimeout(() => loadReports(), 1500);
            } else {
                showNotification('Upload failed', 'error');
            }
        } catch (err) {
            console.error('Upload error:', err);
            showNotification('Error uploading file', 'error');
        }
    };

    input.click();
}

function updateReport(serial) {
    window.location.href = `index.html?serial=${serial}`;
}

async function deleteReport(serial) {
    // Show confirmation message without blocking
    showConfirmation('Delete this report?', () => {
        performDelete(serial);
    });
}

async function performDelete(serial) {
    try {
        const response = await fetch(`${API_URL}/reports/serial/${serial}`, { method: 'DELETE' });
        const result = await response.json();

        if (result.success) {
            showNotification('Report deleted successfully!', 'success');
            setTimeout(() => loadReports(), 1500);
        } else {
            showNotification('Error deleting report', 'error');
        }
    } catch (err) {
        console.error('Delete error:', err);
        showNotification('Error deleting report', 'error');
    }
}

function exportReport(id) {
    window.open(`${API_URL}/reports/${id}/export`, '_blank');
    showNotification('Downloading report...', 'info');
}

// Notification system (instead of alert)
function showNotification(message, type) {
    // Remove existing notification if any
    const existingNotif = document.querySelector('.notification');
    if (existingNotif) {
        existingNotif.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.classList.add('notification-fade');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Confirmation system (instead of confirm)
function showConfirmation(message, onConfirm) {
    // Remove existing confirmation if any
    const existingConfirm = document.querySelector('.confirm-overlay');
    if (existingConfirm) {
        existingConfirm.remove();
    }

    const overlay = document.createElement('div');
    overlay.className = 'confirm-overlay';

    const box = document.createElement('div');
    box.className = 'confirm-box';

    const messageEl = document.createElement('p');
    messageEl.textContent = message;

    const btnContainer = document.createElement('div');
    btnContainer.className = 'confirm-buttons';

    const yesBtn = document.createElement('button');
    yesBtn.textContent = 'Yes';
    yesBtn.className = 'btn-confirm-yes';
    yesBtn.onclick = () => {
        overlay.remove();
        onConfirm();
    };

    const noBtn = document.createElement('button');
    noBtn.textContent = 'No';
    noBtn.className = 'btn-confirm-no';
    noBtn.onclick = () => overlay.remove();

    btnContainer.appendChild(yesBtn);
    btnContainer.appendChild(noBtn);

    box.appendChild(messageEl);
    box.appendChild(btnContainer);
    overlay.appendChild(box);

    document.body.appendChild(overlay);
}