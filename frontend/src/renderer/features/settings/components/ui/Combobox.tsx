import { useEffect, useState } from "react";

import { ChevronDown } from "lucide-react";

import { cn } from "@lib/utils";

import { Input } from "./Input";

export function Combobox({
  value,
  onChange,
  options,
  placeholder,
}: {
  value: string;
  onChange: (val: string) => void;
  options: string[];
  placeholder?: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [wrapperRef, setWrapperRef] = useState<HTMLDivElement | null>(null);

  // Filter duplicates just in case
  const uniqueOptions = Array.from(new Set(options));

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      // Check if wrapperRef exists and if the click target is within it
      if (wrapperRef && !wrapperRef.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef]);

  return (
    <div className="relative" ref={setWrapperRef}>
      <div className="relative">
        <Input
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            if (!isOpen) setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
        />
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-1"
        >
          <ChevronDown className={cn("w-4 h-4 transition-transform duration-200", isOpen && "rotate-180")} />
        </button>
      </div>

      {isOpen && uniqueOptions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-popover/95 backdrop-blur-xl border border-border/50 rounded-xl shadow-xl max-h-60 overflow-y-auto animate-in fade-in zoom-in-95 duration-200">
          <div className="p-1 space-y-0.5">
            {uniqueOptions.map((option, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  onChange(option);
                  setIsOpen(false);
                }}
                className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-muted/50 transition-colors truncate text-foreground/80 hover:text-foreground"
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
