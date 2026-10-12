import { ResponsiveBanner } from "@/components/integrations/responsive-banner";
import { Breadcrumbs } from "@/components/site/breadcrumbs";
import { JsonLd } from "@/components/site/json-ld";
import type { SeoPageDefinition } from "@/config/types";
import { pageSchemas } from "@/lib/schema";
import { EditorialBody, ReviewedDate } from "./editorial-content";

export function FixedTemplateInner({ page }: { page: SeoPageDefinition }) {
  return <><JsonLd data={pageSchemas(page)} /><main className="editorial-main">
    <section className="editorial-inner-hero"><div className="site-container" data-editorial-hero>
      <Breadcrumbs slug={page.slug} current={page.navLabel} />
      {page.hero.eyebrow ? <p className="eyebrow">{page.hero.eyebrow}</p> : null}
      <h1>{page.hero.heading}</h1><p className="editorial-lead">{page.hero.lead}</p>
      <ReviewedDate date={page.lastReviewed} />
    </div></section>
    <ResponsiveBanner />
    <EditorialBody page={page} />
  </main></>;
}
