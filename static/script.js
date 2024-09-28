let translations = {};

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('certForm');
    const resultsDiv = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');
    const downloadButtons = document.getElementById('downloadButtons');
    const fileInputs = document.querySelectorAll('input[type="file"]');
    const languageSelect = document.getElementById('languageSelect');

    // Fetch translations
    fetch('/get_translations')
        .then(response => response.json())
        .then(data => {
            translations = data;
            updateFileInputs();
            updateTooltips();
        })
        .catch(error => console.error('Error fetching translations:', error));

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        if (validateForm()) {
            const formData = new FormData(this);
            
            resultContent.innerHTML = gettext('Generating certificate, please wait...');
            resultsDiv.style.display = 'block';
            downloadButtons.innerHTML = '';

            fetch('/generate', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(result => {
                if (result.success) {
                    displayResults(result.data);
                } else {
                    throw new Error(result.error || gettext('Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                let errorMessage = gettext('An error occurred while generating the certificate: ');
                errorMessage += error.message || gettext('Unknown error');
                resultContent.innerHTML = `<p style="color: red;">${errorMessage}</p>`;
                resultsDiv.style.display = 'block';
            });
        }
    });

    function validateForm() {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('error');
            } else {
                field.classList.remove('error');
            }
        });

        const durationDays = document.getElementById('durationDays');
        if (parseInt(durationDays.value) <= 0 || parseInt(durationDays.value) > 3650) {
            isValid = false;
            durationDays.classList.add('error');
        } else {
            durationDays.classList.remove('error');
        }

        return isValid;
    }

    function displayResults(result) {
        let resultText = gettext("Certificate generation successful!") + "\n\n";
        resultText += gettext("Generated files:") + "\n";
        
        let allFiles = [];
        for (const [key, value] of Object.entries(result)) {
            if (key.endsWith('_password') || key.endsWith('_alias')) {
                resultText += `${key}: ${value}\n`;
            } else {
                resultText += `${key}: ${value}\n`;
                allFiles.push(value);
            }
        }

        resultContent.innerHTML = `<pre>${resultText}</pre>`;
        downloadButtons.innerHTML = `<a href="#" id="downloadAllBtn" class="download-btn download-all-btn">${gettext('Download All Files')}</a>`;
        resultsDiv.style.display = 'block';

        document.getElementById('downloadAllBtn').addEventListener('click', function(e) {
            e.preventDefault();
            downloadAllFiles(allFiles);
        });
    }

    function downloadAllFiles(files) {
        fetch('/download_all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ files: files }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'all_certificates.zip';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
            alert(gettext('An error occurred while downloading the files.'));
        });
    }

    function updateFileInputs() {
        fileInputs.forEach(input => {
            const wrapper = input.closest('.file-upload');
            const fileNameSpan = wrapper.querySelector('.file-name');
            const button = wrapper.querySelector('.file-input-button');
            
            button.innerHTML = `<i class="fas fa-upload"></i> ${gettext('Choose File')}`;
            fileNameSpan.textContent = gettext('No file chosen');

            input.addEventListener('change', function() {
                if (this.files.length > 0) {
                    fileNameSpan.textContent = this.files[0].name;
                } else {
                    fileNameSpan.textContent = gettext('No file chosen');
                }
            });

            button.addEventListener('click', function(e) {
                e.preventDefault();
                input.click();
            });
        });
    }

    function updateTooltips() {
        const tooltips = document.querySelectorAll('.tooltip');
        tooltips.forEach(tooltip => {
            const originalText = tooltip.getAttribute('data-tooltip');
            tooltip.setAttribute('data-tooltip', gettext(originalText));
        });
    }

    languageSelect.addEventListener('change', function() {
        setLanguage(this.value);
    });
});

function gettext(message) {
    return translations[message] || message;
}

function setLanguage(lang) {
    fetch(`/set_language/${lang}`, {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
}