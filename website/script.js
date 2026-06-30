// Smooth-scroll handled via CSS scroll-behavior.
// Lightweight reveal-on-scroll for sections.
document.addEventListener("DOMContentLoaded", function () {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08 }
  );

  document
    .querySelectorAll(".speaker-card, .flow-step, .uni-row")
    .forEach((el) => observer.observe(el));
});
