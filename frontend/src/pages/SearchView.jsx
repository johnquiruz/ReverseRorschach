import { useState } from "react";
import { fetchSearchResults } from "../lib/api";

export default function SearchView() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async () => {
        if (!query.trim()) return;
        setLoading(true);
        const data = await fetchSearchResults(query);
        setResults(data);
        setLoading(false);
    };

    return (
        <div class="blue-grey darken-2 grey-text lighten-5 container">
            <h1>Semantic Painting Search</h1>
            <div>
                <input
                    type="text"
                    value={query}
                    placeholder="Try 'longing', 'sadness', or 'joy'..."
                    onChange={(e) => setQuery(e.target.value)}
                />
                <button onClick={handleSearch}>Search</button>
            </div>
            {loading && <p>Loading results...</p>}
            <div class="row">
                {results.map((result, index) => (
                    <div key={index}>
                        <h2 class="col s12">{result.title}</h2>
                        <p class="col s12">{result.description}</p>
                        <img class="col s12" src={result.image_path} alt={result.title} />
                        <pre class="col s12">
                            {JSON.stringify(result.symbolic_tags, null, 2)}
                        </pre>
                    </div>
                ))}
            </div>
        </div>
    );
}