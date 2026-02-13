import { Search } from 'lucide-react';
import { ChangeEvent } from 'react';
import { Combobox } from '../ui/Combobox';
import { Input } from '../ui/Input';
import { SectionCard } from '../ui/SectionCard';
import { InputGroup } from '../ui/InputGroup';

interface SearchPageProps {
    config: any;
    handleChange: (key: string, value: any) => void;
}

export function SearchPage({ config, handleChange }: SearchPageProps) {
    return (
        <SectionCard title="Web Search" icon={<Search className="w-4 h-4" />} color="text-foreground" gradient="from-muted/20 to-muted/5">
            <InputGroup label="Search Engine" desc="Preferred search provider">
                <Combobox
                    value={config.search_engine || 'Brave'}
                    onChange={(val) => handleChange('search_engine', val)}
                    options={['Brave', 'Bocha']}
                    placeholder="Select search engine"
                />
            </InputGroup>
            {(config.search_engine || 'Brave') === 'Brave' && (
                <InputGroup label="Brave Search API Key" desc="Brave API Key">
                    <Input name="brave_search_api_key" type="password" value={config.brave_search_api_key || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('brave_search_api_key', e.target.value)} placeholder="BSA..." />
                </InputGroup>
            )}
            {(config.search_engine || 'Brave') === 'Bocha' && (
                <InputGroup label="Bocha API Key" desc="Bocha API Key">
                    <Input name="bocha_api_key" type="password" value={config.bocha_api_key || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('bocha_api_key', e.target.value)} placeholder="Enter Bocha API key" />
                </InputGroup>
            )}
            <InputGroup label="Search Result Count" desc="Number of results to return">
                <Input name="search_result_count" type="number" min="1" max="50" value={config.search_result_count ?? 10} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('search_result_count', e.target.value)} />
            </InputGroup>
        </SectionCard>
    );
}
