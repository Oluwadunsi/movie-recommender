from recommender import recommend  # Movie recommendation logic
import streamlit as st                      # Streamlit Web UI

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="centered")
st.title("🎬 Movie Recommender")
st.markdown("**What should I watch tonight on?** – Tell me your mood or vibe, and I'll find the perfect movie for you!")

user_input = st.text_input(
    "Tell me your mood or vibe",
    placeholder="e.g. something funny but clever, cozy christmas movie, intense thriller..."
)

if st.button("Find my movie!") or user_input:
    if user_input.strip():
        with st.spinner("Searching the catalog…"):
            results = recommend(user_input)

        if results:
            st.success(f"Here are {len(results)} perfect picks for you!")
            for movie in results:
                col1, col2 = st.columns([1, 3])
                with col1:
                    poster = movie["Poster"]
                    if poster and poster != "N/A":
                        st.image(poster, use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x450?text=No+Poster", use_column_width=True)
                with col2:
                    st.subheader(f"{movie['Title']} ({movie.get('Year', '?')})")
                    st.write(movie["Plot"])
                    st.caption(f"IMDb: {movie['Rating']}/10 • Mood match: {movie['mood_score']}")
                st.markdown("---")
        else:
            st.warning("No good matches found – try different words!")
    else:
        st.info("Type something above ↑")

# Footer 
st.markdown("---")
st.caption("Non-commercial demo - Data from OMDb API - Built by Eunice Adeniyi")
