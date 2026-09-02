import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AppShell from '../layouts/AppShell'
import api from '../api/client'

type DashboardActivity = {
  id: number
  title: string
  activity_date: string
  start_time?: string | null
  location?: string | null
}

type DashboardNote = {
  id: number
  youth_id: number
  youth_name: string
  note_type?: string | null
  note: string
  created_by_name?: string | null
  created_at: string
}

type DashboardData = {
  active_youth: number
  contacts_due_today: number
  overdue_contacts: number
  activities_this_week: number
  total_case_notes: number
  activities_today: DashboardActivity[]
  upcoming_activities: DashboardActivity[]
  recent_notes: DashboardNote[]
}

const quickActions = [
  { label: 'Add Youth', path: '/youth/new', desc: 'Complete a new youth intake' },
  { label: 'Youth Directory', path: '/youth', desc: 'View your assigned caseload' },
  { label: 'Schedule Activity', path: '/calendar', desc: 'Add an event or appointment' },
  { label: 'Manage Services', path: '/services', desc: 'Review available program services' },
]

function formatDate(value?: string | null) {
  if (!value) return 'Date not listed'
  return new Date(`${value}T12:00:00`).toLocaleDateString(undefined, {
    weekday: 'short', month: 'short', day: 'numeric', year: 'numeric',
  })
}

function formatTime(value?: string | null) {
  if (!value) return 'Time not listed'
  const date = new Date(`2000-01-01T${value}`)
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

function StatCard({ label, value, helper }: { label: string; value: string | number; helper: string }) {
  return <div style={styles.statCard}>
    <p style={styles.statLabel}>{label}</p>
    <strong style={styles.statValue}>{value}</strong>
    <p style={styles.statHelper}>{helper}</p>
  </div>
}

function ActivityCard({ activity }: { activity: DashboardActivity }) {
  return <Link to="/calendar" style={styles.activityCard}>
    <div>
      <strong style={styles.activityTitle}>{activity.title}</strong>
      <p style={styles.activityMeta}>{formatDate(activity.activity_date)} · {formatTime(activity.start_time)}</p>
    </div>
    <span style={styles.badge}>{activity.location || 'Location pending'}</span>
  </Link>
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/mis/dashboard')
      .then((res) => setData(res.data))
      .catch(() => setError('Dashboard information could not be loaded.'))
  }, [])

  return <AppShell title="Dashboard" intro="Track youth participation, case management, upcoming contacts, activities, and program services.">
    {error && <div className="status status--error" style={{ marginBottom: '1rem' }}>{error}</div>}

    <section style={styles.statGrid}>
      <StatCard label="Active Youth" value={data?.active_youth ?? '—'} helper="Youth currently enrolled in the program" />
      <StatCard label="Contacts Due Today" value={data?.contacts_due_today ?? '—'} helper={`${data?.overdue_contacts ?? 0} additional contacts are overdue`} />
      <StatCard label="Activities This Week" value={data?.activities_this_week ?? '—'} helper="Events and appointments scheduled" />
      <StatCard label="Rolling Case Notes" value={data?.total_case_notes ?? '—'} helper="Case management timeline entries" />
    </section>

    <section style={styles.quickGrid}>
      {quickActions.map((card) => <Link key={card.label} to={card.path} style={styles.quickCard}>
        <div><strong>{card.label}</strong><p>{card.desc}</p></div><span>→</span>
      </Link>)}
    </section>

    <section style={styles.panel}>
      <div style={styles.sectionHeader}><div><p style={styles.eyebrow}>Daily schedule</p><h2>Today's Activities</h2></div></div>
      {!data || data.activities_today.length === 0
        ? <p style={styles.emptyText}>No activities are scheduled for today.</p>
        : <div style={styles.list}>{data.activities_today.map((a) => <ActivityCard key={a.id} activity={a} />)}</div>}
    </section>

    <section style={styles.twoColumn}>
      <div style={styles.panel}>
        <div style={styles.sectionHeader}><div><p style={styles.eyebrow}>Coming up</p><h2>Upcoming Activities</h2></div></div>
        {!data || data.upcoming_activities.length === 0
          ? <p style={styles.emptyText}>No upcoming activities.</p>
          : <div style={styles.list}>{data.upcoming_activities.map((a) => <ActivityCard key={a.id} activity={a} />)}</div>}
      </div>

      <div style={styles.panel}>
        <div style={styles.sectionHeader}><div><p style={styles.eyebrow}>Case management</p><h2>Recent Case Notes</h2></div></div>
        {!data || data.recent_notes.length === 0
          ? <p style={styles.emptyText}>No case notes have been added yet.</p>
          : <div style={styles.list}>{data.recent_notes.map((n) => <Link key={n.id} to={`/youth/${n.youth_id}`} style={styles.noteCard}>
              <div><strong>{n.youth_name}</strong><p>{n.note.slice(0, 100)}{n.note.length > 100 ? '…' : ''}</p><small>{n.created_by_name || 'Staff'} · {new Date(n.created_at).toLocaleString()}</small></div>
              <span style={styles.badge}>{n.note_type || 'Case note'}</span>
            </Link>)}</div>}
      </div>
    </section>
  </AppShell>
}

const styles: Record<string, React.CSSProperties> = {
  statGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1rem' },
  statCard: { border: '1px solid #ded3c4', borderRadius: '24px', padding: '1.4rem', background: '#fffdf9', boxShadow: '0 12px 30px rgba(0,0,0,0.06)' },
  statLabel: { margin: 0, color: '#6b6258', fontWeight: 700, letterSpacing: '.04em', textTransform: 'uppercase', fontSize: '.8rem' },
  statValue: { display: 'block', fontSize: '2.4rem', marginTop: '.35rem', color: '#111' },
  statHelper: { margin: '.35rem 0 0', color: '#6b6258' },
  quickGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1rem' },
  quickCard: { border: '1px solid #ded3c4', borderRadius: '20px', padding: '1rem', background: '#f6efe6', color: '#111', textDecoration: 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' },
  panel: { border: '1px solid #ded3c4', borderRadius: '26px', background: '#fff', padding: '1.4rem', marginBottom: '1rem', boxShadow: '0 10px 26px rgba(0,0,0,0.05)' },
  twoColumn: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1rem' },
  sectionHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' },
  eyebrow: { margin: 0, color: '#7a6d5f', textTransform: 'uppercase', letterSpacing: '.08em', fontWeight: 800, fontSize: '.75rem' },
  list: { display: 'grid', gap: '.75rem' },
  activityCard: { border: '1px solid #eadfce', borderRadius: '18px', padding: '1rem', background: '#fffaf3', color: '#111', textDecoration: 'none', display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'center' },
  activityTitle: { fontSize: '1.05rem' },
  activityMeta: { marginTop: '.3rem', color: '#6b6258' },
  noteCard: { borderBottom: '1px solid #eadfce', padding: '.85rem 0', color: '#111', display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'flex-start' },
  badge: { borderRadius: '999px', padding: '.35rem .7rem', background: '#111', color: '#fff', fontWeight: 800, fontSize: '.75rem', whiteSpace: 'nowrap' },
  emptyText: { color: '#6b6258', padding: '.5rem 0' },
}
