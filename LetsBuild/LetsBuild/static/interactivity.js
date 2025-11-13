
document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.grid-container');
  const max = 5;
  const selected = new Set();
  const csvInput = document.querySelector('#interests-input');

  // Make boxes keyboard-accessible
  container.querySelectorAll('[data-id]').forEach(box => {
    box.setAttribute('tabindex', '0');
    box.setAttribute('role', 'button');
    box.setAttribute('aria-pressed', 'false');
  });

  container.addEventListener('click', onToggle);
  container.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      const box = e.target.closest('[data-id]');
      if (box && container.contains(box)) {
        e.preventDefault();
        toggleBox(box);
      }
    }
  });

  function onToggle(e) {
    const box = e.target.closest('[data-id]');
    if (!box || !container.contains(box)) return;
    toggleBox(box);
  }

  function toggleBox(box) {
    const id = box.dataset.id;
    const isSelected = box.classList.contains('selected');

    if (isSelected) {
      box.classList.remove('selected');
      box.setAttribute('aria-pressed', 'false');
      selected.delete(id);
      syncHiddenInputs();
      return;
    }

    if (selected.size >= max) {
      // hit the cap: give feedback and ignore
      box.classList.add('limit-hit');
      setTimeout(() => box.classList.remove('limit-hit'), 250);
      return;
    }

    box.classList.add('selected');
    box.setAttribute('aria-pressed', 'true');
    selected.add(id);
    syncHiddenInputs();
  }

  function syncHiddenInputs() {
    // 1) CSV field (simple to parse server-side)
    if (csvInput) {
      csvInput.value = Array.from(selected).join(',');
    }
    // 2) Also create multiple form values interests[] (handy in Django)
    const form = container.closest('form');
    if (!form) return;

    // remove old dynamic inputs
    form.querySelectorAll('input[name="interests[]"]').forEach(n => n.remove());
    // add current selections
    for (const id of selected) {
      const hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = 'interests[]';
      hidden.value = id; // e.g., "box-7"
      form.appendChild(hidden);
    }
  }
});

