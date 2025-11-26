console.log("project-select.js loaded");

(function () {
    const container = document.getElementById('projects');
    if (!container) return;

    const saveUrl = container.dataset.saveUrl;
    const cards = container.querySelectorAll('.project-card');

    const continueContainer = document.getElementById('continue-container');
    const continueBtn = document.getElementById('continue-btn');

    let selectedIndex = null;

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    function setSelected(index) {
        document.querySelectorAll('.select-btn').forEach(btn =>
        btn.classList.remove('rotated')
        );

        // Add rotation to the active button
        const selectedBtn = document.querySelector(
            `.project-card[data-index="${index}"] .select-btn`
        );
        if (selectedBtn) {
            selectedBtn.classList.add('rotated');
        }



        index = Number(index);


        if (selectedIndex === index) {
            selectedIndex = null;

            cards.forEach(card => {
                card.classList.remove('selected');
                card.setAttribute('aria-pressed', 'false');
            });

            // Hide continue button
            continueContainer.style.display = "none";
            return;
        }

        // Otherwise, select new card
        selectedIndex = index;

        cards.forEach(card => {
            const isSelected = Number(card.dataset.index) === index;
            card.classList.toggle('selected', isSelected);
            card.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
        });

        // Show continue button
        continueContainer.style.display = "flex";
    }

    // Attach card listeners
    cards.forEach(card => {
        const index = card.dataset.index;

        // Click select button only
        const btn = card.querySelector('.select-btn');
        if (btn) {
            btn.addEventListener('click', e => {
                e.stopPropagation();
                setSelected(index);
            });
        }

        // Keyboard support only when focus is on select button
        card.addEventListener('keydown', (e) => {
            if (['Enter', ' '].includes(e.key)) {
                const isButton = document.activeElement.classList.contains('select-btn');
                if (isButton) {
                    e.preventDefault();
                    setSelected(index);
                }
            }
        });
    });

    // Save selected project
    function postSelection(index) {
        fetch(saveUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ index: Number(index) })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;  // <-- redirect to index.html
            } else {
                alert('Could not save project.');
            }
        })
        .catch(err => {
            console.error(err);
            alert('Error saving project.');
        });
    }

    // Continue / choose project button click
    continueBtn.addEventListener('click', () => {
        if (selectedIndex === null) {
            alert("Please select a project first.");
            return;
        }
        postSelection(selectedIndex);
    });
})();

function toggleMenu() {
    const dropdownContent = document.querySelector('.dropdown-content');
    const icon = document.querySelector('.icon');

    if (dropdownContent.style.display == 'flex') {
        dropdownContent.style.display = 'none'
    }
    else {
        dropdownContent.style.display = 'flex';
    }
    dropdownContent.classList.toggle('show');  
    icon.classList.toggle('rotated'); 
}
