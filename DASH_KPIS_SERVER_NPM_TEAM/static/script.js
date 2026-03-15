/**
 * KPI Dashboard - Frontend JavaScript
 * Handles date filtering, API calls, and chart rendering
 */

// Global state
let config = null;
let charts = {};
let currentView = 'hourly'; // 'hourly' or 'daily'
const MAX_DAYS = 7; // Also enforced on backend

// =============================================================================
// INITIALIZATION
// =============================================================================

const APP_PASSWORD = '123123';

document.addEventListener('DOMContentLoaded', async () => {
    // Check if already logged in
    if (sessionStorage.getItem('kpi_auth') === 'true') {
        hideLogin();
        initDashboard();
    } else {
        setupLogin();
    }
});

function setupLogin() {
    const loginBtn = document.getElementById('login-btn');
    const passwordInput = document.getElementById('login-password');
    const loginError = document.getElementById('login-error');

    loginBtn.addEventListener('click', checkPassword);
    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') checkPassword();
    });

    function checkPassword() {
        const pwd = passwordInput.value;
        if (pwd === APP_PASSWORD) {
            sessionStorage.setItem('kpi_auth', 'true');
            hideLogin();
            initDashboard();
        } else {
            loginError.textContent = 'Wrong password';
            passwordInput.value = '';
            passwordInput.focus();
        }
    }
}

function hideLogin() {
    document.getElementById('login-overlay').classList.add('hidden');
}

async function initDashboard() {
    try {
        // Load config from backend
        config = await fetchConfig();

        // Setup date inputs
        setupDateInputs();

        // Setup event listeners
        setupEventListeners();

        // Load default data
        await loadDefaultData();
    } catch (error) {
        showError('Failed to initialize dashboard: ' + error.message);
    }
}

// =============================================================================
// API CALLS
// =============================================================================

async function fetchConfig() {
    const response = await fetch('/api/config');
    if (!response.ok) throw new Error('Failed to load config');
    return response.json();
}

async function fetchDefaultDates() {
    const response = await fetch('/api/default-dates');
    if (!response.ok) throw new Error('Failed to load default dates');
    return response.json();
}

async function fetchKPIData(startDate, endDate, view = 'hourly') {
    const url = `/api/kpi-data?start_date=${startDate}&end_date=${endDate}&view=${view}`;
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch data');
    }

    return data;
}

// =============================================================================
// DATE HANDLING
// =============================================================================

function setupDateInputs() {
    const today = new Date();
    const maxDate = today.toISOString().split('T')[0];

    document.getElementById('start-date').max = maxDate;
    document.getElementById('end-date').max = maxDate;
}

function validateDateRange(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);

    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
        return { valid: false, error: 'Invalid date format' };
    }

    if (start > end) {
        return { valid: false, error: 'Start date must be before end date' };
    }

    // Calculate days difference
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

    // CRITICAL: Enforce 7 day maximum on frontend
    if (diffDays > MAX_DAYS) {
        return {
            valid: false,
            error: `Maximum ${MAX_DAYS} days allowed. You selected ${diffDays} days.`
        };
    }

    return { valid: true, days: diffDays };
}

function getDateRangeFromDays(days) {
    const today = new Date();
    const start = new Date(today);
    start.setDate(today.getDate() - (days - 1));

    return {
        startDate: start.toISOString().split('T')[0],
        endDate: today.toISOString().split('T')[0]
    };
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

function setupEventListeners() {
    // View toggle buttons (Hourly / Daily)
    document.querySelectorAll('.btn-toggle').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const view = e.target.dataset.view;
            currentView = view;

            // Update toggle button states
            document.querySelectorAll('.btn-toggle').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');

            // Reload data with current date range
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;

            if (startDate && endDate) {
                await loadData(startDate, endDate);
            }
        });
    });

    // Quick select buttons
    document.querySelectorAll('.btn-quick').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const days = parseInt(e.target.dataset.days);

            // Validate days limit (should always be valid for these buttons, but double-check)
            if (days > MAX_DAYS) {
                showError(`Maximum ${MAX_DAYS} days allowed`);
                return;
            }

            const { startDate, endDate } = getDateRangeFromDays(days);

            // Update date inputs
            document.getElementById('start-date').value = startDate;
            document.getElementById('end-date').value = endDate;

            // Highlight active button
            document.querySelectorAll('.btn-quick').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');

            // Load data
            await loadData(startDate, endDate);
        });
    });

    // Apply filter button
    document.getElementById('apply-filter').addEventListener('click', async () => {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        if (!startDate || !endDate) {
            showError('Please select both start and end dates');
            return;
        }

        // Validate date range
        const validation = validateDateRange(startDate, endDate);
        if (!validation.valid) {
            showError(validation.error);
            return;
        }

        // Clear quick button highlights
        document.querySelectorAll('.btn-quick').forEach(b => b.classList.remove('active'));

        // Load data
        await loadData(startDate, endDate);
    });

    // Date input change - validate in real-time
    ['start-date', 'end-date'].forEach(id => {
        document.getElementById(id).addEventListener('change', () => {
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;

            if (startDate && endDate) {
                const validation = validateDateRange(startDate, endDate);
                if (!validation.valid) {
                    showError(validation.error);
                } else {
                    clearError();
                }
            }
        });
    });
}

// =============================================================================
// DATA LOADING
// =============================================================================

async function loadDefaultData() {
    try {
        const defaults = await fetchDefaultDates();

        document.getElementById('start-date').value = defaults.start_date;
        document.getElementById('end-date').value = defaults.end_date;

        // Highlight the default days button
        const defaultBtn = document.querySelector(`.btn-quick[data-days="${defaults.default_days}"]`);
        if (defaultBtn) defaultBtn.classList.add('active');

        await loadData(defaults.start_date, defaults.end_date);
    } catch (error) {
        showError('Failed to load default data: ' + error.message);
    }
}

async function loadData(startDate, endDate) {
    showLoading(true);
    clearError();

    try {
        const result = await fetchKPIData(startDate, endDate, currentView);

        if (result.success && result.data) {
            updateCurrentRange(startDate, endDate, result.total_records);
            renderCharts(result.data);
        } else {
            showError('No data returned from server');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// =============================================================================
// CHART RENDERING
// =============================================================================

function renderCharts(data) {
    const container = document.getElementById('charts-container');
    container.innerHTML = '';

    // Destroy existing charts
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};

    if (!data || data.length === 0) {
        container.innerHTML = '<p class="no-data">No data available for the selected date range</p>';
        return;
    }

    // Create labels with separate date and time info for better x-axis display
    const isDaily = currentView === 'daily';
    const labelData = data.map(row => ({
        date: row.date,
        time: row.time || '',
        full: isDaily ? row.date : (row.time ? `${row.date} ${row.time}` : row.date)
    }));

    // Create charts for each KPI group
    Object.entries(config.kpi_groups).forEach(([chartTitle, chartConfig], index) => {
        // Handle both old format (array) and new format (object with columns/threshold)
        const kpiColumns = Array.isArray(chartConfig) ? chartConfig : chartConfig.columns;
        const threshold = Array.isArray(chartConfig) ? null : chartConfig.threshold;

        // Check if any of the KPI columns exist in the data
        const availableColumns = kpiColumns.filter(col => data[0].hasOwnProperty(col));

        if (availableColumns.length === 0) {
            console.warn(`No data for chart: ${chartTitle}`);
            return;
        }

        // Create chart container
        const chartDiv = document.createElement('div');
        chartDiv.className = 'chart-card';
        const thresholdInfo = threshold !== null ? `<span class="threshold-info">Threshold: ${threshold}</span>` : '';
        chartDiv.innerHTML = `
            <h3 class="chart-title">${chartTitle} ${thresholdInfo}</h3>
            <div class="chart-wrapper">
                <canvas id="chart-${index}"></canvas>
            </div>
        `;
        container.appendChild(chartDiv);

        // Prepare datasets
        const datasets = availableColumns.map((col, colIndex) => ({
            label: col.replace(/_/g, ' '),
            data: data.map(row => row[col] !== null ? row[col] : null),
            borderColor: config.colors[colIndex % config.colors.length],
            backgroundColor: config.colors[colIndex % config.colors.length] + '20',
            borderWidth: 2,
            fill: false,
            tension: 0.1,
            pointRadius: 2,
            pointHoverRadius: 5
        }));

        // Add threshold line if defined
        if (threshold !== null) {
            datasets.push({
                label: `Threshold (${threshold})`,
                data: data.map(() => threshold),
                borderColor: '#FFB347',
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [10, 5],
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            });
        }

        // Create chart
        const ctx = document.getElementById(`chart-${index}`).getContext('2d');
        charts[`chart-${index}`] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labelData.map(l => l.full),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                // Show full date and time in tooltip
                                return tooltipItems[0].label;
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(2);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: isDaily ? 'Date' : 'Date / Time'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45,
                            autoSkip: true,
                            maxTicksLimit: isDaily ? 10 : 24,
                            callback: function(value, idx) {
                                const current = labelData[idx];
                                if (!current) return '';

                                // For daily view, just show the date
                                if (isDaily) {
                                    return current.date;
                                }

                                // For hourly view, show date only when it changes
                                const prev = idx > 0 ? labelData[idx - 1] : null;

                                if (!prev || prev.date !== current.date) {
                                    // New date - show date and time
                                    return [current.date, current.time];
                                } else {
                                    // Same date - show only time
                                    return current.time;
                                }
                            }
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: chartTitle
                        },
                        beginAtZero: false
                    }
                }
            }
        });
    });
}

// =============================================================================
// UI HELPERS
// =============================================================================

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
    document.getElementById('charts-container').style.display = show ? 'none' : 'grid';
}

function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = message;
    errorEl.style.display = 'inline';
}

function clearError() {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = '';
    errorEl.style.display = 'none';
}

function updateCurrentRange(startDate, endDate, totalRecords) {
    const rangeEl = document.getElementById('current-range');
    rangeEl.textContent = `Showing: ${startDate} to ${endDate} (${totalRecords} records)`;
}
