import { memo, useCallback, useState } from 'react'
import { Alert, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native'
import AppScaffold from '../components/AppScaffold'
import { theme } from '../constants/theme'
import { postJson } from '../services/api'

type FormState = {
  name: string
  case_numbers: string
  charges: string
  contact_person: string
  contact_person_telephone: string
  contact_person_email: string
}

type FieldProps = {
  label: string
  value: string
  onChangeText: (text: string) => void
  required?: boolean
  multiline?: boolean
  keyboardType?: 'default' | 'phone-pad' | 'email-address'
}

const Field = memo(function Field({
  label,
  value,
  onChangeText,
  required = false,
  multiline = false,
  keyboardType = 'default',
}: FieldProps) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>
        {label}
        {required ? ' *' : ''}
      </Text>
      <TextInput
        style={[styles.input, multiline && styles.textarea]}
        value={value}
        onChangeText={onChangeText}
        multiline={multiline}
        keyboardType={keyboardType}
        textAlignVertical={multiline ? 'top' : 'center'}
        autoCapitalize="sentences"
        autoCorrect={false}
        blurOnSubmit={!multiline}
      />
    </View>
  )
})

const EMPTY_FORM: FormState = {
  name: '',
  case_numbers: '',
  charges: '',
  contact_person: '',
  contact_person_telephone: '',
  contact_person_email: '',
}

export default function FamilyIntakeScreen() {
  const [form, setForm] = useState<FormState>(EMPTY_FORM)

  const updateField = useCallback((key: keyof FormState, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }, [])

  const submit = useCallback(async () => {
    if (!form.name || !form.contact_person || !form.contact_person_telephone || !form.contact_person_email) {
      Alert.alert('Required fields', 'Name, contact person, contact person telephone, and contact person email are required.')
      return
    }

    try {
      await postJson('/resources/public/family-intake', form)
      Alert.alert('Submitted', 'Your family intake has been submitted.')
      setForm(EMPTY_FORM)
    } catch (error: any) {
      Alert.alert('Error', error?.message || 'Something went wrong.')
    }
  }, [form])

  return (
    <AppScaffold title="Family intake" subtitle="Only the required family contact fields must be completed to submit.">
      <View style={styles.panel}>
        <Field
          label="Name"
          value={form.name}
          onChangeText={(text) => updateField('name', text)}
          required
        />

        <Field
          label="Case numbers"
          value={form.case_numbers}
          onChangeText={(text) => updateField('case_numbers', text)}
        />

        <Field
          label="Charges"
          value={form.charges}
          onChangeText={(text) => updateField('charges', text)}
          multiline
        />

        <Field
          label="Contact person"
          value={form.contact_person}
          onChangeText={(text) => updateField('contact_person', text)}
          required
        />

        <Field
          label="Contact person telephone"
          value={form.contact_person_telephone}
          onChangeText={(text) => updateField('contact_person_telephone', text)}
          required
          keyboardType="phone-pad"
        />

        <Field
          label="Contact person email"
          value={form.contact_person_email}
          onChangeText={(text) => updateField('contact_person_email', text)}
          required
          keyboardType="email-address"
        />
      </View>

      <TouchableOpacity style={styles.button} onPress={submit}>
        <Text style={styles.buttonText}>Submit</Text>
      </TouchableOpacity>
    </AppScaffold>
  )
}

const styles = StyleSheet.create({
  panel: {
    backgroundColor: theme.white,
    borderWidth: 1,
    borderColor: theme.line,
    borderRadius: 22,
    padding: 18,
    gap: 14,
  },
  field: {
    gap: 6,
  },
  label: {
    fontWeight: '800',
    color: theme.black,
  },
  input: {
    borderWidth: 1,
    borderColor: theme.line,
    backgroundColor: theme.white,
    borderRadius: 14,
    padding: 14,
  },
  textarea: {
    minHeight: 110,
  },
  button: {
    backgroundColor: theme.black,
    padding: 17,
    borderRadius: 18,
  },
  buttonText: {
    color: theme.white,
    fontWeight: '800',
    textAlign: 'center',
    fontSize: 17,
  },
})