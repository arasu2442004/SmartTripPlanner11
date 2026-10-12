/**
 * Smart Trip Planner - Client Side JavaScript
 * Enhances forms, budget steppers, chip buttons, print triggers, and mobile menus.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Navigation Toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }

    // 2. Budget Quick Chips Selection
    const budgetChips = document.querySelectorAll('.chip-btn[data-budget]');
    const budgetInput = document.getElementById('budgetInput');
    budgetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const val = chip.getAttribute('data-budget');
            if (budgetInput) {
                budgetInput.value = val;
                budgetInput.dispatchEvent(new Event('input'));
            }
        });
    });

    // 3. Starting City Quick Chips
    const cityChips = document.querySelectorAll('.chip-btn[data-city]');
    const cityInput = document.getElementById('startLocationInput');
    cityChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const city = chip.getAttribute('data-city');
            if (cityInput) {
                cityInput.value = city;
            }
        });
    });

    // 4. Steppers for Days and Travelers
    const steppers = document.querySelectorAll('.stepper-wrap');
    steppers.forEach(stepper => {
        const input = stepper.querySelector('.stepper-input');
        const minusBtn = stepper.querySelector('.stepper-minus');
        const plusBtn = stepper.querySelector('.stepper-plus');
        
        if (input && minusBtn && plusBtn) {
            const min = parseInt(input.getAttribute('min') || '1', 10);
            const max = parseInt(input.getAttribute('max') || '30', 10);

            minusBtn.addEventListener('click', (e) => {
                e.preventDefault();
                let current = parseInt(input.value || min, 10);
                if (current > min) {
                    input.value = current - 1;
                }
            });

            plusBtn.addEventListener('click', (e) => {
                e.preventDefault();
                let current = parseInt(input.value || min, 10);
                if (current < max) {
                    input.value = current + 1;
                }
            });
        }
    });

    // 5. Flash Alert Dismissal
    const alertCloses = document.querySelectorAll('.alert-close');
    alertCloses.forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 200);
            }
        });
    });

    // 6. Print Itinerary Action
    const printBtn = document.getElementById('printTripBtn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }
});
