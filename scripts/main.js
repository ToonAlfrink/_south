import jstz from 'jstz';
import ct from 'countries-and-timezones';

(function () {
  const timezone = jstz.determine();
  const countries = ct.getTimezone(timezone.name()).countries;
  const country = countries && countries[countries.length - 1]?.toLowerCase();

  if (!country) return;

  const lang = '/en-' + country;
  if (location.pathname.startsWith(lang)) return;

  let list = location.pathname
    .split('/')
    .map(s => s.trim())
    .filter(s => s.trim());

  if(/^\w+-\w+$/.test(list[0] || '')) list = list.slice(1);

  if (list.length == 0) {
    location.href = lang;
  } else {
    location.href = lang + '/' + list.join('/');
  }
})();
