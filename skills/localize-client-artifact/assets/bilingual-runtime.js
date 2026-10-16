(() => {
  "use strict";

  const config = window.__CLIENT_LOCALIZATION__;
  if (!config || !config.messages) return;

  const sourceLocale = config.sourceLocale || config.source_locale || "en";
  const configuredLocales = Array.isArray(config.locales) ? config.locales : Object.keys(config.locales || {});
  const targetLocales = config.targetLocales || config.target_locales || [];
  const supported = [...new Set(configuredLocales.length ? configuredLocales : [sourceLocale, ...targetLocales])];
  if (!supported.length) return;
  const requestedFallback = config.fallbackLocale || config.fallback_locale;
  const requestedDefault = config.defaultLocale || config.default_locale;
  const fallbackLocale = supported.includes(requestedFallback) ? requestedFallback : sourceLocale;
  const configuredDefault = supported.includes(requestedDefault) ? requestedDefault : fallbackLocale;
  const storageKey = config.storageKey || config.storage_key || "client-artifact-language";
  let locale = configuredDefault;

  function safeStoredLocale() {
    try {
      const value = window.localStorage.getItem(storageKey);
      return supported.includes(value) ? value : null;
    } catch (_error) {
      return null;
    }
  }

  function persistLocale(value) {
    try {
      window.localStorage.setItem(storageKey, value);
    } catch (_error) {
      // Storage is optional; the configured default remains a complete fallback.
    }
  }

  function interpolate(value, parameters = {}) {
    return String(value).replace(/\{([A-Za-z0-9_.-]+)\}/g, (match, key) => (
      Object.prototype.hasOwnProperty.call(parameters, key) ? String(parameters[key]) : match
    ));
  }

  function messageValue(key, requestedLocale = locale) {
    const message = config.messages[key];
    if (!message) return null;
    if (typeof message === "string") return message;
    if (typeof message.source === "string" && message.translations) {
      return requestedLocale === sourceLocale ? message.source : (message.translations[requestedLocale] ?? message.source);
    }
    return message[requestedLocale] ?? message[fallbackLocale] ?? null;
  }

  function t(key, parameters = {}, requestedLocale = locale) {
    const value = messageValue(key, requestedLocale);
    return value == null ? key : interpolate(value, parameters);
  }

  function attributeBindings(element) {
    const value = element.getAttribute("data-i18n-attr") || "";
    return value.split(",").map((item) => item.trim()).filter(Boolean).map((item) => {
      const separator = item.indexOf(":");
      return separator > 0 ? [item.slice(0, separator).trim(), item.slice(separator + 1).trim()] : [];
    }).filter((item) => item.length === 2 && item[0] && item[1]);
  }

  function applyElement(element) {
    const key = element.getAttribute("data-i18n");
    if (key) {
      const value = messageValue(key);
      if (value != null) element.textContent = value;
    }
    attributeBindings(element).forEach(([attribute, attributeKey]) => {
      const value = messageValue(attributeKey);
      if (value != null) element.setAttribute(attribute, value);
    });
  }

  function applySubtree(root = document) {
    if (root.nodeType === Node.ELEMENT_NODE) applyElement(root);
    root.querySelectorAll?.("[data-i18n],[data-i18n-attr]").forEach(applyElement);
    const titleKey = config.document?.titleKey;
    if (titleKey) document.title = t(titleKey);
    const descriptionKey = config.document?.descriptionKey;
    const description = document.querySelector('meta[name="description"]');
    if (descriptionKey && description) description.setAttribute("content", t(descriptionKey));
  }

  function syncControl() {
    document.querySelectorAll("[data-localization-locale]").forEach((button) => {
      const active = button.dataset.localizationLocale === locale;
      button.classList.toggle("active", active);
      button.setAttribute("aria-checked", String(active));
      button.setAttribute("tabindex", active ? "0" : "-1");
    });
  }

  function setLocale(nextLocale, options = {}) {
    if (!supported.includes(nextLocale)) return false;
    locale = nextLocale;
    document.documentElement.lang = locale;
    applySubtree(document);
    syncControl();
    if (options.persist !== false) persistLocale(locale);
    window.dispatchEvent(new CustomEvent("client-artifact-language-change", {
      detail: {locale, previousLocale: options.previousLocale || null},
    }));
    return true;
  }

  function moveSelection(buttons, currentIndex, direction) {
    const nextIndex = (currentIndex + direction + buttons.length) % buttons.length;
    const next = buttons[nextIndex];
    next.focus();
    setLocale(next.dataset.localizationLocale, {previousLocale: locale});
  }

  document.querySelectorAll("[data-localization-locale]").forEach((button) => {
    button.addEventListener("click", () => {
      setLocale(button.dataset.localizationLocale, {previousLocale: locale});
    });
  });

  document.querySelectorAll(".language-switch,[data-localization-switch]").forEach((group) => {
    group.addEventListener("keydown", (event) => {
      const buttons = [...group.querySelectorAll("[data-localization-locale]")];
      if (!buttons.length) return;
      const currentIndex = Math.max(0, buttons.indexOf(document.activeElement));
      if (["ArrowRight", "ArrowDown"].includes(event.key)) {
        event.preventDefault();
        moveSelection(buttons, currentIndex, 1);
      } else if (["ArrowLeft", "ArrowUp"].includes(event.key)) {
        event.preventDefault();
        moveSelection(buttons, currentIndex, -1);
      } else if (event.key === "Home" || event.key === "End") {
        event.preventDefault();
        const next = event.key === "Home" ? buttons[0] : buttons[buttons.length - 1];
        next.focus();
        setLocale(next.dataset.localizationLocale, {previousLocale: locale});
      }
    });
  });

  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => mutation.addedNodes.forEach((node) => {
      if (node.nodeType === Node.ELEMENT_NODE) applySubtree(node);
    }));
  });
  observer.observe(document.documentElement, {childList: true, subtree: true});

  window.ClientArtifactLocalization = {
    getLocale: () => locale,
    setLocale: (nextLocale) => setLocale(nextLocale, {previousLocale: locale}),
    t,
    refresh: () => applySubtree(document),
  };

  setLocale(safeStoredLocale() || configuredDefault, {persist: false});
})();
