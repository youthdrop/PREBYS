import {
  FormEvent,
  useCallback,
  useEffect,
  useState,
} from 'react'

import api from '../api/client'


type CurriculumSession = {
  value: string
  week: string
  title: string
}

type Stipend = {
  id: number
  youth_id: number
  session_date: string
  curriculum_session: string
  attendance_status: string
  amount: number
  payment_status: string
  payment_date?: string | null
  notes?: string | null
  created_by_name?: string | null
  created_at: string
}

type StipendResponse = {
  records: Stipend[]
  total: number
  paid_total: number
  pending_total: number
}

type Props = {
  youthId: number
}


export default function YouthStipends({
  youthId,
}: Props) {
  const today = new Date()
    .toISOString()
    .slice(0, 10)

  const [curriculum, setCurriculum] = useState<
    CurriculumSession[]
  >([])

  const [stipends, setStipends] = useState<
    Stipend[]
  >([])

  const [total, setTotal] = useState(0)
  const [paidTotal, setPaidTotal] = useState(0)
  const [pendingTotal, setPendingTotal] = useState(0)

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [saving, setSaving] = useState(false)

  const [form, setForm] = useState({
    session_date: today,
    curriculum_session: '',
    attendance_status: 'completed',
    amount: '50.00',
    payment_status: 'pending',
    payment_date: '',
    notes: '',
  })

  const loadStipends = useCallback(async () => {
    const response = await api.get<StipendResponse>(
      `/mis/youth/${youthId}/stipends`
    )

    setStipends(response.data.records)
    setTotal(response.data.total)
    setPaidTotal(response.data.paid_total)
    setPendingTotal(response.data.pending_total)
  }, [youthId])

  useEffect(() => {
    const load = async () => {
      try {
        const curriculumResponse = await api.get<
          CurriculumSession[]
        >('/mis/curriculum')

        setCurriculum(curriculumResponse.data)

        await loadStipends()
      } catch (err: any) {
        setError(
          err?.response?.data?.detail
          || 'Unable to load stipend information.'
        )
      }
    }

    load()
  }, [loadStipends])

  const submit = async (
    event: FormEvent,
  ) => {
    event.preventDefault()

    setError('')
    setSuccess('')
    setSaving(true)

    try {
      await api.post(
        `/mis/youth/${youthId}/stipends`,
        {
          session_date: form.session_date,
          curriculum_session:
            form.curriculum_session,
          attendance_status:
            form.attendance_status,
          amount: Number(form.amount),
          payment_status:
            form.payment_status,
          payment_date:
            form.payment_date || null,
          notes:
            form.notes.trim() || null,
        }
      )

      setSuccess(
        'Stipend record saved successfully.'
      )

      setForm({
        session_date: today,
        curriculum_session: '',
        attendance_status: 'completed',
        amount: '50.00',
        payment_status: 'pending',
        payment_date: '',
        notes: '',
      })

      await loadStipends()
    } catch (err: any) {
      setError(
        err?.response?.data?.detail
        || 'Unable to save stipend.'
      )
    } finally {
      setSaving(false)
    }
  }

  const deleteStipend = async (
    stipendId: number,
  ) => {
    const confirmed = window.confirm(
      'Delete this stipend record?'
    )

    if (!confirmed) {
      return
    }

    try {
      await api.delete(
        `/mis/stipends/${stipendId}`
      )

      await loadStipends()
    } catch (err: any) {
      setError(
        err?.response?.data?.detail
        || 'Unable to delete stipend.'
      )
    }
  }

  return (
    <section className="panel stipend-panel">
      <div className="stipend-heading">
        <div>
          <p className="eyebrow">
            Fellowship stipend tracking
          </p>

          <h2>
            Stipends & Curriculum
          </h2>

          <p className="muted">
            Record the curriculum session completed
            by this youth and track stipend payment.
          </p>
        </div>

        <div className="stipend-summary">
          <div>
            <span>Total</span>
            <strong>
              ${total.toFixed(2)}
            </strong>
          </div>

          <div>
            <span>Paid</span>
            <strong>
              ${paidTotal.toFixed(2)}
            </strong>
          </div>

          <div>
            <span>Pending</span>
            <strong>
              ${pendingTotal.toFixed(2)}
            </strong>
          </div>
        </div>
      </div>

      <form
        className="form-grid stipend-form"
        onSubmit={submit}
      >
        <label>
          Session date

          <input
            type="date"
            required
            value={form.session_date}
            onChange={(event) => {
              setForm({
                ...form,
                session_date:
                  event.target.value,
              })
            }}
          />
        </label>

        <label className="full-span">
          Curriculum session

          <select
            required
            value={form.curriculum_session}
            onChange={(event) => {
              setForm({
                ...form,
                curriculum_session:
                  event.target.value,
              })
            }}
          >
            <option value="">
              Select curriculum session
            </option>

            {curriculum.map((session) => (
              <option
                key={session.value}
                value={session.value}
              >
                {session.value}
              </option>
            ))}
          </select>
        </label>

        <label>
          Attendance / completion

          <select
            value={form.attendance_status}
            onChange={(event) => {
              setForm({
                ...form,
                attendance_status:
                  event.target.value,
              })
            }}
          >
            <option value="completed">
              Completed
            </option>

            <option value="attended">
              Attended
            </option>

            <option value="partial">
              Partially completed
            </option>

            <option value="excused">
              Excused
            </option>

            <option value="missed">
              Missed
            </option>
          </select>
        </label>

        <label>
          Stipend amount

          <input
            type="number"
            min="0"
            step="0.01"
            required
            value={form.amount}
            onChange={(event) => {
              setForm({
                ...form,
                amount: event.target.value,
              })
            }}
          />
        </label>

        <label>
          Payment status

          <select
            value={form.payment_status}
            onChange={(event) => {
              setForm({
                ...form,
                payment_status:
                  event.target.value,
              })
            }}
          >
            <option value="pending">
              Pending
            </option>

            <option value="approved">
              Approved
            </option>

            <option value="paid">
              Paid
            </option>

            <option value="held">
              Held
            </option>
          </select>
        </label>

        <label>
          Payment date

          <input
            type="date"
            value={form.payment_date}
            onChange={(event) => {
              setForm({
                ...form,
                payment_date:
                  event.target.value,
              })
            }}
          />
        </label>

        <label className="full-span">
          Notes

          <textarea
            rows={3}
            value={form.notes}
            onChange={(event) => {
              setForm({
                ...form,
                notes: event.target.value,
              })
            }}
            placeholder={
              'Optional stipend or eligibility notes'
            }
          />
        </label>

        {error && (
          <div
            className={
              'status status--error full-span'
            }
          >
            {error}
          </div>
        )}

        {success && (
          <div
            className={
              'status status--success full-span'
            }
          >
            {success}
          </div>
        )}

        <div className="full-span">
          <button
            type="submit"
            disabled={
              saving
              || !form.curriculum_session
            }
          >
            {saving
              ? 'Saving...'
              : 'Add stipend'}
          </button>
        </div>
      </form>

      <div className="stipend-history">
        <h3>Stipend History</h3>

        {stipends.length === 0 ? (
          <p className="muted">
            No stipend records have been added
            for this youth.
          </p>
        ) : (
          <div className="stipend-table-wrap">
            <table className="stipend-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Curriculum</th>
                  <th>Completion</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Paid</th>
                  <th>Added by</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {stipends.map((stipend) => (
                  <tr key={stipend.id}>
                    <td>
                      {stipend.session_date}
                    </td>

                    <td>
                      {stipend.curriculum_session}
                    </td>

                    <td>
                      {stipend.attendance_status}
                    </td>

                    <td>
                      ${Number(
                        stipend.amount
                      ).toFixed(2)}
                    </td>

                    <td>
                      {stipend.payment_status}
                    </td>

                    <td>
                      {stipend.payment_date
                        || '—'}
                    </td>

                    <td>
                      {stipend.created_by_name
                        || 'Staff'}
                    </td>

                    <td>
                      <button
                        type="button"
                        className="danger-button"
                        onClick={() => {
                          deleteStipend(
                            stipend.id
                          )
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}