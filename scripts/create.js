import Tribute from 'tributejs';

(function () {
  const templateName = (location.search && new URLSearchParams(location.search).get('templateName')?.trim()) || 'default';

  function updateTemplateName() {
    const newName = document.getElementById('templateName').value?.trim() || 'default';
    if (templateName !== newName) location.href = newName == 'default' ?  '/create/' : `/create/?templateName=${newName}&basedOn=${templateName}`;
  }

  updateTemplateName();
  document.getElementById('templateName').addEventListener('blur', updateTemplateName);
  document.getElementById('templateName').addEventListener('keydown', e => e.key == 'Enter' && updateTemplateName());

  document.getElementById('csv_file').onchange = function () {
    document.getElementById('csv-form').submit();
  };

  const template_data = JSON.parse(document.getElementById('template_data').textContent);
  document.getElementById('template_data').remove();

  const form = document.getElementById('template-form');
  form.addEventListener('keydown', e =>  e.key == 'Enter' && e.target?.tagName.toLowerCase() && e.preventDefault());

  for (const key in template_data) {
    if (key !== 'templateName' && Object.hasOwnProperty.call(template_data, key) && form[key]) form[key].value = template_data[key] || null;
  }

  const tribute = new Tribute({
    values: JSON.parse(document.getElementById('headers_values').textContent).map(key => ({ key, value: key })),
    trigger: '$',
  });

  tribute.attach(form.querySelectorAll('[type=text]:not(#templateName), textarea'));
})();
