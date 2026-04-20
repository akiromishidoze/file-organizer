import { useEffect, useState } from 'react'
import './App.css'

type Item = {
  name: string
  category: string
  destination: string
  size: number
  status?: string
}

type ApiError = { error: string }

const CATEGORY_COLORS: Record<string, string> = {
  Images: '#f59e0b',
  Videos: '#ef4444',
  Audio: '#8b5cf6',
  Documents: '#3b82f6',
  Spreadsheets: '#10b981',
  Presentations: '#f97316',
  Archives: '#a16207',
  Code: '#06b6d4',
  Executables: '#dc2626',
  Fonts: '#ec4899',
  Torrents: '#84cc16',
  Other: '#6b7280',
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`
}

export default function App() {
  const [path, setPath] = useState('~/Downloads')
  const [resolvedPath, setResolvedPath] = useState('')
  const [items, setItems] = useState<Item[]>([])
  const [loading, setLoading] = useState(false)
  const [organizing, setOrganizing] = useState(false)
  const [error, setError] = useState('')
  const [lastAction, setLastAction] = useState<'preview' | 'organize' | null>(null)
  const [apiReady, setApiReady] = useState<boolean | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(() => setApiReady(true))
      .catch(() => setApiReady(false))
  }, [])

  async function preview() {
    setLoading(true)
    setError('')
    try {
      const r = await fetch(`/api/preview?path=${encodeURIComponent(path)}`)
      const data = await r.json()
      if (!r.ok) throw new Error((data as ApiError).error || 'Request failed')
      setResolvedPath(data.path)
      setItems(data.items)
      setLastAction('preview')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  async function organize() {
    if (items.length === 0) return
    if (!confirm(`Move ${items.length} file(s) in ${resolvedPath}?`)) return
    setOrganizing(true)
    setError('')
    try {
      const r = await fetch('/api/organize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error((data as ApiError).error || 'Request failed')
      setResolvedPath(data.path)
      setItems(data.moved)
      setLastAction('organize')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setOrganizing(false)
    }
  }

  const counts = items.reduce<Record<string, number>>((acc, it) => {
    acc[it.category] = (acc[it.category] || 0) + 1
    return acc
  }, {})

  return (
    <div className="shell">
      <header>
        <h1>File Organizer</h1>
        <p className="sub">Sort a folder's files into category subfolders.</p>
        {apiReady === false && (
          <div className="banner err">
            Backend not reachable on :5174. Start it with{' '}
            <code>python3 backend/server.py</code>.
          </div>
        )}
      </header>

      <section className="controls">
        <label>
          Folder
          <input
            value={path}
            onChange={e => setPath(e.target.value)}
            placeholder="~/Downloads"
            spellCheck={false}
          />
        </label>
        <div className="buttons">
          <button onClick={preview} disabled={loading || organizing}>
            {loading ? 'Scanning…' : 'Preview'}
          </button>
          <button
            className="primary"
            onClick={organize}
            disabled={organizing || loading || items.length === 0 || lastAction !== 'preview'}
          >
            {organizing ? 'Moving…' : `Organize ${items.length || ''}`.trim()}
          </button>
        </div>
      </section>

      {error && <div className="banner err">{error}</div>}

      {resolvedPath && (
        <div className="resolved">
          Resolved: <code>{resolvedPath}</code>
        </div>
      )}

      {Object.keys(counts).length > 0 && (
        <div className="chips">
          {Object.entries(counts).map(([cat, n]) => (
            <span
              key={cat}
              className="chip"
              style={{ background: CATEGORY_COLORS[cat] || '#6b7280' }}
            >
              {cat} · {n}
            </span>
          ))}
        </div>
      )}

      {items.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>File</th>
              <th>Size</th>
              <th>Category</th>
              <th>{lastAction === 'organize' ? 'Moved to' : 'Will move to'}</th>
            </tr>
          </thead>
          <tbody>
            {items.map(it => (
              <tr key={it.name}>
                <td className="name">{it.name}</td>
                <td className="size">{formatSize(it.size)}</td>
                <td>
                  <span
                    className="badge"
                    style={{ background: CATEGORY_COLORS[it.category] || '#6b7280' }}
                  >
                    {it.category}
                  </span>
                </td>
                <td className="dest">
                  {it.category}/{it.destination}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        lastAction && !loading && !error && (
          <div className="empty">
            {lastAction === 'preview' ? 'No files to organize.' : 'All done.'}
          </div>
        )
      )}
    </div>
  )
}
