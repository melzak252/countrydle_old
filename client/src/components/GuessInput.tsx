import { useState, useMemo } from 'react';
import type { CountryDisplay } from '../types';
import { Search } from 'lucide-react';

interface GuessInputProps {
  countries: CountryDisplay[];
  onGuess: (countryId: number, name: string) => Promise<void>;
  isLoading: boolean;
  remainingGuesses: number;
  placeholder?: string;
  className?: string;
}

export default function GuessInput({ countries, onGuess, isLoading, remainingGuesses, placeholder, className }: GuessInputProps) {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const filteredCountries = useMemo(() => {
    if (!query || !countries) return [];
    return countries
      .filter(c => {
        const name = c.name || (c as any).nazwa;
        return name?.toLowerCase().includes(query.toLowerCase());
      })
      .slice(0, 5); // Limit to 5 suggestions
  }, [countries, query]);

  const handleSelect = (country: any) => {
    onGuess(country.id, country.name || country.nazwa);
    setQuery('');
    setShowSuggestions(false);
  };

  const defaultPlaceholder = `Guess the country... (${remainingGuesses} left)`;

  return (
    <div className={`w-full max-w-2xl mx-auto relative ${className || 'mb-6 md:mb-12'}`}>
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowSuggestions(true);
          }}
          onFocus={() => setShowSuggestions(true)}
          placeholder={placeholder || defaultPlaceholder}
          className="w-full bg-zinc-800 border-2 border-zinc-700 rounded-xl px-3 py-2 md:px-4 md:py-3 pl-9 md:pl-10 text-sm md:text-base focus:outline-none focus:border-green-500 transition-colors disabled:opacity-50"
          disabled={isLoading || remainingGuesses <= 0}
        />
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4 md:w-5 md:h-5" />
      </div>

      {showSuggestions && filteredCountries.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-zinc-800 border border-zinc-700 rounded-xl shadow-xl overflow-hidden z-[60]">
          {filteredCountries.map((country) => (
            <button
              key={country.id}
              onClick={() => handleSelect(country)}
              className="w-full text-left px-3 py-2 hover:bg-zinc-700 transition-colors border-b border-zinc-700 last:border-0 text-sm"
            >
              {country.name || (country as any).nazwa}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
