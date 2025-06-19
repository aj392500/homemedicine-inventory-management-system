# Medicine Inventory Manager

A web application to help manage medicine inventory for diabetic patients with varying purchase frequencies and dosage schedules.

## Features

- **Medicine Management**: Add, edit, and delete medicines with detailed information
- **Inventory Tracking**: Track current stock levels with automatic calculations
- **Purchase Frequencies**: Support for different purchase cycles (monthly, 3-monthly, etc.)
- **Low Stock Alerts**: Visual alerts when medicines are running low
- **Purchase History**: Complete record of all medicine purchases
- **Dosage Tracking**: Track how often medicines are taken (daily, twice daily, etc.)
- **Stock Estimation**: Automatic calculation of days remaining based on usage

## Installation

1. Clone or download this repository
2. Install Python 3.7 or higher
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your web browser and go to `http://localhost:5000`

3. Start adding your medicines with their details:
   - Medicine name and dosage
   - How often it's taken (daily, twice daily, etc.)
   - Purchase frequency (monthly, 3-monthly, etc.)
   - Number of pills per purchase
   - Low stock threshold for alerts

4. Record purchases to update inventory levels

5. Monitor inventory status and receive low stock alerts

## Database

The application uses SQLite database (`medicine_inventory.db`) which will be created automatically when you first run the app.

## Medicine Information Fields

- **Name**: Medicine name
- **Dosage**: Strength/dosage (e.g., 500mg)
- **Taking Frequency**: How often the medicine is taken
- **Purchase Frequency**: How often you buy the medicine (30, 60, 90, 180 days)
- **Pills per Purchase**: Number of pills bought each time
- **Low Stock Threshold**: Alert when stock falls below this number
- **Current Stock**: Current number of pills available

## Purchase Tracking

- Record each purchase with quantity and optional cost
- Automatic stock level updates
- Purchase history with dates and notes
- Cost tracking for budgeting purposes

## Alerts and Notifications

- Visual alerts for low stock medicines
- Estimated days remaining calculation
- Next purchase date suggestions based on purchase frequency