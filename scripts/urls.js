import Pagination from 'js-pagination';

const el = document.getElementById('pagination_data');
const pagination = JSON.parse(el.textContent);
el.remove();

// config
Pagination.config({
  ulClass: 'pagination',
  activeClass: 'active',
});

function navigate(data) {
  data['templateName'] = document.getElementById('template-select').value;
  data['skip'] = data['skip'] || new URLSearchParams(location.search || '').get('skip');
  data['limit'] = data['limit'] || new URLSearchParams(location.search || '').get('limit');

  for (const key in data) if (!data[key]) delete data[key];

  location.href = location.pathname + '?' + new URLSearchParams(Object.entries(data)).toString();
}

const page = Math.floor(pagination.skip / pagination.limit) + 1;
let first = true;

const myPager = new Pagination(
  pagination.total,
  pagination.limit,
  function (page) {
    if (first) {
      first = false;
      return;
    }
    navigate({
      skip: (Math.floor(page.current) - 1) * page.size,
      limit: page.size,
    });
  },
  '#pagination_view'
);
myPager.goToPage(page);

document.getElementById('template-select').addEventListener('change', () => navigate({}));
