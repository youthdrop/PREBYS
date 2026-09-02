import { router } from 'expo-router'
import { Image, StyleSheet, Text, TouchableOpacity, View } from 'react-native'

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Image
          source={require('../assets/logo.png')}
          style={styles.logo}
          resizeMode="contain"
        />

        <Text style={styles.title}>Free SD Mobile</Text>
        <Text style={styles.copy}>
          Choose the form you need below.
        </Text>
      </View>

      <TouchableOpacity style={styles.button} onPress={() => router.push('/family-intake')}>
        <Text style={styles.buttonText}>Families</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.buttonAlt} onPress={() => router.push('/volunteer-signup')}>
        <Text style={styles.buttonTextAlt}>Volunteers</Text>
      </TouchableOpacity>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
    justifyContent: 'center',
    gap: 16,
  },
  card: {
    borderWidth: 1,
    borderColor: '#e5e5e5',
    borderRadius: 24,
    padding: 20,
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  logo: {
    width: 120,
    height: 120,
    marginBottom: 12,
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    color: '#111',
    textAlign: 'center',
  },
  copy: {
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
    marginTop: 8,
  },
  button: {
    backgroundColor: '#111',
    padding: 18,
    borderRadius: 18,
  },
  buttonAlt: {
    backgroundColor: '#f5efe6',
    padding: 18,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#e5e5e5',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '800',
    fontSize: 18,
    textAlign: 'center',
  },
  buttonTextAlt: {
    color: '#111',
    fontWeight: '800',
    fontSize: 18,
    textAlign: 'center',
  },
})