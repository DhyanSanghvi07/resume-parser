const toggleBtn = document.getElementById('theme-toggle');
const icon = toggleBtn.querySelector('i');
const body = document.body;

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

const fileInput = document.getElementById('resume-file'); // unified ID
const previewFrame = document.getElementById('previewFrame');
const fileNameDisplay = document.getElementById('file-name-display');
const loadingOverlay = document.getElementById('loading-overlay');
const clearFileBtn = document.getElementById('clear-file-btn');

previewFrame.src = DUMMY_PDF_URL;

function showLoadingOverlay() {
  loadingOverlay.classList.remove('d-none');
}

function hideLoadingOverlay() {
  loadingOverlay.classList.add('d-none');
}

function clearSelectedFile() {
  fileInput.value = '';
  previewFrame.src = DUMMY_PDF_URL;
  updateFileDisplay(null);
  fileInput.classList.remove('is-invalid');
  dropArea.classList.remove('border-danger');
  showToast('File cleared!', 'info', 3000);
}

clearFileBtn.addEventListener('click', clearSelectedFile);

function updateFileDisplay(file) {
  if (file) {
    fileNameDisplay.textContent = `Selected file: ${file.name}`;
    fileNameDisplay.classList.remove('d-none');
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
    clearFileBtn.disabled = false;
  } else {
    previewFrame.src = DUMMY_PDF_URL;
    showToast('Please upload a valid PDF or DOCX file.', 'danger');
    fileInput.classList.add('is-invalid');
    updateFileDisplay(null);
    clearFileBtn.disabled = true;
  }
});

const dropArea = document.querySelector('.upload-box');

['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, e => {
    e.preventDefault();
    e.stopPropagation();
    dropArea.classList.add('drag-over');
  });
});

['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, e => {
    e.preventDefault();
    e.stopPropagation();
    dropArea.classList.remove('drag-over');
  });
});

dropArea.addEventListener('drop', e => {
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    updateFileDisplay(file);
    if (file.type === 'application/pdf' || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      previewFrame.src = URL.createObjectURL(file);
      fileInput.files = files;
      dropArea.classList.remove('border-danger');
      clearFileBtn.disabled = false;
    } else {
      previewFrame.src = DUMMY_PDF_URL;
      showToast('Please upload a valid PDF or DOCX file.', 'danger');
      dropArea.classList.add('border-danger');
      updateFileDisplay(null);
      clearFileBtn.disabled = true;
    }
  }
});

if (!fileInput.files[0]) {
  clearFileBtn.disabled = true;
}

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

  toastEl.addEventListener('hidden.bs.toast', () => {
    toastEl.remove();
  });
}

async function uploadResume(file) {
  const uploadBtn = document.getElementById("upload-btn");
  const originalText = uploadBtn.innerHTML;
  
  showLoadingOverlay(); 

  uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
  uploadBtn.disabled = true;
  clearFileBtn.disabled = true; 

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

    window.location.href = "/Output Page/index.html";
    
  } catch (error) {
    console.error('Upload error:', error);
    showToast("Error uploading resume: " + error.message, 'danger');
    
    uploadBtn.innerHTML = originalText;
    uploadBtn.disabled = false;
    if (fileInput.files.length > 0) {
      clearFileBtn.disabled = false;
    }
  } finally {
    hideLoadingOverlay();
  }
}

document.getElementById("upload-btn").addEventListener("click", () => {
  if (fileInput.files.length === 0) {
    showToast("Please select a file first.", 'warning');
    fileInput.classList.add('is-invalid');
    dropArea.classList.add('border-danger');
    return;
  }
  uploadResume(fileInput.files[0]);
});

