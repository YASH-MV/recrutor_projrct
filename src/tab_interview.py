import streamlit as st
from datetime import date, datetime
from . import data
from . import plots
import pandas as pd


METRICS = ["Communication", "Technical Skills", "Projects", "Problem Solving", "Culture Fit"]


def show_interview():
    st.header("🏢 Interview Evaluation")
    st.markdown("Create interview sessions, add candidates, and evaluate them using standardized metrics.")
    
    # Tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📝 Session Management", "👥 Candidate Evaluation", "📊 Quick Analytics"])
    
    with tab1:
        show_session_management()
    
    with tab2:
        show_candidate_evaluation()
    
    with tab3:
        show_quick_analytics()


def show_session_management():
    """Session creation and management"""
    st.subheader("Create New Session")
    
    with st.form("create_session", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Session Name *", value=f"Session {date.today()}", help="Name for this interview round")
            interviewer = st.text_input("Interviewer", help="Name of the interviewer/panel lead")
        
        with col2:
            session_date = st.date_input("Date", value=date.today())
            position = st.text_input("Position/Role", help="Job position being filled")
        
        notes = st.text_area("Session Notes (optional)", help="Additional context about this interview round")
        
        submitted = st.form_submit_button("✨ Create Session", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("Please enter a session name")
            else:
                sid = data.create_session(
                    name=name,
                    interviewer=interviewer or None,
                    date=str(session_date),
                    notes=notes or None
                )
                st.success(f"✅ Created session: **{name}**")
                st.rerun()
    
    st.divider()
    
    # List existing sessions
    st.subheader("Existing Sessions")
    sessions = data.list_sessions()
    
    if not sessions:
        st.info("No sessions yet. Create one above to get started.")
        return
    
    # Session selector
    session_options = {f"{s['name']} ({s.get('date', 'N/A')})": s['id'] for s in sessions}
    selected_session = st.selectbox("Select Session to View", list(session_options.keys()))
    selected_session_id = session_options[selected_session]
    
    # Display session details
    selected_session_data = next((s for s in sessions if s['id'] == selected_session_id), None)
    
    if selected_session_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Interviewer", selected_session_data.get('interviewer', 'N/A'))
        with col2:
            st.metric("Date", selected_session_data.get('date', 'N/A'))
        with col3:
            candidates_count = len(data.list_candidates(selected_session_id))
            st.metric("Candidates", candidates_count)
        
        if selected_session_data.get('notes'):
            with st.expander("Session Notes"):
                st.write(selected_session_data['notes'])


def show_candidate_evaluation():
    """Candidate addition and scoring"""
    sessions = data.list_sessions()
    
    if not sessions:
        st.info("Please create a session first in the Session Management tab.")
        return
    
    session_options = {f"{s['name']} ({s.get('date', 'N/A')})": s['id'] for s in sessions}
    selected_session = st.selectbox("Select Session", list(session_options.keys()), key="eval_session")
    session_id = session_options[selected_session]
    
    st.subheader("Add Candidate")
    
    with st.form("add_candidate", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            cname = st.text_input("Full Name *", help="Candidate's full name")
            email = st.text_input("Email", help="Email address")
            phone = st.text_input("Phone", help="Contact number")
        
        with col2:
            position = st.text_input("Position Applied", help="Job position")
            exp = st.number_input("Experience (years)", min_value=0, max_value=50, value=0)
        
        notes = st.text_area("Candidate Notes", help="Any additional notes about the candidate")
        
        add = st.form_submit_button("➕ Add Candidate", use_container_width=True)
        
        if add:
            if not cname:
                st.error("Please enter candidate name")
            else:
                cid = data.add_candidate(
                    session_id,
                    cname,
                    email=email or None,
                    phone=phone or None,
                    position=position or None,
                    experience_years=int(exp) if exp else None,
                    notes=notes or None
                )
                st.success(f"✅ Added candidate: **{cname}**")
                st.rerun()
    
    st.divider()
    st.subheader("Evaluate Candidates")
    
    candidates = data.list_candidates(session_id)
    
    if not candidates:
        st.info("No candidates in this session yet. Add candidates above.")
        return
    
    # Display candidates with scoring
    for idx, cand in enumerate(candidates):
        with st.container():
            # Candidate header
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"### 👤 {cand['name']}")
                info_parts = []
                if cand.get('position'):
                    info_parts.append(f"**Position:** {cand['position']}")
                if cand.get('experience_years'):
                    info_parts.append(f"**Experience:** {cand['experience_years']} years")
                if info_parts:
                    st.markdown(" | ".join(info_parts))
            
            with col2:
                scores = data.get_scores_for_candidate(cand['id'])
                if scores:
                    score_dict = {s['metric']: s['value'] for s in scores}
                    avg_score = sum(score_dict.values()) / len(score_dict) if score_dict else 0
                    st.metric("Average Score", f"{avg_score:.2f}/10")
                else:
                    st.info("Not evaluated")
            
            with col3:
                if st.button("📝 Score", key=f"score_btn_{cand['id']}", use_container_width=True):
                    st.session_state[f'scoring_{cand["id"]}'] = True
            
            # Scoring form (expandable)
            if st.session_state.get(f'scoring_{cand["id"]}', False):
                with st.expander(f"Score Candidate: {cand['name']}", expanded=True):
                    _score_candidate(cand['id'], cand['name'], session_id)
            
            # Display existing scores
            if scores:
                score_df = pd.DataFrame(scores)
                st.dataframe(
                    score_df.rename(columns={'metric': 'Metric', 'value': 'Score'}),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Quick visualization
                if len(scores) > 0:
                    fig = plots.plot_candidate_scores(scores, cand['name'])
                    st.plotly_chart(fig, use_container_width=True)
            
            st.divider()


def _score_candidate(candidate_id, name, session_id):
    """Score a candidate with all metrics"""
    existing_scores = data.get_scores_for_candidate(candidate_id)
    existing_dict = {s['metric']: s['value'] for s in existing_scores}
    
    with st.form(f"score_form_{candidate_id}"):
        st.markdown(f"**Evaluating:** {name}")
        
        vals = {}
        cols = st.columns(2)
        
        for idx, m in enumerate(METRICS):
            with cols[idx % 2]:
                default_val = existing_dict.get(m, 5.0)
                vals[m] = st.slider(
                    f"{m}",
                    0.0,
                    10.0,
                    float(default_val),
                    0.5,
                    key=f"{candidate_id}_{m}",
                    help=f"Rate {m} on a scale of 0-10"
                )
        
        note = st.text_area(
            "Interviewer Notes",
            help="Detailed notes about the candidate's performance",
            key=f"notes_{candidate_id}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            sub = st.form_submit_button("💾 Save Scores", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state[f'scoring_{candidate_id}'] = False
            st.rerun()
        
        if sub:
            # Delete existing scores for this candidate
            data.delete_candidate_scores(candidate_id)
            
            # Add new scores
            for metric, val in vals.items():
                data.add_score(candidate_id, metric, float(val))
            
            # Save notes if provided
            if note:
                data.update_candidate_notes(candidate_id, note)
            
            st.success(f"✅ Scores saved for {name}!")
            st.session_state[f'scoring_{candidate_id}'] = False
            st.rerun()


def show_quick_analytics():
    """Quick analytics for the current session"""
    sessions = data.list_sessions()
    
    if not sessions:
        st.info("No sessions available.")
        return
    
    session_options = {f"{s['name']} ({s.get('date', 'N/A')})": s['id'] for s in sessions}
    selected_session = st.selectbox("Select Session", list(session_options.keys()), key="analytics_session")
    session_id = session_options[selected_session]
    
    candidates = data.list_candidates(session_id)
    
    if not candidates:
        st.info("No candidates in this session.")
        return
    
    # Get all scores
    all_data = []
    for cand in candidates:
        scores = data.get_scores_for_candidate(cand['id'])
        if scores:
            row = {'Candidate': cand['name']}
            for score in scores:
                row[score['metric']] = score['value']
            row['Average'] = sum(s['value'] for s in scores) / len(scores)
            all_data.append(row)
    
    if not all_data:
        st.info("No scores available yet.")
        return
    
    df = pd.DataFrame(all_data)
    
    st.subheader("Quick Overview")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Top performers
    if len(df) > 0:
        st.subheader("Top Performers")
        top_avg = df.nlargest(3, 'Average')[['Candidate', 'Average']]
        st.dataframe(top_avg, use_container_width=True, hide_index=True)

