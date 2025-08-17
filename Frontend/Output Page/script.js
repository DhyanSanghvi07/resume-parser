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
        console.error(err);
        document.getElementById("output").innerHTML = `
            <div class="alert alert-warning">
                <h4>No Resume Data Available</h4>
                <p>Please go back to the <a href="../Home Page/index.html">Home Page</a> and upload a resume first.</p>
            </div>`;
    });

function displayResumeData(data) {
    const outputElement = document.getElementById("output");
    
    let html = `
        <div class="card p-4 shadow-sm animate__animated animate__fadeIn">
            <h2 class="mb-3 text-primary">Parsed Resume Output</h2>
    `;

    // Personal Information
    if (data.personal_info) {
        const info = data.personal_info;
        html += `
            <h4 class="text-secondary">Personal Information</h4>
            ${info.name ? `<p><strong>Name:</strong> ${info.name}</p>` : ''}
            ${info.email ? `<p><strong>Email:</strong> ${info.email}</p>` : ''}
            ${info.phone ? `<p><strong>Phone:</strong> ${info.phone}</p>` : ''}
            ${info.location || info.address ? `<p><strong>Location:</strong> ${info.location || info.address}</p>` : ''}
            <hr>
        `;
    }

    // Education
    if (data.education && data.education.length > 0) {
        html += `<h4 class="text-secondary">Education</h4>`;
        data.education.forEach(edu => {
            html += `<p>• ${edu.degree || edu.field || edu.institution || edu}</p>`;
        });
        html += `<hr>`;
    }

    // Experience
    if (data.experience && data.experience.length > 0) {
        html += `<h4 class="text-secondary">Work Experience</h4>`;
        data.experience.forEach(exp => {
            html += `<div class="mb-3">`;
            if (exp.company) html += `<strong>${exp.company}</strong><br>`;
            if (exp.position) html += `<em>${exp.position}</em><br>`;
            if (exp.duration) html += `<small>${exp.duration}</small><br>`;
            if (exp.description) html += `<p>${exp.description}</p>`;
            if (typeof exp === 'string') html += `<p>${exp}</p>`;
            html += `</div>`;
        });
        html += `<hr>`;
    }

    // Skills
    if (data.skills && data.skills.length > 0) {
        html += `<h4 class="text-secondary">Skills</h4>`;
        data.skills.forEach(skill => {
            html += `<span class="badge bg-primary me-2 mb-2">${skill}</span>`;
        });
        html += `<hr>`;
    }

    // Certifications
    if (data.certifications && data.certifications.length > 0) {
        html += `<h4 class="text-secondary">Certifications</h4>`;
        data.certifications.forEach(cert => {
            html += `<p>• ${cert}</p>`;
        });
        html += `<hr>`;
    }

    // Awards
    if (data.awards && data.awards.length > 0) {
        html += `<h4 class="text-secondary">Awards</h4>`;
        data.awards.forEach(award => {
            html += `<p>• ${award}</p>`;
        });
    }

    html += `</div>`;
    outputElement.innerHTML = html;
}
