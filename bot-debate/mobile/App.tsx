import React from "react";
import { NavigationContainer, DarkTheme } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import SetupScreen from "./src/screens/SetupScreen";
import DebateScreen from "./src/screens/DebateScreen";
import SummaryScreen from "./src/screens/SummaryScreen";

export type RootStackParamList = {
  Setup: undefined;
  Debate: { debateId: string; topic: string };
  Summary: { debateId: string; topic: string; summary: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const theme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: "#0f172a",
    card: "#0f172a",
    text: "#f8fafc",
    border: "#1e293b",
    primary: "#38bdf8",
  },
};

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer theme={theme}>
        <StatusBar style="light" />
        <Stack.Navigator
          initialRouteName="Setup"
          screenOptions={{
            headerStyle: { backgroundColor: "#0f172a" },
            headerTintColor: "#f8fafc",
            contentStyle: { backgroundColor: "#0f172a" },
          }}
        >
          <Stack.Screen
            name="Setup"
            component={SetupScreen}
            options={{ title: "Nouveau débat" }}
          />
          <Stack.Screen
            name="Debate"
            component={DebateScreen}
            options={{ title: "Transcript" }}
          />
          <Stack.Screen
            name="Summary"
            component={SummaryScreen}
            options={{ title: "Résumé" }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
