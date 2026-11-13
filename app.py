import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="PulseBoard | Sales Insights", page_icon="📊", layout="wide")
DATA = Path(__file__).parent / "data" / "sales_data.csv"

st.markdown("""
<style>
.block-container {padding-top:1.6rem; padding-bottom:2rem;}
[data-testid="stMetric"] {background:#ffffff; border:1px solid #e8edf5; padding:15px 16px; border-radius:13px;}
[data-testid="stSidebar"] {background:#f5f7fb;}
div[data-testid="stMetric"] label {font-weight:600;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file):
    data = pd.read_csv(file, parse_dates=["order_date"])
    return data

st.title("📊 PulseBoard — Interactive Business Dashboard")
st.caption("Monitor sales, profitability, products and regional performance in one place.")

with st.sidebar:
    st.header("Dashboard filters")
    uploaded = st.file_uploader("Upload sales CSV", type=["csv"])
    data = load_data(uploaded) if uploaded else load_data(DATA)
    required = {"order_id","order_date","city","category","product","quantity","revenue","profit"}
    missing = required - set(data.columns)
    if missing:
        st.error("Missing columns: " + ", ".join(sorted(missing)))
        st.stop()
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    data = data.dropna(subset=["order_date","city","category","revenue","profit"])
    min_date, max_date = data["order_date"].min().date(), data["order_date"].max().date()
    date_range = st.date_input("Order date range", value=(min_date,max_date), min_value=min_date, max_value=max_date)
    cities = st.multiselect("City", sorted(data.city.unique()), default=sorted(data.city.unique()))
    categories = st.multiselect("Category", sorted(data.category.unique()), default=sorted(data.category.unique()))
    st.caption("Filters update all metrics and charts.")

if isinstance(date_range, tuple) and len(date_range)==2:
    start, end = date_range
else:
    start, end = min_date, max_date

filtered = data[
    data["order_date"].dt.date.between(start,end) &
    data["city"].isin(cities) &
    data["category"].isin(categories)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Change the date, city or category selection.")
    st.stop()

revenue = filtered.revenue.sum()
profit = filtered.profit.sum()
orders = filtered.order_id.nunique()
units = filtered.quantity.sum()
margin = (profit/revenue*100) if revenue else 0

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Total revenue", f"₹{revenue:,.0f}")
k2.metric("Total profit", f"₹{profit:,.0f}")
k3.metric("Orders", f"{orders:,}")
k4.metric("Units sold", f"{units:,}")
k5.metric("Profit margin", f"{margin:.1f}%")

st.divider()
tab1,tab2,tab3 = st.tabs(["📈 Performance overview","🏙️ Product & regional insights","💡 Actionable insights"])

with tab1:
    a,b = st.columns([1.6,1])
    with a:
        st.subheader("Revenue trend")
        trend = filtered.set_index("order_date").resample("MS").agg(revenue=("revenue","sum"),profit=("profit","sum")).reset_index()
        fig = px.line(trend, x="order_date", y=["revenue","profit"], markers=True,
                      labels={"order_date":"Month","value":"Amount (₹)","variable":"Metric"},
                      color_discrete_sequence=["#2563eb","#16a34a"])
        fig.update_layout(legend_title_text="", margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig,use_container_width=True)
    with b:
        st.subheader("Revenue by category")
        cat = filtered.groupby("category",as_index=False).revenue.sum().sort_values("revenue",ascending=False)
        fig = px.pie(cat, names="category", values="revenue", hole=.52)
        fig.update_layout(margin=dict(l=0,r=0,t=20,b=0), legend_title_text="")
        st.plotly_chart(fig,use_container_width=True)

    st.subheader("Sales volume and profitability")
    monthly = filtered.set_index("order_date").resample("MS").agg(
        orders=("order_id","nunique"), units=("quantity","sum"), profit=("profit","sum")
    ).reset_index()
    fig = px.bar(monthly, x="order_date", y="orders", labels={"order_date":"Month","orders":"Orders"},
                 color="orders", color_continuous_scale="Blues")
    fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False)
    st.plotly_chart(fig,use_container_width=True)

with tab2:
    left,right = st.columns(2)
    with left:
        st.subheader("Revenue by city")
        city = filtered.groupby("city",as_index=False).agg(revenue=("revenue","sum"),profit=("profit","sum"))
        city = city.sort_values("revenue",ascending=False)
        fig = px.bar(city, x="city", y="revenue", color="profit", color_continuous_scale="Tealgrn",
                     labels={"revenue":"Revenue (₹)","profit":"Profit (₹)"})
        fig.update_layout(margin=dict(l=0,r=0,t=15,b=0))
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.subheader("Top products")
        product = filtered.groupby("product",as_index=False).agg(revenue=("revenue","sum"),units=("quantity","sum"))
        product = product.sort_values("revenue",ascending=False).head(10)
        fig = px.bar(product.sort_values("revenue"), x="revenue", y="product", orientation="h",
                     color="revenue", color_continuous_scale="Blues",
                     labels={"revenue":"Revenue (₹)","product":"Product"})
        fig.update_layout(margin=dict(l=0,r=0,t=15,b=0))
        st.plotly_chart(fig,use_container_width=True)

    st.subheader("Category performance")
    performance = filtered.groupby("category",as_index=False).agg(
        revenue=("revenue","sum"),profit=("profit","sum"),units=("quantity","sum")
    )
    performance["profit_margin_pct"] = (performance.profit/performance.revenue*100).round(1)
    st.dataframe(performance.sort_values("revenue",ascending=False),use_container_width=True,hide_index=True)

with tab3:
    st.subheader("What the selected data is telling you")
    city_totals = filtered.groupby("city").revenue.sum().sort_values(ascending=False)
    category_totals = filtered.groupby("category").revenue.sum().sort_values(ascending=False)
    product_totals = filtered.groupby("product").revenue.sum().sort_values(ascending=False)
    best_city = city_totals.index[0]
    best_cat = category_totals.index[0]
    best_product = product_totals.index[0]
    low_margin = filtered.groupby("category").apply(
        lambda x: (x.profit.sum()/x.revenue.sum()*100) if x.revenue.sum() else 0,
        include_groups=False
    ).sort_values()
    st.markdown(f"- **Top city:** {best_city} contributes the highest revenue (₹{city_totals.iloc[0]:,.0f}).")
    st.markdown(f"- **Leading category:** {best_cat} is the strongest category by revenue (₹{category_totals.iloc[0]:,.0f}).")
    st.markdown(f"- **Top product:** {best_product} generates the highest product revenue (₹{product_totals.iloc[0]:,.0f}).")
    if len(low_margin):
        st.markdown(f"- **Margin watch:** {low_margin.index[0]} has the lowest category profit margin ({low_margin.iloc[0]:.1f}%). Review discounting and costs.")
    st.markdown("- **Suggested action:** Prioritise inventory and campaigns in the strongest city/category, while reviewing pricing and costs in the lowest-margin category.")

st.divider()
st.subheader("Filtered transaction details")
st.dataframe(filtered.sort_values("order_date",ascending=False),use_container_width=True,hide_index=True)
st.download_button("⬇️ Download filtered report", filtered.to_csv(index=False).encode("utf-8"),
                   "filtered_sales_report.csv","text/csv")
st.caption("Demo dataset is synthetic and intended for learning. Replace it with verified business data before making operational decisions.")
