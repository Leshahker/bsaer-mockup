document.querySelectorAll("[data-menu]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const nav = document.querySelector("nav.primary");
    const open = nav.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", String(open));
  });
});

document.querySelectorAll("[data-filters]").forEach((root) => {
  const buttons = [...root.querySelectorAll(".filter")];
  const rows = [...document.querySelectorAll("[data-type]")];
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("is-on"));
      button.classList.add("is-on");
      const type = button.dataset.filter;
      rows.forEach((row) => {
        row.hidden = type !== "all" && row.dataset.type !== type;
      });
    });
  });
});

const form = document.querySelector("[data-join-form]");
if (form) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const done = document.querySelector("[data-join-done]");
    form.hidden = true;
    if (done) done.hidden = false;
  });
}

const library = document.querySelector("[data-library]");
if (library) {
  const links = [...library.querySelectorAll("[data-section]")];
  const panels = [...library.querySelectorAll("[data-panel]")];
  const valid = new Set(links.map((link) => link.dataset.section));

  const show = (id) => {
    const section = valid.has(id) ? id : "books";
    links.forEach((link) => {
      link.classList.toggle("is-on", link.dataset.section === section);
    });
    panels.forEach((panel) => {
      panel.hidden = panel.dataset.panel !== section;
    });
    if (location.hash.replace("#", "") !== section) {
      history.replaceState(null, "", `#${section}`);
    }
  };

  links.forEach((link) => {
    link.addEventListener("click", () => show(link.dataset.section));
  });

  const fromHash = location.hash.replace("#", "");
  show(fromHash || "books");
  window.addEventListener("hashchange", () => {
    show(location.hash.replace("#", "") || "books");
  });
}
