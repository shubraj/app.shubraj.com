(() => {
  const $ = (id) => document.getElementById(id);
  const mdInput = $('mdInput');
  const htmlInput = $('htmlInput');
  const output = $('convOutput');
  const mdToHtmlBtn = $('mdToHtml');
  const htmlToMdBtn = $('htmlToMd');
  const clearMd = $('clearMd');
  const clearHtml = $('clearHtml');
  if (!mdInput) return;

  const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced'
  });

  mdToHtmlBtn?.addEventListener('click', () => {
    try {
      output.value = marked.parse(mdInput.value || '');
    } catch (e) {
      output.value = 'Conversion error: ' + e.message;
    }
  });

  htmlToMdBtn?.addEventListener('click', () => {
    try {
      output.value = turndownService.turndown(htmlInput.value || '');
    } catch (e) {
      output.value = 'Conversion error: ' + e.message;
    }
  });

  clearMd?.addEventListener('click', () => { mdInput.value = ''; });
  clearHtml?.addEventListener('click', () => { htmlInput.value = ''; });
})();


