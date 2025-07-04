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
        <div class="blue-grey darken-2 grey-text lighten-6 container" style={{ paddingLeft: "30px", paddingRight: "30px" }}>
            
            <h1>ReverseRorschach</h1>
            <h3>Search for emotions in paintings</h3>
            <div style={{ padding: "16px 0" }}>
                <input
                    type="text"
                    value={query}
                    placeholder="Try 'longing', 'sadness', or 'joy'..."
                    onChange={(e) => setQuery(e.target.value)}
                    style={{ color: "tomato", fontSize: "28px", padding: "8px" }} // Only input text color and padding
                />
                <button style={{ padding: "8px 16px" }} onClick={handleSearch}>Search</button>
            </div>
            {loading && <p>Loading results...</p>}
            <div>
                {results.map((result, index) => (
                    <div class="row" key={index}>
                        <h2 class="col s12">{result.title}</h2>
                        <h4 class="col s12">by {result.author}</h4>
                        <div class="row">
                            <img class="col s7" src={result.image_path} alt={result.title} />
                            <div
                                class="col s5"
                                style={{
                                    background: "rgba(0,0,0,0.0)", // very faint transparent background
                                    padding: "12px",
                                    marginBottom: "8px"
                                }}
                            >
                                <p><strong>GEMINI:</strong></p>
                                <div style={{
                                    background: "rgba(0,0,0,0.06)",
                                    padding: "8px",
                                    marginBottom: "15px"
                                }}>
                                    {result.description}
                                </div>
                                <p><strong>VISUAL SIGNATURE (AI-INFERRED):</strong></p>
                                <pre style={{
                                    background: "rgba(0,0,0,0.06)",
                                    padding: "8px",
                                    margin: 0
                                }}>
                                    {JSON.stringify(result.symbolic_tags, null, 2)}
                                </pre>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}