const toggleBtn = document.getElementById("theme-toggle");
const icon = toggleBtn.querySelector("i");
const body = document.body;

if (localStorage.getItem("theme") === "dark") {
  body.classList.add("dark-mode");
  body.classList.remove("light-mode");
  icon.classList.remove("fa-moon");
  icon.classList.add("fa-sun");
}

toggleBtn.addEventListener("click", () => {
  const isDark = body.classList.toggle("dark-mode");
  body.classList.toggle("light-mode");
  icon.classList.toggle("fa-sun", isDark);
  icon.classList.toggle("fa-moon", !isDark);
  localStorage.setItem("theme", isDark ? "dark" : "light");
});

// Fetch with retry
async function fetchWithRetry(url, retries = 3, delay = 500) {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      if (i < retries - 1) {
        await new Promise((resolve) =>
          setTimeout(resolve, delay * Math.pow(2, i))
        );
      } else {
        throw err;
      }
    }
  }
}

// Load and display parsed resume data
fetchWithRetry("/output.json")
  .then((data) => {
    displayResumeData(data);
  })
  .catch((err) => {
    console.error("Error loading output data:", err);
    document.getElementById("output").innerHTML = `
      <div class="text-center p-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 fw-semibold">Loading parsed resume data...</p>
      </div>`;
    showToast(
      "No parsed data available. Please upload a resume first.",
      "warning"
    );
  });

// Toast notification function
function showToast(message, type = "info", delay = 5000) {
  const toastContainer = document.querySelector(".toast-container");
  const toastId = `toast-${Date.now()}`;

  const toastHtml = `
    <div id="${toastId}" 
         class="toast align-items-center text-white bg-${type} border-0 shadow-sm" 
         role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <i class="fas fa-info-circle me-2"></i> ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  toastContainer.insertAdjacentHTML("beforeend", toastHtml);
  const toastEl = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastEl, { delay: delay });
  toast.show();

  toastEl.addEventListener("hidden.bs.toast", () => {
    toastEl.remove();
  });
}

// Display Resume Data
function displayResumeData(data) {
  const outputAccordion = document.getElementById("output-accordion");
  outputAccordion.innerHTML = "";

  // Accordion wrapper
  function createAccordionItem(id, title, contentHtml, show = false) {
    return `
      <div class="accordion-item rounded-3 shadow-sm mb-3 border-0">
        <h2 class="accordion-header" id="heading${id}">
          <button class="accordion-button ${
            show ? "" : "collapsed"
          } fw-semibold" 
                  type="button" data-bs-toggle="collapse" 
                  data-bs-target="#collapse${id}" 
                  aria-expanded="${show}" aria-controls="collapse${id}">
            ${title}
          </button>
        </h2>
        <div id="collapse${id}" 
             class="accordion-collapse collapse ${show ? "show" : ""}" 
             aria-labelledby="heading${id}" data-bs-parent="#output-accordion">
          <div class="accordion-body">
            ${contentHtml}
          </div>
        </div>
      </div>
    `;
  }

  let sectionCounter = 0;

  // Personal Info
  if (data.personal_info) {
    const info = data.personal_info;
    let content = `
      ${
        info.name
          ? `<p><i class="fas fa-user me-2 text-primary"></i><strong>Name:</strong> ${info.name}</p>`
          : ""
      }
      ${
        info.email
          ? `<p><i class="fas fa-envelope me-2 text-danger"></i><strong>Email:</strong> ${info.email}</p>`
          : ""
      }
      ${
        info.phone
          ? `<p><i class="fas fa-phone me-2 text-success"></i><strong>Phone:</strong> ${info.phone}</p>`
          : ""
      }
    `;

    if (info.social_links && Object.keys(info.social_links).length > 0) {
      content += `<p><i class="fas fa-link me-2 text-warning"></i><strong>Social Links:</strong></p>`;
      content += `<div class="d-flex flex-wrap gap-2">`;
      for (const [platform, url] of Object.entries(info.social_links)) {
        content += `
          <a href="${url}" target="_blank" class="btn btn-outline-primary btn-sm d-flex align-items-center">
            <i class="fab fa-${platform.toLowerCase()} me-1"></i> ${platform}
          </a>
        `;
      }
      content += `</div>`;
    }

    outputAccordion.insertAdjacentHTML(
      "beforeend",
      createAccordionItem(
        `Personal${sectionCounter++}`,
        '<i class="fas fa-id-card me-2"></i>Personal Information',
        content,
        true
      )
    );
  }

  // Education
  if (data.education && data.education.length > 0) {
    let content = "";

    // Reverse to show latest first
    [...data.education].reverse().forEach((edu) => {
      content += `
      <div class="mb-3 p-3 border rounded shadow-sm d-flex justify-content-between align-items-center">
        <div>
          ${
            edu.degree && edu.degree !== "N/A"
              ? `
            <h6 class="fw-bold text-success mb-1">
              <i class="fas fa-graduation-cap me-2"></i>${edu.degree}
            </h6>`
              : ""
          }

          ${
            edu.university && edu.university !== "N/A"
              ? `
            <p class="mb-0"><i class="fas fa-university me-2 text-primary"></i>${edu.university}</p>`
              : ""
          }

          ${
            edu.grade && edu.grade !== "N/A"
              ? `
            <p class="mb-0"><i class="fas fa-star me-2 text-info"></i>${edu.grade}</p>`
              : ""
          }
        </div>
        
        ${
          edu.years && edu.years !== "N/A"
            ? `
        <div class="text-end">
          <span class="badge bg-light text-dark border">
            <i class="fas fa-calendar-alt me-1 text-warning"></i>${edu.years}
          </span>
        </div>`
            : ""
        }
      </div>
    `;
    });

    outputAccordion.insertAdjacentHTML(
      "beforeend",
      createAccordionItem(
        `Education${sectionCounter++}`,
        '<i class="fas fa-book me-2"></i>Education',
        content
      )
    );
  }

  // Experience
  if (data.experience && data.experience.length > 0) {
    let content = "";
    data.experience.forEach((exp) => {
      content += `<div class="mb-3 p-3 border rounded bg-light">`;

      // Role
      if (exp.role)
        content += `<strong><i class="fas fa-user-tie me-2 text-primary"></i>${exp.role}</strong><br>`;

      // Company and Duration
      let companyDuration = "";
      if (exp.company) companyDuration += exp.company;
      if (exp.duration && exp.duration !== "Not Found")
        companyDuration += ` (${exp.duration})`;
      if (companyDuration)
        content += `<em><i class="fas fa-building me-2"></i>${companyDuration}</em><br>`;

      // Responsibilities
      if (exp.responsibilities && exp.responsibilities.length > 0) {
        content += `<ul class="mt-2">`;
        exp.responsibilities.forEach((res) => {
          content += `<li>${res}</li>`;
        });
        content += `</ul>`;
      }

      content += `</div>`;
    });

    outputAccordion.insertAdjacentHTML(
      "beforeend",
      createAccordionItem(
        `Experience${sectionCounter++}`,
        '<i class="fas fa-briefcase me-2"></i>Work Experience',
        content
      )
    );
  }

  // Skills
  if (data.skills && data.skills.length > 0) {
    let content = "";
    data.skills.forEach((skill) => {
      content += `<span class="badge bg-gradient bg-primary text-light me-2 mb-2 shadow-sm">
        <i class="fas fa-check-circle me-1"></i>${skill}
      </span>`;
    });
    outputAccordion.insertAdjacentHTML(
      "beforeend",
      createAccordionItem(
        `Skills${sectionCounter++}`,
        '<i class="fas fa-tools me-2"></i>Skills',
        content
      )
    );
  }

  // Certifications
  if (data.certifications && data.certifications.length > 0) {
    let content = "";
    data.certifications.forEach((cert) => {
      content += `<p><i class="fas fa-certificate me-2 text-info"></i>${cert}</p>`;
    });
    outputAccordion.insertAdjacentHTML(
      "beforeend",
      createAccordionItem(
        `Certifications${sectionCounter++}`,
        '<i class="fas fa-award me-2"></i>Certifications',
        content
      )
    );
  }

  // Awards
  if (data.awards && data.awards.length > 0) {
    let content = "";
    data.awards.forEach((award) => {
      content += `<p><i class="fas fa-trophy me-2 text-warning"></i>${award}</p>`;
    });
    outputAccordion.insertAdjacentHTML(
      "beforeend",
      createAccordionItem(
        `Awards${sectionCounter++}`,
        '<i class="fas fa-medal me-2"></i>Awards',
        content
      )
    );
  }

  // No Data Case
  if (outputAccordion.innerHTML === "") {
    outputAccordion.innerHTML = `
      <div class="alert alert-info text-center shadow-sm animate__animated animate__fadeIn">
        <h4><i class="fas fa-info-circle me-2"></i>No Sections Found</h4>
        <p>The parser could not extract any recognizable sections from the uploaded resume.</p>
        <p>Please try uploading a different resume or ensure it's clearly formatted.</p>
      </div>`;
  } else {
    // Attach download buttons
    const downloadJsonBtn = document.getElementById("download-json-btn");
    const downloadPdfBtn = document.getElementById("download-pdf-btn");
    window.parsedResumeData = data;

    downloadJsonBtn.addEventListener("click", () => {
      if (!window.parsedResumeData) {
        showToast("No data to download.", "warning");
        return;
      }
      const jsonString = JSON.stringify(window.parsedResumeData, null, 2);
      const blob = new Blob([jsonString], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "parsed_resume.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("JSON downloaded!", "success", 2000);
    });

    downloadPdfBtn.addEventListener("click", async () => {
      if (!window.parsedResumeData) {
        showToast("No data to download.", "warning");
        return;
      }
      showToast("Generating PDF...", "info", 3000);
      try {
        const response = await fetch("/download_pdf", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(window.parsedResumeData),
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(
            `PDF generation failed: ${response.status} ${response.statusText} - ${errorText}`
          );
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "parsed_resume.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast("PDF downloaded!", "success", 2000);
      } catch (error) {
        console.error("PDF download error:", error);
        showToast(`PDF download failed: ${error.message}`, "danger");
      }
    });
  }
}
