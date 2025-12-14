# Minimal CLI UI for Adaptive ML Tutor

import sys

# Add member paths
sys.path.append(r"C:\TEAM-42\member4")
sys.path.append(r"C:\TEAM-42\member3")
sys.path.append(r"C:\TEAM-42\member2")

from main import run_system

print("\n==============================")
print("   ADAPTIVE ML TUTOR (DEMO)   ")
print("==============================\n")

user_name = input("Enter your name: ")
print(f"\nWelcome, {user_name} 👋\n")

print("Starting adaptive learning session...\n")

# Run full system
run_system()

print("\nThank you for using Adaptive ML Tutor!")
