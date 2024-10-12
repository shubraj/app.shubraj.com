window.addEventListener('load', () => {
   const loadingAnimation = document.querySelector('.loading-animation');
   loadingAnimation.style.opacity = '0';
   setTimeout(() => {
       loadingAnimation.style.display = 'none';
   }, 500);

   // Check if dark mode was enabled before and persist it
   const darkMode = localStorage.getItem('darkMode');
   if (darkMode === 'enabled') {
       body.classList.add('dark-mode');
       darkModeToggle.textContent = '☀️'; // Update button to sun icon
   }
});

// Dark Mode Toggle
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;

darkModeToggle.addEventListener('click', () => {
   body.classList.toggle('dark-mode');
   
   if (body.classList.contains('dark-mode')) {
       localStorage.setItem('darkMode', 'enabled'); // Save dark mode preference
       darkModeToggle.textContent = '☀️'; // Change to sun icon
   } else {
       localStorage.setItem('darkMode', 'disabled'); // Save light mode preference
       darkModeToggle.textContent = '🌓'; // Change to moon icon
   }
});

// Mobile Navigation Toggle
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('nav ul');

navToggle.addEventListener('click', () => {
   navMenu.classList.toggle('show');
});
