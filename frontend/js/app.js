const API_BASE_URL = 'http://localhost:8000/api';

// Global State
let currentUserId = null;

// DOM Elements
const authSection = document.getElementById('authSection');
const mainContent = document.getElementById('mainContent');
const userStatus = document.getElementById('userStatus');
const authMessage = document.getElementById('authMessage');

// Event Listeners
document.getElementById('authForm').addEventListener('submit', handleRegister);
document.getElementById('loginBtn').addEventListener('click', handleLogin);
document.getElementById('profileForm').addEventListener('submit', handleSaveProfile);
document.getElementById('expenseForm').addEventListener('submit', handleAddExpense);
document.getElementById('goalForm').addEventListener('submit', handleAddGoal);
document.getElementById('runSimulationBtn').addEventListener('click', handleRunSimulation);
document.getElementById('getAdviceBtn').addEventListener('click', handleGetAdvice);

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
            loginUser(data.id, data.name);
        } else {
            showAuthMessage(data.detail, 'error');
        }
    } catch (err) {
        showAuthMessage('Network error.', 'error');
    }
}

async function handleLogin() {
    // Basic mock login: Since we don't have a specific login endpoint in the tutorial,
    // we just fetch all users and find the one matching the email.
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
            loginUser(user.id, user.name);
        } else {
            showAuthMessage('User not found. Please register.', 'error');
        }
    } catch (err) {
        showAuthMessage('Network error.', 'error');
    }
}

function loginUser(id, name) {
    currentUserId = id;
    userStatus.textContent = `Logged in as: ${name || 'User ' + id}`;
    authSection.classList.add('hidden');
    mainContent.classList.remove('hidden');
}

function showAuthMessage(text, type) {
    authMessage.textContent = text;
    authMessage.className = `message ${type}`;
}

// --- Data Entry ---

async function handleSaveProfile(e) {
    e.preventDefault();
    const income = parseFloat(document.getElementById('monthlyIncome').value);
    const savings = parseFloat(document.getElementById('currentSavings').value);
    
    // In a real app we'd check if profile exists and use PUT instead of POST if it does.
    // For simplicity, we assume POST or handle error and fallback to PUT.
    try {
        let res = await fetch(`${API_BASE_URL}/users/${currentUserId}/profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ monthly_income: income, current_savings: savings })
        });
        
        if (res.status === 400) {
            // Probably exists, try PUT
            res = await fetch(`${API_BASE_URL}/users/${currentUserId}/profile`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ monthly_income: income, current_savings: savings })
            });
        }
        
        if (res.ok) {
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
            alert('Expense added!');
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
            alert('Goal added!');
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
            ? '<span class="sim-positive">Yes - On Track!</span>' 
            : '<span class="sim-negative">No - Action Required</span>';
            
        simContent.innerHTML = `
            <div class="sim-grid">
                <div class="sim-item">
                    <div class="sim-label">Income</div>
                    <div class="sim-value">$${data.monthly_income.toFixed(2)}</div>
                </div>
                <div class="sim-item">
                    <div class="sim-label">Expenses</div>
                    <div class="sim-value">$${data.total_monthly_expenses.toFixed(2)}</div>
                </div>
                <div class="sim-item">
                    <div class="sim-label">Savings Capacity</div>
                    <div class="sim-value">$${data.monthly_savings_capacity.toFixed(2)}</div>
                </div>
                <div class="sim-item">
                    <div class="sim-label">Goals Require</div>
                    <div class="sim-value">$${data.required_monthly_for_goals.toFixed(2)}/mo</div>
                </div>
            </div>
            <div style="margin-top: 1rem; text-align: center;">
                <span class="sim-label">Goals Feasible?</span><br>
                <strong>${isFeasibleHtml}</strong>
            </div>
        `;
    } catch (err) {
        simContent.innerHTML = `<p class="placeholder-text sim-negative">Error: ${err.message}</p>`;
    }
}

async function handleGetAdvice() {
    const aiContent = document.getElementById('aiAdviceContent');
    const btn = document.getElementById('getAdviceBtn');
    
    btn.textContent = 'Generating...';
    btn.disabled = true;
    aiContent.innerHTML = '<p class="placeholder-text">Consulting FinPilot AI...</p>';
    
    try {
        const res = await fetch(`${API_BASE_URL}/users/${currentUserId}/advice`);
        if (!res.ok) throw new Error('Failed to fetch AI advice');
        
        const data = await res.json();
        
        // Very basic markdown to HTML for bolding and line breaks
        let formattedAdvice = data.advice
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
            
        aiContent.innerHTML = `<p>${formattedAdvice}</p>`;
    } catch (err) {
        aiContent.innerHTML = `<p class="placeholder-text sim-negative">Error: ${err.message}</p>`;
    } finally {
        btn.textContent = 'Get Advice';
        btn.disabled = false;
    }
}
