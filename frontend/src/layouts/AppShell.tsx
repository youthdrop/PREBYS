import TopNav from '../components/TopNav'

export default function AppShell({ title, intro, children }: { title: string; intro?: string; children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <TopNav />
      <main className="content-wrap">
        <section className="page-hero">
          <div>
            <p className="eyebrow">Youth Drop-In Center management information system</p>
            <h1>{title}</h1>
            {intro && <p className="hero-copy">{intro}</p>}
          </div>
        </section>
        {children}
      </main>
    </div>
  )
}
