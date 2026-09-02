import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import AppShell from '../layouts/AppShell'
import api from '../api/client'

type Hearing = {
  id: number
  name: string
  case_numbers?: string | null
  next_court_date: string
  next_court_time?: string | null
  court_site?: string | null
  court_location?: string | null
  hearing_type?: string | null
  volunteer_assigned?: string | null
  attorney_name?: string | null
  judge_name?: string | null
  prosecutor_name?: string | null
}

function normalizeDate(value?: string | null) {
  if (!value) return ''
  return value.slice(0, 10)
}

function dateKey(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function prettyDate(value: string) {
  return new Date(value + 'T00:00:00').toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

function prettyTime(value?: string | null) {
  if (!value) return 'Time TBD'
  return new Date(`2000-01-01T${value}`).toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  })
}

function slug(value?: string | null) {
  return (value || 'unscheduled')
    .toLowerCase()
    .replace(/\s+/g, '-')

}

function shortType(value?: string | null) {
  if (!value) return 'Hearing'
  if (value === 'Preliminary Hearing') return 'Prelim'
  if (value === 'Further Proceedings') return 'Further'
  if (value === 'Resentencing Hearing') return 'Resentence'
  if (value === 'SB 1437 Hearing') return 'SB 1437'
  return value
}

export default function CalendarPage() {
  const [hearings, setHearings] = useState<Hearing[]>([])
  const [selectedDate, setSelectedDate] = useState(dateKey(new Date()))
  const [courtFilter, setCourtFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [monthCursor, setMonthCursor] = useState(new Date())

  useEffect(() => {
    api.get('/resources/calendar')
      .then((res) => setHearings(res.data || []))
      .catch((err) => console.error('Calendar failed:', err))
  }, [])

  const filtered = useMemo(() => {
    return hearings.filter((h) => {
      return (!courtFilter || h.court_site === courtFilter) &&
        (!typeFilter || h.hearing_type === typeFilter)
    })
  }, [hearings, courtFilter, typeFilter])

  const courts = Array.from(new Set(hearings.map(h => h.court_site).filter(Boolean))) as string[]
  const hearingTypes = Array.from(new Set(hearings.map(h => h.hearing_type).filter(Boolean))) as string[]

  const year = monthCursor.getFullYear()
  const month = monthCursor.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startOffset = firstDay.getDay()

  const days = Array.from({ length: startOffset + lastDay.getDate() }, (_, i) => {
    if (i < startOffset) return null
    return new Date(year, month, i - startOffset + 1)
  })

  const hearingsByDate = filtered.reduce<Record<string, Hearing[]>>((acc, h) => {
    const key = normalizeDate(h.next_court_date)
    if (!key) return acc

    acc[key] = acc[key] || []
    acc[key].push(h)

    return acc
  }, {})

  const selectedHearings = (hearingsByDate[selectedDate] || []).sort((a, b) =>
    (a.next_court_time || '').localeCompare(b.next_court_time || '')
  )

  return (
    <AppShell title="Court Calendar" intro="Court calendar and daily docket for hearings, volunteers, and court-support planning.">
      <section className="calendar-toolbar">
        <div>
          <p className="eyebrow">Calendar Controls</p>
          <h2>{monthCursor.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}</h2>
        </div>

        <div className="calendar-actions">
          <button type="button" onClick={() => setMonthCursor(new Date(year, month - 1, 1))}>
            ← Previous
          </button>
          <button type="button" onClick={() => {
            const today = new Date()
            setMonthCursor(today)
            setSelectedDate(dateKey(today))
          }}>
            Today
          </button>
          <button type="button" onClick={() => setMonthCursor(new Date(year, month + 1, 1))}>
            Next →
          </button>
        </div>
      </section>

      <section className="calendar-filters">
        <label>
          Court
          <select value={courtFilter} onChange={(e) => setCourtFilter(e.target.value)}>
            <option value="">All courts</option>
            {courts.map(court => <option key={court} value={court}>{court}</option>)}
          </select>
        </label>

        <label>
          Hearing Type
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="">All hearing types</option>
            {hearingTypes.map(type => <option key={type} value={type}>{type}</option>)}
          </select>
        </label>
      </section>

      <section className="calendar-pro-layout">
        <div className="calendar-pro-panel">
          <div className="calendar-pro-grid">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div className="calendar-pro-weekday" key={day}>{day}</div>
            ))}

            {days.map((day, index) => {
              if (!day) return <div key={index} className="calendar-pro-day calendar-pro-empty" />

              const key = dateKey(day)
              const dayHearings = hearingsByDate[key] || []
              const isSelected = selectedDate === key
              const isToday = key === dateKey(new Date())

              return (
                <button
                  key={key}
                  type="button"
                  className={[
                    'calendar-pro-day',
                    isSelected ? 'calendar-pro-selected' : '',
                    isToday ? 'calendar-pro-today' : '',
                  ].join(' ')}
                  onClick={() => setSelectedDate(key)}
                >
                  <div className="calendar-pro-day-head">
                    <span>{day.getDate()}</span>
                    {dayHearings.length > 0 && <strong>{dayHearings.length}</strong>}
                  </div>

                  <div className="calendar-pro-events">
                    {dayHearings.slice(0, 3).map(h => (
                      <span key={h.id} className={`court-chip court-chip-${slug(h.hearing_type)}`}>
                        {prettyTime(h.next_court_time)} · {shortType(h.hearing_type)}
                      </span>
                    ))}
                    {dayHearings.length > 3 && (
                      <span className="court-chip court-chip-more">
                        +{dayHearings.length - 3} more
                      </span>
                    )}
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        <aside className="daily-docket">
          <div className="daily-docket-head">
            <p className="eyebrow">Daily Docket</p>
            <h2>{prettyDate(selectedDate)}</h2>
            <p>{selectedHearings.length} scheduled hearing{selectedHearings.length === 1 ? '' : 's'}</p>
          </div>

          {selectedHearings.length === 0 ? (
            <div className="empty-docket">
              <strong>No hearings scheduled.</strong>
              <p>Select another date or clear your filters.</p>
            </div>
          ) : (
            <div className="docket-list">
              {selectedHearings.map(h => (
                <Link key={h.id} to={`/intakes/${h.id}`} className="docket-pro-card">
                  <div className="docket-time">
                    <strong>{prettyTime(h.next_court_time)}</strong>
                    <span>{h.court_site || h.court_location || 'Court TBD'}</span>
                  </div>

                  <div className="docket-main">
                    <div className="docket-title-row">
                      <h3>{h.name}</h3>
                      <span className={`hearing-pill hearing-pill-${slug(h.hearing_type)}`}>
                        {h.hearing_type || 'Hearing type not selected'}
                      </span>
                    </div>

                    <div className="docket-details-grid">
                      <p>📁 Case: {h.case_numbers || 'N/A'}</p>
                      <p>👥 Volunteer: {h.volunteer_assigned || 'Not assigned'}</p>
                      <p>⚖️ Attorney: {h.attorney_name || 'Not listed'}</p>
                      <p>🏛 Judge: {h.judge_name || 'Not listed'}</p>
                    </div>
                  </div>

                  <span className="docket-arrow">→</span>
                </Link>
              ))}
            </div>
          )}
        </aside>
      </section>
    </AppShell>
  )
}
