"use client";

import { useEffect } from "react";
import { adsterra } from "@/config/adsterra";

export function SocialBar() {
  useEffect(() => {
    // Defer past the development Strict Mode effect replay. Root navigation
    // keeps this script alive; even a remount cannot initialize it again.
    const timer = window.setTimeout(() => {
      if (document.querySelector('script[data-adsterra-social-bar]')) return;
      const script = document.createElement("script");
      script.dataset.cfasync = "false";
      script.src = adsterra.socialBarScriptUrl;
      script.dataset.adsterraSocialBar = "";
      document.body.appendChild(script);
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  return null;
}
