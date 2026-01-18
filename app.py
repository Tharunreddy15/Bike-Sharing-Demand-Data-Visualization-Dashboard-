import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------
# LOAD DATA
# -----------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['hour']  = df['datetime'].dt.hour
    df['weekday'] = df['datetime'].dt.day_name()

    # season mapping
    season_map = {1:'spring', 2:'summer', 3:'fall', 4:'winter'}
    df['season_name'] = df['season'].map(season_map)

    # weather mapping
    weather_map = {1:'Clear', 2:'Mist/Cloudy', 3:'Light Rain/Snow', 4:'Heavy Rain/Fog'}
    df['weather_name'] = df['weather'].map(weather_map)

    # day_period split
    df['day_period'] = pd.cut(
        df['hour'],
        bins=[0, 6, 12, 18, 24],
        labels=['night', 'morning', 'afternoon', 'evening'],
        right=False
    )
    return df

df = load_data()

# -----------------------------------------------------
# DASHBOARD TITLE
# -----------------------------------------------------
st.title("🚲 Bike Sharing Demand Dashboard")
st.write("Interactive dashboard to explore Washington DC bike rental patterns.")

# -----------------------------------------------------
# WIDGETS (3 or more required)
# -----------------------------------------------------
years = st.multiselect("Select Year(s):", options=sorted(df['year'].unique()), default=[2011, 2012])
season = st.selectbox("Select Season:", options=['All'] + list(df['season_name'].unique()))
hour_range = st.slider("Select Hour Range:", 0, 23, (0, 23))

# FILTER DATA
filtered = df[df['year'].isin(years)]
if season != "All":
    filtered = filtered[filtered['season_name'] == season]
filtered = filtered[(filtered['hour'] >= hour_range[0]) & (filtered['hour'] <= hour_range[1])]
# -----------------------------
# KPI CARDS
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

total = int(filtered["count"].sum())
avg_per_hour = float(filtered.groupby("hour")["count"].mean().mean())
peak_hour = int(filtered.groupby("hour")["count"].mean().idxmax())
peak_hour_val = float(filtered.groupby("hour")["count"].mean().max())

c1.metric("Total rentals (filtered)", f"{total:,}")
c2.metric("Avg rentals/hour", f"{avg_per_hour:,.0f}")
c3.metric("Peak hour", f"{peak_hour}:00")
c4.metric("Peak hour avg", f"{peak_hour_val:,.0f}")


# -----------------------------------------------------
# PLOT 1 — Mean count by hour
# -----------------------------------------------------
st.subheader("📈 Mean Bike Rentals by Hour")
hour_mean = filtered.groupby('hour')['count'].mean().reset_index()
fig1 = px.line(hour_mean, x='hour', y='count', markers=True)
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------------------------------
# PLOT 2 — Mean by season
# -----------------------------------------------------
st.subheader("🌦 Mean Rentals by Weather Condition")
weather_mean = filtered.groupby('weather_name')['count'].mean().reset_index()
fig2 = px.bar(weather_mean, x='weather_name', y='count')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------
# PLOT 3 — Mean rentals by day_period & working day
# -----------------------------------------------------
st.subheader("🕒 Mean Rentals by Day Period")
dayp = filtered.groupby(['day_period'])['count'].mean().reset_index()
fig3 = px.bar(dayp, x='day_period', y='count')
st.plotly_chart(fig3, use_container_width=True)

if {"weekday", "hour", "count"}.issubset(filtered.columns):
    st.subheader("🔥 Demand Heatmap: Hour vs Weekday")
    heat = (
        filtered.pivot_table(index="weekday", columns="hour", values="count", aggfunc="mean")
        .reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    )
    fig_h = px.imshow(heat, aspect="auto")
    st.plotly_chart(fig_h, use_container_width=True)


# -----------------------------------------------------
# SUMMARY TEXT
# -----------------------------------------------------
st.subheader("📌 Insights")
st.write("""
- Rentals vary strongly by hour — morning and evening peaks.
- Seasonal patterns show highest rentals in summer/fall.
- Weather heavily affects bike usage.
""")

