(() => {
  const form = document.querySelector('.archive-tools');
  if (form) {
    const search = document.querySelector('#journal-search');
    const category = document.querySelector('#journal-category');
    const entries = Array.from(document.querySelectorAll('[data-entry]'));
    const filter = () => {
      const query = search.value.trim().toLocaleLowerCase();
      let count = 0;
      entries.forEach(entry => {
        const show = (!category.value || entry.dataset.category === category.value) && entry.dataset.search.includes(query);
        entry.hidden = !show;
        if (show) count++;
      });
      document.querySelector('#result-count').textContent = `${count} ${count === 1 ? 'entry' : 'entries'}`;
      document.querySelector('#no-results').hidden = count !== 0;
    };
    form.addEventListener('submit', event => event.preventDefault());
    search.addEventListener('input', filter);
    category.addEventListener('change', filter);
    form.addEventListener('reset', () => setTimeout(filter, 0));
  }
  const copy = document.querySelector('#copy-link');
  if (copy) copy.addEventListener('click', async () => {
    const status = document.querySelector('#copy-status');
    try {
      await navigator.clipboard.writeText(window.location.href.split('#')[0]);
      status.textContent = 'Link copied.';
    } catch (_) {
      status.textContent = 'Copy the page address from your browser to share this essay.';
    }
  });
})();
