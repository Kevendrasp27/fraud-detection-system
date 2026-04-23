const API = 'http://13.201.133.55:8000';

/* ── API health check ── */
async function checkApi() {
    const dot  = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    try {
        await fetch(`${API}/docs`, { method: 'HEAD', signal: AbortSignal.timeout(3000) });
        dot.classList.add('online');
        text.textContent = 'API connected';
    } catch {
        dot.classList.add('offline');
        text.textContent = 'API offline — start the backend server';
    }
}
checkApi();

/* ── Form submit ── */
document.getElementById('prediction-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn        = document.getElementById('submit-btn');
    const btnText    = btn.querySelector('.btn-text');
    const btnLoader  = btn.querySelector('.btn-loader');
    const resultCard = document.getElementById('result-card');

    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    btn.disabled = true;
    resultCard.classList.add('hidden');

    const amount        = parseFloat(document.getElementById('amount').value);
    const oldbalanceOrg = parseFloat(document.getElementById('oldbalanceOrg').value);
    const newbalanceOrig= parseFloat(document.getElementById('newbalanceOrig').value);
    const oldbalanceDest= parseFloat(document.getElementById('oldbalanceDest').value);
    const newbalanceDest= parseFloat(document.getElementById('newbalanceDest').value);

    try {
        const res = await fetch(`${API}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest })
        });

        if (!res.ok) throw new Error(`Server returned ${res.status}`);

        const { prediction, probability } = await res.json();
        showResult(prediction, probability, { amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest });

    } catch (err) {
        showError(err.message);
    } finally {
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
        btn.disabled = false;
    }
});

/* ── Render result ── */
function showResult(prediction, probability, tx) {
    const isFraud    = prediction === 'Fraud';
    const resultCard = document.getElementById('result-card');
    const pct        = (probability * 100);

    resultCard.className = 'result-card ' + (isFraud ? 'fraud-result' : 'safe-result');

    document.getElementById('result-label').textContent =
        isFraud ? '⚠ Fraud Detected' : '✓ Transaction Safe';

    document.getElementById('result-sublabel').textContent =
        isFraud
            ? 'This transaction shows high-risk patterns'
            : 'No suspicious patterns detected';

    document.querySelector('.icon-fraud').classList.toggle('hidden', !isFraud);
    document.querySelector('.icon-safe').classList.toggle('hidden',  isFraud);

    /* confidence bar */
    const bar = document.getElementById('confidence-bar');
    const val = document.getElementById('confidence-value');
    bar.style.width = '0%';
    val.textContent = '0%';

    resultCard.classList.remove('hidden');

    requestAnimationFrame(() => {
        setTimeout(() => {
            bar.style.width = pct.toFixed(1) + '%';
            animateNumber(val, 0, pct, 1100, v => v.toFixed(1) + '%');
        }, 80);
    });

    /* risk factors */
    const factors = buildFactors(tx, probability);
    const container = document.getElementById('result-factors');
    container.innerHTML = factors
        .map(f => `<div class="factor"><span class="factor-icon">${f.icon}</span><span>${f.text}</span></div>`)
        .join('');
}

function buildFactors(tx, prob) {
    const factors = [];
    const { amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest } = tx;

    /* Amount size */
    if (amount > 500000)
        factors.push({ icon: '💸', text: `Very large transfer: $${fmt(amount)} — high-risk threshold` });
    else if (amount > 100000)
        factors.push({ icon: '💰', text: `Large transfer: $${fmt(amount)}` });
    else
        factors.push({ icon: '💵', text: `Transaction amount: $${fmt(amount)}` });

    /* Sender balance consistency */
    const expectedNew = oldbalanceOrg - amount;
    const senderDelta  = Math.abs(expectedNew - newbalanceOrig);
    if (senderDelta > 1)
        factors.push({ icon: '⚠️', text: `Sender balance discrepancy of $${fmt(senderDelta)} — funds unaccounted for` });
    else
        factors.push({ icon: '✅', text: `Sender balance consistent after deduction` });

    /* Receiver balance consistency */
    const receiverGain = newbalanceDest - oldbalanceDest;
    if (Math.abs(receiverGain - amount) > 1 && newbalanceDest === oldbalanceDest)
        factors.push({ icon: '🚩', text: `Receiver balance unchanged despite transfer — suspicious` });
    else
        factors.push({ icon: '📊', text: `Receiver balance change: +$${fmt(Math.max(0, receiverGain))}` });

    return factors;
}

/* ── Error state ── */
function showError(msg) {
    const resultCard = document.getElementById('result-card');
    resultCard.className = 'result-card fraud-result';
    document.getElementById('result-label').textContent    = 'Connection Error';
    document.getElementById('result-sublabel').textContent = msg;
    document.querySelector('.icon-fraud').classList.remove('hidden');
    document.querySelector('.icon-safe').classList.add('hidden');
    document.getElementById('confidence-bar').style.width  = '0%';
    document.getElementById('confidence-value').textContent = '–';
    document.getElementById('result-factors').innerHTML =
        `<div class="factor"><span class="factor-icon">🔌</span><span>Make sure the backend is running: <code>venv\\Scripts\\python.exe -m uvicorn app.main:app --reload</code></span></div>`;
    resultCard.classList.remove('hidden');
}

/* ── Helpers ── */
function animateNumber(el, from, to, duration, format) {
    const start = performance.now();
    function tick(now) {
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        el.textContent = format(from + (to - from) * eased);
        if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

function fmt(n) {
    return n.toLocaleString('en-US', { maximumFractionDigits: 2 });
}
