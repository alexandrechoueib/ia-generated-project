import React, { useMemo, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { createDebate, getApiUrl } from "../api/client";
import type { Complexity } from "../types/debate";
import type { RootStackParamList } from "../../App";

type Props = NativeStackScreenProps<RootStackParamList, "Setup">;

const COMPLEXITIES: { value: Complexity; label: string }[] = [
  { value: "tout_public", label: "Tout public" },
  { value: "intermediaire", label: "Intermédiaire" },
  { value: "expert", label: "Expert" },
];

const MESSAGE_OPTIONS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20];

export default function SetupScreen({ navigation }: Props) {
  const [topic, setTopic] = useState("");
  const [totalMessages, setTotalMessages] = useState(6);
  const [complexity, setComplexity] = useState<Complexity>("tout_public");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = useMemo(
    () => topic.trim().length >= 3 && !loading,
    [topic, loading]
  );

  async function onStart() {
    setError(null);
    setLoading(true);
    try {
      const created = await createDebate({
        topic: topic.trim(),
        total_messages: totalMessages,
        complexity,
      });
      navigation.replace("Debate", { debateId: created.id, topic: created.topic });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      keyboardShouldPersistTaps="handled"
    >
      <Text style={styles.title}>Débat Grok vs GPT</Text>
      <Text style={styles.subtitle}>
        Grok défend le POUR · GPT défend le CONTRE · résumé neutre à la fin
      </Text>
      <Text style={styles.meta}>API : {getApiUrl()}</Text>

      <Text style={styles.label}>Sujet du débat</Text>
      <TextInput
        style={styles.input}
        placeholder="Ex. Faut-il interdire les voitures en centre-ville ?"
        placeholderTextColor="#64748b"
        value={topic}
        onChangeText={setTopic}
        multiline
      />

      <Text style={styles.label}>Nombre de messages (pair)</Text>
      <View style={styles.row}>
        {MESSAGE_OPTIONS.map((n) => (
          <Pressable
            key={n}
            onPress={() => setTotalMessages(n)}
            style={[styles.chip, totalMessages === n && styles.chipActive]}
          >
            <Text
              style={[
                styles.chipText,
                totalMessages === n && styles.chipTextActive,
              ]}
            >
              {n}
            </Text>
          </Pressable>
        ))}
      </View>

      <Text style={styles.label}>Complexité</Text>
      <View style={styles.row}>
        {COMPLEXITIES.map((c) => (
          <Pressable
            key={c.value}
            onPress={() => setComplexity(c.value)}
            style={[styles.chip, complexity === c.value && styles.chipActive]}
          >
            <Text
              style={[
                styles.chipText,
                complexity === c.value && styles.chipTextActive,
              ]}
            >
              {c.label}
            </Text>
          </Pressable>
        ))}
      </View>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <Pressable
        style={[styles.button, !canSubmit && styles.buttonDisabled]}
        disabled={!canSubmit}
        onPress={onStart}
      >
        {loading ? (
          <ActivityIndicator color="#0f172a" />
        ) : (
          <Text style={styles.buttonText}>Lancer le débat</Text>
        )}
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  content: { padding: 20, paddingBottom: 40 },
  title: {
    color: "#f8fafc",
    fontSize: 28,
    fontWeight: "800",
    marginBottom: 8,
  },
  subtitle: { color: "#94a3b8", fontSize: 14, marginBottom: 6, lineHeight: 20 },
  meta: { color: "#64748b", fontSize: 12, marginBottom: 24 },
  label: {
    color: "#e2e8f0",
    fontSize: 14,
    fontWeight: "700",
    marginBottom: 8,
    marginTop: 12,
  },
  input: {
    backgroundColor: "#1e293b",
    borderColor: "#334155",
    borderWidth: 1,
    borderRadius: 12,
    color: "#f8fafc",
    padding: 14,
    minHeight: 88,
    textAlignVertical: "top",
    fontSize: 16,
  },
  row: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: {
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#334155",
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: "#1e293b",
  },
  chipActive: {
    backgroundColor: "#38bdf8",
    borderColor: "#38bdf8",
  },
  chipText: { color: "#cbd5e1", fontWeight: "600" },
  chipTextActive: { color: "#0f172a" },
  button: {
    marginTop: 28,
    backgroundColor: "#38bdf8",
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: "center",
  },
  buttonDisabled: { opacity: 0.5 },
  buttonText: { color: "#0f172a", fontWeight: "800", fontSize: 16 },
  error: {
    color: "#fda4af",
    marginTop: 16,
    backgroundColor: "#4c0519",
    padding: 12,
    borderRadius: 10,
  },
});
