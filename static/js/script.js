// Smart CRM - Custom JavaScript

// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Confirm delete action
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[method="POST"]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Check if form has required fields
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
});

// Phone number formatting (optional enhancement)
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // Remove all non-digit characters
            let value = e.target.value.replace(/\D/g, '');
            // Format as (XXX) XXX-XXXX if US number
            if (value.length > 6) {
                value = '(' + value.substring(0, 3) + ') ' + value.substring(3, 6) + '-' + value.substring(6, 10);
            } else if (value.length > 3) {
                value = '(' + value.substring(0, 3) + ') ' + value.substring(3);
            }
            e.target.value = value;
        });
    }
});

// Status change confirmation
document.addEventListener('DOMContentLoaded', function() {
    const statusSelects = document.querySelectorAll('.status-select');
    
    statusSelects.forEach(function(select) {
        const originalValue = select.value;
        
        select.addEventListener('change', function(e) {
            // Optional: Show confirmation for status changes
            // Uncomment if you want confirmation on status change
            /*
            if (!confirm('Are you sure you want to change the status?')) {
                e.preventDefault();
                select.value = originalValue;
                return false;
            }
            */
        });
    });
});

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add loading state to submit buttons
document.addEventListener('DOMContentLoaded', function() {
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            if (button.form && button.form.checkValidity()) {
                button.disabled = true;
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
            }
        });
    });
});
