import Link from "next/link";
import { Fragment } from "react";
import { NativeAdSlot } from "@/components/integrations/native-ad-slot";
import { ArrowUpRight } from "lucide-react";
import type { HomePageDefinition, InternalLink, PageSection, SeoPageDefinition, SourceLink } from "@/config/types";
import { routePath } from "@/lib/urls";
import { Faq } from "@/components/site/faq";
import { DataTable } from "@/components/site/data-table";
import { getRelatedPages, visibleCorePages } from "@/content/registry";

function TopicLinks({ links, headings = false }: { links: InternalLink[]; headings?: boolean }) {
  return <div className="editorial-topic-links">{links.map((link) => <Link key={link.slug} href={routePath(link.slug)} className="editorial-topic-card">
    <div className="editorial-topic-title">{headings ? <h3>{link.label}</h3> : <strong>{link.label}</strong>}<ArrowUpRight size={18} aria-hidden="true" /></div>
    {link.description ? <span className="editorial-topic-description">{link.description}</span> : null}
  </Link>)}</div>;
}

function Bullets({ items }: { items?: string[] }) {
  return items?.length ? <ul className="editorial-bullets">{items.map((item) => <li key={item}>{item}</li>)}</ul> : null;
}

export function EditorialSections({ sections }: { sections: PageSection[] }) {
  return <div className="editorial-sections">{sections.map((section, sectionIndex) => {
    // Insert after an existing, complete block without rewriting or moving copy.
    const after = sectionIndex !== 0 ? null : section.intro ? "intro"
      : section.paragraphs?.length ? "paragraphs" : section.bullets?.length ? "bullets"
      : section.subsections?.length ? "subsection" : section.steps?.length ? "steps"
      : section.table ? "table" : section.links?.length ? "links" : null;
    return <section id={section.id} key={section.id}>
    {section.eyebrow ? <p className="eyebrow">{section.eyebrow}</p> : null}
    <h2>{section.heading}</h2>
    {section.intro ? <p>{section.intro}</p> : null}
    {after === "intro" ? <NativeAdSlot /> : null}
    {section.paragraphs?.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
    {after === "paragraphs" ? <NativeAdSlot /> : null}
    <Bullets items={section.bullets} />
    {after === "bullets" ? <NativeAdSlot /> : null}
    {section.subsections?.map((subsection, subsectionIndex) => <Fragment key={subsection.heading}><div className="editorial-subsection">
      <h3>{subsection.heading}</h3>
      {subsection.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
      <Bullets items={subsection.bullets} />
      {subsection.table ? <DataTable table={subsection.table} /> : null}
      {subsection.links?.length ? <TopicLinks links={subsection.links} /> : null}
    </div>{after === "subsection" && subsectionIndex === 0 ? <NativeAdSlot /> : null}</Fragment>)}
    {section.steps?.length ? <ol className="editorial-steps">{section.steps.map((step, index) => <li key={step.heading}>
      <span className="editorial-step-number" aria-hidden="true">{String(index + 1).padStart(2, "0")}</span>
      <div><h3>{step.heading}</h3><p>{step.description}</p></div>
    </li>)}</ol> : null}
    {after === "steps" ? <NativeAdSlot /> : null}
    {section.table ? <DataTable table={section.table} /> : null}
    {after === "table" ? <NativeAdSlot /> : null}
    {section.links?.length ? <TopicLinks links={section.links} headings={section.id === "popular-guides"} /> : null}
    {after === "links" ? <NativeAdSlot /> : null}
  </section>;
  })}</div>;
}

export function SourceLinks({ sources }: { sources?: SourceLink[] }) {
  if (!sources?.length) return null;
  return <section id="sources" className="editorial-sources"><h2>Sources and Further Reading</h2>
    <ul>{sources.map((source) => {
      const url = new URL(source.url);
      if (url.protocol !== "https:") throw new Error("Source links must use HTTPS");
      return <li key={source.url}><a href={source.url} rel="noopener noreferrer">{source.label}<span aria-hidden="true"> ↗</span></a>{source.description ? <p>{source.description}</p> : null}</li>;
    })}</ul>
  </section>;
}

export function EditorialContents({ page }: { page: HomePageDefinition | SeoPageDefinition }) {
  return <nav className="editorial-contents" aria-label="Contents"><p className="eyebrow">On this page</p>
    <ol>{page.sections.map((section, index) => <li key={section.id}><a href={`#${section.id}`}><span aria-hidden="true">{String(index + 1).padStart(2, "0")}</span>{section.heading}</a></li>)}
      {page.faq?.length ? <li><a href="#faq">Frequently Asked Questions</a></li> : null}
      <li><a href="#related-guides">Related Guides</a></li>
      {page.sources?.length ? <li><a href="#sources">Sources and Further Reading</a></li> : null}
    </ol>
  </nav>;
}

export function EditorialBody({ page }: { page: HomePageDefinition | SeoPageDefinition }) {
  const related = page.pageType === "home" ? visibleCorePages : getRelatedPages(page);
  return <div className="site-container editorial-body"><article className="editorial-article" data-editorial-content>
    <EditorialSections sections={page.sections} />
    {page.faq?.length ? <Faq items={page.faq} /> : null}
    <section id="related-guides"><p className="eyebrow">Your next step</p><h2>Related Guides</h2>
      <TopicLinks links={related.map((item) => ({ slug: item.slug, label: item.navLabel, description: item.description }))} />
      <p className="editorial-home-link"><Link href="/">Nivalis Nights guide hub</Link></p>
    </section>
    <SourceLinks sources={page.sources} />
  </article><aside className="editorial-sidebar"><EditorialContents page={page} />
    <div className="editorial-sidebar-note"><p className="eyebrow">Follow your current objective</p><p>Check your journal, inventory, and on-screen prompts as you go. Choose the guide that matches the step you are on.</p><Link href="/guide-wiki/">Open Guide & Wiki →</Link></div>
  </aside></div>;
}

export function ReviewedDate({ date }: { date: string }) {
  return <p className="editorial-reviewed">Last reviewed <time dateTime={date}>{new Intl.DateTimeFormat("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" }).format(new Date(`${date}T00:00:00Z`))}</time></p>;
}
