// Theme toggle logic
const toggleBtn = document.getElementById('theme-toggle');
const icon = toggleBtn.querySelector('i');
const body = document.body;

if (localStorage.getItem('theme') === 'dark') {
  body.classList.add('dark-mode');
  body.classList.remove('light-mode');
  icon.classList.remove('fa-moon');
  icon.classList.add('fa-sun');
}

toggleBtn.addEventListener('click', () => {
  const isDark = body.classList.toggle('dark-mode');
  body.classList.toggle('light-mode');
  icon.classList.toggle('fa-sun', isDark);
  icon.classList.toggle('fa-moon', !isDark);
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
});