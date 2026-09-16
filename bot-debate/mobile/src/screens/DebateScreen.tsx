import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Bubble } from "../components/Bubble";
import { getDebate, runDebate } from "../api/client";
import type { Debate, Message } from "../types/debate";
import type { RootStackParamList } from "../../App";

type Props = NativeStackScreenProps<RootStackParamList, "Debate">;

export default function DebateScreen({ navigation, route }: Props) {
  const { debateId, topic } = route.params;
  const [debate, setDebate] = useState<Debate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const scrollRef = useRef<ScrollView>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    try {
      const d = await getDebate(debateId);
      setDebate(d);
      setError(d.error || null);
      if (d.status === "completed") {
        if (pollRef.current) {
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur de chargement");
    }
  }, [debateId]);

  const startRun = useCallback(async () => {
    setRunning(true);
    setError(null);
    try {
      const d = await runDebate(debateId);
      setDebate(d);
      if (d.error) setError(d.error);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Échec du lancement");
      await refresh();
    } finally {
      setRunning(false);
    }
  }, [debateId, refresh]);

  useEffect(() => {
    void refresh();
    pollRef.current = setInterval(() => {
      void refresh();
    }, 2500);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [refresh]);

  useEffect(() => {
    if (debate?.status === "created" && !running) {
      void startRun();
    }
  }, [debate?.status, running, startRun]);

  useEffect(() => {
    scrollRef.current?.scrollToEnd({ animated: true });
  }, [debate?.messages.length]);

  const bubbles: Message[] =
    debate?.messages.filter((m) => m.speaker !== "summary") || [];

  const isDone = debate?.status === "completed";
  const isFailed = debate?.status === "failed";
  const isBusy =
    running || debate?.status === "running" || debate?.status === "created";

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.topic} numberOfLines={2}>
          {topic}
        </Text>
        <Text style={styles.status}>
          {isDone
            ? "Terminé"
            : isFailed
              ? "Échec"
              : isBusy
                ? "Débat en cours…"
                : debate?.status || "…"}
        </Text>
      </View>

      <ScrollView
        ref={scrollRef}
        style={styles.list}
        contentContainerStyle={styles.listContent}
      >
        {bubbles.length === 0 && isBusy ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator color="#38bdf8" size="large" />
            <Text style={styles.loadingText}>
              Les modèles préparent leurs arguments…
            </Text>
          </View>
        ) : null}

        {bubbles.map((m) => (
          <Bubble key={`${m.speaker}-${m.index}`} message={m} />
        ))}

        {error ? <Text style={styles.error}>{error}</Text> : null}
      </ScrollView>

      <View style={styles.footer}>
        {isFailed ? (
          <Pressable style={styles.secondary} onPress={() => void startRun()}>
            <Text style={styles.secondaryText}>Réessayer</Text>
          </Pressable>
        ) : null}
        {isDone ? (
          <Pressable
            style={styles.primary}
            onPress={() =>
              navigation.navigate("Summary", {
                debateId,
                topic,
                summary: debate?.summary || "",
              })
            }
          >
            <Text style={styles.primaryText}>Voir le résumé</Text>
          </Pressable>
        ) : (
          <Pressable
            style={styles.ghost}
            onPress={() => navigation.navigate("Setup")}
          >
            <Text style={styles.ghostText}>Nouveau débat</Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  header: {
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#1e293b",
  },
  topic: { color: "#f8fafc", fontSize: 18, fontWeight: "700" },
  status: { color: "#94a3b8", marginTop: 4, fontSize: 13 },
  list: { flex: 1 },
  listContent: { padding: 16, paddingBottom: 24 },
  loadingBox: { alignItems: "center", marginTop: 48, gap: 16 },
  loadingText: { color: "#94a3b8", textAlign: "center" },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#1e293b",
    gap: 10,
  },
  primary: {
    backgroundColor: "#38bdf8",
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: "center",
  },
  primaryText: { color: "#0f172a", fontWeight: "800", fontSize: 16 },
  secondary: {
    backgroundColor: "#1e293b",
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#334155",
  },
  secondaryText: { color: "#e2e8f0", fontWeight: "700" },
  ghost: { alignItems: "center", paddingVertical: 8 },
  ghostText: { color: "#94a3b8" },
  error: {
    color: "#fda4af",
    backgroundColor: "#4c0519",
    padding: 12,
    borderRadius: 10,
    marginTop: 12,
  },
});
