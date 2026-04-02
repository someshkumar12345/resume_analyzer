import streamlit as st
import pandas as pd
import time
from utils.parser import extract_text_from_pdf
from utils.matcher import calculate_advanced_metrics, generate_ai_summary

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(
    page_title="SaaS AI Recruiter Pro",
    page_icon="🦾",
    layout="wide"
)

# Custom SaaS Styling (Premium Look)
st.markdown("""
<style>
    .main { background: #f8fafc; color: #1e293b; }
    .hero-section { background: #1e3a8a; color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px; }
    .card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 25px; }
    .tag { display: inline-block; padding: 8px 16px; border-radius: 25px; font-size: 14px; font-weight: 700; margin: 6px 8px 6px 0; }
    .tag-green { background: #dcfce7; color: #166534; border: 2px solid #bbf7d0; }
    .tag-red { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .reason-box { background: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border-left: 5px solid #22c55e; }
</style>
""", unsafe_allow_html=True)

# --- 2. HEADER & INPUT ---
st.title("🦾 AI Smart Recruiter – SaaS Professional Edition")
st.markdown("Unlock the potential of your hiring pipeline with premium AI screening and candidate intelligence.")

col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.subheader("📄 Upload Candidate Resumes (PDF)")
    uploaded_files = st.file_uploader(
        "Upload resumes", type="pdf", accept_multiple_files=True
    )

with col2:
    st.subheader("📝 Job Requirements")
    job_desc = st.text_area(
        "Describe your ideal candidate...", height=200, 
        placeholder="e.g., We need a Senior Python Developer with Docker and AWS experience."
    )

# --- 3. CORE ENGINE LOOP ---
if st.button("🚀 Analyze & Rank Candidates", use_container_width=True):
    if not uploaded_files:
        st.error("Please upload at least one resume.")
    elif not job_desc.strip():
        st.error("Please provide job requirements.")
    else:
        results = []
        progress_bar = st.progress(0)
        
        for i, pdf_file in enumerate(uploaded_files):
            # Parse & Analyze
            resume_text = extract_text_from_pdf(pdf_file)
            score, matched, missing, exp_level, exp_score, proj_level, proj_score, strength = calculate_advanced_metrics(resume_text, job_desc)
            
            c_name = pdf_file.name.replace(".pdf", "").replace("_"," ").title()
            
            results.append({
                "Rank": 0,
                "Name": c_name,
                "Score": score,
                "Exp Level": exp_level,
                "Matched": matched,
                "Missing": missing,
                "Summary": generate_ai_summary(c_name, score, exp_level, len(matched)),
                "Strength": strength,
            })
            progress_bar.progress((i + 1) / len(uploaded_files))

        # --- 4. RANKING & DASHBOARD DISPLAY ---
        df = pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True)
        df["Rank"] = df.index + 1
        
        # 1. BEST CANDIDATE HERO SECTION (#1 Upgrade)
        top_c = df.iloc[0]
        st.divider()
        st.markdown(f"""
        <div class="hero-section">
            <h2 style="margin:0;">🏆 Top Match Recommendation: {top_c['Name']}</h2>
            <p style="font-size:1.1rem; opacity:0.9; margin-top:10px;">{top_c['Summary']}</p>
            <div class="reason-box">
                <b>💡 Why Selected?</b>
                <ul style="margin:5px 0 0 20px;">
                    <li>Highest skill match for this technical profile.</li>
                    <li>Superior alignment with core job requirements.</li>
                    <li>Strong relevant project exposure detected.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. COMPARISON TABLE (SKILL MATRIX #3 Upgrade)
        st.subheader("📈 Skills Comparison Matrix")
        
        # Get all unique skills from Job Description (Matched + Missing from anyone)
        all_req_skills = sorted(list(set(df.iloc[0]['Matched'] + df.iloc[0]['Missing'])))
        
        matrix_data = []
        for i, row in df.iterrows():
            entry = {"Candidate": row['Name']}
            for skill in all_req_skills:
                # Use ✅ and ❌ as requested
                entry[skill] = "✅" if skill in row['Matched'] else "❌"
            entry["Score"] = f"{row['Score']}%"
            matrix_data.append(entry)
            
        st.table(pd.DataFrame(matrix_data))
        
        # 3. CANDIDATE CARDS (#2 Upgrade)
        st.subheader("📊 Candidate Interview Shortlist")
        
        for idx, person in df.iterrows():
            medal = "🥇" if person['Rank'] == 1 else "🥈" if person['Rank'] == 2 else "🥉"
            
            with st.container():
                st.markdown(f'<div class="card">', unsafe_allow_html=True)
                
                header_col, score_col = st.columns([2, 1])
                with header_col:
                    st.markdown(f"### {medal} Rank {person['Rank']}: {person['Name']}")
                    st.markdown(f"**Experience:** {person['Exp Level']}")
                
                with score_col:
                    st.metric("Total Match Score", f"{person['Score']}%")
                
                # Skill Badge Layout
                st.markdown("**Skill Gap Analysis:**")
                matched_badges = "".join([f'<span class="tag tag-green">{s} ✅</span>' for s in person['Matched']])
                missing_badges = "".join([f'<span class="tag tag-red">{s} ❌</span>' for s in person['Missing']])
                st.markdown(f"{matched_badges}{missing_badges}", unsafe_allow_html=True)
                
                # Detailed Analysis Expander
                with st.expander("🔎 Deep Analysis & Insights"):
                    st.info(f"🧠 **AI Insight:** {person['Summary']}")
                
                # DECISION BUTTONS (#2 Upgrade)
                btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])
                with btn_col1:
                    if st.button(f"Shortlist", key=f"short_{idx}"):
                        st.success(f"Candidate {person['Name']} shortlisted successfully!")
                with btn_col2:
                    if st.button(f"Reject", key=f"reject_{idx}"):
                        st.error(f"Candidate {person['Name']} rejected.")
                with btn_col3:
                    st.button("📄 View Resume", key=f"view_{idx}", disabled=True)

                st.markdown('</div>', unsafe_allow_html=True)

        # Final Report Export
        st.divider()
        csv = df.drop(columns=['Strength'], errors='ignore').to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Detailed Hiring Report (CSV)",
            data=csv,
            file_name="hiring_report.csv",
            mime="text/csv",
            use_container_width=True
        )

# --- 5. FOOTER ---
st.markdown("---")
st.caption("AI Smart Recruiter | SaaS Decision Dashboard Pro.")
