import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center px-2.5 py-0.5 text-xs font-semibold transition-smooth focus:outline-none focus:ring-2 focus-visible:ring-[hsl(var(--color-ring))] focus:ring-offset-2 rounded-full",
  {
    variants: {
      variant: {
        default:
          "glass-card text-[hsl(var(--color-primary))] border-[hsl(var(--color-primary))]/30 hover:glass",
        secondary:
          "glass-card text-[hsl(var(--color-foreground))] hover:glass",
        destructive:
          "glass-card text-[hsl(var(--color-destructive))] border-[hsl(var(--color-destructive))]/30 hover:glass",
        outline: "glass text-[hsl(var(--color-foreground))] hover:glass-card",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
