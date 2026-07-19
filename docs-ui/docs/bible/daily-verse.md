# Versículo Diario

Retorna un versículo aleatorio que cambia cada día

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/daily</code>
</div>
<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/daily/{version}</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `version` | string | No | Versión bíblica (default: rvr1960). Ver [versiones disponibles](/versions) |

## Respuesta

```json
{
  "id": 27845,
  "book_id": 44,
  "book_name": "Hechos",
  "chapter": 26,
  "verse": 21,
  "text": "Por causa de esto los judíos, prendiéndome en el templo, intentaron matarme.",
  "version": "rvr1960"
}
```

## Ejemplos de Consumo

# Versículo Aleatorio

Retorna un versículo completamente aleatorio (cambia en cada llamado)

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/random</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `version` | string | No | Versión bíblica (default: rvr1960) |

## Respuesta

```json
{
  "id": 27845,
  "book_id": 44,
  "book_name": "Hechos",
  "chapter": 26,
  "verse": 21,
  "text": "Por causa de esto los judíos, prendiéndome en el templo, intentaron matarme.",
  "version": "rvr1960"
}
```

::: info
A diferencia de `/daily`, este endpoint no usa semilla diaria — cada llamado retorna un versículo diferente.
:::

::: code-group

```bash [cURL]
curl BASE_URL/daily

# Con versión específica
curl BASE_URL/daily/nvi
```

```javascript [JavaScript (Express/Node.js)]
const getDailyVerse = async (version = 'rvr1960') => {
  const response = await fetch(`BASE_URL/daily/${version}`);

  if (!response.ok) {
    throw new Error(`Error: ${response.status}`);
  }

  const verse = await response.json();
  console.log(`${verse.book_name} ${verse.chapter}:${verse.verse}`);
  console.log(verse.text);

  return verse;
};

// Uso
getDailyVerse('nvi')
  .then(verse => console.log(verse))
  .catch(err => console.error(err));
```

```typescript [React + TypeScript]
import { useState, useEffect } from 'react';

interface BibleVerse {
  id: number;
  book_id: number;
  book_name: string;
  chapter: number;
  verse: number;
  text: string;
  version: string;
}

type BibleVersion = 'rvr1960' | 'nvi' | 'ntv' | 'pdt' | 'bad' | 'blsee' | 'rvc' | 'rvg';

const useDailyVerse = (version: BibleVersion = 'rvr1960') => {
  const [verse, setVerse] = useState<BibleVerse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVerse = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/daily/${version}`);
        if (!res.ok) throw new Error('Error al cargar versículo');
        const data: BibleVerse = await res.json();
        setVerse(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchVerse();
  }, [version]);

  return { verse, loading, error };
};

// Componente
function DailyVerse() {
  const { verse, loading, error } = useDailyVerse('nvi');

  if (loading) return <div className="loading">Cargando...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!verse) return null;

  return (
    <article className="verse-card">
      <h3>{verse.book_name} {verse.chapter}:{verse.verse}</h3>
      <blockquote>{verse.text}</blockquote>
      <footer className="version-tag">{verse.version.toUpperCase()}</footer>
    </article>
  );
}

export default DailyVerse;
```

```typescript [Next.js + TypeScript (Server Component)]
interface BibleVerse {
  id: number;
  book_id: number;
  book_name: string;
  chapter: number;
  verse: number;
  text: string;
  version: string;
}

type BibleVersion = 'rvr1960' | 'nvi' | 'ntv' | 'pdt' | 'bad' | 'blsee' | 'rvc' | 'rvg';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'BASE_URL';

async function getDailyVerse(version: BibleVersion = 'rvr1960'): Promise<BibleVerse> {
  const response = await fetch(`${API_BASE}/daily/${version}`, {
    next: { revalidate: 3600 }
  });

  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// Next.js Server Component (App Router)
export default async function DailyVersePage() {
  const verse = await getDailyVerse('nvi');

  return (
    <main className="container">
      <article className="verse-card">
        <header>
          <h1>{verse.book_name} {verse.chapter}:{verse.verse}</h1>
          <span className="badge">{verse.version.toUpperCase()}</span>
        </header>
        <blockquote className="verse-text">
          {verse.text}
        </blockquote>
      </article>
    </main>
  );
}
```

```python [Python]
import requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class BibleVerse:
    id: int
    book_id: int
    book_name: str
    chapter: int
    verse: int
    text: str
    version: str

    @classmethod
    def from_dict(cls, data: dict) -> 'BibleVerse':
        return cls(**data)

def get_daily_verse(version: str = 'rvr1960') -> BibleVerse:
    """Obtiene el versículo diario de la API."""
    url = f"BASE_URL/daily/{version}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return BibleVerse.from_dict(response.json())

# Uso
if __name__ == '__main__':
    verse = get_daily_verse('nvi')
    print(f"{verse.book_name} {verse.chapter}:{verse.verse}")
    print(verse.text)
```

```kotlin [Kotlin (Android/Spring)]
import kotlinx.serialization.Serializable
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.engine.cio.CIO

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

class BibleApiClient {
    private val client = HttpClient(CIO)
    private val baseUrl = "BASE_URL"

    suspend fun getDailyVerse(version: String = "rvr1960"): BibleVerse {
        return client.get("$baseUrl/daily/$version").body()
    }

    fun close() {
        client.close()
    }
}

// Uso con Coroutines
suspend fun main() {
    val client = BibleApiClient()
    try {
        val verse = client.getDailyVerse("nvi")
        println("${verse.book_name} ${verse.chapter}:${verse.verse}")
        println(verse.text)
    } finally {
        client.close()
    }
}
```

```swift [Swift (iOS)]
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
        case id, book_id, book_name, chapter, verse, text, version
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        bookId = try container.decode(Int.self, forKey: .book_id)
        bookName = try container.decode(String.self, forKey: .book_name)
        chapter = try container.decode(Int.self, forKey: .chapter)
        verse = try container.decode(Int.self, forKey: .verse)
        text = try container.decode(String.self, forKey: .text)
        version = try container.decode(String.self, forKey: .version)
    }
}

class BibleAPIClient {
    private let baseURL = "BASE_URL"

    func getDailyVerse(version: String = "rvr1960") async throws -> BibleVerse {
        guard let url = URL(string: "\(baseURL)/daily/\(version)") else {
            throw URLError(.badURL)
        }

        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode(BibleVerse.self, from: data)
    }
}

// Uso
Task {
    let client = BibleAPIClient()
    do {
        let verse = try await client.getDailyVerse(version: "nvi")
        print("\(verse.bookName) \(verse.chapter):\(verse.verse)")
        print(verse.text)
    } catch {
        print("Error: \(error.localizedDescription)")
    }
}
```

:::
