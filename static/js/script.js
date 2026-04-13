document.addEventListener("DOMContentLoaded", () => {
    highlightActiveLink();
    animateCards();
    initSmoothScroll();
    initFakeToggles();
    initButtonEffects();
    initNumberHover();
});

function highlightActiveLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".nav-links a");

    navLinks.forEach(link => {
        const href = link.getAttribute("href");
        if (href === currentPath) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });
}

function animateCards() {
    const cards = document.querySelectorAll(
        ".stat-card, .mini-card, .mini-stat-card, .chart-card, .panel-card, .report-card, .insight-card, .feature-card"
    );

    cards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        card.style.transition = "all 0.5s ease";

        setTimeout(() => {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, 100 + index * 80);
    });
}

function initSmoothScroll() {
    const allLinks = document.querySelectorAll('a[href^="#"]');

    allLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            const targetId = this.getAttribute("href");
            if (targetId.length > 1) {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }
            }
        });
    });
}

function initFakeToggles() {
    const toggles = document.querySelectorAll('.switch input[type="checkbox"]');

    toggles.forEach(toggle => {
        toggle.addEventListener("change", function () {
            const settingRow = this.closest(".setting-row");
            if (settingRow) {
                settingRow.style.transition = "all 0.25s ease";
                settingRow.style.transform = "scale(0.98)";

                setTimeout(() => {
                    settingRow.style.transform = "scale(1)";
                }, 150);
            }
        });
    });
}

function initButtonEffects() {
    const buttons = document.querySelectorAll(
        ".primary-btn, .secondary-btn, .wide-btn, .send-btn, .quick-chip"
    );

    buttons.forEach(button => {
        button.addEventListener("mouseenter", () => {
            button.style.transition = "all 0.2s ease";
            button.style.transform = "translateY(-2px)";
        });

        button.addEventListener("mouseleave", () => {
            button.style.transform = "translateY(0)";
        });

        button.addEventListener("mousedown", () => {
            button.style.transform = "scale(0.98)";
        });

        button.addEventListener("mouseup", () => {
            button.style.transform = "translateY(-2px)";
        });
    });
}

function initNumberHover() {
    const valueBlocks = document.querySelectorAll(
        ".stat-card h2, .mini-stat-card h2, .result-box p, .highlight-number"
    );

    valueBlocks.forEach(block => {
        block.addEventListener("mouseenter", () => {
            block.style.transition = "all 0.2s ease";
            block.style.transform = "scale(1.03)";
        });

        block.addEventListener("mouseleave", () => {
            block.style.transform = "scale(1)";
        });
    });
}