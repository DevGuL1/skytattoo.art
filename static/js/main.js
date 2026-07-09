/* Skytattoo.art — front-end interactions
   - sticky navbar state
   - mobile menu toggle
   - GSAP scroll reveals + hero animation
   (Portfolio filtering lives inline on the pages that use Isotope.)
*/
(function () {
  "use strict";

  /* ----- Sticky navbar background on scroll ----- */
  const navbar = document.getElementById("navbar");
  const onScroll = () => {
    if (!navbar) return;
    navbar.classList.toggle("scrolled", window.scrollY > 40);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ----- Mobile menu ----- */
  const burger = document.getElementById("burger");
  const menu = document.getElementById("mobile-menu");
  if (burger && menu) {
    burger.addEventListener("click", () => menu.classList.toggle("hidden"));
  }

  /* ----- GSAP animations ----- */
  if (window.gsap) {
    if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

    // Hero intro timeline.
    const hero = document.querySelector("[data-hero]");
    if (hero) {
      const playHeroAnim = () => {
        const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
        tl.from("[data-hero-eyebrow]", { y: 20, opacity: 0, duration: 0.6 })
          .from("[data-hero-title]", { y: 40, opacity: 0, duration: 0.9 }, "-=0.3")
          .from("[data-hero-sub]", { y: 20, opacity: 0, duration: 0.7 }, "-=0.5")
          .from("[data-hero-cta]", { y: 20, opacity: 0, duration: 0.6, stagger: 0.12 }, "-=0.4");
      };

      if (document.getElementById("loading-screen")) {
        window.addEventListener("loaderComplete", playHeroAnim);
      } else {
        playHeroAnim();
      }
    }

    // Generic reveal-on-scroll for anything with .reveal.
    gsap.utils.toArray(".reveal").forEach((el) => {
      gsap.to(el, {
        opacity: 1,
        y: 0,
        duration: 0.9,
        ease: "power2.out",
        scrollTrigger: {
          trigger: el,
          start: "top 85%",
          toggleActions: "play none none none",
        },
      });
    });

    // Staggered reveal for grids marked with data-reveal-grid. Using .from()
    // means the children are visible by default and only animate in.
    gsap.utils.toArray("[data-reveal-grid]").forEach((grid) => {
      gsap.from(grid.children, {
        opacity: 0,
        y: 30,
        duration: 0.7,
        ease: "power2.out",
        stagger: 0.08,
        scrollTrigger: { trigger: grid, start: "top 85%" },
      });
    });
  } else {
    // GSAP failed to load — make sure reveal content is never left hidden.
    document.querySelectorAll(".reveal").forEach((el) => {
      el.style.opacity = 1;
      el.style.transform = "none";
    });
  }
})();
