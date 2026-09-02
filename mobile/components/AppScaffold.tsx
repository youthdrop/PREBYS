import { ReactNode } from 'react'
import { SafeAreaView, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native'
import { router } from 'expo-router'
import { theme } from '../constants/theme'

export default function AppScaffold({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.navbar}>
        <TouchableOpacity onPress={() => router.replace('/')}><Text style={styles.navText}>Home</Text></TouchableOpacity>
        <View style={styles.brandWrap}>
          <View style={styles.seal}><Text style={styles.sealText}>FS</Text></View>
          <Text style={styles.brand}>Free SD</Text>
        </View>
        <TouchableOpacity onPress={() => router.canGoBack() ? router.back() : router.replace('/')}><Text style={styles.navText}>Back</Text></TouchableOpacity>
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.pageTitle}>{title}</Text>
        {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        {children}
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: theme.background },
  navbar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 18, paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: theme.line, backgroundColor: theme.white },
  navText: { color: theme.black, fontWeight: '700' },
  brandWrap: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  seal: { width: 34, height: 34, borderRadius: 10, backgroundColor: theme.black, alignItems: 'center', justifyContent: 'center' },
  sealText: { color: theme.white, fontWeight: '800' },
  brand: { fontSize: 18, fontWeight: '800', color: theme.black },
  container: { padding: 20, gap: 16, paddingBottom: 48 },
  pageTitle: { fontSize: 28, fontWeight: '800', color: theme.black },
  subtitle: { color: theme.muted, lineHeight: 22 },
})
