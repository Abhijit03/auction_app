// Main application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeFormHandlers();
    initializeCountdowns();
    initializeImagePreview();
    autoCloseAlerts();
    initializeBidForms();
    initializeProductInteractions();
    initializeSearch();
});

// Form handlers for login and registration
function initializeFormHandlers() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // Login form handling
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(loginForm);
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Signing in...';
            submitBtn.disabled = true;
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    const result = await response.text();
                    try {
                        const jsonResult = JSON.parse(result);
                        if (jsonResult.success) {
                            window.location.href = jsonResult.redirect || '/';
                        } else {
                            showFlashMessage(jsonResult.error, 'error');
                        }
                    } catch {
                        // If not JSON, assume it's HTML and let form submit normally
                        loginForm.submit();
                    }
                }
            } catch (error) {
                showFlashMessage('Login failed. Please try again.', 'error');
            } finally {
                // Reset button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Register form handling
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(registerForm);
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Validate passwords match
            const password = registerForm.querySelector('#password').value;
            const confirmPassword = registerForm.querySelector('#confirm_password').value;
            
            if (password !== confirmPassword) {
                showFlashMessage('Passwords do not match', 'error');
                return;
            }
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating account...';
            submitBtn.disabled = true;
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    const result = await response.text();
                    try {
                        const jsonResult = JSON.parse(result);
                        if (jsonResult.success) {
                            window.location.href = jsonResult.redirect || '/';
                        } else {
                            showFlashMessage(jsonResult.error, 'error');
                        }
                    } catch {
                        // If not JSON, assume it's HTML and let form submit normally
                        registerForm.submit();
                    }
                }
            } catch (error) {
                showFlashMessage('Registration failed. Please try again.', 'error');
            } finally {
                // Reset button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }
}

// Bid form handling with Indian Rupees
function initializeBidForms() {
    const bidForms = document.querySelectorAll('form[id="bidForm"]');
    
    bidForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Placing Bid...';
            submitBtn.disabled = true;
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showFlashMessage(result.message, 'success');
                    
                    // Update price display with Indian Rupees
                    const priceElement = document.querySelector('.price-section .h2');
                    if (priceElement) {
                        priceElement.textContent = `₹${result.new_price.toFixed(2)}`;
                        priceElement.classList.add('price-change');
                        setTimeout(() => priceElement.classList.remove('price-change'), 1000);
                    }
                    
                    // Update current price in product cards if present
                    const currentPriceElements = document.querySelectorAll('.h5.text-primary');
                    currentPriceElements.forEach(element => {
                        if (element.textContent.includes('₹')) {
                            element.textContent = `₹${result.new_price.toFixed(2)}`;
                        }
                    });
                    
                    // Update bid count
                    const bidCountElement = document.querySelector('.price-section .text-muted');
                    if (bidCountElement && bidCountElement.textContent.includes('bids')) {
                        bidCountElement.textContent = `${result.bid_count} bids placed`;
                    }
                    
                    // Update bid history
                    updateBidHistory(result.new_price);
                    
                    // Reset form with new minimum bid
                    const bidInput = form.querySelector('#bidAmount');
                    if (bidInput) {
                        bidInput.min = result.new_price + 1;
                        bidInput.value = result.new_price + 1;
                        // Update the minimum bid text
                        const minBidText = form.querySelector('.form-text');
                        if (minBidText) {
                            minBidText.textContent = `Minimum bid: ₹${(result.new_price + 1).toFixed(2)}`;
                        }
                    }
                } else {
                    showFlashMessage(result.error, 'error');
                }
            } catch (error) {
                showFlashMessage('Error placing bid. Please try again.', 'error');
            } finally {
                // Reset button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    });
}

// Update bid history dynamically
function updateBidHistory(newPrice) {
    const bidHistory = document.querySelector('.list-group-flush');
    if (bidHistory) {
        // Create new bid entry
        const newBidItem = document.createElement('div');
        newBidItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        newBidItem.innerHTML = `
            <div>
                <strong>₹${newPrice.toFixed(2)}</strong>
                <small class="text-muted ms-2">by You</small>
            </div>
            <small class="text-muted">Just now</small>
        `;
        
        // Add to top of bid history
        bidHistory.insertBefore(newBidItem, bidHistory.firstChild);
        
        // Update bid count in the header if exists
        const bidCountHeader = document.querySelector('.card-header h5');
        if (bidCountHeader) {
            const currentCount = parseInt(bidCountHeader.textContent.match(/\d+/)) || 0;
            // This would need to be updated based on actual count from server
        }
    }
}

// Image preview functionality
function initializeImagePreview() {
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!allowedTypes.includes(file.type)) {
                    showFlashMessage('Please select a valid image file (JPEG, PNG, GIF)', 'error');
                    this.value = '';
                    return;
                }
                
                // Validate file size (max 16MB)
                if (file.size > 16 * 1024 * 1024) {
                    showFlashMessage('Image size must be less than 16MB', 'error');
                    this.value = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    createImagePreview(e.target.result);
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

function createImagePreview(imageSrc) {
    let preview = document.getElementById('imagePreview');
    if (!preview) {
        preview = document.createElement('div');
        preview.id = 'imagePreview';
        preview.className = 'mt-3 text-center';
        document.getElementById('image').parentNode.appendChild(preview);
    }
    
    preview.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h6 class="card-title">Image Preview</h6>
                <img src="${imageSrc}" class="img-thumbnail mb-2" style="max-height: 200px; max-width: 100%;" alt="Preview">
                <div class="mt-2">
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeImagePreview()">
                        <i class="fas fa-times me-1"></i>Remove Image
                    </button>
                </div>
            </div>
        </div>
    `;
}

function removeImagePreview() {
    const preview = document.getElementById('imagePreview');
    const imageInput = document.getElementById('image');
    
    if (preview) preview.remove();
    if (imageInput) imageInput.value = '';
}

// Countdown timer functionality for auctions
function initializeCountdowns() {
    const countdownElements = document.querySelectorAll('.time-remaining');
    
    countdownElements.forEach(element => {
        const text = element.textContent;
        if (text.includes('left')) {
            startDynamicCountdown(element);
        }
    });
}

function startDynamicCountdown(element) {
    const text = element.textContent;
    const match = text.match(/(\d+)d\s*(\d+)h/);
    
    if (match) {
        const days = parseInt(match[1]);
        const hours = parseInt(match[2]);
        const endTime = new Date();
        endTime.setDate(endTime.getDate() + days);
        endTime.setHours(endTime.getHours() + hours);
        
        updateCountdown(element, endTime);
    }
}

function updateCountdown(element, endTime) {
    function update() {
        const now = new Date();
        const timeLeft = endTime - now;
        
        if (timeLeft <= 0) {
            element.innerHTML = '<i class="fas fa-clock me-1"></i>Auction ended';
            element.className = 'time-remaining small text-danger mb-3';
            return;
        }
        
        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        
        let timeString = '';
        if (days > 0) {
            timeString = `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            timeString = `${hours}h ${minutes}m`;
        } else {
            timeString = `${minutes}m`;
        }
        
        element.innerHTML = `<i class="fas fa-clock me-1"></i>${timeString} left`;
        
        // Update color based on urgency
        if (days === 0 && hours < 1) {
            element.className = 'time-remaining small text-danger mb-3';
        } else if (days === 0 && hours < 24) {
            element.className = 'time-remaining small text-warning mb-3';
        } else {
            element.className = 'time-remaining small text-success mb-3';
        }
    }
    
    update();
    const interval = setInterval(update, 60000); // Update every minute
    
    // Store interval ID on element for cleanup
    element.dataset.countdownInterval = interval;
}

// Clean up countdown intervals when leaving page
window.addEventListener('beforeunload', function() {
    const countdownElements = document.querySelectorAll('.time-remaining');
    countdownElements.forEach(element => {
        const intervalId = element.dataset.countdownInterval;
        if (intervalId) {
            clearInterval(intervalId);
        }
    });
});

// Flash message functionality
function showFlashMessage(message, type = 'info') {
    // Remove existing custom flash messages
    const existingMessages = document.querySelectorAll('.custom-flash-message');
    existingMessages.forEach(msg => msg.remove());
    
    const alertClass = type === 'error' ? 'danger' : type;
    const iconClass = type === 'error' ? 'exclamation-triangle' : 
                     type === 'success' ? 'check-circle' : 'info-circle';
    
    const flashMessage = document.createElement('div');
    flashMessage.className = `alert alert-${alertClass} alert-dismissible fade show custom-flash-message`;
    flashMessage.innerHTML = `
        <i class="fas fa-${iconClass} me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main content
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(flashMessage, main.firstChild);
    } else {
        document.body.insertBefore(flashMessage, document.body.firstChild);
    }
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (flashMessage.parentNode) {
            const bsAlert = new bootstrap.Alert(flashMessage);
            bsAlert.close();
        }
    }, 5000);
}

// Auto-close Bootstrap alerts
function autoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.custom-flash-message)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

// Product card interactions
function initializeProductInteractions() {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        // Add click animation
        card.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' || e.target.closest('a')) return;
            
            const link = this.querySelector('a.btn');
            if (link) {
                link.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    link.style.transform = '';
                }, 150);
            }
        });
        
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
}

// Search and filter functionality
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            filterProducts(e.target.value, categoryFilter ? categoryFilter.value : '');
        }, 300));
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function(e) {
            filterProducts(searchInput ? searchInput.value : '', e.target.value);
        });
    }
}

function filterProducts(searchTerm, category) {
    const productCards = document.querySelectorAll('.product-card');
    let visibleCount = 0;
    
    productCards.forEach(card => {
        const productName = card.querySelector('.card-title').textContent.toLowerCase();
        const productDescription = card.querySelector('.card-text').textContent.toLowerCase();
        const productCategory = card.querySelector('.text-muted:last-child')?.textContent.toLowerCase() || '';
        
        const matchesSearch = !searchTerm || 
                            productName.includes(searchTerm.toLowerCase()) || 
                            productDescription.includes(searchTerm.toLowerCase());
        
        const matchesCategory = !category || productCategory.includes(category.toLowerCase());
        
        if (matchesSearch && matchesCategory) {
            card.style.display = '';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show "no results" message if needed
    const noResults = document.getElementById('noResults');
    if (noResults) {
        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Price formatting for Indian Rupees
function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(price);
}

// Initialize all product cards
document.addEventListener('DOMContentLoaded', function() {
    initializeProductInteractions();
    initializeSearch();
});

// Export functions for global access
window.removeImagePreview = removeImagePreview;
window.showFlashMessage = showFlashMessage;
window.formatPrice = formatPrice;