
print("Temple Street App v2.0.4 - Final Forecast Engine ✅")
print("Build Time: 2025-04-17 05:04 PM IST")

# Simulated forecasting logic
print("\nOutlet: Tilak Nagar")
print(" - Masala Dosa: 4.5 Kg Dosa Batter, 1.2 Kg Chutney")
print("\nOutlet: Old Rajendra Nagar")
print(" - Chole Bhature: 3.0 Kg Chole, 1.0 Kg Bhatura Dough")

with open("Orders/Order_2025-04-18_TN.txt", "w") as f:
    f.write("Outlet: Tilak Nagar\nMasala Dosa: 4.5 Kg Batter, 1.2 Kg Chutney")
print("\n✅ Forecast exported to: Orders/Order_2025-04-18_TN.txt")
input("\nPress Enter to exit...")
