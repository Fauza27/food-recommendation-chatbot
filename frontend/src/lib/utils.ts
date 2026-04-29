import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Helper untuk menggunakan CSS variables
export const colors = {
  background: "hsl(var(--color-background))",
  foreground: "hsl(var(--color-foreground))",
  card: "hsl(var(--color-card))",
  cardForeground: "hsl(var(--color-card-foreground))",
  popover: "hsl(var(--color-popover))",
  popoverForeground: "hsl(var(--color-popover-foreground))",
  primary: "hsl(var(--color-primary))",
  primaryForeground: "hsl(var(--color-primary-foreground))",
  secondary: "hsl(var(--color-secondary))",
  secondaryForeground: "hsl(var(--color-secondary-foreground))",
  muted: "hsl(var(--color-muted))",
  mutedForeground: "hsl(var(--color-muted-foreground))",
  accent: "hsl(var(--color-accent))",
  accentForeground: "hsl(var(--color-accent-foreground))",
  destructive: "hsl(var(--color-destructive))",
  destructiveForeground: "hsl(var(--color-destructive-foreground))",
  border: "hsl(var(--color-border))",
  input: "hsl(var(--color-input))",
  ring: "hsl(var(--color-ring))",
};
