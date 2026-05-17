const API_BASE_URL = 'http://localhost:8000/api';

// Global State
let currentUserId = null;
let deleteConfirmations = {};
let budgetChartInstance = null;
let allocationChartInstance = null;

// DOM Elements
const authSection = document.getElementById('authSection');
const mainContent = document.getElementById('mainContent');
const userStatus = document.getElementById('userStatus');
const authMessage = document.getElementById('authMessage');
const logoutBtn = document.getElementById('logoutBtn');

// Event Listeners
document.getElementById('authForm').addEventListener('submit', handleRegister);
document.getElementById('loginBtn').addEventListener('click', handleLogin);
logoutBtn.addEventListener('click', handleLogout);
document.getElementById('profileForm').addEventListener('submit', handleSaveProfile);
document.getElementById('expenseForm').addEventListener('submit', handleAddExpense);
document.getElementById('goalForm').addEventListener('submit', handleAddGoal);
document.getElementById('getAdviceBtn').addEventListener('click', handleGetAdvice);
document.getElementById('runSimulationBtn').addEventListener('click', handleRunSimulation);

// Run advice query on Enter key press
document.getElementById('aiCustomQuery').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleGetAdvice();
    }
});

// --- Helpers ---
function escapeHtml(str) {
    if (!str) return '';
    return str.toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function escapeQuote(str) {
    if (!str) return '';
    return str.toString().replace(/'/g, "\\'");
}

function formatCurrency(val) {
    if (val === undefined || val === null || isNaN(val)) return '₹0';
    if (val % 1 === 0) {
        return '₹' + Math.round(val).toLocaleString('en-IN', {maximumFractionDigits: 0});
    } else {
        return '₹' + val.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
}

// Light Weight Markdown Parser for AI response
function renderMarkdown(text) {
    if (!text) return '';
    
    // Split into paragraphs/lines and process
    let lines = text.split('\n');
    let html = '';
    let inList = false;
    
    for (let line of lines) {
        line = line.trim();
        if (!line) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            continue;
        }
        
        // Match Header 2
        if (line.startsWith('## ')) {
            if (inList) { html += '</ul>'; inList = false; }
            html += `<h3 style="margin-top: 1.25rem; margin-bottom: 0.5rem; color: var(--accent-color); font-weight: 700;">${line.substring(3)}</h3>`;
            continue;
        }
        
        // Match Bullet Points
        if (line.startsWith('- ') || line.startsWith('* ')) {
            if (!inList) {
                html += '<ul style="padding-left: 1.25rem; margin-bottom: 0.75rem; list-style-type: square;">';
                inList = true;
            }
            let itemContent = line.substring(2);
            // Inline strong and em
            itemContent = itemContent
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>');
            html += `<li style="margin-bottom: 0.35rem;">${itemContent}</li>`;
            continue;
        }
        
        // Normal text line
        if (inList) { html += '</ul>'; inList = false; }
        let inlineProcessed = line
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
        html += `<p style="margin-bottom: 0.75rem;">${inlineProcessed}</p>`;
    }
    
    if (inList) {
        html += '</ul>';
    }
    return html;
}

// --- Chart Rendering Helpers ---
function updateBudgetChart(expenses, targetSavings, surplus) {
    const ctx = document.getElementById('budgetChart').getContext('2d');
    const wrapper = document.getElementById('budgetChartWrapper');
    
    wrapper.classList.remove('hidden');
    
    if (budgetChartInstance) {
        budgetChartInstance.destroy();
    }
    
    budgetChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Total Expenses', 'Planned Savings', 'Remaining Surplus'],
            datasets: [{
                data: [expenses, targetSavings, Math.max(0, surplus)],
                backgroundColor: [
                    'rgba(244, 63, 94, 0.75)', // Rose
                    'rgba(99, 102, 241, 0.75)', // Indigo
                    'rgba(16, 185, 129, 0.75)'  // Emerald
                ],
                borderColor: [
                    'rgba(244, 63, 94, 1)',
                    'rgba(99, 102, 241, 1)',
                    'rgba(16, 185, 129, 1)'
                ],
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        font: {
                            family: "'Outfit', 'Inter', sans-serif",
                            size: 11
                        },
                        padding: 12,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.raw || 0;
                            return ` ${context.label}: ${formatCurrency(val)}`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

function updateAllocationChart(riskPercent) {
    const ctx = document.getElementById('allocationChart').getContext('2d');
    const wrapper = document.getElementById('allocationChartWrapper');
    
    wrapper.classList.remove('hidden');
    
    let gold = 15;
    let safe = Math.max(15, Math.min(75, 100 - riskPercent));
    let mutualFunds = 100 - safe - gold;
    
    if (allocationChartInstance) {
        allocationChartInstance.destroy();
    }
    
    allocationChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [
                `Safe Deposits & PPF (${safe}%)`,
                `SGBs & Gold (${gold}%)`,
                `Mutual & Index Funds (${mutualFunds}%)`
            ],
            datasets: [{
                data: [safe, gold, mutualFunds],
                backgroundColor: [
                    'rgba(148, 163, 184, 0.75)', // Slate Grey
                    'rgba(234, 179, 8, 0.75)',   // Gold
                    'rgba(168, 85, 247, 0.75)'   // Purple
                ],
                borderColor: [
                    'rgba(148, 163, 184, 1)',
                    'rgba(234, 179, 8, 1)',
                    'rgba(168, 85, 247, 1)'
                ],
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        font: {
                            family: "'Outfit', 'Inter', sans-serif",
                            size: 10
                        },
                        padding: 10,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.label}`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// --- Check Session on Load ---
window.addEventListener('DOMContentLoaded', async () => {
    const savedUserId = localStorage.getItem('finpilot_user_id');
    const savedUserName = localStorage.getItem('finpilot_user_name');
    if (savedUserId) {
        await loginUser(parseInt(savedUserId), savedUserName);
    }
});

// --- Authentication ---

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    
    try {
        const res = await fetch(`${API_BASE_URL}/users/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });
        const data = await res.json();
        
        if (res.ok) {
            await loginUser(data.id, data.name);
        } else {
            showAuthMessage(data.detail, 'error');
        }
    } catch (err) {
        showAuthMessage('Network error.', 'error');
    }
}

async function handleLogin() {
    const email = document.getElementById('email').value;
    if (!email) {
        showAuthMessage('Please enter an email to log in.', 'error');
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE_URL}/users/`);
        const users = await res.json();
        const user = users.find(u => u.email === email);
        
        if (user) {
            await loginUser(user.id, user.name);
        } else {
            showAuthMessage('User not found. Please register.', 'error');
        }
    } catch (err) {
        showAuthMessage('Network error.', 'error');
    }
}

async function loginUser(id, name) {
    currentUserId = id;
    
    // Save to localStorage for page-reload persistence
    localStorage.setItem('finpilot_user_id', id);
    localStorage.setItem('finpilot_user_name', name || `User ${id}`);
    
    userStatus.textContent = `Logged in as: ${name || 'User ' + id}`;
    logoutBtn.classList.remove('hidden');
    authSection.classList.add('hidden');
    mainContent.classList.remove('hidden');
    
    // Reset delete confirmations on login
    deleteConfirmations = {};
    
    // Load financial data and lists on login
    await loadUserData();
}

function handleLogout() {
    // Clear localStorage session
    localStorage.removeItem('finpilot_user_id');
    localStorage.removeItem('finpilot_user_name');
    currentUserId = null;
    deleteConfirmations = {};
    
    userStatus.textContent = 'Not Logged In';
    logoutBtn.classList.add('hidden');
    authSection.classList.remove('hidden');
    mainContent.classList.add('hidden');
    
    // Reset inputs and forms
    document.getElementById('authForm').reset();
    document.getElementById('profileForm').reset();
    document.getElementById('expenseForm').reset();
    document.getElementById('goalForm').reset();
    
    document.getElementById('simulationContent').innerHTML = '<p class="placeholder-text">Click \'Run Simulation\' to see your financial trajectory.</p>';
    document.getElementById('aiAdviceContent').innerHTML = '<p class="placeholder-text">Ask your AI advisor for tailored financial advice based on your current simulation, or enter a custom question below!</p>';
}

function showAuthMessage(text, type) {
    authMessage.textContent = text;
    authMessage.className = `message ${type}`;
}

// --- Data Synchronization ---

async function loadUserData() {
    await fetchProfile();
    await fetchExpenses();
    await fetchGoals();
    await handleRunSimulation();
    await handleGetAdvice(); // Automatically load the AI's initial perspectives!
}

async function fetchProfile() {
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/profile`);
        if (res.ok) {
            const profile = await res.json();
            document.getElementById('monthlyIncome').value = profile.monthly_income || '';
            document.getElementById('currentSavings').value = profile.current_savings || '';
            document.getElementById('monthlySavings').value = profile.target_savings || '';
            if (profile.risk_tolerance) {
                const riskVal = parseInt(profile.risk_tolerance.replace('%', '')) || 50;
                document.getElementById('riskTolerance').value = riskVal;
                updateAllocationChart(riskVal);
            }
        }
    } catch (err) {
        console.error("Error loading profile:", err);
    }
}

// --- Expenses CRUD ---

async function fetchExpenses() {
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/expenses`);
        if (res.ok) {
            const expenses = await res.json();
            renderExpenses(expenses);
        }
    } catch (err) {
        console.error("Error loading expenses:", err);
    }
}

function renderExpenses(expenses) {
    const list = document.getElementById('expensesList');
    list.innerHTML = '';
    expenses.forEach(exp => {
        const row = document.createElement('div');
        row.className = 'item-row';
        row.id = `expense-row-${exp.id}`;
        
        row.innerHTML = `
            <div class="item-info">
                <span class="item-name">${escapeHtml(exp.name)}</span>
                <span class="item-meta">${formatCurrency(exp.amount)}/mo</span>
            </div>
            <div class="item-actions">
                <button type="button" class="btn-icon btn-edit" onclick="toggleEditExpense(${exp.id}, '${escapeQuote(exp.name)}', ${exp.amount})">✏️</button>
                <button type="button" class="btn-icon btn-delete" onclick="handleDeleteExpense(${exp.id})">🗑️</button>
            </div>
        `;
        list.appendChild(row);
    });
}

function toggleEditExpense(id, name, amount) {
    const row = document.getElementById(`expense-row-${id}`);
    
    if (row.classList.contains('editing')) {
        fetchExpenses();
        return;
    }
    
    row.classList.add('editing');
    row.innerHTML = `
        <div class="inline-edit-fields">
            <input type="text" id="edit-expense-name-${id}" class="inline-input" value="${escapeHtml(name)}" required style="flex: 2;">
            <input type="number" id="edit-expense-amount-${id}" class="inline-input" step="1" value="${amount}" placeholder="Amount (₹)" required>
        </div>
        <div class="item-actions">
            <button type="button" class="btn-icon btn-save" onclick="handleSaveExpenseEdit(${id})">💾</button>
            <button type="button" class="btn-icon" onclick="fetchExpenses()">❌</button>
        </div>
    `;
}

async function handleSaveExpenseEdit(id) {
    const name = document.getElementById(`edit-expense-name-${id}`).value;
    const amount = parseFloat(document.getElementById(`edit-expense-amount-${id}`).value);
    
    if (!name || isNaN(amount)) {
        alert('Please fill out all fields with valid data.');
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/expenses/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, amount })
        });
        
        if (res.ok) {
            await fetchExpenses();
            await handleRunSimulation();
        } else {
            alert('Failed to update expense.');
        }
    } catch (err) {
        console.error(err);
    }
}

// PREMIUM INLINE DELETE (No ugly confirm popups)
async function handleDeleteExpense(id) {
    const key = `expense_${id}`;
    const row = document.getElementById(`expense-row-${id}`);
    const delBtn = row.querySelector('.btn-delete');
    
    if (!deleteConfirmations[key]) {
        // Toggle warning state
        deleteConfirmations[key] = true;
        delBtn.textContent = 'Sure? 🗑️';
        delBtn.style.borderColor = 'var(--error-color)';
        delBtn.style.color = 'var(--error-color)';
        
        // Reset confirmation warning after 3 seconds
        setTimeout(() => {
            if (deleteConfirmations[key]) {
                delete deleteConfirmations[key];
                fetchExpenses();
            }
        }, 3000);
        return;
    }
    
    // User clicked a second time, proceed with actual deletion
    delete deleteConfirmations[key];
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/expenses/${id}`, {
            method: 'DELETE'
        });
        
        if (res.ok) {
            await fetchExpenses();
            await handleRunSimulation();
        } else {
            alert('Failed to delete expense.');
        }
    } catch (err) {
        console.error(err);
    }
}

// --- Goals CRUD ---

async function fetchGoals() {
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/goals`);
        if (res.ok) {
            const goals = await res.json();
            renderGoals(goals);
        }
    } catch (err) {
        console.error("Error loading goals:", err);
    }
}

function renderGoals(goals) {
    const list = document.getElementById('goalsList');
    list.innerHTML = '';
    goals.forEach(goal => {
        const row = document.createElement('div');
        row.className = 'item-row';
        row.id = `goal-row-${goal.id}`;
        
        row.innerHTML = `
            <div class="item-info">
                <span class="item-name">${escapeHtml(goal.name)}</span>
                <span class="item-meta">${formatCurrency(goal.target_amount)} in ${goal.months_to_goal} mos (Requires ${formatCurrency(goal.target_amount / goal.months_to_goal)}/mo)</span>
            </div>
            <div class="item-actions">
                <button type="button" class="btn-icon btn-edit" onclick="toggleEditGoal(${goal.id}, '${escapeQuote(goal.name)}', ${goal.target_amount}, ${goal.months_to_goal})">✏️</button>
                <button type="button" class="btn-icon btn-delete" onclick="handleDeleteGoal(${goal.id})">🗑️</button>
            </div>
        `;
        list.appendChild(row);
    });
}

function toggleEditGoal(id, name, targetAmount, monthsToGoal) {
    const row = document.getElementById(`goal-row-${id}`);
    
    if (row.classList.contains('editing')) {
        fetchGoals();
        return;
    }
    
    row.classList.add('editing');
    row.innerHTML = `
        <div class="inline-edit-fields">
            <input type="text" id="edit-goal-name-${id}" class="inline-input" value="${escapeHtml(name)}" required style="flex: 2;">
            <input type="number" id="edit-goal-target-${id}" class="inline-input" step="1" value="${targetAmount}" placeholder="Target (₹)" required>
            <input type="number" id="edit-goal-months-${id}" class="inline-input" value="${monthsToGoal}" placeholder="Months" required>
        </div>
        <div class="item-actions">
            <button type="button" class="btn-icon btn-save" onclick="handleSaveGoalEdit(${id})">💾</button>
            <button type="button" class="btn-icon" onclick="fetchGoals()">❌</button>
        </div>
    `;
}

async function handleSaveGoalEdit(id) {
    const name = document.getElementById(`edit-goal-name-${id}`).value;
    const target = parseFloat(document.getElementById(`edit-goal-target-${id}`).value);
    const months = parseInt(document.getElementById(`edit-goal-months-${id}`).value);
    
    if (!name || isNaN(target) || isNaN(months)) {
        alert('Please fill out all fields with valid data.');
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/goals/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, target_amount: target, months_to_goal: months })
        });
        
        if (res.ok) {
            await fetchGoals();
            await handleRunSimulation();
        } else {
            alert('Failed to update goal.');
        }
    } catch (err) {
        console.error(err);
    }
}

// PREMIUM INLINE DELETE (No ugly confirm popups)
async function handleDeleteGoal(id) {
    const key = `goal_${id}`;
    const row = document.getElementById(`goal-row-${id}`);
    const delBtn = row.querySelector('.btn-delete');
    
    if (!deleteConfirmations[key]) {
        deleteConfirmations[key] = true;
        delBtn.textContent = 'Sure? 🗑️';
        delBtn.style.borderColor = 'var(--error-color)';
        delBtn.style.color = 'var(--error-color)';
        
        setTimeout(() => {
            if (deleteConfirmations[key]) {
                delete deleteConfirmations[key];
                fetchGoals();
            }
        }, 3000);
        return;
    }
    
    delete deleteConfirmations[key];
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/goals/${id}`, {
            method: 'DELETE'
        });
        
        if (res.ok) {
            await fetchGoals();
            await handleRunSimulation();
        } else {
            alert('Failed to delete goal.');
        }
    } catch (err) {
        console.error(err);
    }
}

// --- Data Entry ---

async function handleSaveProfile(e) {
    e.preventDefault();
    const income = parseFloat(document.getElementById('monthlyIncome').value);
    const savingsInput = document.getElementById('currentSavings').value;
    const savings = savingsInput ? parseFloat(savingsInput) : 0.0;
    const targetSavings = parseFloat(document.getElementById('monthlySavings').value);
    const riskInput = document.getElementById('riskTolerance').value;
    const risk = riskInput ? riskInput + '%' : '50%';
    
    try {
        let res = await fetch(`${API_BASE_URL}/users/${currentUserId}/profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ monthly_income: income, current_savings: savings, risk_tolerance: risk, target_savings: targetSavings })
        });
        
        if (res.status === 400) {
            // Probably exists, try PUT
            res = await fetch(`${API_BASE_URL}/users/${currentUserId}/profile`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ monthly_income: income, current_savings: savings, risk_tolerance: risk, target_savings: targetSavings })
            });
        }
        
        if (res.ok) {
            const riskVal = parseInt(riskInput) || 50;
            updateAllocationChart(riskVal);
            await handleRunSimulation();
            await handleGetAdvice(); // Auto-load initial AI advice perspective!
            alert('Profile saved!');
        } else {
            alert('Failed to save profile.');
        }
    } catch (err) {
        console.error(err);
    }
}

async function handleAddExpense(e) {
    e.preventDefault();
    const name = document.getElementById('expenseName').value;
    const amount = parseFloat(document.getElementById('expenseAmount').value);
    
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/expenses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, amount, is_recurring: true })
        });
        if (res.ok) {
            document.getElementById('expenseForm').reset();
            await fetchExpenses();
            await handleRunSimulation();
        }
    } catch (err) {
        console.error(err);
    }
}

async function handleAddGoal(e) {
    e.preventDefault();
    const name = document.getElementById('goalName').value;
    const target = parseFloat(document.getElementById('goalAmount').value);
    const months = parseInt(document.getElementById('goalMonths').value);
    
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/goals`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, target_amount: target, months_to_goal: months })
        });
        if (res.ok) {
            document.getElementById('goalForm').reset();
            await fetchGoals();
            await handleRunSimulation();
        }
    } catch (err) {
        console.error(err);
    }
}

// --- Results & AI ---

async function handleRunSimulation() {
    const simContent = document.getElementById('simulationContent');
    simContent.innerHTML = '<p class="placeholder-text">Calculating...</p>';
    
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/simulation`);
        if (!res.ok) throw new Error('Failed to fetch simulation');
        
        const data = await res.json();
        
        const isFeasibleHtml = data.is_feasible 
            ? '<span class="sim-positive">Yes - planned savings covers goals!</span>' 
            : '<span class="sim-negative">No - planned savings insufficient</span>';
            
        const isSavingsFeasibleHtml = data.savings_plan_feasible
            ? '<span class="sim-positive">Yes - within your budget surplus!</span>'
            : '<span class="sim-negative">No - exceeds actual surplus!</span>';
            
        simContent.innerHTML = `
            <div class="sim-grid">
                <div class="sim-item">
                    <div class="sim-label">Monthly Income</div>
                    <div class="sim-value">${formatCurrency(data.monthly_income)}</div>
                </div>
                <div class="sim-item">
                    <div class="sim-label">Total Expenses</div>
                    <div class="sim-value">${formatCurrency(data.total_monthly_expenses)}</div>
                </div>
                <div class="sim-item">
                    <div class="sim-label">Actual Budget Surplus</div>
                    <div class="sim-value">${formatCurrency(data.monthly_savings_capacity)}</div>
                </div>
                <div class="sim-item">
                    <div class="sim-label">Planned Target Savings</div>
                    <div class="sim-value">${formatCurrency(data.target_savings)}</div>
                </div>
            </div>
            <div style="margin-top: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem; background: rgba(0,0,0,0.15); padding: 1rem; border-radius: 12px; border: var(--glass-border);">
                <div>
                    <span class="sim-label">Savings feasible within budget surplus?:</span><br>
                    <strong>${isSavingsFeasibleHtml}</strong>
                </div>
                <div>
                    <span class="sim-label">Will planned savings cover goals?:</span><br>
                    <strong>${isFeasibleHtml}</strong>
                </div>
                <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.5rem; margin-top: 0.25rem;">
                    <span class="sim-label">Goals Require:</span> 
                    <strong style="color: var(--accent-color);">${formatCurrency(data.required_monthly_for_goals)}/mo</strong>
                </div>
            </div>
        `;
        
        updateBudgetChart(data.total_monthly_expenses, data.target_savings, data.monthly_savings_capacity - data.target_savings);
    } catch (err) {
        simContent.innerHTML = `<p class="placeholder-text sim-negative">Error: ${err.message}</p>`;
    }
}

async function handleGetAdvice() {
    const queryInput = document.getElementById('aiCustomQuery');
    const query = queryInput.value.trim();
    const aiContent = document.getElementById('aiAdviceContent');
    const btn = document.getElementById('getAdviceBtn');
    
    btn.textContent = 'Analyzing...';
    btn.disabled = true;
    aiContent.innerHTML = '<p class="placeholder-text">Consulting FinPilot AI Advisor...</p>';
    
    try {
        let url = `${API_BASE_URL}/users/${currentUserId}/advice`;
        if (query) {
            url += `?query=${encodeURIComponent(query)}`;
        }
        
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to fetch AI advice');
        
        const data = await res.json();
        
        // Process Markdown and render
        let formattedAdvice = renderMarkdown(data.advice);
            
        aiContent.innerHTML = formattedAdvice;
        
        // Clear question box if they asked a custom query
        if (query) {
            queryInput.value = '';
        }
    } catch (err) {
        aiContent.innerHTML = `<p class="placeholder-text sim-negative">Error: ${err.message}</p>`;
    } finally {
        btn.textContent = 'Ask AI';
        btn.disabled = false;
    }
}
