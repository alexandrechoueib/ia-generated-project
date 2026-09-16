import React from "react";
import { StyleSheet, Text, View } from "react-native";
import type { Message } from "../types/debate";

const COLORS = {
  grok: { bg: "#1e3a5f", border: "#38bdf8", label: "#7dd3fc" },
  gpt: { bg: "#3b1f4a", border: "#c084fc", label: "#e9d5ff" },
  summary: { bg: "#1f2937", border: "#94a3b8", label: "#cbd5e1" },
};

const LABELS = {
  grok: "Grok — POUR",
  gpt: "GPT — CONTRE",
  summary: "Résumé neutre",
};

export function Bubble({ message }: { message: Message }) {
  const palette = COLORS[message.speaker];
  const align = message.speaker === "gpt" ? "flex-end" : "flex-start";

  return (
    <View style={[styles.wrap, { alignSelf: align }]}>
      <Text style={[styles.label, { color: palette.label }]}>
        {LABELS[message.speaker]}
      </Text>
      <View
        style={[
          styles.bubble,
          {
            backgroundColor: palette.bg,
            borderColor: palette.border,
          },
        ]}
      >
        <Text style={styles.content}>{message.content}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    maxWidth: "92%",
    marginVertical: 8,
  },
  label: {
    fontSize: 12,
    fontWeight: "700",
    marginBottom: 4,
    marginHorizontal: 4,
  },
  bubble: {
    borderWidth: 1,
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  content: {
    color: "#f8fafc",
    fontSize: 15,
    lineHeight: 22,
  },
});
