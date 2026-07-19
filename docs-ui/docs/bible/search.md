# Buscar

Búsqueda de texto en toda la Biblia (insensible a tildes)

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/search/{query}</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `query` | string | Sí | Texto a buscar (URL encoded) |
| `version` | string | No | Versión bíblica (query param) |

## Respuesta

```json
{
  "busqueda": "amor",
  "cantidad": 30,
  "resultados": [
    {
      "id": 251,
      "book_id": 1,
      "book_name": "Génesis",
      "chapter": 10,
      "verse": 16,
      "text": "al jebuseo, al amorreo, al gergeseo,",
      "version": "rvr1960"
    }
  ]
}
```

::: info
La búsqueda retorna máximo 30 resultados. Es insensible a tildes, así que "amor" encuentra "amó".
:::

## Ejemplos de Consumo

::: code-group

```bash [cURL]
# Búsqueda básica
curl "https://api.tu-dominio.com/search/amor"

# Con versión específica
curl "https://api.tu-dominio.com/search/amor?version=nvi"

# Búsqueda con tildes (insensible)
curl "https://api.tu-dominio.com/search/amó"
```

```javascript [JavaScript]
async function searchBible(query, version = 'rvr1960') {
  const encodedQuery = encodeURIComponent(query);
  const response = await fetch(
    `https://api.tu-dominio.com/search/${encodedQuery}?version=${version}`
  );

  if (!response.ok) {
    throw new Error(`Error ${response.status}`);
  }

  const data = await response.json();
  console.log(`Se encontraron ${data.cantidad} resultados`);

  return data;
}

// Uso
const results = await searchBible('amor al projimo');
results.resultados.forEach(verse => {
  console.log(`${verse.book_name} ${verse.chapter}:${verse.verse}`);
});
```

```typescript [React + TypeScript]
import { useState, useCallback } from 'react';

interface BibleVerse {
  id: number;
  book_id: number;
  book_name: string;
  chapter: number;
  verse: number;
  text: string;
  version: string;
}

interface SearchResponse {
  busqueda: string;
  cantidad: number;
  resultados: BibleVerse[];
}

type BibleVersion = 'rvr1960' | 'nvi' | 'ntv' | 'pdt' | 'bad' | 'blsee' | 'rvc' | 'rvg';

function useBibleSearch() {
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string, version: BibleVersion = 'rvr1960') => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const encodedQuery = encodeURIComponent(query);
      const res = await fetch(`/search/${encodedQuery}?version=${version}`);

      if (!res.ok) throw new Error('Error en la búsqueda');

      const data: SearchResponse = await res.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }, []);

  return { results, loading, error, search };
}

// Componente de búsqueda
function BibleSearch() {
  const [query, setQuery] = useState('');
  const { results, loading, error, search } = useBibleSearch();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    search(query, 'nvi');
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar en la Biblia..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {results && (
        <div className="results">
          <p>Se encontraron {results.cantidad} resultados</p>
          {results.resultados.map(verse => (
            <article key={verse.id} className="verse-result">
              <h4>{verse.book_name} {verse.chapter}:{verse.verse}</h4>
              <p>{verse.text}</p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

export default BibleSearch;
```

```python [Python]
import requests
from urllib.parse import quote
from dataclasses import dataclass
from typing import List

@dataclass
class BibleVerse:
    id: int
    book_id: int
    book_name: str
    chapter: int
    verse: int
    text: str
    version: str

@dataclass
class SearchResponse:
    busqueda: str
    cantidad: int
    resultados: List[BibleVerse]

def search_bible(query: str, version: str = 'rvr1960') -> SearchResponse:
    """Busca texto en la Biblia. Insensible a tildes."""
    encoded_query = quote(query)
    url = f"https://api.tu-dominio.com/search/{encoded_query}?version={version}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    verses = [BibleVerse(**v) for v in data['resultados']]

    return SearchResponse(
        busqueda=data['busqueda'],
        cantidad=data['cantidad'],
        resultados=verses
    )

# Uso
if __name__ == '__main__':
    results = search_bible('amor al projimo', 'nvi')
    print(f"Se encontraron {results.cantidad} resultados")

    for verse in results.resultados[:5]:
        print(f"{verse.book_name} {verse.chapter}:{verse.verse}")
        print(f"  {verse.text[:80]}...")
```

```kotlin [Kotlin]
import kotlinx.serialization.Serializable
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.http.*

@Serializable
data class BibleVerse(
    val id: Int,
    val book_id: Int,
    val book_name: String,
    val chapter: Int,
    val verse: Int,
    val text: String,
    val version: String
)

@Serializable
data class SearchResponse(
    val busqueda: String,
    val cantidad: Int,
    val resultados: List<BibleVerse>
)

class BibleSearchClient {
    private val client = HttpClient()
    private val baseUrl = "https://api.tu-dominio.com"

    suspend fun search(query: String, version: String = "rvr1960"): SearchResponse {
        return client.get("$baseUrl/search/${query.encodeURLPath()}") {
            parameter("version", version)
        }.body()
    }

    fun close() = client.close()
}

// Uso con Coroutines
suspend fun main() {
    val client = BibleSearchClient()
    try {
        val results = client.search("amor al projimo", "nvi")
        println("Se encontraron ${results.cantidad} resultados")

        results.resultados.take(5).forEach { verse ->
            println("${verse.book_name} ${verse.chapter}:${verse.verse}")
            println("  ${verse.text.take(80)}...")
        }
    } finally {
        client.close()
    }
}
```

```swift [Swift]
import Foundation

struct BibleVerse: Codable, Identifiable {
    let id: Int
    let bookId: Int
    let bookName: String
    let chapter: Int
    let verse: Int
    let text: String
    let version: String

    enum CodingKeys: String, CodingKey {
        case id, chapter, verse, text, version
        case bookId = "book_id"
        case bookName = "book_name"
    }
}

struct SearchResponse: Codable {
    let busqueda: String
    let cantidad: Int
    let resultados: [BibleVerse]
}

class BibleSearchClient {
    private let baseURL = "https://api.tu-dominio.com"

    func search(query: String, version: String = "rvr1960") async throws -> SearchResponse {
        let encodedQuery = query.addingPercentEncoding(
            withAllowedCharacters: .urlPathAllowed
        ) ?? query

        guard let url = URL(string: "\(baseURL)/search/\(encodedQuery)?version=\(version)") else {
            throw URLError(.badURL)
        }

        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode(SearchResponse.self, from: data)
    }
}

// Uso
Task {
    let client = BibleSearchClient()
    do {
        let results = try await client.search(query: "amor al projimo", version: "nvi")
        print("Se encontraron \(results.cantidad) resultados")

        for verse in results.resultados.prefix(5) {
            print("\(verse.bookName) \(verse.chapter):\(verse.verse)")
            print("  \(String(verse.text.prefix(80)))...")
        }
    } catch {
        print("Error: \(error.localizedDescription)")
    }
}
```

:::
