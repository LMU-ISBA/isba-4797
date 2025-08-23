document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Intersection Observer for content sections animation
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all content sections
    document.querySelectorAll('.content-section').forEach(section => {
        observer.observe(section);
    });

    // Focus cards hover effect enhancement
    document.querySelectorAll('.focus-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Email protection with confirmation
    const emailLink = document.querySelector('.email-link');
    if (emailLink) {
        emailLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            const email = this.getAttribute('data-email');
            const confirmed = confirm(`Open email client to send message to ${email}?`);
            
            if (confirmed) {
                window.location.href = `mailto:${email}`;
            }
        });
    }

    // Add accessible skip link for keyboard navigation
    const skipLink = document.createElement('a');
    skipLink.href = '#course-description';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: var(--primary-color);
        color: white;
        padding: 8px;
        text-decoration: none;
        z-index: 1000;
        border-radius: 0 0 4px 0;
        font-weight: 600;
        transition: top 0.3s;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.top = '0px';
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);

    // Enhanced table accessibility
    document.querySelectorAll('table').forEach(table => {
        // Add table caption for screen readers
        const caption = document.createElement('caption');
        caption.textContent = table.closest('.grading-table') ? 'Grading breakdown' : 'Course schedule';
        caption.style.cssText = 'position: absolute; left: -10000px; width: 1px; height: 1px; overflow: hidden;';
        table.insertBefore(caption, table.firstChild);
        
        // Make tables more keyboard navigable
        table.setAttribute('role', 'table');
        table.querySelectorAll('th').forEach(th => {
            th.setAttribute('scope', 'col');
        });
    });

    // Add loading animation completion
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
        
        // Stagger animation of focus cards
        document.querySelectorAll('.focus-card').forEach((card, index) => {
            card.style.animationDelay = `${0.2 + (index * 0.1)}s`;
            card.style.animation = 'fadeInUp 0.6s ease forwards';
        });
    });

    // Responsive table handling
    function handleResponsiveTables() {
        const tables = document.querySelectorAll('.schedule-table table, .grading-table table');
        
        tables.forEach(table => {
            const wrapper = table.parentElement;
            
            if (window.innerWidth < 768) {
                wrapper.style.overflowX = 'auto';
                wrapper.style.webkitOverflowScrolling = 'touch';
                
                // Add scroll hint for mobile
                if (!wrapper.querySelector('.scroll-hint')) {
                    const hint = document.createElement('div');
                    hint.className = 'scroll-hint';
                    hint.textContent = '← Scroll horizontally to view all columns →';
                    hint.style.cssText = `
                        text-align: center;
                        font-size: 0.8rem;
                        color: var(--text-muted);
                        margin-top: 10px;
                        font-style: italic;
                    `;
                    wrapper.appendChild(hint);
                }
            } else {
                const hint = wrapper.querySelector('.scroll-hint');
                if (hint) {
                    hint.remove();
                }
            }
        });
    }

    // Handle responsive tables on load and resize
    handleResponsiveTables();
    window.addEventListener('resize', handleResponsiveTables);

    // Improve focus management
    document.addEventListener('keydown', function(e) {
        // Skip to main content with Alt+M
        if (e.altKey && e.key === 'm') {
            e.preventDefault();
            document.querySelector('#course-description').focus();
        }
    });

    // Add visual feedback for interactive elements
    document.querySelectorAll('a, button, .focus-card, .scale-item').forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid var(--primary-color)';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });

    // Performance optimization: Debounce resize events
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            handleResponsiveTables();
        }, 250);
    });

    // Add print preparation
    window.addEventListener('beforeprint', function() {
        // Expand any collapsed content for printing
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.opacity = '1';
            section.style.transform = 'none';
        });
    });

    // Error handling for missing elements
    function safeQuerySelector(selector, callback) {
        const element = document.querySelector(selector);
        if (element && typeof callback === 'function') {
            callback(element);
        }
    }

    // Initialize any dynamic content safely
    safeQuerySelector('.hero-question', (element) => {
        element.setAttribute('role', 'heading');
        element.setAttribute('aria-level', '1');
    });

    // Add semantic improvements
    document.querySelectorAll('.policy').forEach((policy, index) => {
        policy.setAttribute('role', 'region');
        policy.setAttribute('aria-labelledby', `policy-${index}`);
        
        const heading = policy.querySelector('h3');
        if (heading) {
            heading.id = `policy-${index}`;
        }
    });
});