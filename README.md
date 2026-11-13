# PulseBoard — Interactive Business Dashboard

PulseBoard is an interactive sales analytics dashboard built with Python, Streamlit, Pandas and Plotly. It turns sales records into clear performance metrics, trends, comparisons and actionable insights.

## Features
- Interactive filters for date range, city and product category
- KPI cards: revenue, profit, orders, units sold and profit margin
- Monthly revenue and profit trend
- Revenue share by category
- Monthly order volume
- City-wise revenue and profit comparison
- Top 10 products
- Category performance table
- Automatically generated business insights
- Upload your own CSV and download filtered data

## Folder structure
```text
interactive_dashboard_project/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── sales_data.csv
```

## Run in VS Code (Windows)
1. Extract the ZIP file.
2. Open the extracted `interactive_dashboard_project` folder in VS Code.
3. Open Terminal → New Terminal.
4. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Run:
   ```bash
   python -m streamlit run app.py
   ```
7. Open the local URL printed in the terminal (usually http://localhost:8501).

## Upload your own data
Use the sidebar CSV uploader. Your CSV must include:
- `order_id`
- `order_date` (YYYY-MM-DD recommended)
- `city`
- `category`
- `product`
- `quantity`
- `revenue`
- `profit`

Optional columns from the sample file include `unit_price`, `discount_pct` and `cost`.

## GitHub upload
Create an empty GitHub repository, extract this ZIP, and open the project folder in VS Code. Then run:
```bash
git init
git add .
git commit -m "Add interactive business dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
Replace the remote URL with your repository URL.

## Dataset note
`data/sales_data.csv` is synthetic sample data generated for demonstration. Do not use it to make real business decisions. Replace it with validated sales records for a real analysis.
