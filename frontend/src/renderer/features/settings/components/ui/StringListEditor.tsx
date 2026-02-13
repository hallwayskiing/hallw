import { useState } from 'react';
import { Input } from './Input';

export function StringListEditor({ label, desc, items, onChange, placeholder }: {
    label: string;
    desc?: string;
    items: string[];
    onChange: (items: string[]) => void;
    placeholder?: string;
}) {
    const [inputValue, setInputValue] = useState('');

    const handleAdd = () => {
        const trimmed = inputValue.trim();
        if (trimmed && !items.includes(trimmed)) {
            onChange([...items, trimmed]);
            setInputValue('');
        }
    };

    const handleRemove = (index: number) => {
        onChange(items.filter((_, i) => i !== index));
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAdd();
        }
    };

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-foreground">{label}</label>
                {desc && <span className="text-xs text-muted-foreground">{desc}</span>}
            </div>

            {/* Input row */}
            <div className="flex gap-2">
                <Input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                />
                <button
                    type="button"
                    onClick={handleAdd}
                    className="px-4 py-2 text-sm font-medium bg-zinc-500/20 text-foreground hover:bg-zinc-500/30 rounded-xl transition-colors"
                >
                    Add
                </button>
            </div>

            {/* Tags */}
            {items.length > 0 && (
                <div className="flex flex-wrap gap-2">
                    {items.map((item, index) => (
                        <span
                            key={index}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-zinc-500/15 text-foreground rounded-lg text-sm group"
                        >
                            {item}
                            <button
                                type="button"
                                onClick={() => handleRemove(index)}
                                className="w-4 h-4 flex items-center justify-center rounded-full hover:bg-zinc-500/30 transition-colors"
                            >
                                ×
                            </button>
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}
