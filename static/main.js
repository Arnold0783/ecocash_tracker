// --------------------
// 1. PIE CHART (Income vs Expense)
// --------------------
const el = document.getElementById('chart-data');
const income = parseFloat(el?.dataset.income) || 0;
const expense = parseFloat(el?.dataset.expense) || 0;

const ctx = document.getElementById('incomeExpenseChart')?.getContext('2d');

if (ctx) {
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Income', 'Expense'],
            datasets: [{
                data: [income, expense],
                backgroundColor: ['#16a34a', '#dc2626']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

// --------------------
// 2. MONTHLY TREND CHART
// --------------------
const monthlyEl = document.getElementById('monthly-data');
if (monthlyEl) {
    const labels = JSON.parse(monthlyEl.dataset.labels.replace(/'/g, '"'));
    const values = JSON.parse(monthlyEl.dataset.values.replace(/'/g, '"'));

    const ctx2 = document.getElementById('monthlyChart')?.getContext('2d');

    if (ctx2) {
        new Chart(ctx2, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Spending Trend (ZWL)',
                    data: values,
                    borderWidth: 2,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59,130,246,0.2)',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: true, position: 'bottom' } }
            }
        });
    }
}

// --------------------
// 3. AI INSIGHTS FETCH
// --------------------
fetch('/insights')
    .then(res => res.json())
    .then(data => {
        const insightEl = document.getElementById('insight-text');
        if (insightEl) insightEl.innerText = data.insight || "No insights available.";
    });

// --------------------
// 4. BUDGET SYSTEM (Dynamic)
// --------------------
const budgets = { food: 5000, airtime: 2000, bills: 3000 };
const categoryDataEl = document.getElementById("category-data");
let categoryTotals = {};

if (categoryDataEl) {
    try { categoryTotals = JSON.parse(categoryDataEl.textContent); } 
    catch(e) { categoryTotals = {}; }
}

const updateBudget = (category, spent, limit) => {
    const percent = Math.min((spent / limit) * 100, 100);
    const bar = document.getElementById(`${category}-progress`);
    const text = document.getElementById(`${category}-progress-text`);
    if (bar && text) {
        bar.style.width = percent + '%';
        text.innerText = `ZWL ${spent.toFixed(2)} / ${limit}`;
    }
};

updateBudget('food', categoryTotals.food || 0, budgets.food);
updateBudget('airtime', categoryTotals.airtime || 0, budgets.airtime);
updateBudget('bills', categoryTotals.bills || 0, budgets.bills);

// --------------------
// 5. SMART ALERTS
// --------------------
const alertBox = document.getElementById("smart-alert");

if (alertBox) {
    let message = "";
    if (expense > income) message = "⚠️ Expenses exceed income!";
    else if ((categoryTotals.airtime || 0) > budgets.airtime) message = "📱 Airtime budget exceeded!";
    else if ((categoryTotals.food || 0) > budgets.food) message = "🍔 Food budget exceeded!";

    if (message) {
        alertBox.innerText = message;
        alertBox.classList.remove("hidden");
        alertBox.classList.add("animate-pulse"); // Tailwind animation
    }
}

// --------------------
// 6. SMART CATEGORY SUGGESTION
// --------------------
const categoryInput = document.getElementById('category-input');
const descriptionInput = document.getElementById('desc-input');

if (categoryInput && descriptionInput) {
    descriptionInput.addEventListener('input', () => {
        const desc = descriptionInput.value.trim();
        if (desc.length < 3) return;

        fetch('/suggest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: desc })
        })
        .then(res => res.json())
        .then(data => {
            if (data?.suggested_category) {
                categoryInput.value = data.suggested_category;
            }
        })
        .catch(err => console.error("Category suggestion error:", err));
    });
}

// --------------------
// 7. LIVE USD RATE (optional)
// --------------------
const rateEl = document.getElementById("rate-text");
if (rateEl) {
    fetch('/rate')
        .then(res => res.json())
        .then(data => { rateEl.innerText = `1 USD ≈ ${data.rate} ZWL`; })
        .catch(err => { rateEl.innerText = "⚠️ Rate unavailable"; });
}