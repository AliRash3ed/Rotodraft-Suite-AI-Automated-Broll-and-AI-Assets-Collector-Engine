/* ═══════════════════════════════════════════════════════════════
   ROTODRAFT SUITE — UNIFIED ANALYTICS & EVENT TELEMETRY ENGINE
   Supports: Google Analytics 4 (GA4), Web Vitals, Custom Conversion Tracking
   ═══════════════════════════════════════════════════════════════ */

(function() {
  'use strict';

  // Configurable GA4 ID (Defaults to local tracker; users can set window.GA_MEASUREMENT_ID)
  const GA_ID = window.GA_MEASUREMENT_ID || 'G-ROTODRAFT2026';

  // 1. Initialize Google Analytics 4 Script Dynamically
  function loadGoogleAnalytics(id) {
    if (!id || id === 'G-XXXXXXXXXX') return;
    
    // Inject gtag.js
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${id}`;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag(){ window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', id, {
      send_page_view: true,
      cookie_flags: 'SameSite=None;Secure'
    });

    console.log(`[RotoDraft Analytics] GA4 initialized with ID: ${id}`);
  }

  // 2. Universal Custom Event Dispatcher
  function trackEvent(eventName, params = {}) {
    const eventPayload = {
      event_category: params.category || 'Engagement',
      event_label: params.label || window.location.pathname,
      value: params.value || 1,
      page_title: document.title,
      page_location: window.location.href,
      timestamp: new Date().toISOString(),
      ...params
    };

    // Send to Google Analytics if available
    if (typeof window.gtag === 'function') {
      window.gtag('event', eventName, eventPayload);
    }

    // Log in local console for debugging
    console.log(`📊 [Analytics Event] ${eventName}:`, eventPayload);
  }
  window.trackEvent = trackEvent;

  // 3. Auto-Track All Interaction Elements (Buttons, Links, Downloads)
  function initAutoTracking() {
    document.addEventListener('click', (e) => {
      const target = e.target.closest('a, button, [data-track]');
      if (!target) return;

      const trackName = target.getAttribute('data-track');
      const href = target.getAttribute('href') || '';
      const text = target.innerText.trim();

      if (trackName) {
        trackEvent(trackName, { text, href });
      } else if (href.includes('github.com')) {
        trackEvent('click_github_link', { category: 'Social & Repo', href, text });
      } else if (href.includes('colab.research.google.com')) {
        trackEvent('click_google_colab', { category: 'Cloud Run', href });
      } else if (href.endsWith('.zip')) {
        trackEvent('download_repo_zip', { category: 'Download', href });
      } else if (href.startsWith('mailto:')) {
        trackEvent('click_email_contact', { category: 'Lead', href });
      }
    });

    // 4. Track Scroll Depth Milestones (25%, 50%, 75%, 100%)
    const scrollMilestones = { 25: false, 50: false, 75: false, 100: false };
    window.addEventListener('scroll', () => {
      const scrollPercent = Math.round(
        ((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight) * 100
      );

      [25, 50, 75, 100].forEach(m => {
        if (scrollPercent >= m && !scrollMilestones[m]) {
          scrollMilestones[m] = true;
          trackEvent(`scroll_depth_${m}%`, { category: 'Scroll Tracking', depth: m });
        }
      });
    }, { passive: true });

    // 5. Track Web Vitals (Performance Telemetry)
    if ('performance' in window && 'getEntriesByType' in performance) {
      window.addEventListener('load', () => {
        setTimeout(() => {
          const navEntries = performance.getEntriesByType('navigation');
          if (navEntries.length > 0) {
            const nav = navEntries[0];
            trackEvent('web_vitals_timing', {
              category: 'Performance',
              dom_complete_ms: Math.round(nav.domComplete),
              load_event_ms: Math.round(nav.loadEventEnd),
              dns_ms: Math.round(nav.domainLookupEnd - nav.domainLookupStart)
            });
          }
        }, 1000);
      });
    }
  }

  // Auto-run on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      loadGoogleAnalytics(GA_ID);
      initAutoTracking();
    });
  } else {
    loadGoogleAnalytics(GA_ID);
    initAutoTracking();
  }

})();
