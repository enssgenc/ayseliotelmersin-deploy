/* Ayseli Hotel: mount the official Reseliva widget after React hydration. */
(() => {
  "use strict";
  const bookingUrl = "https://www.reseliva.com/booknow/Ayseli-Otel/?lang=tr";

  function enhanceWidget() {
    const root = document.getElementById("reseliva-widget");
    const form = root?.querySelector("form");
    if (!form || form.dataset.ayseliReady) return;
    form.dataset.ayseliReady = "true";
    // Keep the destination fixed to the hotel's HTTPS booking page.
    form.action = "https://www.reseliva.com/booknow/Ayseli-Otel/";

    for (const [id, text] of [["pCheckInDate", "Giriş tarihi"], ["pCheckOutDate", "Çıkış tarihi"]]) {
      const input = root.querySelector(`#${id}`);
      const label = document.createElement("label");
      label.htmlFor = id;
      label.className = "reseliva-date-label";
      label.textContent = text;
      input.before(label);
      input.setAttribute("aria-label", text);
    }
    const guestToggle = root.querySelector("#res-div-wrap");
    guestToggle.tabIndex = 0;
    guestToggle.setAttribute("role", "button");
    guestToggle.setAttribute("aria-label", "Yetişkin sayısını seçin");
    guestToggle.setAttribute("aria-controls", "divPersons");
    guestToggle.addEventListener("keydown", event => {
      if (event.target !== guestToggle) return;
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        guestToggle.click();
      }
    });
    const panel = root.querySelector("#divPersons");
    panel.style.display = "none";
    const updateExpanded = () => guestToggle.setAttribute("aria-expanded", String(getComputedStyle(panel).display !== "none"));
    new MutationObserver(updateExpanded).observe(panel, { attributes: true, attributeFilter: ["style", "class"] });
    updateExpanded();
    root.addEventListener("keydown", event => {
      if (event.key === "Escape") {
        panel.style.display = "none";
        guestToggle.focus();
      }
    });
    const counterLabels = ["Yetişkin sayısını azalt", "Yetişkin sayısını artır", "Çocuk sayısını azalt", "Çocuk sayısını artır"];
    root.querySelectorAll(".res-btn-sm").forEach((button, index) => button.setAttribute("aria-label", counterLabels[index]));

    form.addEventListener("submit", event => {
      const parseDate = value => {
        const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(value);
        if (!match) return null;
        const date = new Date(Number(match[3]), Number(match[2]) - 1, Number(match[1]));
        return date.getFullYear() === Number(match[3]) && date.getMonth() === Number(match[2]) - 1 && date.getDate() === Number(match[1]) ? date : null;
      };
      const checkIn = parseDate(form.elements.pCheckInDate.value);
      const checkOut = parseDate(form.elements.pCheckOutDate.value);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const error = document.getElementById("reseliva-error");
      if (!checkIn || !checkOut || checkIn < today || checkOut <= checkIn) {
        event.preventDefault();
        error.textContent = "Lütfen bugünden itibaren bir giriş ve girişten sonraki bir çıkış tarihi seçin.";
        root.querySelector(checkIn && checkIn >= today ? "#pCheckOutDate" : "#pCheckInDate").focus();
        return;
      }
      error.textContent = "";
    });
  }

  window.ayseliMountReseliva = () => {
    if (!document.getElementById("reseliva-widget") || document.getElementById("reseliva_widget")) return;
    window.RW = {
      type: "bar",
      hotelUrl: ["Ayseli-Otel"],
      lang: "tr",
      currency: "TRY",
      // This hotel's current engine resets any search with children to 2 people.
      // Keep family enquiries on the explicit hotel contact link until configured.
      maxChild: 0,
      method: "GET",
      target: "_self",
      buttonLabel: "FİYATLARI GÖR",
      btnBgColor: "#264b3c",
      btnFontColor: "#ffffff"
    };
    const script = document.createElement("script");
    script.id = "reseliva_widget";
    script.src = "https://www.reseliva.com/ReselivaWidget/JS/rw_script.js";
    script.onload = enhanceWidget;
    script.onerror = () => {
      const error = document.getElementById("reseliva-error");
      error.textContent = "Rezervasyon kutucuğu yüklenemedi. Rezervasyon ekranını bağlantıdan açabilirsiniz.";
      document.getElementById("reseliva-direct-link").href = bookingUrl;
    };
    document.head.appendChild(script);
  };
})();
