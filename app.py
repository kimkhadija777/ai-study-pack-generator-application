import streamlit as st

from workflow import (
    generate_study_pack,
    WorkflowError
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📚 AI Study Pack Generator")

st.caption(
    "Personalized multi-stage study pack powered by Groq"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📋 Study Preferences")

    subject = st.text_input(
        "Subject",
        "Computer Networks"
    )

    topic = st.text_input(
        "Topic",
        "OSI Model"
    )

    level = st.selectbox(
        "Student Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

    days = st.number_input(
        "Study Days",
        min_value=1,
        max_value=30,
        value=3,
        step=1
    )

    language = st.selectbox(
        "Language",
        [
            "English",
            "Urdu",
            "Roman Urdu"
        ]
    )

    generate = st.button(
        "🚀 Generate Study Pack",
        type="primary",
        use_container_width=True
    )


# ============================================================
# GENERATE
# ============================================================

if generate:

    if not subject.strip() or not topic.strip():

        st.error(
            "Please enter both a subject and topic."
        )

    else:

        progress = st.progress(0)

        status = st.empty()

        try:

            def update(stage, percent):

                status.info(stage)

                progress.progress(percent)


            result = generate_study_pack(

                subject=subject.strip(),

                topic=topic.strip(),

                level=level,

                study_days=int(days),

                language=language,

                progress_callback=update
            )


            progress.progress(100)

            status.success(
                "🎉 Study pack generated successfully!"
            )


            # =================================================
            # TABS
            # =================================================

            tabs = st.tabs(
                [
                    "📚 Final Pack",
                    "🗺️ Plan",
                    "📖 Content",
                    "❓ Assessment",
                    "🔎 Review"
                ]
            )


            with tabs[0]:

                st.markdown(
                    result["final_pack"]
                )


            with tabs[1]:

                st.markdown(
                    result["plan"]
                )


            with tabs[2]:

                st.markdown(
                    result["content"]
                )


            with tabs[3]:

                st.markdown(
                    result["assessment"]
                )


            with tabs[4]:

                st.markdown(
                    result["review"]
                )


        except WorkflowError as e:

            progress.empty()

            status.empty()

            st.error(str(e))


        except Exception as e:

            progress.empty()

            status.empty()

            st.error(
                "Something unexpected went wrong. "
                "Please try again."
            )

            st.exception(e)
