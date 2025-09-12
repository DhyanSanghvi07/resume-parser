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

// Load and display parsed resume data
fetch("/output.json")
    .then(res => {
        if (!res.ok) {
            throw new Error('No parsed data available');
        }
        return res.json();
    })
    .then(data => {
        displayResumeData(data);
    })
    .catch(err => {
        console.error('Error loading output data:', err);
        document.getElementById("output").innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading parsed resume data...</p>
            </div>`;
        showToast('No parsed data available. Please upload a resume first.', 'warning');
    });

// Toast notification function (copied from Home Page script for consistency)
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

function displayResumeData(data) {
    const outputAccordion = document.getElementById("output-accordion");
    outputAccordion.innerHTML = ''; // Clear loading spinner/message
    
    // Helper function to create an accordion item
    function createAccordionItem(id, title, contentHtml, show = false) {
        const accordionItem = `
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading${id}">
                    <button class="accordion-button ${show ? '' : 'collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${id}" aria-expanded="${show}" aria-controls="collapse${id}">
                        ${title}
                    </button>
                </h2>
                <div id="collapse${id}" class="accordion-collapse collapse ${show ? 'show' : ''}" aria-labelledby="heading${id}" data-bs-parent="#output-accordion">
                    <div class="accordion-body">
                        ${contentHtml}
                    </div>
                </div>
            </div>
        `;
        return accordionItem;
    }

    let sectionCounter = 0;

    // Personal Information
    if (data.personal_info) {
        const info = data.personal_info;
        let content = `
            ${info.name ? `<p><strong>Name:</strong> ${info.name} ${createCopyButton(info.name, 'Copy Name')}</p>` : ''}
            ${info.email ? `<p><strong>Email:</strong> ${info.email} ${createCopyButton(info.email, 'Copy Email')}</p>` : ''}
            ${info.phone ? `<p><strong>Phone:</strong> ${info.phone} ${createCopyButton(info.phone, 'Copy Phone')}</p>` : ''}
        `;

        if (info.social_links && Object.keys(info.social_links).length > 0) {
            content += `<p><strong>Social Links:</strong></p>`;
            for (const [platform, url] of Object.entries(info.social_links)) {
                content += `<p>• <a href="${url}" target="_blank">${platform}</a> ${createCopyButton(url, 'Copy Link')}</p>`;
            }
        }

        outputAccordion.insertAdjacentHTML('beforeend', createAccordionItem(`Personal${sectionCounter++}`, 'Personal Information', content, true));
    }

    // Education
    if (data.education && data.education.length > 0) {
        let content = '';
        data.education.forEach(edu => {
            const eduText = edu.degree || edu.field || edu.institution || edu;
            content += `<p>• ${eduText} ${createCopyButton(eduText, 'Copy Education')}</p>`;
        });
        outputAccordion.insertAdjacentHTML('beforeend', createAccordionItem(`Education${sectionCounter++}`, 'Education', content));
    }

    // Experience
    if (data.experience && data.experience.length > 0) {
        let content = '';
        data.experience.forEach(exp => {
            let expText = '';
            if (exp.company) expText += ` ${exp.company}`; // Add space before company
            if (exp.position) expText += `, ${exp.position}`; // Add comma and space
            if (exp.duration) expText += ` (${exp.duration})`; // Add space and parentheses
            if (exp.description) expText += `: ${exp.description}`;
            if (typeof exp === 'string') expText = exp;

            content += `<div class="mb-3">`;
            if (exp.company) content += `<strong>${exp.company}</strong><br>`;
            if (exp.position) content += `<em>${exp.position}</em><br>`;
            if (exp.duration) content += `<small>${exp.duration}</small><br>`;
            if (exp.description) content += `<p>${exp.description}</p>`;
            if (typeof exp === 'string') content += `<p>${exp}</p>`;
            content += `${createCopyButton(expText.trim(), 'Copy Experience')}</div>`; // Add copy button here
        });
        outputAccordion.insertAdjacentHTML('beforeend', createAccordionItem(`Experience${sectionCounter++}`, 'Work Experience', content));
    }

    // Skills
    if (data.skills && data.skills.length > 0) {
        let content = '';
        data.skills.forEach(skill => {
            content += `<span class="badge bg-primary me-2 mb-2">${skill} ${createCopyButton(skill, 'Copy Skill')}</span>`;
        });
        outputAccordion.insertAdjacentHTML('beforeend', createAccordionItem(`Skills${sectionCounter++}`, 'Skills', content));
    }

    // Certifications
    if (data.certifications && data.certifications.length > 0) {
        let content = '';
        data.certifications.forEach(cert => {
            content += `<p>• ${cert} ${createCopyButton(cert, 'Copy Certification')}</p>`;
        });
        outputAccordion.insertAdjacentHTML('beforeend', createAccordionItem(`Certifications${sectionCounter++}`, 'Certifications', content));
    }

    // Awards
    if (data.awards && data.awards.length > 0) {
        let content = '';
        data.awards.forEach(award => {
            content += `<p>• ${award} ${createCopyButton(award, 'Copy Award')}</p>`;
        });
        outputAccordion.insertAdjacentHTML('beforeend', createAccordionItem(`Awards${sectionCounter++}`, 'Awards', content));
    }

    // Helper function to create a copy button
    function createCopyButton(textToCopy, tooltipText = 'Copy') {
        return `
            <span class="copy-icon ms-2" style="cursor: pointer;" title="${tooltipText}" data-bs-toggle="tooltip" data-bs-placement="top" data-text-to-copy="${textToCopy.replace(/"/g, '&quot;')}">
                <i class="fas fa-copy"></i>
            </span>
        `;
    }

    // Initialize tooltips after content is added (or re-added)
    // This needs to be called after outputAccordion.insertAdjacentHTML
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        })
    }

    // Add event listeners for copy buttons
    function addCopyButtonListeners() {
        // Prevent duplicate listeners by replacing each .copy-icon with a fresh clone (removes previous listeners)
        document.querySelectorAll('.copy-icon').forEach(orig => {
            const clone = orig.cloneNode(true);
            orig.parentNode.replaceChild(clone, orig);
        });

        // Attach listeners to the fresh clones
        document.querySelectorAll('.copy-icon').forEach(button => {
            button.addEventListener('click', async (event) => {
                const textToCopy = event.currentTarget.dataset.textToCopy;

                // Try clipboard write first; only after success do non-critical UI updates.
                try {
                    await navigator.clipboard.writeText(textToCopy);
                    showToast('Copied to clipboard!', 'success', 2000);
                } catch (err) {
                    console.error('Failed to copy: ', err);
                    showToast('Failed to copy to clipboard.', 'danger');
                    return; // stop here — don't run tooltip code if clipboard failed
                }

                // Non-critical UI updates (tooltip/title) — keep in its own try/catch so they don't trigger failure toast
                try {
                    const originalTitle = event.currentTarget.title;
                    event.currentTarget.title = 'Copied!';
                    // Using getInstance may return null; guard it
                    const tooltip = bootstrap ? bootstrap.Tooltip.getInstance(event.currentTarget) : null;
                    if (tooltip) tooltip.hide();
                    setTimeout(() => {
                        event.currentTarget.title = originalTitle;
                        if (tooltip) tooltip.show();
                    }, 1000);
                } catch (uiErr) {
                    // ignore tooltip-related errors — they must not make the user think copy failed
                    console.warn('Tooltip update failed (ignored):', uiErr);
                }
            });
        });
    }


    // If no data found at all
    if (outputAccordion.innerHTML === '') {
        outputAccordion.innerHTML = `
            <div class="alert alert-info text-center animate__animated animate__fadeIn">
                <h4><i class="fas fa-info-circle"></i> No Sections Found</h4>
                <p>The parser could not extract any recognizable sections from the uploaded resume.</p>
                <p>Please try uploading a different resume or ensure it's clearly formatted.</p>
            </div>`;
    } else {
        // If data was successfully loaded, initialize tooltips and add copy button listeners
        initializeTooltips();
        addCopyButtonListeners();

        // Get download buttons
        const downloadJsonBtn = document.getElementById('download-json-btn');
        const downloadPdfBtn = document.getElementById('download-pdf-btn');

        // Store the parsed data globally or pass it for download functions
        window.parsedResumeData = data; 

        // Download JSON
        downloadJsonBtn.addEventListener('click', () => {
            if (!window.parsedResumeData) {
                showToast('No data to download.', 'warning');
                return;
            }
            const jsonString = JSON.stringify(window.parsedResumeData, null, 2);
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'parsed_resume.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast('JSON downloaded!', 'success', 2000);
        });

        // Download PDF
        downloadPdfBtn.addEventListener('click', async () => {
            if (!window.parsedResumeData) {
                showToast('No data to download.', 'warning');
                return;
            }
            showToast('Generating PDF...', 'info', 3000);
            try {
                const response = await fetch('/download_pdf', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(window.parsedResumeData),
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`PDF generation failed: ${response.status} ${response.statusText} - ${errorText}`);
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'parsed_resume.pdf';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                showToast('PDF downloaded!', 'success', 2000);

            } catch (error) {
                console.error('PDF download error:', error);
                showToast(`PDF download failed: ${error.message}`, 'danger');
            }
        });
    }
}
