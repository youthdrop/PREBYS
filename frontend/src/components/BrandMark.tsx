export default function BrandMark({ subtitle = 'Court support & management information system' }: { subtitle?: string }) {
  return (
    <div className="brand-mark">
      <div className="brand-mark__seal">FS</div>
      <div>
        <div className="brand-mark__name">Youth Drop-In Center</div>
        <div className="brand-mark__subtitle">{subtitle}</div>
      </div>
    </div>
  )
}
