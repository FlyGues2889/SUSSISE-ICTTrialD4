const RISK_ORDER = { low: 0, medium: 1, medium_low: 1, medium_high: 2, high: 3 }
const ROUND_WINDOW_MS = 10000

function toTs(value) {
  return Date.parse((value || '').replace(' ', 'T')) || 0
}

export function pickLatestRoundRisk(items = [], fallback = 'medium') {
  if (!Array.isArray(items) || !items.length) return fallback
  const sorted = [...items].sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
  const latestTs = toTs(sorted[0].created_at)
  const round = sorted.filter((it) => Math.abs(toTs(it.created_at) - latestTs) <= ROUND_WINDOW_MS)
  const pool = round.length ? round : [sorted[0]]
  const worst = pool.reduce(
    (acc, it) => ((RISK_ORDER[it.risk_level] ?? 0) > (RISK_ORDER[acc.risk_level] ?? 0) ? it : acc),
    pool[0]
  )
  return worst.risk_level || fallback
}