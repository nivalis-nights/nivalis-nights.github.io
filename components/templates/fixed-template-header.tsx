"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRef, useState } from "react";
import { Menu, X } from "lucide-react";
import { siteConfig } from "@/config/site";
import type { InternalLink } from "@/config/types";
import { assetPath, routePath } from "@/lib/urls";

export function FixedTemplateHeader({ links }: { links: InternalLink[] }) {
  const pathname = usePathname() || "/";
  const [open, setOpen] = useState(false);
  const toggle = useRef<HTMLButtonElement>(null);
  const current = pathname.replace(/\/+$/, "") || "/";
  return <header className="editorial-header" onKeyDown={(event) => {
    if (event.key === "Escape" && open) { setOpen(false); toggle.current?.focus(); }
  }}><div className="site-container editorial-header-row">
    <Link href="/" className="editorial-brand" onClick={() => setOpen(false)}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={assetPath(siteConfig.assets.logo)} alt="" width={38} height={38} />
      <span>{siteConfig.shortName}<small>Independent Wiki & Guides</small></span>
    </Link>
    <button type="button" ref={toggle} className="editorial-menu-toggle" aria-label={open ? "Close navigation" : "Open navigation"} aria-expanded={open} aria-controls="primary-navigation" onClick={() => setOpen(!open)}>{open ? <X size={21} /> : <Menu size={21} />}<span>Menu</span></button>
    <nav id="primary-navigation" aria-label="Primary navigation" className={`editorial-nav${open ? " is-open" : ""}`}>
      {links.map((link) => <Link key={link.slug} href={routePath(link.slug)} aria-current={(routePath(link.slug).replace(/\/+$/, "") || "/") === current ? "page" : undefined} onClick={() => setOpen(false)}>{link.label}</Link>)}
    </nav>
  </div></header>;
}
