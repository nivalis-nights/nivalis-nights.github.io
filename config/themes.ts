import type { ThemeConfig, ThemePresetName } from "./types";

export const themes: Partial<Record<ThemePresetName, ThemeConfig>> = {
  "obsidian-red": {
    name: "obsidian-red" as ThemePresetName,
    label: "Site Theme",
    description: "Selected site theme",
    tokens: {
  "background": "221 51% 7%",
  "foreground": "0 0% 99%",
  "card": "221 51% 12%",
  "card-foreground": "0 0% 99%",
  "primary": "25 95% 53%",
  "primary-foreground": "0 0% 0%",
  "secondary": "221 51% 18%",
  "muted": "221 51% 15%",
  "muted-foreground": "0 0% 99%",
  "border": "221 51% 23%",
  "radius": ".75rem",
  "card-shadow": "0 22px 70px hsl(25 95% 53% / .16)",
  "hero-gradient": "radial-gradient(circle at 78% 14%, hsl(25 95% 53% / .2), transparent 36%)",
  "background-pattern": "radial-gradient(hsl(25 95% 53% / .05) 1px, transparent 1px)",
  "font-sans": "\"Source Sans 3\", ui-sans-serif, system-ui, sans-serif",
  "font-heading": "\"Source Serif 4\", Georgia, Cambria, serif",
  "heading-weight": "600",
  "heading-letter-spacing": "-0.02em"
},
  },
};
