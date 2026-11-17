# Cortana Project

A Raspberry Pi 5–based AI assistant with a custom animated, touchscreen interface inspired by Cortana from Halo. The system combines an OpenAI-powered conversational assistant with real-time weather information, animated Pygame states, and fullscreen Chromium access to services such as YouTube and Gemini.

The project is designed as a dedicated always-on assistant rather than a desktop application. A main Python process handles commands and AI requests while a separate Pygame process manages the character animation and display, allowing the interface to remain responsive while other features run independently.
