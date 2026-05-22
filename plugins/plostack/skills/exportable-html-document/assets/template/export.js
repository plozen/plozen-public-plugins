document.querySelector('[data-export="pdf"]')?.addEventListener('click', () => {
  window.print();
});

document.querySelector('[data-export="pptx"]')?.addEventListener('click', () => {
  document.dispatchEvent(new CustomEvent('exportable-html:pptx-requested'));
});
