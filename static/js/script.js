import { animate, scroll, inView, stagger } from "https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm";

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initial Hero Animations
    animate("h1", { y: [50, 0], opacity: [0, 1] }, { duration: 0.8, delay: 0.2, easing: "ease-out" });
    animate(".hero p", { y: [30, 0], opacity: [0, 1] }, { duration: 0.8, delay: 0.4, easing: "ease-out" });
    animate(".hero-actions", { y: [30, 0], opacity: [0, 1] }, { duration: 0.8, delay: 0.6, easing: "ease-out" });

    // Floating cards entrance
    animate(".card-left", { x: [-100, 0], opacity: [0, 1], rotate: [-5, 0] }, { duration: 1, delay: 0.5 });
    animate(".card-right", { x: [100, 0], opacity: [0, 1], rotate: [5, 0] }, { duration: 1, delay: 0.7 });

    // Floating animation loop (after entrance)
    setTimeout(() => {
        animate(".card-left", { y: ["-15px", "15px", "-15px"] }, { duration: 6, repeat: Infinity, ease: "easeInOut" });
        animate(".card-right", { y: ["15px", "-15px", "15px"] }, { duration: 7, repeat: Infinity, ease: "easeInOut" });
    }, 1500);

    // 2. Scroll Animations - Features Grid
    inView(".feature-card", (info) => {
        animate(info.target, { y: [100, 0], opacity: [0, 1] }, { duration: 0.6, easing: "ease-out" });
    });

    // 3. Scroll Animations - Flow Steps
    inView(".flow-step", (info) => {
        animate(info.target, { opacity: [0, 1], y: [60, 0] }, { duration: 0.8, easing: "ease-out" });
        
        // Also animate the image inside slightly
        const img = info.target.querySelector('.flow-image');
        if(img) {
            animate(img, { scale: [0.95, 1] }, { duration: 1, delay: 0.2 });
        }
    }, { margin: "-100px" });

    // 4. Tech Stack Cards stagger
    inView(".tech-grid", (info) => {
        const cards = info.target.querySelectorAll(".tech-card");
        animate(cards, { y: [50, 0], opacity: [0, 1] }, { 
            delay: stagger(0.15),
            duration: 0.6,
            easing: "ease-out"
        });
    });

    // 5. Navbar blur background effect on scroll
    const navbar = document.querySelector(".navbar");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            navbar.style.backgroundColor = "rgba(10, 10, 10, 0.85)";
            navbar.style.boxShadow = "0 10px 30px rgba(0, 0, 0, 0.5)";
        } else {
            navbar.style.backgroundColor = "rgba(10, 10, 10, 0.5)";
            navbar.style.boxShadow = "none";
        }
    });

    // 6. Smooth Scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
