(function () {
  const MAX = 5;

  function bind(container) {
    if (!container || container.dataset.interestsBound === '1') return;
    container.dataset.interestsBound = '1';

    const form = container.closest('form');
    const csvInput = form ? form.querySelector('#interests-input') : null;
    const selected = new Set();

    container.querySelectorAll('[data-id]').forEach(box => {
      box.tabIndex = 0;
      box.setAttribute('role', 'button');
      box.setAttribute('aria-pressed', 'false');
    });

    container.addEventListener('click', (e) => {
      const box = e.target.closest('[data-id]');
      if (box) toggle(box);
    });

    container.addEventListener('keydown', (e) => {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      const box = e.target.closest('[data-id]');
      if (!box) return;
      e.preventDefault();
      toggle(box);
    });

    function toggle(box) {
      const id = box.dataset.id;
      if (box.classList.contains('selected')) {
        box.classList.remove('selected');
        box.setAttribute('aria-pressed', 'false');
        selected.delete(id);
        sync();
        return;
      }
      if (selected.size >= MAX) {
        box.classList.add('limit-hit');
        setTimeout(() => box.classList.remove('limit-hit'), 250);
        return;
      }
      box.classList.add('selected');
      box.setAttribute('aria-pressed', 'true');
      selected.add(id);
      sync();
    }

    function sync() {
      if (csvInput) csvInput.value = Array.from(selected).join(',');
      if (!form) return;

      form.querySelectorAll('input[name="interests[]"]').forEach(n => n.remove());
      for (const id of selected) {
        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = 'interests[]';
        hidden.value = id;
        form.appendChild(hidden);
      }
    }
  }

  function tryBind(root) {
    const node = (root || document).querySelector('.grid-container');
    if (node) bind(node);
  }


  document.addEventListener('DOMContentLoaded', () => tryBind(document));


  document.body.addEventListener('htmx:afterSwap', (e) => {
    tryBind(e.detail && e.detail.target);
  });
})();
