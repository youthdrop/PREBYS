import { useState } from 'react'
import { Alert, Pressable, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native'
import AppScaffold from '../components/AppScaffold'
import { theme } from '../constants/theme'
import { postJson } from '../services/api'

const courts = ['Central', 'El Cajon', 'Vista', 'Southbay']

export default function VolunteerSignupScreen() {
  const [form, setForm] = useState({ name: '', email: '', telephone: '', availability: '', travel_courts: '' })
  const [selectedCourts, setSelectedCourts] = useState<string[]>([])

  const toggleCourt = (court: string) => {
    const next = selectedCourts.includes(court)
      ? selectedCourts.filter((item) => item !== court)
      : [...selectedCourts, court]
    setSelectedCourts(next)
    setForm({ ...form, travel_courts: next.join(', ') })
  }

  const submit = async () => {
    try {
      await postJson('/resources/public/volunteer-signup', form)
      Alert.alert('Submitted', 'Volunteer sign-up received.')
      setForm({ name: '', email: '', telephone: '', availability: '', travel_courts: '' })
      setSelectedCourts([])
    } catch (error: any) {
      Alert.alert('Error', error.message)
    }
  }

  return (
    <AppScaffold title="Volunteer sign up" subtitle="Tell us how to reach you, when you are available, and which courts you can travel to.">
      <View style={styles.panel}>
        <Field label="Name" value={form.name} onChangeText={(text) => setForm({ ...form, name: text })} />
        <Field label="Email" value={form.email} onChangeText={(text) => setForm({ ...form, email: text })} keyboardType="email-address" />
        <Field label="Telephone" value={form.telephone} onChangeText={(text) => setForm({ ...form, telephone: text })} keyboardType="phone-pad" />
        <Field label="Days and times available" value={form.availability} onChangeText={(text) => setForm({ ...form, availability: text })} multiline />
        <View style={styles.field}>
          <Text style={styles.label}>Courts they can travel to</Text>
          <View style={styles.courtWrap}>
            {courts.map((court) => {
              const active = selectedCourts.includes(court)
              return (
                <Pressable key={court} onPress={() => toggleCourt(court)} style={[styles.pill, active && styles.pillActive]}>
                  <Text style={[styles.pillText, active && styles.pillTextActive]}>{court}</Text>
                </Pressable>
              )
            })}
          </View>
        </View>
      </View>
      <TouchableOpacity style={styles.button} onPress={submit}><Text style={styles.buttonText}>Submit</Text></TouchableOpacity>
    </AppScaffold>
  )
}

function Field({ label, value, onChangeText, multiline = false, keyboardType = 'default' as const }: any) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        style={[styles.input, multiline && styles.textarea]}
        value={value}
        onChangeText={onChangeText}
        multiline={multiline}
        keyboardType={keyboardType}
        textAlignVertical={multiline ? 'top' : 'center'}
      />
    </View>
  )
}

const styles = StyleSheet.create({
  panel: { backgroundColor: theme.white, borderWidth: 1, borderColor: theme.line, borderRadius: 22, padding: 18, gap: 14 },
  field: { gap: 6 },
  label: { fontWeight: '800', color: theme.black },
  input: { borderWidth: 1, borderColor: theme.line, backgroundColor: theme.white, borderRadius: 14, padding: 14 },
  textarea: { minHeight: 100 },
  courtWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  pill: { paddingHorizontal: 14, paddingVertical: 10, borderRadius: 999, backgroundColor: theme.cream, borderWidth: 1, borderColor: theme.line },
  pillActive: { backgroundColor: theme.black, borderColor: theme.black },
  pillText: { color: theme.black, fontWeight: '700' },
  pillTextActive: { color: theme.white },
  button: { backgroundColor: theme.black, padding: 17, borderRadius: 18 },
  buttonText: { color: theme.white, fontWeight: '800', textAlign: 'center', fontSize: 17 },
})
