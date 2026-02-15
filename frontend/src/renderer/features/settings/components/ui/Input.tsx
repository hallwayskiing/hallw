import React from "react";

import { cn } from "@lib/utils";

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={cn(
        "w-full bg-input/30 border border-input/50 rounded-xl px-4 py-2.5 text-sm transition-[border-color,box-shadow,background-color] duration-200 transform-gpu",
        "focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 focus:ring-offset-0 text-foreground placeholder:text-muted-foreground/40",
        "appearance-none [Webkit-tap-highlight-color:transparent]",
        props.type === "password" && "font-mono tracking-wider",
        className
      )}
    />
  );
}
