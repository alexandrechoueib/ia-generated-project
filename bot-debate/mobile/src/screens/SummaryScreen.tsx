import React from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { RootStackParamList } from "../../App";

type Props = NativeStackScreenProps<RootStackParamList, "Summary">;

export default function SummaryScreen({ navigation, route }: Props) {
  const { topic, summary } = route.params;

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>Résumé neutre</Text>
        <Text style={styles.topic}>{topic}</Text>
        <View style={styles.card}>
          <Text style={styles.summary}>
            {summary?.trim() || "Aucun résumé disponible."}
          </Text>
        </View>
      </ScrollView>
      <View style={styles.footer}>
        <Pressable
          style={styles.primary}
          onPress={() => navigation.navigate("Setup")}
        >
          <Text style={styles.primaryText}>Nouveau débat</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  content: { padding: 20, paddingBottom: 40 },
  kicker: {
    color: "#38bdf8",
    fontWeight: "800",
    textTransform: "uppercase",
    letterSpacing: 1,
    fontSize: 12,
    marginBottom: 8,
  },
  topic: {
    color: "#f8fafc",
    fontSize: 22,
    fontWeight: "800",
    marginBottom: 16,
  },
  card: {
    backgroundColor: "#1e293b",
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#334155",
    padding: 16,
  },
  summary: { color: "#e2e8f0", fontSize: 16, lineHeight: 24 },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#1e293b",
  },
  primary: {
    backgroundColor: "#38bdf8",
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: "center",
  },
  primaryText: { color: "#0f172a", fontWeight: "800", fontSize: 16 },
});
