import type { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";
import { themes } from "@/config/themes";
import { assetPath } from "@/lib/urls";

export const dynamic = "force-static";

export default function manifest(): MetadataRoute.Manifest {
  const theme = themes[siteConfig.theme.preset];
  return {
    name: siteConfig.siteName,
    short_name: siteConfig.shortName,
    description: siteConfig.description,
    start_url: assetPath("/"),
    display: "standalone",
    background_color: `hsl(${siteConfig.theme.overrides?.background ?? theme?.tokens.background ?? "221 51% 7%"})`,
    theme_color: `hsl(${siteConfig.theme.overrides?.primary ?? theme?.tokens.primary ?? "25 95% 53%"})`,
    icons: [{ src: assetPath(siteConfig.assets.logo), sizes: "256x256", type: "image/jpeg" }],
  };
}
