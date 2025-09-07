import re
import streamlit as st
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "links.json"

# =============================
# Data Load Functions
# =============================
def load_data():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def extract_unique(data, fields):
    values = set()
    for item in data:
        for field in fields:
            val = str(item.get(field, "")).strip()
            if val and val != "-":
                values.add(val)
    return sorted(values)

# Load initial data
data = load_data()
df = pd.DataFrame(data)

# Normalize positions
for pos_field in ["pos_1", "pos_2", "pos_3"]:
    df[pos_field] = df[pos_field].astype(str)
for movie in data:
    for pos_field in ["pos_1", "pos_2", "pos_3"]:
        movie[pos_field] = str(movie.get(pos_field, ""))

# =============================
# Streamlit Config
# =============================
st.set_page_config(page_title="Links Explorer", layout="wide")
st.title("🎬 Links Explorer")

# =============================
# 🔍 FILTERS (Sidebar)
# =============================
st.sidebar.markdown("## 🔍 Filters")

cat_fields = ["cat_1", "cat_2", "cat_3", "cat_4", "cat_5", "cat_6"]

duration_range = st.sidebar.slider("Duration (minutes)", 0, 300, (60, 150))
rating_range = st.sidebar.slider("Rating Range", 1, 10, (1, 10))

core_cats = extract_unique(data, ["core_cat"])
core_cat_selected = st.sidebar.multiselect("Core Categories", core_cats)

all_cats = extract_unique(data, cat_fields)
cats_selected = st.sidebar.multiselect("Other Categories", all_cats)

tag_search = st.sidebar.text_input("Tags (comma-separated)")

all_actors = extract_unique(data, ["star_1", "star_2", "star_3"])
actors_selected = st.sidebar.multiselect("Actors", all_actors)

all_studios = extract_unique(data, ["studio"])
studio_selected = st.sidebar.multiselect("Studios", all_studios)

all_positions = extract_unique(data, ["pos_1", "pos_2", "pos_3"])
positions_selected = st.sidebar.multiselect("Positions", all_positions)

# =============================
# 🎯 Filter Logic
# =============================
def matches_filters(movie):
    try:
        duration = int(movie.get("duration", 0))
    except ValueError:
        duration = 0
    if not (duration_range[0] <= duration <= duration_range[1]):
        return False

    try:
        rate = float(movie.get("rate", 0))
    except ValueError:
        rate = 0
    if not (rating_range[0] <= rate <= rating_range[1]):
        return False

    if core_cat_selected and movie.get("core_cat", "") not in core_cat_selected:
        return False

    movie_cats = [str(movie.get(cat, "")).strip().lower() for cat in cat_fields]
    if cats_selected and not any(cat.lower() in movie_cats for cat in cats_selected):
        return False

    movie_actors = [movie.get("star_1", ""), movie.get("star_2", ""), movie.get("star_3", "")]
    if actors_selected and not all(actor in movie_actors for actor in actors_selected):
        return False

    movie_positions = [movie.get("pos_1", ""), movie.get("pos_2", ""), movie.get("pos_3", "")]
    if positions_selected and not any(pos in movie_positions for pos in positions_selected):
        return False

    if studio_selected and movie.get("studio", "") not in studio_selected:
        return False

    if tag_search:
        tags = [t.strip().lower() for t in tag_search.split(",") if t.strip()]
        movie_tags = str(movie.get("general_tags", "")).lower()
        if not all(tag in movie_tags for tag in tags):
            return False

    return True

# Filter the data
filtered = list(filter(matches_filters, data))
df_filtered = pd.DataFrame(filtered)

# =============================
# 🔀 Sorting Controls (strip layout)
# =============================
st.markdown(f"### 🎞️ Filtered Links — {len(df_filtered)} result(s) displayed")

cols = st.columns([3, 3, 3])
with cols[0]:
    primary_sort = st.radio("Priority", ["Duration", "Rating", "None"], horizontal=True)
with cols[1]:
    dur_order = st.radio("Duration", ["Max", "Min", "None"], horizontal=True)
with cols[2]:
    rate_order = st.radio("Rating", ["Max", "Min", "None"], horizontal=True)

# =============================
# Apply Sorting
# =============================
sort_instructions = []

if primary_sort == "Duration":
    if dur_order != "None":
        sort_instructions.append(("duration", dur_order == "Min"))
    if rate_order != "None":
        sort_instructions.append(("rate", rate_order == "Min"))
elif primary_sort == "Rating":
    if rate_order != "None":
        sort_instructions.append(("rate", rate_order == "Min"))
    if dur_order != "None":
        sort_instructions.append(("duration", dur_order == "Min"))

for col_name, ascending in reversed(sort_instructions):
    df_filtered = df_filtered.sort_values(by=col_name, ascending=ascending)

# =============================
# Display Cards (2-column layout)
# =============================
st.markdown(
    """
    <style>
    [data-testid="stSidebar"]{
      min-width: 0px;
      max-width: 450px;
      }
    .movie-card {
    font-size: 18px;
    padding: 12px;
    margin-bottom: 1px;
    margin-top: 1px;
    margin-left: 1px;
    margin-right: 1px;
    border-radius: 0px;
    background-color: #000;
    border: 1px
    solid #999;
    }
    .movie-link {
    font-color: #0095ff;
    margin-top: 12px;
    font-size: 18px;
    }
    .stApp {
        background-color: #; /* Replace with your desired color */
    }
    </style>
    """, unsafe_allow_html=True
)

if len(df_filtered) > 0:
    def merge_fields(row, fields):
        return ", ".join([str(row.get(f, "")).strip() for f in fields if str(row.get(f, "")).strip() not in ["", "-"]])

    # Display cards in 2 columns
    for i in range(0, len(df_filtered), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(df_filtered):
                movie = df_filtered.iloc[i + j]
                stars = merge_fields(movie, ["star_1", "star_2", "star_3"])
                cats = merge_fields(movie, cat_fields)
                positions = merge_fields(movie, ["pos_1", "pos_2", "pos_3"])

                with cols[j]:
                    st.markdown(
                        f"""
                        <div class="movie-card">
                            <p><b>🎥 Duration:</b> {movie.get('duration', '?')} min | <b>⭐</b> {movie.get('rate', '?')}</p>
                            <p><b>Studio:</b> {movie.get('studio', '')}</p>
                            <p><b>Core:</b> {movie.get('core_cat', '')}</p>
                            <p><b>Stars:</b> {stars}</p>
                            <p><b>Categories:</b> {cats}</p>
                            <p><b>Positions:</b> {positions}</p>
                            <p><b>Tags:</b> {movie.get('general_tags', '')}</p>
                            <p class="movie-link"><a href="{movie.get('main_link', '')}" target="_blank">🔗Open</a></p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
else:
    st.info("No movies match your filters.")