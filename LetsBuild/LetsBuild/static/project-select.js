(function () {
    const container = document.getElementById('projects');
    if (!container) return;

    const saveUrl = container.dataset.saveUrl;
    const cards = container.querySelectorAll('.project-card');
    let continueContainer = document.getElementById('continue-container');
    const continueBtn = document.getElementById('continue-btn');
    if (!continueContainer) continueContainer = document.querySelector('.continue-btn-box');

    let selectedIndex = null;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

        function setSelected(index) {
        selectedIndex = Number(index);
        cards.forEach(card => {
            const isSelected = card.dataset.index === String(index);
            card.classList.toggle('selected', isSelected);
            card.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
        });
            if (continueContainer) {
                try { continueContainer.style.display = 'flex'; } catch(e) { continueContainer.style.display = 'block'; }
            }
    }

    cards.forEach(card => {
        card.addEventListener('click', () => setSelected(card.dataset.index));
        const btn = card.querySelector('.select-btn');
        if (btn) {
            btn.addEventListener('click', (e) => { e.stopPropagation(); setSelected(btn.dataset.index); });
        }
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setSelected(card.dataset.index); }
        });
    });

    function postSelection(index) {
        if (!saveUrl) { alert('Save URL not configured.'); return; }
        continueBtn.disabled = true;
        fetch(saveUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
            body: JSON.stringify({ index: Number(index) })
        })
        .then(response => {
            if (!response.ok) return response.text().then(t => { throw new Error(t || 'Server error'); });
            return response.json();
        })
        .then(data => {
            if (data && data.success) window.location.reload(); else alert('Could not save project.');
        })
        .catch(err => { console.error('Save error:', err); alert('Error saving project: ' + (err.message || err)); })
        .finally(() => { continueBtn.disabled = false; });
    }

    if (continueBtn) continueBtn.addEventListener('click', () => {
        if (selectedIndex === null) { alert('Please select a project first.'); return; }
        postSelection(selectedIndex);
    });
})();
