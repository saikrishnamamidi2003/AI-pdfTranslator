// PDF Translator JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Page navigation elements
    const howItWorksBtn = document.getElementById('howItWorksBtn');
    const translateBtn = document.getElementById('translateBtn');
    const getStartedBtn = document.getElementById('getStartedBtn');
    const howItWorksSection = document.getElementById('howItWorksSection');
    const translateSection = document.getElementById('translateSection');
    
    // File upload elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const removeFileBtn = document.getElementById('removeFile');
    const uploadForm = document.getElementById('uploadForm');
    
    // Language elements
    const sourceLanguage = document.getElementById('sourceLanguage');
    const targetLanguage = document.getElementById('targetLanguage');
    const swapLanguagesBtn = document.getElementById('swapLanguages');
    
    // Initialize page
    init();
    
    function init() {
        // Set up event listeners
        setupNavigation();
        setupFileUpload();
        setupLanguageHandling();
        setupFormSubmission();
        
        // Check URL hash for initial page
        const hash = window.location.hash;
        if (hash === '#translate') {
            showTranslateSection();
        } else {
            showHowItWorksSection();
        }
    }
    
    function setupNavigation() {
        howItWorksBtn.addEventListener('click', showHowItWorksSection);
        translateBtn.addEventListener('click', showTranslateSection);
        if (getStartedBtn) {
            getStartedBtn.addEventListener('click', showTranslateSection);
        }
    }
    
    function showHowItWorksSection() {
        howItWorksSection.style.display = 'block';
        translateSection.style.display = 'none';
        
        // Update button states
        howItWorksBtn.classList.add('active');
        translateBtn.classList.remove('active');
        
        // Update URL
        window.history.pushState({}, '', '#how-it-works');
    }
    
    function showTranslateSection() {
        howItWorksSection.style.display = 'none';
        translateSection.style.display = 'block';
        
        // Update button states
        howItWorksBtn.classList.remove('active');
        translateBtn.classList.add('active');
        
        // Update URL
        window.history.pushState({}, '', '#translate');
    }
    
    function setupFileUpload() {
        // Drag and drop events
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        
        // File input change
        fileInput.addEventListener('change', handleFileSelect);
        
        // Remove file button
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', removeFile);
        }
        
        // Click to upload
        uploadArea.addEventListener('click', function(e) {
            // Don't trigger if clicking on remove button
            if (e.target.closest('button')) {
                return;
            }
            if (!fileInfo.style.display || fileInfo.style.display === 'none') {
                fileInput.click();
            }
        });
    }
    
    function handleDragOver(e) {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    }
    
    function handleDragLeave(e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
    }
    
    function handleDrop(e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (validateFile(file)) {
                // Create a new DataTransfer object to properly set files
                const dt = new DataTransfer();
                dt.items.add(file);
                fileInput.files = dt.files;
                displayFileInfo(file);
            }
        }
    }
    
    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file && validateFile(file)) {
            displayFileInfo(file);
        }
    }
    
    function validateFile(file) {
        // Check file type
        if (file.type !== 'application/pdf') {
            showAlert('Please select a PDF file only.', 'error');
            return false;
        }
        
        // Check file size (16MB limit)
        const maxSize = 16 * 1024 * 1024; // 16MB in bytes
        if (file.size > maxSize) {
            showAlert('File size exceeds 16MB limit. Please choose a smaller file.', 'error');
            return false;
        }
        
        return true;
    }
    
    function displayFileInfo(file) {
        const fileName = file.name;
        const fileSize = formatFileSize(file.size);
        
        // Update file info display
        fileInfo.querySelector('.file-name').textContent = fileName;
        fileInfo.querySelector('.file-size').textContent = fileSize;
        
        // Show file info, hide upload content
        uploadArea.querySelector('.upload-content').style.display = 'none';
        fileInfo.style.display = 'block';
        
        // Change upload area appearance
        uploadArea.style.border = '2px solid #28a745';
        uploadArea.style.backgroundColor = 'rgba(40, 167, 69, 0.1)';
    }
    
    function removeFile() {
        // Reset file input
        fileInput.value = '';
        
        // Reset upload area
        uploadArea.querySelector('.upload-content').style.display = 'block';
        fileInfo.style.display = 'none';
        uploadArea.style.border = '3px dashed #dee2e6';
        uploadArea.style.backgroundColor = '';
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function setupLanguageHandling() {
        // Auto-detect common language selections
        if (sourceLanguage && targetLanguage) {
            // Set default values if available
            const userLang = navigator.language.split('-')[0];
            if (sourceLanguage.querySelector(`option[value="${userLang}"]`)) {
                sourceLanguage.value = userLang;
            }
        }
        
        // Language swap functionality
        if (swapLanguagesBtn) {
            swapLanguagesBtn.addEventListener('click', swapLanguages);
        }
        
        // Prevent same language selection
        sourceLanguage.addEventListener('change', validateLanguageSelection);
        targetLanguage.addEventListener('change', validateLanguageSelection);
    }
    
    function swapLanguages() {
        const sourceValue = sourceLanguage.value;
        const targetValue = targetLanguage.value;
        
        if (sourceValue && targetValue) {
            sourceLanguage.value = targetValue;
            targetLanguage.value = sourceValue;
            
            // Add visual feedback
            swapLanguagesBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Swapped!';
            setTimeout(() => {
                swapLanguagesBtn.innerHTML = '<i class="fas fa-exchange-alt"></i> Swap Languages';
            }, 1000);
        } else {
            showAlert('Please select both languages first.', 'warning');
        }
    }
    
    function validateLanguageSelection() {
        const sourceValue = sourceLanguage.value;
        const targetValue = targetLanguage.value;
        
        if (sourceValue && targetValue && sourceValue === targetValue) {
            showAlert('Source and target languages cannot be the same.', 'warning');
            
            // Reset the last changed select
            if (event.target === sourceLanguage) {
                sourceLanguage.value = '';
            } else {
                targetLanguage.value = '';
            }
        }
    }
    
    function setupFormSubmission() {
        if (uploadForm) {
            uploadForm.addEventListener('submit', handleFormSubmit);
        }
    }
    
    function handleFormSubmit(e) {
        e.preventDefault(); // Prevent default submission
        
        // Debug form submission
        console.log('Form submission started');
        console.log('File input files:', fileInput.files);
        console.log('File count:', fileInput.files.length);
        
        if (fileInput.files.length > 0) {
            console.log('File details:', {
                name: fileInput.files[0].name,
                size: fileInput.files[0].size,
                type: fileInput.files[0].type
            });
        }
        
        // Validate form before submission
        if (!validateForm()) {
            return false;
        }
        
        // Create FormData and manually add all form fields
        const formData = new FormData();
        
        // Add file
        if (fileInput.files[0]) {
            formData.append('file', fileInput.files[0]);
            console.log('File added to FormData:', fileInput.files[0].name);
        }
        
        // Add language selections
        formData.append('source_language', sourceLanguage.value);
        formData.append('target_language', targetLanguage.value);
        
        console.log('FormData contents:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        // Show loading state
        showLoadingState();
        showProgress();
        
        // Submit with fetch
        fetch(uploadForm.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('Response received:', response.status);
            if (response.redirected) {
                // After successful translation, refresh the history and reset form
                refreshTranslationHistory().then(() => {
                    // Reset form state immediately
                    resetFormState();
                    
                    // Show success message with download option
                    const successMessage = `
                        <div class="d-flex align-items-center justify-content-between">
                            <span>Translation completed successfully!</span>
                            <a href="${response.url}" class="btn btn-sm btn-primary ms-2">
                                <i class="fas fa-download"></i> Download Now
                            </a>
                        </div>
                    `;
                    showAlert(successMessage, 'success');
                    
                    // Clear any previous file selection
                    if (fileInput) {
                        fileInput.value = '';
                        removeFile();
                    }
                });
            } else {
                return response.text();
            }
        })
        .then(html => {
            if (html) {
                // Replace current page content
                document.open();
                document.write(html);
                document.close();
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            showAlert('An error occurred during upload. Please try again.', 'error');
            resetFormState();
        });
        
        return false;
    }
    
    function validateForm() {
        const file = fileInput.files[0];
        const source = sourceLanguage.value;
        const target = targetLanguage.value;
        
        if (!file) {
            showAlert('Please select a PDF file to upload.', 'error');
            return false;
        }
        
        if (!source) {
            showAlert('Please select a source language.', 'error');
            return false;
        }
        
        if (!target) {
            showAlert('Please select a target language.', 'error');
            return false;
        }
        
        if (source === target) {
            showAlert('Source and target languages cannot be the same.', 'error');
            return false;
        }
        
        return true;
    }
    
    function resetFormState() {
        const submitBtn = document.getElementById('translateSubmit');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-magic"></i> Translate PDF';
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-warning');
            submitBtn.classList.add('btn-success');
        }
        
        // Re-enable form inputs
        const inputs = uploadForm.querySelectorAll('input, select, button');
        inputs.forEach(input => {
            input.disabled = false;
        });
        
        // Hide progress
        const progressContainer = document.querySelector('.progress-container');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
        
        // Reset file input display
        const fileInfo = document.querySelector('.file-info');
        if (fileInfo) {
            fileInfo.style.display = 'none';
        }
        
        // Reset drag and drop area
        const dropZone = document.querySelector('.drop-zone');
        if (dropZone) {
            dropZone.classList.remove('drag-over');
            dropZone.style.display = 'block';
        }
    }
    
    function showLoadingState() {
        const submitBtn = document.getElementById('translateSubmit');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Translating...';
            submitBtn.disabled = true;
        }
        
        // Disable form inputs
        const inputs = uploadForm.querySelectorAll('input, select, button');
        inputs.forEach(input => {
            if (input !== submitBtn) {
                input.disabled = true;
            }
        });
    }
    
    function showProgress() {
        // Create progress bar if it doesn't exist
        let progressContainer = document.querySelector('.progress-container');
        if (!progressContainer) {
            progressContainer = document.createElement('div');
            progressContainer.className = 'progress-container';
            progressContainer.innerHTML = `
                <div class="progress">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
                <p class="text-center mt-2">Processing your PDF...</p>
            `;
            uploadForm.appendChild(progressContainer);
        }
        
        progressContainer.style.display = 'block';
        
        // Simulate progress
        const progressBar = progressContainer.querySelector('.progress-bar');
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            progressBar.style.width = progress + '%';
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 500);
    }
    
    function showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of translate section
        const translateCard = translateSection.querySelector('.card-body');
        translateCard.insertBefore(alertDiv, translateCard.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    function refreshTranslationHistory() {
        return fetch('/api/history', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            const historyContainer = document.querySelector('.recent-translations .list-group');
            if (historyContainer && data.history) {
                // Clear current history
                historyContainer.innerHTML = '';
                
                if (data.history.length === 0) {
                    historyContainer.innerHTML = '<div class="text-muted p-3">No recent translations</div>';
                } else {
                    // Build new history items
                    data.history.forEach(item => {
                        const historyItem = document.createElement('div');
                        historyItem.className = 'list-group-item d-flex justify-content-between align-items-start';
                        
                        // Get language names from LANGUAGES mapping if available
                        const sourceLang = getLanguageName(item.source_language);
                        const targetLang = getLanguageName(item.target_language);
                        
                        historyItem.innerHTML = `
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">${item.original_filename}</div>
                                <small class="text-muted">${sourceLang} → ${targetLang}</small>
                                <br><small class="text-muted">${item.created_at}</small>
                            </div>
                            <a href="/download/${item.translated_filename}" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-download"></i> Download
                            </a>
                        `;
                        
                        historyContainer.appendChild(historyItem);
                    });
                }
                console.log('Translation history refreshed with', data.history.length, 'items');
            }
        })
        .catch(error => {
            console.error('Failed to refresh history:', error);
        });
    }
    
    function getLanguageName(code) {
        // Basic language mapping - extend as needed
        const languages = {
            'en': 'English',
            'hi': 'Hindi', 
            'te': 'Telugu',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic'
        };
        return languages[code] || code;
    }
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', function() {
        const hash = window.location.hash;
        if (hash === '#translate') {
            showTranslateSection();
        } else {
            showHowItWorksSection();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + U for upload
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            if (translateSection.style.display !== 'none') {
                fileInput.click();
            }
        }
        
        // Escape to go back to how it works
        if (e.key === 'Escape') {
            showHowItWorksSection();
        }
    });
});
