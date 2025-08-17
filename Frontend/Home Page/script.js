// Theme toggle logic
const toggleBtn = document.getElementById('theme-toggle');
const icon = toggleBtn.querySelector('i');
const body = document.body;

// Constants
const DUMMY_PDF_URL = 'https://msnlabs.com/img/resume-sample.pdf';

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
const fileNameDisplay = document.getElementById('file-name-display');
const loadingOverlay = document.getElementById('loading-overlay');
const clearFileBtn = document.getElementById('clear-file-btn');

// Set initial preview source
previewFrame.src = DUMMY_PDF_URL;

function showLoadingOverlay() {
  loadingOverlay.classList.remove('d-none');
}

function hideLoadingOverlay() {
  loadingOverlay.classList.add('d-none');
}

function clearSelectedFile() {
  fileInput.value = ''; // Clear the file input
  previewFrame.src = DUMMY_PDF_URL; // Revert preview to dummy PDF
  updateFileDisplay(null); // Clear displayed file name
  fileInput.classList.remove('is-invalid');
  dropArea.classList.remove('border-danger');
  showToast('File cleared!', 'info', 3000);
}

// Add event listener for the Clear button
clearFileBtn.addEventListener('click', clearSelectedFile);

function updateFileDisplay(file) {
  if (file) {
    fileNameDisplay.textContent = `Selected file: ${file.name}`;
    fileNameDisplay.classList.remove('d-none');
    // Clear any previous error states related to file input
    fileInput.classList.remove('is-invalid');
    dropArea.classList.remove('border-danger');
  } else {
    fileNameDisplay.textContent = '';
    fileNameDisplay.classList.add('d-none');
  }
}

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  updateFileDisplay(file);
  if (file && (file.type === 'application/pdf' || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
    previewFrame.src = URL.createObjectURL(file);
    fileInput.classList.remove('is-invalid');
    // Enable clear button if file is valid
    clearFileBtn.disabled = false;
  } else {
    previewFrame.src = DUMMY_PDF_URL; // Fallback to dummy PDF
    showToast('Please upload a valid PDF or DOCX file.', 'danger');
    fileInput.classList.add('is-invalid');
    updateFileDisplay(null); // Clear file name display for invalid files
    clearFileBtn.disabled = true; // Disable clear button for invalid file
  }
});

const dropArea = document.querySelector('.upload-box');

// Prevent default drag/drop behavior
['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, e => {
    e.preventDefault();
    e.stopPropagation();
    dropArea.classList.add('drag-over'); // Add drag-over class
  });
});

['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, e => {
    e.preventDefault();
    e.stopPropagation();
    dropArea.classList.remove('drag-over'); // Remove drag-over class
  });
});

// Handle dropped file
dropArea.addEventListener('drop', e => {
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    updateFileDisplay(file);
    if (file.type === 'application/pdf' || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      previewFrame.src = URL.createObjectURL(file);
      fileInput.files = files; // sync to input
      dropArea.classList.remove('border-danger');
      clearFileBtn.disabled = false; // Enable clear button
    } else {
      previewFrame.src = DUMMY_PDF_URL; // Fallback to dummy PDF
      showToast('Please upload a valid PDF or DOCX file.', 'danger');
      dropArea.classList.add('border-danger');
      updateFileDisplay(null); // Clear file name display for invalid files
      clearFileBtn.disabled = true; // Disable clear button
    }
  }
});

// Initial state: disable clear button if no file selected
// Assuming fileInput might be empty on load, so we initialize clear button state
if (!fileInput.files[0]) {
  clearFileBtn.disabled = true;
}

// Error message handling functions (replaced by toasts)
// const errorMessageDiv = document.getElementById('error-message');
// function displayErrorMessage(message) { /* ... */ }
// function clearErrorMessage() { /* ... */ }

// Toast notification function
function showToast(message, type = 'info', delay = 5000) {
  const toastContainer = document.querySelector('.toast-container');
  const toastId = `toast-${Date.now()}`;
  
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  const toastEl = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastEl, { delay: delay });
  toast.show();

  // Remove toast from DOM after it's hidden
  toastEl.addEventListener('hidden.bs.toast', () => {
    toastEl.remove();
  });
}

// Upload to backend
async function uploadResume(file) {
  const uploadBtn = document.getElementById("upload-btn");
  const originalText = uploadBtn.innerHTML;
  
  showLoadingOverlay(); // Show loading overlay

  // Show loading state
  uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
  uploadBtn.disabled = true;
  clearFileBtn.disabled = true; // Disable clear button during upload
  // clearErrorMessage(); // No longer needed, toasts handle visibility

  try {
    const formData = new FormData();
    formData.append("resume", file);

    const response = await fetch("/parse", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || response.statusText);
    }

    // Success - redirect to output page
    window.location.href = "/Output Page/index.html";
    
  } catch (error) {
    console.error('Upload error:', error);
    showToast("Error uploading resume: " + error.message, 'danger');
    
    // Reset button state
    uploadBtn.innerHTML = originalText;
    uploadBtn.disabled = false;
    // Re-enable clear button if upload failed (and file still selected)
    if (fileInput.files.length > 0) {
      clearFileBtn.disabled = false;
    }
  } finally {
    hideLoadingOverlay(); // Always hide overlay, regardless of success or failure
  }
}

document.getElementById("upload-btn").addEventListener("click", () => {
  if (fileInput.files.length === 0) {
    showToast("Please select a file first.", 'warning');
    fileInput.classList.add('is-invalid');
    dropArea.classList.add('border-danger');
    // clearFileBtn.disabled = true; // Already handled by initial state
    return;
  }
  uploadResume(fileInput.files[0]);
});

