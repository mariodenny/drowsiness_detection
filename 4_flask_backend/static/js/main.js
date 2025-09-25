document.addEventListener('DOMContentLoaded', function() {
    const statusBox = document.getElementById('status-box');
    const lastStatusElem = document.getElementById('last-status');
    const lastConfidenceElem = document.getElementById('last-confidence');
    const lastTimeElem = document.getElementById('last-time');
    const tableBody = document.querySelector('#alerts-table tbody');

    function fetchAlerts() {
        fetch('/api/alerts')
            .then(response => response.json())
            .then(data => {
                updateTable(data.alerts);
                updateStatusBox(data.alerts);
            })
            .catch(error => console.error('Error fetching alerts:', error));
    }

    function updateStatusBox(alerts) {
        if (alerts.length === 0) return;

        const latestAlert = alerts[0];
        lastStatusElem.textContent = latestAlert.status;
        lastConfidenceElem.textContent = `Confidence: ${(latestAlert.confidence * 100).toFixed(1)}%`;
        lastTimeElem.textContent = `Time: ${latestAlert.received_at}`;

        statusBox.className = 'status-box'; // Reset class
        if (latestAlert.status === 'DROWSY') {
            statusBox.classList.add('drowsy');
        } else if (latestAlert.status === 'YAWNING') {
            statusBox.classList.add('yawning');
        } else if (latestAlert.status === 'AWAKE') {
            statusBox.classList.add('awake');
        }
    }

    function updateTable(alerts) {
        tableBody.innerHTML = ''; // Clear existing rows
        alerts.forEach(alert => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${alert.id}</td>
                <td class="status-cell-${alert.status}">${alert.status}</td>
                <td>${(alert.confidence * 100).toFixed(1)}%</td>
                <td>${alert.device_id}</td>
                <td>${alert.received_at}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    // Fetch data every 2 seconds
    setInterval(fetchAlerts, 2000);
    // Initial fetch
    fetchAlerts();
});