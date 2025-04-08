/**
 * Maharashtra Lokadhikar Samiti - Borrower Management System
 * Main JavaScript file for common functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            var alert = bootstrap.Alert.getOrCreateInstance(message);
            if (alert) {
                alert.close();
            }
        }, 5000);
    });
    
    // Sidebar toggle on mobile
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const topNavbar = document.getElementById('topNavbar');
    
    if (menuToggle && sidebar && mainContent && topNavbar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-collapsed');
            mainContent.classList.toggle('full-width');
            topNavbar.classList.toggle('full-width');
        });
        
        // Check screen size and collapse sidebar on small screens
        function checkScreenSize() {
            if (window.innerWidth < 992) {
                sidebar.classList.add('sidebar-collapsed');
                mainContent.classList.add('full-width');
                topNavbar.classList.add('full-width');
            } else {
                sidebar.classList.remove('sidebar-collapsed');
                mainContent.classList.remove('full-width');
                topNavbar.classList.remove('full-width');
            }
        }
        
        // Initial check
        checkScreenSize();
        
        // Listen for window resize
        window.addEventListener('resize', checkScreenSize);
    }
    
    // About modal
    const aboutLink = document.getElementById('about-link');
    if (aboutLink) {
        aboutLink.addEventListener('click', function(e) {
            e.preventDefault();
            const aboutModal = new bootstrap.Modal(document.getElementById('aboutModal'));
            aboutModal.show();
        });
    }
    
    // Date picker initialization for date inputs
    const dateInputs = document.querySelectorAll('.date-picker');
    dateInputs.forEach(function(input) {
        if (typeof flatpickr !== 'undefined') {
            flatpickr(input, {
                dateFormat: "Y-m-d",
                allowInput: true
            });
        }
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // Confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const previewContainer = document.querySelector('.preview-container');
            const fileName = document.getElementById('fileName');
            const fileDetails = document.getElementById('fileDetails');
            
            if (previewContainer && fileName && fileDetails && this.files.length > 0) {
                const file = this.files[0];
                
                // Update file name
                fileName.textContent = file.name;
                
                // Format file size
                let fileSize = file.size;
                let sizeText = '';
                if (fileSize < 1024) {
                    sizeText = fileSize + ' bytes';
                } else if (fileSize < 1024 * 1024) {
                    sizeText = (fileSize / 1024).toFixed(2) + ' KB';
                } else {
                    sizeText = (fileSize / (1024 * 1024)).toFixed(2) + ' MB';
                }
                
                fileDetails.textContent = sizeText + (file.type ? ' • ' + file.type : '');
                
                // Show preview container
                previewContainer.style.display = 'block';
            }
        });
    });
});