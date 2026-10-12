"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { assetPath } from "@/lib/urls";

function BannerInstance() {
  const [device, setDevice] = useState<"mobile" | "desktop" | null>(null);

  useEffect(() => {
    // Freeze the choice for this visit: resizing must not execute a second unit.
    const timer = window.setTimeout(() => {
      setDevice(window.matchMedia("(min-width: 768px)").matches ? "desktop" : "mobile");
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  return <div className="site-container ad-banner" data-banner-ad-slot>
    <span className="ad-label">Advertisement</span>
    <div className="ad-banner-frame" data-device={device ?? undefined}>
      {device ? <iframe
        src={assetPath(`/adsterra/${device}.html`)}
        title="Advertisement"
        width={device === "desktop" ? 728 : 320}
        height={device === "desktop" ? 90 : 50}
        scrolling="no"
      /> : null}
    </div>
  </div>;
}

export function ResponsiveBanner() {
  // Each client-side visit gets one fresh frame; the previous frame is removed.
  const pathname = usePathname();
  return <BannerInstance key={pathname} />;
}
