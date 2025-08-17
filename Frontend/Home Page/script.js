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

// Resume preview logic
const fileInput = document.getElementById('resume-file'); // unified ID
const previewFrame = document.getElementById('previewFrame');

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (file && file.type === 'application/pdf') {
    previewFrame.src = URL.createObjectURL(file);
  } else {
    previewFrame.src = '';
    alert('Please upload a valid PDF file.');
  }
});

const dropArea = document.querySelector('.upload-box');

// Prevent default drag/drop behavior
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, e => {
    e.preventDefault();
    e.stopPropagation();
  });
});

// Highlight on drag enter/over
['dragenter', 'dragover'].forEach(eventName => {
  dropArea.classList.add('highlight');
});

// Remove highlight on drag leave/drop
['dragleave', 'drop'].forEach(eventName => {
  dropArea.classList.remove('highlight');
});

// Handle dropped file
dropArea.addEventListener('drop', e => {
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    if (file.type === 'application/pdf') {
      previewFrame.src = URL.createObjectURL(file);
      fileInput.files = files; // sync to input
    } else {
      previewFrame.src = '';
      alert('Please upload a valid PDF file.');
    }
  }
});

// Upload to backend
async function uploadResume(file) {
  const uploadBtn = document.getElementById("upload-btn");
  const originalText = uploadBtn.innerHTML;
  
  // Show loading state
  uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
  uploadBtn.disabled = true;

  try {
    const formData = new FormData();
    formData.append("resume", file);

    const response = await fetch("/parse", {
      method: "POST",
      body: formData
    });
console.log(response,"response");
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || response.statusText);
    }

    // Success - redirect to output page
    window.location.href = "/Output Page/index.html";
    
  } catch (error) {
    console.error('Upload error:', error);
    alert("Error uploading resume: " + error.message);
    
    // Reset button state
    uploadBtn.innerHTML = originalText;
    uploadBtn.disabled = false;
  }
}

document.getElementById("upload-btn").addEventListener("click", () => {
  if (fileInput.files.length === 0) {
    alert("Please select a file first");
    return;
  }
  uploadResume(fileInput.files[0]);
});
