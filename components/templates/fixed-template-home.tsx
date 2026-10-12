import Link from "next/link";
import { ArrowRight, ArrowUpRight } from "lucide-react";
import { ResponsiveBanner } from "@/components/integrations/responsive-banner";
import { JsonLd } from "@/components/site/json-ld";
import { siteConfig } from "@/config/site";
import type { HomePageDefinition } from "@/config/types";
import { visibleCorePages } from "@/content/registry";
import { homeSchemas } from "@/lib/schema";
import { assetPath, routePath } from "@/lib/urls";
import { EditorialBody, ReviewedDate } from "./editorial-content";

export function FixedTemplateHome({ home }: { home: HomePageDefinition }) {
  return <><JsonLd data={homeSchemas(home)} /><main className="editorial-main">
    <section className="editorial-home-hero"><div className="site-container">
      <div className="editorial-magazine"><div className="editorial-hero-copy" data-editorial-hero>
        <p className="eyebrow">{home.hero.eyebrow}</p><h1>{home.hero.heading}</h1>
        <p className="editorial-lead">{home.hero.lead}</p>
        <div className="editorial-actions">
          {home.hero.primaryLink ? <Link className="button-primary" href={routePath(home.hero.primaryLink.slug)}>{home.hero.primaryLink.label}<ArrowRight size={17} aria-hidden="true" /></Link> : null}
          {home.hero.secondaryLink ? <a className="button-secondary" href={home.hero.secondaryLink.url} rel="noopener noreferrer">{home.hero.secondaryLink.label}<ArrowUpRight size={17} aria-label="External site" /></a> : null}
        </div><ReviewedDate date={home.lastReviewed} />
      </div><div className="editorial-hero-visual">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={assetPath(siteConfig.assets.cover)} alt="Nivalis Nights cover art featuring the neon city skyline" width={460} height={215} fetchPriority="high" />
        <div className="editorial-facts"><p className="eyebrow">The city at a glance</p><dl>
          {[["Platform", "Steam / PC"], ["Developer", siteConfig.game.developer], ["Publisher", siteConfig.game.publisher], ["Released", "September 29, 2026"]].map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}
        </dl><p className="editorial-cover-caption">{home.hero.supportingText}</p></div>
      </div></div>
      <nav className="editorial-quick-nav" aria-label="Find a guide">{visibleCorePages.map((page, index) => <Link key={page.slug} href={routePath(page.slug)}><span>{String(index + 1).padStart(2, "0")}</span><strong>{page.navLabel}</strong><ArrowUpRight size={15} aria-hidden="true" /></Link>)}</nav>
    </div></section>
    <ResponsiveBanner />
    <EditorialBody page={home} />
  </main></>;
}
