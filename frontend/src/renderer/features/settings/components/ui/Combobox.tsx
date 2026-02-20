import { cn } from "@lib/utils";

import { ChevronDown, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import { Input } from "./Input";

export function Combobox({
  value,
  onChange,
  options,
  placeholder,
  onDelete,
}: {
  value: string;
  onChange: (val: string) => void;
  options: string[];
  placeholder?: string;
  onDelete?: (val: string) => void;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [wrapperRef, setWrapperRef] = useState<HTMLDivElement | null>(null);

  // Filter duplicates just in case
  const uniqueOptions = Array.from(new Set(options));

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
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
            {uniqueOptions.map((option) => (
              <div
                key={option}
                className="group relative flex items-center gap-1 rounded-lg hover:bg-muted/50 transition-colors px-1"
              >
                <button
                  type="button"
                  onClick={() => {
                    onChange(option);
                    setIsOpen(false);
                  }}
                  className="flex-1 text-left px-2 py-2 text-sm truncate text-foreground/80 group-hover:text-foreground transition-colors"
                >
                  {option}
                </button>
                {onDelete && (
                  <button
                    type="button"
                    onClick={() => onDelete(option)}
                    className="p-1.5 rounded-md text-muted-foreground hover:text-red-500 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all shrink-0"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
